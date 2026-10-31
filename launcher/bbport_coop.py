"""Bundled mark3317 BBSC fork and local co-op services.
Client binaries ship with the launcher; mutable accounts, saves and journals stay in
LOCALAPPDATA. Upstream authors and licences are recorded in THIRD_PARTY.md.
"""
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
import zipfile

REPO = 'mark3317/BBSC'
RELEASES = f'https://github.com/{REPO}/releases'
DISCORD = 'https://discord.gg/Df7BCmfWdt'
# The BBSC packages this launcher uses, found by name in BBSC's GitHub releases: the newest
# release that has one is installed, so a new BBSC version needs no launcher update.
#   client: BBSC-<version>-BBport.zip (bbsc.dll, bbsc-launch.exe, the account tool, BBSC's own
#           BBport build in emulator\)
#   server: BBSC-<version>-Server.zip (shadnet.exe, BBSC-GameServer.exe) - only for hosting
ASSET_PATTERNS = {'client': r'BBSC-(?P<version>[0-9][^-]*)-BBport\.zip',
                  'server': r'BBSC-(?P<version>[0-9][^-]*)-Server\.zip'}
# Where each package lives under %LOCALAPPDATA%\bbport-coop, and the folders of the 0.0.1 era
# (fixed names) still used when they are all there is.
PACKAGE_FOLDERS = {'client': 'bbsc-client', 'server': 'bbsc-server'}
LEGACY_FOLDERS = {'client': 'BBSC-0.0.1-BBport', 'server': 'BBSC-0.0.1-Server'}
VERSION_FILE = 'bbport-package.json'
# What survives an update of a package: logs, backups and BBSC's own files about the player's
# world; the host's server keeps its accounts and registration key.
KEEP_ON_UPDATE = {'client': ('bbsc/logs', 'bbsc/save-backups', 'bbsc/own-world', 'bbsc/captures',
                             'tools/account.dat'),
                  'server': ('server/shadnet.cfg', 'server/db', 'server/logs')}
SHADNET_PORT, MATCHING_PORT, WEBAPI_PORT, GAME_PORT, RELAY_PORT = 31313, 31314, 31315, 20443, 20444
INVITE_PREFIX = 'BBCOOP-'
NO_WINDOW = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
# Tailscale's own address on every tailnet: a route to it goes out through the Tailscale adapter.
TAILSCALE_DNS = '100.100.100.100'
# Inbound rules for hosting: the server ports, from Tailscale's range and this PC's own networks
# only. The game itself takes the other players' P2P connections from anywhere (a co-op server
# on the internet: the players' PCs talk directly, or through the server's relay).
FIREWALL_RANGES = ('100.64.0.0/10', 'LocalSubnet')
FIREWALL_PORTS = (('shadnet', 'TCP', SHADNET_PORT), ('matching', 'UDP', MATCHING_PORT),
                  ('webapi', 'TCP', WEBAPI_PORT), ('game server', 'TCP', GAME_PORT),
                  ('relay', 'TCP', RELAY_PORT), ('sessions', 'TCP', 18671), ('STUN', 'UDP', 3478))
RULE_PREFIX = 'Bloodborne co-op'
# Shipped with a launcher package (next to Bloodborne.exe):
#   coop-server.json  {"name": "...", "invite": "BBCOOP-..."} - the co-op server players join when
#                     their own invite code is empty (a friends' package: name, password, Play)
#   coop/bbsc/        a BBSC build of our own (bbsc.dll, bbsc-launch.exe) with coop/bbsc.json
#                     {"base": "<BBSC version>"}: put over the official files of that version only
DEFAULT_SERVER_FILE = 'coop-server.json'
OVERRIDE_DIR = Path('coop') / 'bbsc'
OVERRIDE_FILE = Path('coop') / 'bbsc.json'


class CoopError(Exception):
    pass


def port_dir():
    frozen = getattr(sys, 'frozen', False)
    return Path(sys.executable).resolve().parent if frozen else Path(__file__).resolve().parent.parent


def coop_dir():
    from bbport_paths import profile_dir
    return profile_dir() / 'coop'


def package_dir(kind):
    return port_dir() / 'coop' / kind


