#!/usr/bin/env bash
# coopdev.sh - dev/test loop for the BBSC-GL co-op mod and the BBGL launcher, run from Claude's
# Linux VM (folders mounted under ~/mnt) over ssh to mark_pc (builds, PC install), local_pc (laptop)
# and remote_server (VPS co-op server). Windows-side work is coopdev.ps1 (copied to <root>\coop-dev).
#
#   coopdev.sh setup                         ssh key/config/known_hosts into ~/.ssh (from ~/mnt/claude-ssh)
#   coopdev.sh status                        git state of both repos, game/launcher on pc+laptop, VPS services
#   coopdev.sh commit bbsc|port "<msg>" [new files...]   git add -u (+ listed new files) && commit on mark_pc
#                                            (trailers: $CLAUDE_COAUTHOR, $CLAUDE_SESSION if set)
#   coopdev.sh push bbsc|port                push the working branch to the `mark` remote (the fork)
#   coopdev.sh build mod|port|package [--skip-build]     background job on mark_pc; see `job`
#   coopdev.sh job [name] [--wait]           state / tail of a build job (mod, port, package)
#   coopdev.sh deploy mod|launcher pc|laptop|all
#   coopdev.sh deploy server                 BBSC/server/gameserver/*.py -> VPS, backup, restart, check
#   coopdev.sh save list|snap|restore pc|laptop [name] [desc]
#   coopdev.sh test begin "<label>"          marks the start of a test run (time, VPS log offsets)
#   coopdev.sh test collect [run-id]         logs since the start -> ~/mnt/bloodborne_pc/out/coop-dev/runs/<id>/
#   coopdev.sh userdir pc|laptop <folder>   launcher's save folder (user_dir); tests: pc D:\\Games\\Bloodborne\\testHost,
#                                            laptop C:\\Games\\Bloodborne\\test; friends' games on pc: D:\\Games\\Bloodborne\\ddd
#   coopdev.sh ps pc|laptop "<powershell>"   run a PowerShell one-liner there (UTF-8 output)
set -uo pipefail

MNT=$HOME/mnt
PORT_REPO_W='C:\Users\markn\CLionProjects\bloodborne_pc'
BBSC_REPO_W='C:\Users\markn\CLionProjects\BBSC'
PORT_REPO_M='/c/Users/markn/CLionProjects/bloodborne_pc'
STATE=$MNT/bloodborne_pc/out/coop-dev/state; mkdir -p "$STATE/jobs"   # mounted: survives between shell calls
JOBS_W="$PORT_REPO_W\\out\\coop-dev\\state\\jobs"
RUNS=$MNT/bloodborne_pc/out/coop-dev/runs
PS1=$MNT/bloodborne_pc/tools/coop-dev/coopdev.ps1

host_of() { case $1 in pc) echo mark_pc;; laptop) echo local_pc;; *) echo "unknown machine $1" >&2; exit 2;; esac; }
root_of() { case $1 in pc) echo 'D:\Games\Bloodborne';; laptop) echo 'C:\Games\Bloodborne';; esac; }
fwd() { echo "${1//\\//}"; }          # C:\a\b -> C:/a/b (scp/sftp paths)
machines() { if [[ $1 == all ]]; then echo pc laptop; else echo "$1"; fi; }

# coopdev.ps1 on <machine>, freshly copied there first
winps() {
    local m=$1; shift
    local h r; h=$(host_of "$m"); r=$(root_of "$m")
    ssh "$h" "if not exist \"$r\\coop-dev\" mkdir \"$r\\coop-dev\"" >/dev/null &&
    scp -q "$PS1" "$h:$(fwd "$r")/coop-dev/coopdev.ps1" &&
    ssh "$h" "powershell -NoProfile -ExecutionPolicy Bypass -File \"$r\\coop-dev\\coopdev.ps1\" $*" 2>&1 | tr -d '\r'
}

repo_w() { case $1 in bbsc) echo "$BBSC_REPO_W";; port) echo "$PORT_REPO_W";; *) echo "repo: bbsc|port" >&2; exit 2;; esac; }

cmd_setup() { bash "$MNT/claude-ssh/setup-vm.sh"; }

