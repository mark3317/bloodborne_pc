#!/usr/bin/env bash
# Reproducible launcher + pinned BBSC fork + built-in button packs.
set -euo pipefail
cd -- "$(dirname -- "$0")/../.."
source ./msys2-env.sh
[[ -f mods-src/BBSC/emulator/mod/build-mod-bbport.cmd ]] || git submodule update --init mods-src/BBSC
git -C mods-src/BBSC submodule update --init emulator/externals/fmt emulator/externals/xbyak
MSYS2_ARG_CONV_EXCL='*' cmd.exe /d /c "$(cygpath -w "$PWD/mods-src/BBSC/emulator/mod/build-mod-bbport.cmd")"
if [[ ${SKIP_BUILD:-0} != 1 ]]; then bash build.sh; fi
bash packaging/windows/build_coop_server.sh
bash packaging/windows/package.sh
out/qt-venv/Scripts/python.exe packaging/windows/verify-release.py out/stage/bbport-windows
out/qt-venv/Scripts/python.exe - <<'PY'
from pathlib import Path
import hashlib, zipfile
root=Path('out/stage/bbport-windows')
archive=Path('dist/bbport-coop-1.0.0-windows-x64.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as out:
    for path in sorted(root.rglob('*')):
        if path.is_file(): out.write(path,path.relative_to(root.parent).as_posix())
archive.with_suffix('.zip.sha256').write_text(hashlib.sha256(archive.read_bytes()).hexdigest()+'  '+archive.name+'\n')
print(archive, archive.stat().st_size)
PY
