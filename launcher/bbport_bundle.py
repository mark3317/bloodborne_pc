"""Install the release's immutable co-op payload without replacing player data."""
import hashlib
import json
from pathlib import Path
import shutil
import os


def install(source, destination):
    source, destination = Path(source), Path(destination)
    manifest = json.loads((source / 'bundle.json').read_text(encoding='utf-8'))
    # Validate the entire payload before changing the installed copy.
    for name, digest in manifest['files'].items():
        relative = Path(name)
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('Invalid bundled path')
        if hashlib.sha256((source / relative).read_bytes()).hexdigest() != digest:
            raise ValueError(f'Damaged bundled file: {name}. Re-extract the launcher release.')
    for name, digest in manifest['files'].items():
        target = destination / name
        if target.is_file() and hashlib.sha256(target.read_bytes()).hexdigest() == digest:
            continue
        # Host configuration belongs to the user after the first install.
        if target.exists() and name in ('server/shadnet.cfg', 'server/worlds.cfg', 'server/scoreboards.cfg'):
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_name(target.name + '.bundle-tmp')
        shutil.copyfile(source / name, temporary)
        os.replace(temporary, target)
    destination.mkdir(parents=True, exist_ok=True)
    (destination / 'bbport-package.json').write_text(
        json.dumps({'version': manifest['version'], 'source': manifest['source']}), encoding='utf-8')
    return manifest['version']