cmd_status() {
    for r in bbsc port; do
        echo "== git $r"; ssh mark_pc "cd /d $(repo_w $r) && git branch --show-current && git status --short && git log --oneline -3" | tr -d '\r'
    done
    for m in pc laptop; do echo "== $m"; winps "$m" -Action status || echo "($m unreachable)"; done
    echo "== vps"; ssh remote_server 'systemctl is-active bbsc-gameserver bbsc-shadnet | paste -sd" "; ls -t /opt/bbsc/logs | head -1'
}

cmd_commit() {
    local r=$1 msg=$2; shift 2
    local w; w=$(repo_w "$r")
    local f=$STATE/commit-msg.txt
    printf '%s\n\nCo-Authored-By: %s\n' "$msg" "${CLAUDE_COAUTHOR:-Claude <noreply@anthropic.com>}" > "$f"
    [[ -n ${CLAUDE_SESSION:-} ]] && printf 'Claude-Session: %s\n' "$CLAUDE_SESSION" >> "$f"
    scp -q "$f" "mark_pc:$(fwd "$w")/.git/COOPDEV_MSG" || return 1
    local add=""; for p in "$@"; do add+=" \"$p\""; done
    ssh mark_pc "cd /d $w && git add -u ${add:+&& git add --$add} && git commit -q -F .git/COOPDEV_MSG && del .git\\COOPDEV_MSG && git log --oneline -1 && git status --short" | tr -d '\r'
}

cmd_push() {
    local w; w=$(repo_w "$1")
    ssh mark_pc "cd /d $w && for /f %b in ('git branch --show-current') do git push mark %b" 2>&1 | tr -d '\r'
}

job_done() {  # no job, or its .rc is newer than its start
    local n=$1
    [[ ! -f $STATE/jobs/$n.start ]] && return 0
    [[ -f $STATE/jobs/$n.rc && $(stat -c %Y "$STATE/jobs/$n.rc") -ge $(cat "$STATE/jobs/$n.start") ]]
}

job_start() {  # name, command line for cmd.exe on mark_pc; runs detached, output in state/jobs/<name>.log
    local n=$1 c=$2
    job_done "$n" || { echo "job $n is already running" >&2; return 1; }
    # (the VM cannot delete in mounted folders: the .cmd clears its own old .rc on the Windows side)
    printf '@echo off\r\ndel "%s\\%s.rc" 2>nul\r\n%s > "%s\\%s.log" 2>&1\r\necho %%errorlevel%% > "%s\\%s.rc"\r\n' \
        "$JOBS_W" "$n" "$c" "$JOBS_W" "$n" "$JOBS_W" "$n" > "$STATE/jobs/$n.cmd"
    date +%s > "$STATE/jobs/$n.start"
    winps pc -Action job-start -Source "\"$JOBS_W\\$n.cmd\"" && echo "job $n started: coopdev.sh job $n --wait"
}

cmd_build() {
    local what=$1; shift || true
    local msys="set MSYSTEM=CLANG64&& C:\\msys64\\usr\\bin\\bash.exe -lc"
    case $what in
    mod) job_start mod "call $BBSC_REPO_W\\emulator\\mod\\build-mod-bbport.cmd && type $BBSC_REPO_W\\build\\mod-build.log" ;;
    port) job_start port "$msys \"cd $PORT_REPO_M && bash build.sh\"" ;;
    package)
        local skip=0; [[ ${1:-} == --skip-build ]] && skip=1
        # the server players join by default = the one this PC's install uses
        local inv name
        inv=$(python3 -c "import json;print(json.load(open('$MNT/bbport-coop/coop-server.json')).get('invite',''))" 2>/dev/null)
        name=$(python3 -c "import json;print(json.load(open('$MNT/bbport-coop/coop-server.json')).get('name',''))" 2>/dev/null)
        job_start package "$msys \"cd $PORT_REPO_M && SKIP_BUILD=$skip COOP_INVITE='$inv' COOP_NAME='$name' bash packaging/windows/build-coop-package.sh\"" ;;
    *) echo "build mod|port|package" >&2; return 2 ;;
    esac
}