def installed(kind):
    folder = package_dir(kind)
    if kind == 'client':
        return all((folder / p).is_file() for p in ('bbsc/bbsc-launch.exe', 'bbsc/bbsc.dll',
                                                     'account/shadnet-sample.exe'))
    return all((folder / 'server' / p).is_file() for p in ('shadnet.exe', 'BBSC-GameServer.exe',
                                                            'shadnet.cfg'))


def installed_version(kind):
    try:
        return str(json.loads((package_dir(kind) / 'bundle.json').read_text(encoding='utf-8'))['version'])
    except (OSError, ValueError, KeyError, TypeError):
        return ''


def _version_key(version):
    return tuple(int(part) if part.isdigit() else 0 for part in re.split(r'[.\-_]', version))


# --- Download -------------------------------------------------------------------------------------

def _github(path):
    request = urllib.request.Request(f'https://api.github.com/repos/{REPO}/{path}',
                                     headers={'User-Agent': 'bbport-launcher',
                                              'Accept': 'application/vnd.github+json'})
    with urllib.request.urlopen(request, timeout=30) as reply:
        return json.load(reply)


def latest_release(kind):
    """(version, tag, asset name, url, sha256) of the newest BBSC release with this package."""
    pattern = re.compile(ASSET_PATTERNS[kind])
    found = []
    for release in _github('releases?per_page=30'):
        if release.get('draft'):
            continue
        for asset in release.get('assets', []):
            match = pattern.fullmatch(str(asset.get('name', '')))
            if not match:
                continue
            digest = str(asset.get('digest') or '')
            if not digest.startswith('sha256:'):
                continue  # nothing to check it against
            found.append((match['version'], str(release.get('tag_name', '')), asset['name'],
                          asset['browser_download_url'], digest.split(':', 1)[1].lower(),
                          str(release.get('published_at', ''))))
    if not found:
        raise CoopError(f'No BBSC release has a {ASSET_PATTERNS[kind]} package ({RELEASES}).')
    found.sort(key=lambda item: (_version_key(item[0]), item[5]))
    return found[-1][:5]


def update_available(kind):
    have = installed_version(kind) if installed(kind) else ''
    source = port_dir() / 'coop' / kind / 'bundle.json'
    if not source.is_file():
        raise CoopError('Bundled co-op files are missing. Re-extract the launcher release.')
    newest = json.loads(source.read_text(encoding='utf-8'))['version']
    return have, newest if have != newest else ''


def _safe_extract(archive, destination):
    root = destination.resolve()
    for member in archive.infolist():
        target = (destination / member.filename).resolve()
        if root != target and root not in target.parents:
            raise CoopError(f'Unsafe path in the package: {member.filename}')
    archive.extractall(destination)


def _package_root(staging):
    """The package's own folder inside an unpacked zip (BBSC-<version>-BBport\\), or the zip's root."""
    entries = [entry for entry in staging.iterdir() if not entry.name.startswith('__MACOSX')]
    return entries[0] if len(entries) == 1 and entries[0].is_dir() else staging


def _install(kind, zip_path, version, source):
    staging = Path(tempfile.mkdtemp(prefix='.bbsc-unpack-', dir=coop_dir()))
    try:
        with zipfile.ZipFile(zip_path) as archive:
            _safe_extract(archive, staging)
        new = _package_root(staging)
        probe = 'bbsc/bbsc.dll' if kind == 'client' else 'server/shadnet.exe'
        if not (new / probe).is_file():
            raise CoopError(f'{Path(zip_path).name} is not a BBSC {kind} package (no {probe}).')
        old = package_dir(kind)
        if old.is_dir():
            for keep in KEEP_ON_UPDATE[kind]:
                if (old / keep).exists():
                    target = new / keep
                    if target.is_dir():
                        shutil.rmtree(target)
                    elif target.exists():
                        target.unlink()
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(old / keep), str(target))
        if not version and kind == 'client':
            try:
                version = str(json.loads((new / 'bbsc' / 'mod.json').read_text(encoding='utf-8'))['version'])
            except (OSError, ValueError, KeyError, TypeError):
                version = ''
        (new / VERSION_FILE).write_text(json.dumps({'version': version, 'source': source}, indent=2) + '\n',
                                        encoding='utf-8')
        folder = coop_dir() / PACKAGE_FOLDERS[kind]
        if folder.exists():
            shutil.rmtree(folder)
        shutil.move(str(new), str(folder))
        legacy = coop_dir() / LEGACY_FOLDERS[kind]
        if legacy.is_dir() and legacy != folder:
            shutil.rmtree(legacy, ignore_errors=True)  # its kept files moved over above
    finally:
        shutil.rmtree(staging, ignore_errors=True)
    if kind == 'client':
        apply_override()
    return folder


