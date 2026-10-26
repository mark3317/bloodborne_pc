#!/usr/bin/env bash
# The launcher package for friends, ready for seamless co-op on one co-op server (MSYS2 CLANG64):
#   bash packaging/windows/build-coop-package.sh
# Steps: bb-probe.exe (build.sh, with the BBSC relay), the launcher package (package.sh), then
#   coop-server.json  the server players join with an empty invite code   (COOP_INVITE, COOP_NAME)
#   coop/bbsc/        our own BBSC build put over the official BBSC of the same version
#                     (COOP_BBSC_BUILD = a folder with bbsc.dll, bbsc-launch.exe, mod.json;
#                     default ../BBSC/build/mod from BBSC's emulator/mod/build-mod-bbport.cmd)
# DLSS: COOP_DLSS_FROM = a folder with bbport_dlss.dll + nvngx_dlss.dll (an installed bbport's
#   bin\) when packaging/windows/build_dlss.sh is not used.
# Output: dist/bbport-coop-windows.zip (one folder, bbport-windows\).
set -euo pipefail
cd -- "$(dirname -- "$0")/../.."
source ./msys2-env.sh

COOP_INVITE=${COOP_INVITE:-}
COOP_NAME=${COOP_NAME:-}
COOP_BBSC_BUILD=${COOP_BBSC_BUILD:-../BBSC/build/mod}
COOP_DLSS_FROM=${COOP_DLSS_FROM:-}

if [[ ${SKIP_BUILD:-0} != 1 ]]; then
    bash build.sh
fi
if [[ -n $COOP_DLSS_FROM ]]; then
    for dll in bbport_dlss.dll nvngx_dlss.dll nvngx_dlssg.dll; do
        [[ -f $COOP_DLSS_FROM/$dll ]] && cp "$COOP_DLSS_FROM/$dll" out/
    done
    [[ -f out/NVIDIA-DLSS-LICENSE.txt ]] || {
        lic=$(ls "$COOP_DLSS_FROM"/../licenses/NVIDIA-DLSS-LICENSE*.txt 2>/dev/null | head -1 || true)
        if [[ -n $lic ]]; then cp "$lic" out/NVIDIA-DLSS-LICENSE.txt; else : > out/NVIDIA-DLSS-LICENSE.txt; fi
    }
fi
bash packaging/windows/package.sh

dest=out/stage/bbport-windows
if [[ -n $COOP_INVITE ]]; then
    python - "$dest/coop-server.json" "$COOP_NAME" "$COOP_INVITE" <<'PY'
import json, sys
path, name, invite = sys.argv[1:4]
with open(path, 'w', encoding='utf-8') as out:
    json.dump({'name': name, 'invite': invite}, out, indent=2)
    out.write('\n')
PY
    echo "Co-op server: ${COOP_NAME:-unnamed}"
else
    echo "No COOP_INVITE: players paste an invite code themselves" >&2
fi
if [[ -f $COOP_BBSC_BUILD/bbsc.dll && -f $COOP_BBSC_BUILD/mod.json ]]; then
    mkdir -p "$dest/coop/bbsc"
    cp "$COOP_BBSC_BUILD"/bbsc.dll "$dest/coop/bbsc/"
    [[ -f $COOP_BBSC_BUILD/bbsc-launch.exe ]] && cp "$COOP_BBSC_BUILD"/bbsc-launch.exe "$dest/coop/bbsc/"
    python - "$COOP_BBSC_BUILD/mod.json" "$dest/coop/bbsc.json" <<'PY'
import json, sys
version = json.load(open(sys.argv[1], encoding='utf-8'))['version']
with open(sys.argv[2], 'w', encoding='utf-8') as out:
    json.dump({'base': version, 'note': 'bbport build of BBSC (opening guard); used over BBSC ' + version + ' only'}, out, indent=2)
    out.write('\n')
print('Own BBSC build for BBSC', version)
PY
else
    echo "No own BBSC build in $COOP_BBSC_BUILD: the official BBSC is used" >&2
fi

rm -f dist/bbport-coop-windows.zip
python - out/stage dist/bbport-coop-windows.zip <<'PY'
import os, sys, zipfile
root, archive = sys.argv[1], sys.argv[2]
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as out:
    for folder, _, files in os.walk(root):
        for name in files:
            path = os.path.join(folder, name)
            out.write(path, os.path.relpath(path, root).replace(os.sep, '/'))
PY
du -sh "$dest" dist/bbport-coop-windows.zip