cmd_job() {
    local n=${1:-} wait=0
    [[ ${2:-} == --wait || ${1:-} == --wait ]] && wait=1
    [[ $n == --wait ]] && n=""
    if [[ -z $n ]]; then
        for f in "$STATE"/jobs/*.start; do [[ -e $f ]] || continue; n=$(basename "$f" .start)
            echo "$n: $(job_done "$n" && echo "done rc=$(tr -d ' \r\n' < "$STATE/jobs/$n.rc")" || echo running) since $(date -d @"$(cat "$f")" +%T)"; done
        return
    fi
    if (( wait )); then local t=0; while ! job_done "$n" && (( t < 160 )); do sleep 5; t=$((t+5)); done; fi
    tail -n 25 "$STATE/jobs/$n.log" 2>/dev/null | tr -d '\r'
    if job_done "$n"; then echo "== $n done rc=$(tr -d ' \r\n' < "$STATE/jobs/$n.rc")"; else echo "== $n still running ($(( $(date +%s) - $(cat "$STATE/jobs/$n.start") ))s)"; fi
}

cmd_deploy() {
    local what=$1 where=${2:-}
    case $what in
    mod)
        local src=$MNT/BBSC/build/mod
        [[ -f $src/bbsc.dll ]] || { echo "no $src/bbsc.dll: build mod first" >&2; return 1; }
        for m in $(machines "$where"); do
            echo "== deploy mod -> $m"
            if [[ $m == pc ]]; then winps pc -Action deploy-mod -Source "\"$BBSC_REPO_W\\build\\mod\""
            else
                local h r; h=$(host_of "$m"); r=$(root_of "$m")
                ssh "$h" "if not exist \"$r\\coop-dev\\mod\" mkdir \"$r\\coop-dev\\mod\"" &&
                scp -q "$src/bbsc.dll" "$src/bbsc-launch.exe" "$src/mod.json" "$h:$(fwd "$r")/coop-dev/mod/" &&
                winps "$m" -Action deploy-mod -Source "\"$r\\coop-dev\\mod\""
            fi
        done ;;
    launcher)
        for m in $(machines "$where"); do
            echo "== deploy launcher -> $m"
            if [[ $m == pc ]]; then winps pc -Action deploy-launcher -Source "\"$PORT_REPO_W\\out\\stage\\Bloodborne Game Launcher\""
            else
                local zip=$MNT/bloodborne_pc/dist/bbgl-windows.zip h r
                h=$(host_of "$m"); r=$(root_of "$m")
                ssh "$h" "if not exist \"$r\\coop-dev\" mkdir \"$r\\coop-dev\"" &&
                scp -q "$zip" "$h:$(fwd "$r")/coop-dev/bbgl-windows.zip" &&
                winps "$m" -Action deploy-launcher -Source "\"$r\\coop-dev\\bbgl-windows.zip\""
            fi
        done ;;
    server)
        local s=$MNT/BBSC/server/gameserver st; st=$(TZ=Europe/Moscow date +%Y%m%d-%H%M%S)
        ssh remote_server "cp -a /opt/bbsc/gameserver /opt/bbsc/backups/gameserver-$st && ls -dt /opt/bbsc/backups/gameserver-* | tail -n +6 | xargs -r rm -rf" &&
        scp -q "$s"/*.py "$s"/ss_info_template.xml remote_server:/opt/bbsc/gameserver/ &&
        ssh remote_server "chown -R bbsc:bbsc /opt/bbsc/gameserver && python3 -m py_compile /opt/bbsc/gameserver/bbsc_gameserver.py && systemctl restart bbsc-gameserver && sleep 3 && systemctl is-active bbsc-gameserver && journalctl -u bbsc-gameserver -n 8 --no-pager -o cat"
        echo "backup: /opt/bbsc/backups/gameserver-$st" ;;
    *) echo "deploy mod|launcher pc|laptop|all, deploy server" >&2; return 2 ;;
    esac
}

cmd_save() {
    local op=$1 m=$2 name=${3:-} desc=${4:-}
    case $op in
    list) winps "$m" -Action save-list ;;
    snap) winps "$m" -Action save-snap -Name "\"$name\"" -Desc "\"$desc\"" ;;
    restore) winps "$m" -Action save-restore -Name "\"$name\"" ;;
    *) echo "save list|snap|restore pc|laptop [name] [desc]" >&2; return 2 ;;
    esac
}

cmd_test() {
    case $1 in
    begin)
        local id; id=$(TZ=Europe/Moscow date +%Y%m%d-%H%M%S)
        local d=$RUNS/$id; mkdir -p "$d"
        local now; now=$(date +%s)
        local glog; glog=$(ssh remote_server 'f=$(ls -t /opt/bbsc/logs/gameserver-*.log | head -1); echo "$f $(stat -c %s "$f")"')
        printf 'label=%s\nstart=%s\nstart_iso=%s\nvps_gamelog=%s\n' "${2:-}" "$now" "$(date -u -d @"$now" +%FT%TZ)" "$glog" > "$d/run.txt"
        echo "$id" > "$STATE/current-run"
        echo "run $id started; test, then: coopdev.sh test collect" ;;
    collect)
        local id=${2:-$(cat "$STATE/current-run")} d
        d=$RUNS/$id; [[ -f $d/run.txt ]] || { echo "no run $id" >&2; return 1; }
        local start; start=$(sed -n 's/^start=//p' "$d/run.txt")
        for m in pc laptop; do
            echo "== collect $m"
            local h r; h=$(host_of "$m"); r=$(root_of "$m")
            if winps "$m" -Action collect -Since "$start" -RunId "$id" > "$d/$m-collect.txt"; then
                scp -q -r "$h:$(fwd "$r")/coop-dev/runs/$id" "$d/$m" && tail -n 1 "$d/$m-collect.txt"
            else echo "($m: collect failed, see $d/$m-collect.txt)"; fi
        done
        echo "== collect vps"; mkdir -p "$d/vps"
        read -r gf goff < <(sed -n 's/^vps_gamelog=//p' "$d/run.txt")
        ssh remote_server "journalctl -u bbsc-gameserver -u bbsc-shadnet --since @$start --no-pager -o short-iso | grep -v -E 'stats (30|60)s: (rx|clients)=0[ ;,]'" > "$d/vps/journal.txt"
        ssh remote_server "f=\$(ls -t /opt/bbsc/logs/gameserver-*.log | head -1); if [ \"\$f\" = '$gf' ]; then tail -c +\$(( ${goff:-0} + 1 )) \"\$f\"; else cat \"\$f\"; fi | grep -v -E 'stats (30|60)s: (rx|clients)=0[ ;,]'" > "$d/vps/gameserver.log"
        echo "== $d"; (cd "$d" && find . -type f -printf '%10s %p\n' | sort -k2)
        echo "-- error-ish lines per file:"
        (cd "$d" && grep -r -I -c -i -P '(?<!send_)errors?(?!s?=0)|exception|crash|fail|assert|desync|traceback' --include='*.log' --include='*.txt' . | grep -v ':0$') ;;
    *) echo "test begin|collect" >&2; return 2 ;;
    esac
}

cmd_userdir() { winps "$1" -Action set-user-dir -Source "\"$2\""; }

cmd_ps() {  # the script goes over as a file: no cmd.exe quoting
    local m=$1 h r f; h=$(host_of "$m"); r=$(root_of "$m"); f=$STATE/ps-$$.ps1
    printf '[Console]::OutputEncoding=[Text.Encoding]::UTF8\r\n%s\r\n' "$2" > "$f"
    ssh "$h" "if not exist \"$r\\coop-dev\" mkdir \"$r\\coop-dev\"" >/dev/null &&
    scp -q "$f" "$h:$(fwd "$r")/coop-dev/adhoc.ps1" &&
    ssh "$h" "powershell -NoProfile -ExecutionPolicy Bypass -File \"$r\\coop-dev\\adhoc.ps1\"" 2>&1 | tr -d '\r'
}

c=${1:-}; shift || true
case $c in
setup|status|commit|push|build|job|deploy|save|test|userdir|ps) "cmd_$c" "$@" ;;
*) sed -n '2,20p' "$0"; exit 2 ;;
esac