def download(kind, progress=None):
    """Compatibility entry point: validate installed binaries, never copy them to the profile."""
    from bbport_bundle import verify
    try:
        return verify(package_dir(kind))
    except (OSError, ValueError, KeyError) as error:
        raise CoopError(f'Bundled co-op files are damaged. Re-extract the launcher release: {error}') from error


def install_zip(kind, zip_path, progress=None):
    """Installs a BBSC package zip the player downloaded (a test build, or no GitHub access)."""
    coop_dir().mkdir(parents=True, exist_ok=True)
    if progress:
        progress(f'Installing {Path(zip_path).name}…')
    _install(kind, Path(zip_path), '', str(zip_path))
    return installed_version(kind)


def apply_override():
    """Synchronize the pinned fork; old package versions are no longer a dependency."""
    return download('client')


def default_invite():
    """The co-op server a launcher package was made for (coop-server.json), or ''."""
    try:
        data = json.loads((port_dir() / DEFAULT_SERVER_FILE).read_text(encoding='utf-8'))
        return str(data.get('invite', '')).strip()
    except (OSError, ValueError, AttributeError):
        return ''


def default_server_name():
    try:
        data = json.loads((port_dir() / DEFAULT_SERVER_FILE).read_text(encoding='utf-8'))
        return str(data.get('name', '')).strip()
    except (OSError, ValueError, AttributeError):
        return ''


def bbsc_emulator():
    """BBSC's own BBport build in the client package (emulator\\bb-probe.exe), or None."""
    probe = package_dir('client') / 'emulator' / 'bb-probe.exe'
    return probe if probe.is_file() else None


# --- Network ---------------------------------------------------------------------------------------

def tailscale_exe():
    """tailscale.exe: on PATH (the installer adds it, wherever it was installed), else the default folder."""
    # Full name, not bare 'tailscale': what which() returns is then unambiguously the
    # file we hand to subprocess.run, not 'tailscale' + whichever PATHEXT entry matched.
    found = shutil.which('tailscale.exe')
    if found:
        return Path(found)
    for variable in ('ProgramW6432', 'ProgramFiles'):
        folder = os.environ.get(variable)
        if folder and (Path(folder) / 'Tailscale' / 'tailscale.exe').is_file():
            return Path(folder) / 'Tailscale' / 'tailscale.exe'
    return None


def tailscale_ip():
    return _tailscale_ip_from_cli() or _tailscale_ip_from_route()


def _tailscale_ip_from_cli():
    exe = tailscale_exe()
    if not exe:
        return None
    try:
        out = subprocess.run([str(exe), 'ip', '-4'], capture_output=True, text=True,
                             timeout=10, creationflags=NO_WINDOW).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    for line in out.split():
        if is_tailscale(line):
            return line
    return None


def _tailscale_ip_from_route():
    """This PC's address on the Tailscale adapter, when the CLI can't be run (no packet is sent)."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
        try:
            probe.connect((TAILSCALE_DNS, 9))
            ip = probe.getsockname()[0]
        except OSError:
            return None
    return ip if is_tailscale(ip) else None


def is_tailscale(address):
    parts = address.split('.')
    return len(parts) == 4 and parts[0] == '100' and parts[1].isdigit() and 64 <= int(parts[1]) <= 127


def local_ip():
    """This PC's address on its home network (no packet is sent)."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
        try:
            probe.connect(('192.0.2.1', 9))
            return probe.getsockname()[0]
        except OSError:
            return None


