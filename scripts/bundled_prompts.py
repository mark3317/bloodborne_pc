"""Rebuild bundled button textures from the player's own verified game archive."""
import hashlib
import json
import os
from pathlib import Path


def install(choice, game, mods, assets):
    import bsdiff4
    from fromsoft import dcx_decompress, dcx_compress
    assets = Path(assets)
    manifest = json.loads((assets / 'manifest.json').read_text(encoding='utf-8'))
    entry = manifest['packs'][choice]
    base = Path(game) / 'dvdroot_ps4/menu/common.tpf.dcx'
    template = base.read_bytes()
    data = dcx_decompress(template)
    if hashlib.sha256(data).hexdigest() != manifest['base_sha256']:
        raise ValueError('Button prompts need the original Bloodborne 1.09 menu/common.tpf.dcx.')
    delta = (assets / entry['patch']).read_bytes()
    if hashlib.sha256(delta).hexdigest() != entry['patch_sha256']:
        raise ValueError('Damaged bundled button prompts. Re-extract the launcher release.')
    result = bsdiff4.patch(data, delta)
    if hashlib.sha256(result).hexdigest() != entry['sha256']:
        raise ValueError('Button prompt verification failed.')
    folder = Path(mods) / entry['name']
    target = folder / 'menu/common.tpf.dcx'
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix('.tmp')
    temporary.write_bytes(dcx_compress(result, template))
    os.replace(temporary, target)
    (folder / 'SOURCE.txt').write_text(entry['credit'] + '\n', encoding='utf-8')
    return folder
