"""Fail packaging when runtime dependencies, bundled mods or release hygiene are wrong."""
import hashlib
import json
from pathlib import Path
import sys


def verify(root):
    root = Path(root).resolve(strict=True)
    for name in ('Bloodborne.exe', 'bin/bb-probe.exe', 'run.py', 'README.ru.md', 'THIRD_PARTY.md',
                 'coop/client/bbsc/bbsc.dll', 'coop/client/bbsc/bbsc-launch.exe',
                 'coop/client/account/shadnet-sample.exe', 'coop/server/server/shadnet.exe',
                 'coop/server/server/BBSC-GameServer.exe', 'mods/manifest.json',
                 'licenses/BBSC-LICENSE.txt'):
        if not (root / name).is_file():
            raise ValueError(f'Missing release file: {name}')
    for kind in ('client', 'server'):
        folder = root / 'coop' / kind
        manifest = json.loads((folder / 'bundle.json').read_text(encoding='utf-8'))
        for name, expected in manifest['files'].items():
            if hashlib.sha256((folder / name).read_bytes()).hexdigest() != expected:
                raise ValueError(f'Bundle checksum mismatch: {kind}/{name}')
    prompts = root / 'mods'
    ready = json.loads((prompts / 'manifest.json').read_text(encoding='utf-8'))['files']
    for name, digest in ready.items():
        if hashlib.sha256((prompts / name).read_bytes()).hexdigest() != digest:
            raise ValueError('Damaged ready-made prompt mod')
    allowed_archives = {'mods/' + name for name in ready if name.endswith('.dcx')}
    for line in (root / 'coop/server/server/shadnet.cfg').read_text(encoding='utf-8').splitlines():
        if line.startswith('RegistrationSecretKey=') and line.split('=', 1)[1].strip():
            raise ValueError('Personal registration key in release')
    if 'coopSetup()' in (root / 'launcher/qml/SettingsWorkspace.qml').read_text(encoding='utf-8'):
        raise ValueError('Obsolete BBSC preparation button in release')
    for path in root.rglob('*'):
        if not path.is_file():
            continue
        name = path.name.lower()
        parts = {p.lower() for p in path.relative_to(root).parts}
        if (name in ('settings.json', 'account.dat', 'eboot.bin', 'param.sfo', 'coop-server.json',
                     'bbport.ini', 'mods.json', 'patches.json', 'online-data.json')
                or (name.endswith(('.dcx', '.tpf', '.bdt', '.bhd', '.dmp', '.log', '.bak', '.pyc'))
                    and path.relative_to(root).as_posix() not in allowed_archives)
                or parts & {'savedata', 'captures', 'own-world', 'bell-pending', 'guest-items',
                            'shared-progress', 'discord rich presence', 'atlas', '__pycache__'}):
            raise ValueError(f'Unexpected release file: {path.relative_to(root)}')
    print('Release payload and hygiene: PASS')


if __name__ == '__main__':
    verify(sys.argv[1])
