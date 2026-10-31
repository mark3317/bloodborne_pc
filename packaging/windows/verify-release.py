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
                 'coop/server/server/BBSC-GameServer.exe', 'bundled-mods/prompts/manifest.json',
                 'licenses/BBSC-LICENSE.txt'):
        if not (root / name).is_file():
            raise ValueError(f'Missing release file: {name}')
    for kind in ('client', 'server'):
        folder = root / 'coop' / kind
        manifest = json.loads((folder / 'bundle.json').read_text(encoding='utf-8'))
        for name, expected in manifest['files'].items():
            if hashlib.sha256((folder / name).read_bytes()).hexdigest() != expected:
                raise ValueError(f'Bundle checksum mismatch: {kind}/{name}')
    for path in root.rglob('*'):
        if not path.is_file():
            continue
        name = path.name.lower()
        parts = {p.lower() for p in path.relative_to(root).parts}
        if (name in ('settings.json', 'account.dat', 'eboot.bin', 'param.sfo', 'coop-server.json')
                or name.endswith(('.dcx', '.tpf', '.bdt', '.bhd', '.dmp', '.log', '.bak', '.pyc'))
                or parts & {'savedata', 'captures', 'own-world', 'bell-pending', 'guest-items',
                            'shared-progress', 'discord rich presence', 'atlas', '__pycache__'}):
            raise ValueError(f'Unexpected release file: {path.relative_to(root)}')
    print('Release payload and hygiene: PASS')


if __name__ == '__main__':
    verify(sys.argv[1])