def host_address():
    """(address, network name): Tailscale when it is connected, else the home network."""
    ip = tailscale_ip()
    if ip:
        return ip, 'Tailscale'
    ip = local_ip()
    if ip:
        return ip, 'your home network only (Tailscale is not connected)'
    return None, None


# --- One-time setup (one administrator prompt) ---------------------------------------------------

def _quoted(text):
    """A PowerShell single-quoted string: a path with an apostrophe (C:\\Users\\O'Neil) broke the
    script, and the setup then never finished."""
    return "'" + str(text).replace("'", "''") + "'"


def _firewall_script(game_exe):
    ranges = ','.join(f"'{r}'" for r in FIREWALL_RANGES)
    lines = ['$ErrorActionPreference = "Continue"', f'$ranges = @({ranges})']
    for label, protocol, port in FIREWALL_PORTS:
        rule = f'{RULE_PREFIX} {label} {port}'
        lines.append(f"Remove-NetFirewallRule -DisplayName '{rule}' -ErrorAction SilentlyContinue")
        lines.append(f"New-NetFirewallRule -DisplayName '{rule}' -Direction Inbound -Protocol {protocol} "
                     f"-LocalPort {port} -RemoteAddress $ranges -Action Allow | Out-Null")
    rule = f'{RULE_PREFIX} game'
    lines.append(f"Remove-NetFirewallRule -DisplayName '{rule}' -ErrorAction SilentlyContinue")
    lines.append(f"New-NetFirewallRule -DisplayName '{rule}' -Direction Inbound -Program {_quoted(game_exe)} "
                 "-Action Allow | Out-Null")
    redist = package_dir('server') / 'server' / 'vc_redist.x64.exe'
    lines.append("$key = 'HKLM:\\SOFTWARE\\Microsoft\\VisualStudio\\14.0\\VC\\Runtimes\\x64'")
    lines.append(f"if (-not ((Test-Path $key) -and (Get-ItemProperty $key).Installed -eq 1) -and "
                 f"(Test-Path {_quoted(redist)})) {{ Start-Process {_quoted(redist)} -ArgumentList '/install /quiet /norestart' -Wait }}")
    return '\r\n'.join(lines) + '\r\n'


def setup_done(game_exe):
    command = (f"$r = Get-NetFirewallRule -DisplayName '{RULE_PREFIX} game' -ErrorAction SilentlyContinue; "
               f"if ($r -and (($r | Get-NetFirewallApplicationFilter).Program -eq {_quoted(game_exe)})) {{ exit 0 }} else {{ exit 1 }}")
    try:
        return subprocess.run(['powershell', '-NoProfile', '-Command', command], timeout=30,
                              creationflags=NO_WINDOW).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def run_setup(game_exe):
    """Firewall rules (Tailscale and home network only) and the C++ runtime the servers need.
    Windows asks the player once for administrator rights."""
    script = coop_dir() / 'setup-firewall.ps1'
    coop_dir().mkdir(parents=True, exist_ok=True)
    script.write_text(_firewall_script(game_exe), encoding='utf-8-sig')
    if not run_as_administrator('powershell.exe', f'-NoProfile -ExecutionPolicy Bypass -File "{script}"'):
        raise CoopError('Co-op needs a Yes on the Windows administrator prompt (firewall rules); '
                        'the answer was No. Try Start hosting again.')
    if not setup_done(game_exe):
        raise CoopError('The firewall rules were not made although Windows allowed the setup. '
                        'A firewall program other than Windows Defender Firewall may manage them; '
                        f'the setup script is {script}.')


