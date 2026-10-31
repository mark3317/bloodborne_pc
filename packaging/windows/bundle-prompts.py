"""Build icon mods before packaging, so switching them only changes selection."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from bundled_prompts import install

destination = Path(sys.argv[1]) / 'mods'
cache = ROOT / 'out/vendor/ready-prompts'
for choice in ('Xbox', 'Keyboard'):
    manifest = json.loads((ROOT / 'bundled-mods/prompts/manifest.json').read_text(encoding='utf-8'))
    name = manifest['packs'][choice]['name']
    if not (cache / name / 'menu/common.tpf.dcx').is_file():
        game = os.environ.get('BB_PROMPT_GAME_DIR')
        if not game:
            raise RuntimeError('Set BB_PROMPT_GAME_DIR to your original 1.09 game to build icon mods.')
        install(choice, game, cache, ROOT / 'bundled-mods/prompts')
    shutil.copytree(cache / name, destination / name, dirs_exist_ok=True)
files = {p.relative_to(destination).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
         for p in sorted(destination.rglob('*')) if p.is_file()}
(destination / 'manifest.json').write_text(json.dumps({'files': files}, indent=2), encoding='utf-8')
