"""One writable profile for the Windows launcher; installed files stay immutable."""
import os
from pathlib import Path
import shutil


def profile_dir():
    return Path(os.environ.get('APPDATA', Path.home())) / 'bbport-launcher'


def initialize(port):
    root = profile_dir()
    root.mkdir(parents=True, exist_ok=True)
    port = Path(port)
    # Import existing portable data once, without overwriting the user's profile.
    # Old installations remain untouched until the user retires that installation.
    marker = root / 'profile-layout-v2'
    if not marker.exists():
        for name in ('bbport.ini', 'mods.json', 'patches.json', 'input.ini', 'user'):
            source, target = port / name, root / name
            if source.exists() and not target.exists():
                if source.is_dir():
                    shutil.copytree(source, target)
                else:
                    shutil.copy2(source, target)
        legacy = Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'bbport-coop'
        # Mutable BBSC journals and the host database are independent of installed binaries.
        for old, new in (('bbsc-client/bbsc', 'bbsc'),
                         ('BBSC-0.0.2-BBport/bbsc', 'bbsc'),
                         ('shadnet-bbport', 'server'), ('bbsc-server/server', 'server')):
            source = legacy / old
            for item in source.rglob('*'):
                if (not item.is_file() or item.suffix.lower() in ('.exe', '.dll')
                        or item.name in ('mod.json', 'SOURCE.txt', 'LICENSE.txt')):
                    continue
                target = root / 'coop' / new / item.relative_to(source)
                if not target.exists():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, target)
        marker.write_text('2\n', encoding='utf-8')
    # Ship patch definitions with the application, keep user additions in the profile.
    for source in (port / 'patches').rglob('*'):
        if source.is_file():
            target = root / 'patches' / source.relative_to(Path(port) / 'patches')
            if not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
    # Ready-made icon mods live in the installation; selection stays in AppData.
    import json
    mods_marker = root / 'ready-mods-layout-v1'
    if not mods_marker.exists():
        config = root / 'mods.json'
        profile = json.loads(config.read_text(encoding='utf-8')) if config.exists() else {}
        disabled = set(profile.get('disabled', []))
        known = set(profile.get('enabled', [])) | set(profile.get('order', []))
        for name in ('Xbox Prompts (Dommo)', 'Keyboard Prompts (PCBButtons)'):
            if name not in known:
                disabled.add(name)
        profile['disabled'] = sorted(disabled)
        config.write_text(json.dumps(profile, indent=2), encoding='utf-8')
        for source in (root / 'mods').iterdir() if (root / 'mods').is_dir() else ():
            target = port / 'mods' / source.name
            if source.is_dir() and not target.exists():
                shutil.copytree(source, target)
        mods_marker.write_text('1\n', encoding='utf-8')
    return root