def run_as_administrator(program, parameters, verb='runas'):
    """Runs program with administrator rights, hidden, and waits for it. False when the player
    said No. The launcher asks Windows itself: a prompt requested by a process in the background
    (it was a hidden PowerShell's Start-Process -Verb RunAs) opens only as a flashing taskbar
    button, and players saw no prompt at all (#49). Asked by the launcher, whose window is in
    front after the click, it opens over it."""
    import ctypes
    from ctypes import wintypes

    class ShellExecuteInfo(ctypes.Structure):
        _fields_ = [('cbSize', wintypes.DWORD), ('fMask', ctypes.c_ulong), ('hwnd', wintypes.HWND),
                    ('lpVerb', wintypes.LPCWSTR), ('lpFile', wintypes.LPCWSTR), ('lpParameters', wintypes.LPCWSTR),
                    ('lpDirectory', wintypes.LPCWSTR), ('nShow', ctypes.c_int), ('hInstApp', wintypes.HINSTANCE),
                    ('lpIDList', ctypes.c_void_p), ('lpClass', wintypes.LPCWSTR), ('hkeyClass', wintypes.HKEY),
                    ('dwHotKey', wintypes.DWORD), ('hIconOrMonitor', wintypes.HANDLE), ('hProcess', wintypes.HANDLE)]

    shell32 = ctypes.WinDLL('shell32', use_last_error=True)
    shell32.ShellExecuteExW.argtypes = [ctypes.POINTER(ShellExecuteInfo)]
    user32, kernel32 = ctypes.windll.user32, ctypes.windll.kernel32
    user32.GetForegroundWindow.restype = wintypes.HWND
    window = user32.GetForegroundWindow()
    owner = wintypes.DWORD()
    user32.GetWindowThreadProcessId(window, ctypes.byref(owner))
    ctypes.windll.ole32.CoInitializeEx(None, 0x2 | 0x4)  # the shell wants COM on this thread
    info = ShellExecuteInfo(cbSize=ctypes.sizeof(ShellExecuteInfo),
                            fMask=0x40 | 0x100 | 0x400,  # NOCLOSEPROCESS, NOASYNC, FLAG_NO_UI (errors come back)
                            hwnd=window if owner.value == os.getpid() else None,
                            lpVerb=verb, lpFile=program, lpParameters=parameters, nShow=0)
    if not shell32.ShellExecuteExW(ctypes.byref(info)):
        error = ctypes.get_last_error()
        if error == 1223:  # ERROR_CANCELLED: the player said No
            return False
        raise CoopError(f'Windows could not run the co-op setup: {ctypes.FormatError(error)}')
    if info.hProcess:
        kernel32.WaitForSingleObject(wintypes.HANDLE(info.hProcess), 0xFFFFFFFF)
        kernel32.CloseHandle(wintypes.HANDLE(info.hProcess))
    return True


# --- Hosting -----------------------------------------------------------------------------------------

# This port's build of the co-op shadNet server (packaging/windows/build_coop_server.sh):
# Wozzardman's shadnet-p2p with one patch, so clients on shadPS4 0.20's network code (this port
# since 1.9.5) get STUN replies; BBSC's own shadnet.exe drops their signaling packets. BBSC's game
# server is used as it is.
PORT_DIR = (Path(sys.executable).resolve().parent if getattr(sys, 'frozen', False)
            else Path(__file__).resolve().parent.parent)


def bundled_server():
    for folder in (PORT_DIR / 'coop' / 'server' / 'server',
                   PORT_DIR / 'bin' / 'coop-server', PORT_DIR / 'out' / 'coop-server'):
        if (folder / 'shadnet.exe').is_file():
            return folder
    return None


def shadnet_dir(sync=False):
    """Only configuration, database and logs live in the writable profile."""
    target = coop_dir() / 'server'
    if sync:
        target.mkdir(parents=True, exist_ok=True)
        for name in ('shadnet.cfg', 'worlds.cfg', 'scoreboards.cfg'):
            source = package_dir('server') / 'server' / name
            if not (target / name).exists():
                shutil.copy2(source, target / name)
    return target


def registration_key():
    """The host's own key (created on first use): only players who have it can make accounts."""
    cfg = shadnet_dir() / 'shadnet.cfg'
    if not cfg.is_file():
        cfg = shadnet_dir(sync=True) / 'shadnet.cfg'
    text = cfg.read_text(encoding='utf-8')
    for line in text.splitlines():
        if line.startswith('RegistrationSecretKey='):
            value = line.split('=', 1)[1].strip()
            if value:
                return value
            key = secrets.token_hex(20)
            cfg.write_text(text.replace(line, f'RegistrationSecretKey={key}'), encoding='utf-8')
            return key
    key = secrets.token_hex(20)
    cfg.write_text(text.rstrip('\n') + f'\nRegistrationSecretKey={key}\n', encoding='utf-8')
    return key


