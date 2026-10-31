"""Assemble a self-contained client and server from the pinned fork and vendor tools.

Only shadNet runtime/account dependencies are taken from the checksum-pinned archive.
The BBSC mod and game server are built from mods-src/BBSC, never from that archive.
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[2]
FORK = ROOT / 'mods-src/BBSC'
VENDORS = {
    'BBport': '001efc0a03b47bd6b2660c598fd6d172d2aaae3201a4982134d1f215918acd3c',
}


def vendor(kind):
    name = f'BBSC-0.0.2-{kind}.zip'
    path = ROOT / 'out/vendor' / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        temporary = path.with_suffix('.part')
        urllib.request.urlretrieve(f'https://github.com/CLSAMG22/BBSC/releases/download/v0.0.2/{name}', temporary)
        temporary.replace(path)
    if hashlib.sha256(path.read_bytes()).hexdigest() != VENDORS[kind]:
        raise RuntimeError(f'Vendor checksum mismatch: {name}')
    return zipfile.ZipFile(path)


def extract_vendor(kind, prefix, destination, allowed):
    with vendor(kind) as archive:
        base = f'BBSC-0.0.2-{kind}/{prefix}/'
        for name in archive.namelist():
            relative = name.removeprefix(base)
            if not name.startswith(base) or not allowed(relative):
                continue
            if '..' in Path(relative).parts or Path(relative).is_absolute():
                raise RuntimeError('Unsafe vendor path')
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.read(name))


def main():
    dest = ROOT / 'out/stage/bbport-windows/coop'
    client, server = dest / 'client', dest / 'server'
    (client / 'bbsc').mkdir(parents=True, exist_ok=True)
    (server / 'server').mkdir(parents=True, exist_ok=True)
    for name in ('bbsc.dll', 'bbsc-launch.exe', 'mod.json'):
        shutil.copy2(FORK / 'build/mod' / name, client / 'bbsc' / name)
    extract_vendor('BBport', 'account', client / 'account', lambda n: n.endswith(('.dll', '.exe')))
    shutil.copytree(ROOT / 'out/coop-server', server / 'server', dirs_exist_ok=True)
    for name in ('shadnet.cfg', 'worlds.cfg', 'scoreboards.cfg'):
        shutil.copy2(FORK / 'server/server' / name, server / 'server' / name)
    # Frozen from this exact submodule revision, including its relay fixes.
    subprocess.run([sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean', '--onefile',
                    '--log-level', 'WARN', '--name', 'BBSC-GameServer',
                    '--distpath', str(ROOT / 'out/bbsc-server-dist'),
                    '--workpath', str(ROOT / 'out/bbsc-server-work'),
                    '--specpath', str(ROOT / 'out/bbsc-server-work'),
                    '--add-data', str(FORK / 'server/gameserver/ss_info_template.xml') + ';.',
                    str(FORK / 'server/gameserver/bbsc_gameserver.py')], check=True)
    shutil.copy2(ROOT / 'out/bbsc-server-dist/BBSC-GameServer.exe', server / 'server')
    revision = subprocess.check_output(['git', '-C', str(FORK), 'rev-parse', 'HEAD'], text=True).strip()
    version = json.loads((FORK / 'emulator/mod/mod.json').read_text(encoding='utf-8'))['version']
    for folder in (client, server):
        manifest = {'version': version, 'source': f'https://github.com/mark3317/BBSC/tree/{revision}',
                    'files': {p.relative_to(folder).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in sorted(folder.rglob('*')) if p.is_file() and p.name != 'bundle.json'}}
        (folder / 'bundle.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    licenses = dest.parent / 'licenses'
    shutil.copy2(FORK / 'LICENSE', licenses / 'BBSC-LICENSE.txt')
    shutil.copy2(FORK / 'server/gameserver/LICENSE.NoDreamForHunter', licenses / 'NoDreamForHunter-LICENSE.txt')
    (dest / 'SOURCE.json').write_text(json.dumps({'bbsc_commit': revision, 'version': version,
                                               'vendor_sha256': VENDORS}, indent=2) + '\n')


if __name__ == '__main__':
    main()