class Host:
    """The two server programs while this launcher hosts."""

    def __init__(self):
        self.processes = []
        self.address = None

    @property
    def running(self):
        return any(p.poll() is None for p in self.processes)

    def start(self, address):
        self.stop()
        server = package_dir('server') / 'server'
        shadnet = shadnet_dir()
        # Servers left over from a launcher that closed without stopping them hold the ports.
        end_leftovers(server)
        if shadnet != server:
            end_leftovers(shadnet)
        shadnet = shadnet_dir(sync=True)
        logs = shadnet / 'logs'
        logs.mkdir(exist_ok=True)
        stamp = time.strftime('%Y%m%d-%H%M%S')
        env = dict(os.environ, SHADNET_BLOODBORNE_SEAMLESS_COOP='1',
                   BBSC_SERVER_DATA_DIR=str(shadnet))
        shadnet_log = open(logs / f'shadnet-{stamp}.log', 'w', encoding='utf-8', errors='replace')
        self.processes.append(subprocess.Popen([str(server / 'shadnet.exe')], cwd=shadnet, env=env,
                                               stdout=shadnet_log, stderr=subprocess.STDOUT,
                                               stdin=subprocess.DEVNULL, creationflags=NO_WINDOW))
        time.sleep(2)
        game_log = open(logs / f'gameserver-{stamp}.log', 'w', encoding='utf-8', errors='replace')
        self.processes.append(subprocess.Popen(
            [str(server / 'BBSC-GameServer.exe'), '--shadnet', address, '--host', '0.0.0.0',
             '--advertise', address, '--summon-interval', '5', '--no-playlog', '--log-dir', str(logs)],
            cwd=shadnet, stdout=game_log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
            creationflags=NO_WINDOW))
        time.sleep(1)
        if not self.running or any(p.poll() is not None for p in self.processes):
            self.stop()
            raise CoopError(f'A co-op server stopped at start; see {logs}.')
        self.address = address

    def stop(self):
        for process in self.processes:
            if process.poll() is None:
                end_tree(process)
        self.processes = []
        self.address = None


def end_tree(process):
    """BBSC-GameServer.exe runs a second copy of itself as a child: end the whole tree, or the
    child keeps the ports after Stop hosting."""
    if os.name == 'nt':
        subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'], capture_output=True,
                       creationflags=NO_WINDOW)
    else:
        process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


def end_leftovers(server):
    """Ends shadnet.exe and BBSC-GameServer.exe processes started from this server folder."""
    if os.name != 'nt':
        return
    folder = str(Path(server).resolve()).replace("'", "''")
    script = (f"Get-CimInstance Win32_Process | Where-Object {{ $_.ExecutablePath -and "
              f"$_.ExecutablePath.StartsWith('{folder}\\', 'OrdinalIgnoreCase') }} | "
              "ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }")
    subprocess.run(['powershell', '-NoProfile', '-NonInteractive', '-Command', script],
                   capture_output=True, creationflags=NO_WINDOW)


# --- Invites and accounts ------------------------------------------------------------------------

def make_invite(address, key):
    data = json.dumps({'a': address, 'k': key}, separators=(',', ':')).encode()
    return INVITE_PREFIX + base64.urlsafe_b64encode(data).decode().rstrip('=')


def read_invite(code):
    # Chat apps wrap long codes over lines and add spaces: none belong to the code.
    code = ''.join(code.split())
    if not code.startswith(INVITE_PREFIX):
        raise CoopError(f'An invite code starts with {INVITE_PREFIX}')
    body = code[len(INVITE_PREFIX):]
    try:
        data = json.loads(base64.urlsafe_b64decode(body + '=' * (-len(body) % 4)))
        address, key = str(data['a']), str(data.get('k', ''))
    except (ValueError, KeyError, TypeError):
        raise CoopError('That invite code is damaged; ask the host to copy it again.') from None
    return address, key


def _account_tool(address, *arguments):
    tool = package_dir('client') / 'account' / 'shadnet-sample.exe'
    account_dir = coop_dir() / 'account'
    account_dir.mkdir(parents=True, exist_ok=True)
    if not tool.is_file():
        raise CoopError('Set up co-op first (the BBSC package is missing).')
    try:
        result = subprocess.run([str(tool), address, str(SHADNET_PORT), *arguments], capture_output=True,
                                text=True, timeout=30, cwd=account_dir, creationflags=NO_WINDOW)
    except subprocess.TimeoutExpired:
        raise CoopError(f'No answer from the co-op server at {address}. Is the host hosting, '
                        'and are you both on Tailscale?') from None
    return (result.stdout or '') + (result.stderr or '')


def create_account(address, key, name, password):
    """Creates the account on the host's server, then checks it signs in. An existing account
    (the same name and password) only gets the check."""
    if not (3 <= len(name) <= 16 and all(c.isalnum() or c in '-_' for c in name)):
        raise CoopError('A co-op name is 3-16 letters, numbers, - or _.')
    if len(password) < 4:
        raise CoopError('Choose a password of at least 4 characters (one you use nowhere else).')
    out = _account_reply(address, 'login', name, password)
    if '[login] OK' in out:
        return 'signed in'
    # The server answers LoginInvalidPassword for an unknown name too: only creating it tells.
    if _account_error(out) == 'LoginAlreadyLoggedIn':
        raise _account_failure(address, name, out)
    arguments = ['register', name, password, f'{name}@bbport-coop.invalid']
    if key:
        arguments.append(key)
    out = _account_reply(address, *arguments)
    if 'Account created successfully' not in out:
        raise _account_failure(address, name, out)
    out = _account_reply(address, 'login', name, password)
    if '[login] OK' not in out:
        raise _account_failure(address, name, out)
    return 'created'


# Connection attempts to the account server: the host's own server may still be starting
# (Start hosting asks it right after starting it), which used to read as a taken name (#28).
ACCOUNT_RETRY_WINDOW_S, ACCOUNT_RETRY_S = 10, 2


def _account_reply(address, *arguments):
    """The account tool's output, asked again for a few seconds while the server refuses the
    connection."""
    deadline = time.monotonic() + ACCOUNT_RETRY_WINDOW_S
    while True:
        out = _account_tool(address, *arguments)
        if _account_error(out) != 'connect' or time.monotonic() + ACCOUNT_RETRY_S > deadline:
            return out
        time.sleep(ACCOUNT_RETRY_S)


def _account_error(out):
    """What failed in the account tool's output: 'connect', 'timeout', the server's error name
    (Unauthorized, CreationExistingUsername, ...) or ''."""
    if '[connect] FAILED' in out:
        return 'connect'
    for line in out.splitlines():
        if line.startswith(('[login] FAILED:', '[create] FAILED:')):
            return line.split(':', 1)[1].strip()
    return 'timeout' if '[timeout]' in out else ''


def _account_failure(address, name, out):
    """The co-op account error for the player, from the account tool's output. All of these
    used to say "the name may be taken, or the invite is from another host" (#28)."""
    error = _account_error(out)
    if error in ('connect', 'timeout'):
        return CoopError(f'No answer from the co-op server at {address}. The host must be hosting '
                         '(launcher open), and both of you on Tailscale or the same network.')
    if error == 'Unauthorized':
        return CoopError("The invite code does not match the host's server: it is from an older "
                         'session or another host. Ask the host to copy the invite code again.')
    if error == 'LoginAlreadyLoggedIn':
        return CoopError(f'{name} is signed in on the host\'s server right now. Every player needs '
                         'their own co-op name; if it is yours, close the game that uses it first.')
    if error in ('CreationExistingUsername', 'CreationExistingEmail', 'LoginInvalidPassword'):
        return CoopError(f'{name} is already taken on the host\'s server, with another password. Use '
                         'the password you chose with this name before, or another co-op name.')
    if error == 'InvalidInput':
        return CoopError(f"The host's server does not accept the name {name}; choose another.")
    detail = error or (out.strip().splitlines() or ['no answer'])[-1]
    return CoopError(f"The host's server did not create the account ({detail}).")


# --- The game ------------------------------------------------------------------------------------

def co_op_environment(env, address, name, password, probe, save_copy=None):
    """The normal game environment, pointed at the host's servers with BBSC loaded. run.py writes
    this launch's server redirects (user/host_overrides.json) from these values."""
    launcher = package_dir('client') / 'bbsc' / 'bbsc-launch.exe'
    # BBSC's own redirect (its play-bbport.ps1): the game server and the summon messenger the
    # BBSC game server's server info names, both on the host.
    overrides = coop_dir() / 'host_overrides.json'
    overrides.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps({
        'https://ss4.scej-network.jp:20443': f'http://{address}:{GAME_PORT}',
        'http://thehuntersdream.com:18671/summon_messenger': f'http://{address}:{WEBAPI_PORT}',
        'https://thehuntersdream.com:18671/summon_messenger': f'http://{address}:{WEBAPI_PORT}',
    }, indent=2) + '\n'
    overrides.write_text(text, encoding='utf-8')
    # BBSC reads the same file itself, but only from <folder the game starts in>\user (run.py
    # starts it in the port's folder), its exe's folder\user or %APPDATA%\shadPS4. Every normal
    # online launch rewrites the port's user\host_overrides.json, so this copy serves this
    # co-op launch only.
    from bbport_paths import profile_dir
    port_user = profile_dir() / 'user'  # the launcher's own user\ (also with BBSC's emulator)
    port_user.mkdir(parents=True, exist_ok=True)
    (port_user / 'host_overrides.json').write_text(text, encoding='utf-8')
    env = dict(env)
    # Co-op runs on the shadNet backend against the host's servers, never The Hunter's Dream's,
    # whatever pool the main online settings choose (run.py drops these again for BB_COOP=1).
    for key in ('BB_NET_BACKEND', 'BB_THD_TOKEN', 'BB_THD_ONLINE_ID', 'BB_THD_SERVER', 'BB_THD_AUTH',
                'BB_THD_RULESET'):
        env.pop(key, None)
    # BBSC's co-op kit (its Hunt Bell, Kin Bell and the rest, which replace the vanilla bells) is
    # only given after BBSC has copied the save folder BBSC_SAVE_DIR names (BBSC's
    # BackupBbscSaves; it finds saves only in shadPS4's layout otherwise). Copying the save the
    # running game has open failed every time, so the kit never came and a new character had no
    # bell to start co-op with. BBSC gets the copy this launcher made just before the session
    # (`save_copy`, backup_saves), which nothing has open; the bells still go into the live save.
    save_dir = (active_save_dir(save_copy) if save_copy else None) or \
        active_save_dir(Path(env.get('BB_USER_DIR') or port_user))
    if save_dir:
        env['BBSC_SAVE_DIR'] = str(save_dir)
    env.update({
        'BBSC_DATA_DIR': str(coop_dir() / 'bbsc'),
        'BBSC_RELAY': f'{address}:{RELAY_PORT}',  # BBSC's relay (warps, world sync) on the host
        'BB_PROBE': str(launcher),
        'BBSC_EMULATOR': str(probe),
        'BB_ONLINE': '1',
        'BB_SHADNET_SERVER': f'{address}:{SHADNET_PORT}',
        'BB_SHADNET_WEBAPI': f'http://{address}:{WEBAPI_PORT}',
        'BB_HOST_OVERRIDES': str(overrides),
        'BB_SHADNET_NPID': name,
        'BB_SHADNET_PASSWORD': password,
        'BB_USER_NAME': name,
        'BB_COOP': '1',
    })
    return env


def active_save_dir(user_dir):
    """The game's save folder (SPRJ0005, userdata0000...) written most recently, or None."""
    newest = None
    for folder in Path(user_dir).glob('savedata/*/CUSA00207/SPRJ0005'):
        times = [f.stat().st_mtime for f in folder.glob('userdata00*') if f.is_file()]
        if times and (newest is None or max(times) > newest[0]):
            newest = (max(times), folder)
    return newest[1] if newest else None


def backup_saves(user_dir):
    """A copy of the saves before every co-op session (BBSC 0.0.1 is a first test)."""
    saves = Path(user_dir) / 'savedata'
    if not saves.is_dir():
        return None
    target = Path(user_dir) / 'coop-backups' / time.strftime('%Y%m%d-%H%M%S') / 'savedata'
    shutil.copytree(saves, target)
    return target.parent
