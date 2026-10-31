# coopdev.ps1 - Windows side of the co-op dev/test loop (run over ssh by coopdev.sh).
#   powershell -NoProfile -ExecutionPolicy Bypass -File coopdev.ps1 -Action <action> [-Install <dir>] [-Root <dir>] ...
# Actions:
#   status            game running?, install, user dir, active save, BBSC package, snapshots
#   deploy-mod        -Source <dir with bbsc.dll, bbsc-launch.exe[, mod.json]>: into <install>\coop\bbsc and the
#                     active BBSC client package (%LOCALAPPDATA%\bbport-coop\...\bbsc), old files -> *.bak-<stamp>
#   deploy-launcher   -Source <staged Bloodborne Game Launcher folder or .zip>: over <install>, user files kept;
#                     the first time a full backup of the install goes to <root>\coop-dev\backups\
#   save-list         snapshots in <root>\coop-dev\saves
#   save-snap         -Name <name> [-Desc <text>]: the active SPRJ0005 (+ BBSC own-world / bell-pending)
#   save-restore      -Name <name>: the current save goes to _auto-<stamp> first, then the snapshot is mirrored back
#   set-user-dir      -Source <folder>: the launcher's user_dir (saves) -> that folder; prints the old one
#   job-start         -Source <a .cmd file>: runs it detached (WMI, survives the ssh session), prints the pid
#   collect           -Since <unix seconds> -RunId <id>: logs newer than Since -> <root>\coop-dev\runs\<id>\
# All refuse to touch saves/installs while the game runs.
param(
    [Parameter(Mandatory = $true)][string]$Action,
    [string]$Install = '',
    [string]$Root = '',
    [string]$Source = '',
    [string]$Name = '',
    [string]$Desc = '',
    [long]$Since = 0,
    [string]$RunId = ''
)
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'

if (-not $Install) {
    $installRoot = Split-Path $PSScriptRoot -Parent
    $Install = Join-Path $installRoot 'Bloodborne Game Launcher'
    if (-not (Test-Path -LiteralPath $Install)) { $Install = Join-Path $installRoot 'bbport-coop' }
}
if (-not $Root) { $Root = Split-Path $Install -Parent }
$Dev = Join-Path $Root 'coop-dev'
$GameProcs = 'bb-probe', 'bb-play', 'bbsc-launch'
$UserFiles = 'user', 'out', 'mods', 'bbport.ini', 'input.ini', 'mods.json', 'patches.json', 'last_run.log', 'coop-server.json'

function SettingsFile {
    foreach ($candidate in @(
        (Join-Path $env:LOCALAPPDATA 'bbgl\settings.json'),
        (Join-Path $env:LOCALAPPDATA 'bbport-launcher\settings.json'),
        (Join-Path $env:APPDATA 'bbport-launcher\settings.json'),
        (Join-Path $env:APPDATA 'bbport-launcher-coop\settings.json'))) {
        if (Test-Path -LiteralPath $candidate) { return $candidate }
    }
    return $null
}
function Settings {
    $settingsPath = SettingsFile
    if ($settingsPath) { return Get-Content -LiteralPath $settingsPath -Raw -Encoding UTF8 | ConvertFrom-Json }
    return $null
}
function UserDir {
    $s = Settings
    if ($s -and $s.user_dir) { return [IO.Path]::GetFullPath($s.user_dir) }
    $settingsPath = SettingsFile
    if ($settingsPath) { return (Join-Path (Split-Path $settingsPath -Parent) 'user') }
    return (Join-Path $Install 'user')
}
function ActiveSave {
    $u = UserDir
    $c = Get-ChildItem -Path (Join-Path $u 'savedata') -Directory -ErrorAction SilentlyContinue |
        ForEach-Object { Get-Item (Join-Path $_.FullName 'CUSA00207\SPRJ0005') -ErrorAction SilentlyContinue } |
        Sort-Object LastWriteTime -Descending | Select-Object -First 1
    return $c
}
function ClientPkg {
    $bundled = Join-Path $Install 'coop\client'
    if (Test-Path (Join-Path $bundled 'bbsc\bbsc.dll')) { return $bundled }
    $base = Join-Path $env:LOCALAPPDATA 'bbport-coop'
    foreach ($n in 'bbsc-client', 'BBSC-0.0.1-BBport') {
        $p = Join-Path $base $n
        if (Test-Path (Join-Path $p 'bbsc\bbsc.dll')) { return $p }
    }
    return $null
}
function DataPkg {
    $profile = Join-Path $env:LOCALAPPDATA 'bbgl\coop'
    if (Test-Path -LiteralPath $profile) { return $profile }
    return (ClientPkg)
}
function GameRunning { return @(Get-Process -Name $GameProcs -ErrorAction SilentlyContinue) }
function RequireStopped {
    $r = GameRunning
    if ($r.Count) { throw "GAME_RUNNING: close the game first ($(($r | ForEach-Object Name) -join ', '))" }
}
function Mirror($from, $to) {
    robocopy $from $to /MIR /R:2 /W:1 /NFL /NDL /NJH /NJS /NP | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "robocopy $from -> $to failed ($LASTEXITCODE)" }
}

switch ($Action) {
'status' {
    $r = GameRunning
    "game_running=$([bool]$r.Count) $(($r | ForEach-Object { "$($_.Name)#$($_.Id)" }) -join ' ')"
    "install=$Install exists=$(Test-Path $Install)"
    "user_dir=$(UserDir)"
    $a = ActiveSave; "active_save=$($a.FullName) modified=$($a.LastWriteTime)"
    $p = ClientPkg; "bbsc_package=$p"
    if ($p) { "bbsc_dll=$((Get-FileHash (Join-Path $p 'bbsc\bbsc.dll') -Algorithm MD5).Hash) $((Get-Item (Join-Path $p 'bbsc\bbsc.dll')).LastWriteTime)" }
    $o = Join-Path $Install 'coop\bbsc\bbsc.dll'
    if (Test-Path $o) { "override_dll=$((Get-FileHash $o -Algorithm MD5).Hash)" }
    "snapshots=$((Get-ChildItem (Join-Path $Dev 'saves') -Directory -ErrorAction SilentlyContinue | ForEach-Object Name) -join ', ')"
}
'deploy-mod' {
    RequireStopped
    if (-not (Test-Path (Join-Path $Source 'bbsc.dll'))) { throw "no bbsc.dll in $Source" }
    $targets = @(Join-Path $Install 'coop\bbsc')
    $p = ClientPkg; if ($p) { $targets += (Join-Path $p 'bbsc') }
    foreach ($t in $targets) {
        New-Item -ItemType Directory -Force $t | Out-Null
        foreach ($f in 'bbsc.dll', 'bbsc-launch.exe') {
            $src = Join-Path $Source $f; $dst = Join-Path $t $f
            if (-not (Test-Path $src)) { continue }
            if (Test-Path $dst) {
                if ((Get-FileHash $src).Hash -eq (Get-FileHash $dst).Hash) { "same  $dst"; continue }
                Copy-Item $dst "$dst.bak-$stamp"
                Get-ChildItem "$dst.bak-*" | Sort-Object Name -Descending | Select-Object -Skip 3 | Remove-Item -Force
            }
            Copy-Item $src $dst -Force; "copied $dst"
        }
    }
}
'deploy-launcher' {
    RequireStopped
    if (Get-Process -Name 'Bloodborne', 'Play Bloodborne' -ErrorAction SilentlyContinue) { throw 'LAUNCHER_RUNNING: close the launcher first' }
    $src = $Source
    if ($Source -like '*.zip') {
        $src = Join-Path $Dev "unpack"
        if (Test-Path $src) { Remove-Item $src -Recurse -Force }
        Expand-Archive -Path $Source -DestinationPath $src -Force
        $src = Join-Path $src 'Bloodborne Game Launcher'
    }
    if (-not (Test-Path (Join-Path $src 'Bloodborne.exe'))) { throw "no Bloodborne.exe in $src" }
    $backups = Join-Path $Dev 'backups'
    if (-not (Get-ChildItem $backups -Directory -ErrorAction SilentlyContinue)) {
        $b = Join-Path $backups "install-$stamp"
        robocopy $Install $b /E /R:2 /W:1 /NFL /NDL /NJH /NJS /NP /XD (Join-Path $Install 'out') (Join-Path $Install 'user') | Out-Null
        if ($LASTEXITCODE -ge 8) { throw "backup failed ($LASTEXITCODE)" }
        "backup=$b"
    }
    $xf = $UserFiles | Where-Object { $_ -like '*.*' }
    $xd = $UserFiles | Where-Object { $_ -notlike '*.*' } | ForEach-Object { Join-Path $Install $_ }
    # coop-server.json: keep the installed one when it names a server, else take the package's
    if (-not (Test-Path (Join-Path $Install 'coop-server.json'))) { $xf = $xf | Where-Object { $_ -ne 'coop-server.json' } }
    robocopy $src $Install /E /R:2 /W:1 /NFL /NDL /NJH /NJS /NP /XF $xf /XD $xd | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "robocopy failed ($LASTEXITCODE)" }
    "deployed $src -> $Install (robocopy rc=$LASTEXITCODE)"
    "bb-probe=$((Get-FileHash (Join-Path $Install 'bin\bb-probe.exe') -Algorithm MD5).Hash)"
}
'save-list' {
    Get-ChildItem (Join-Path $Dev 'saves') -Directory -ErrorAction SilentlyContinue | Sort-Object Name | ForEach-Object {
        $i = Join-Path $_.FullName 'info.json'
        $d = if (Test-Path $i) { Get-Content $i -Raw | ConvertFrom-Json } else { $null }
        "{0,-32} {1}  {2}" -f $_.Name, $d.created, $d.desc
    }
}
'save-snap' {
    RequireStopped
    if (-not $Name) { throw 'need -Name' }
    $a = ActiveSave; if (-not $a) { throw 'no save found' }
    $dst = Join-Path $Dev "saves\$Name"
    if ((Test-Path $dst) -and -not $Name.StartsWith('_auto-')) { throw "snapshot $Name exists" }
    Mirror $a.FullName (Join-Path $dst 'SPRJ0005')
    $sys = "$($a.FullName).sce_sys"; if (Test-Path $sys) { Mirror $sys (Join-Path $dst 'SPRJ0005.sce_sys') }
    $p = DataPkg
    foreach ($n in 'own-world', 'bell-pending') {
        if ($p -and (Test-Path (Join-Path $p "bbsc\$n"))) { Mirror (Join-Path $p "bbsc\$n") (Join-Path $dst "bbsc-$n") }
    }
    @{ name = $Name; desc = $Desc; created = (Get-Date -Format 's'); source = $a.FullName; machine = $env:COMPUTERNAME } |
        ConvertTo-Json | Set-Content (Join-Path $dst 'info.json') -Encoding UTF8
    "snapshot=$dst"
}
'save-restore' {
    RequireStopped
    $src = Join-Path $Dev "saves\$Name"
    if (-not (Test-Path (Join-Path $src 'SPRJ0005'))) { throw "no snapshot $Name" }
    $a = ActiveSave; if (-not $a) { throw 'no active save folder' }
    & $PSCommandPath -Action save-snap -Install $Install -Root $Root -Name "_auto-$stamp" -Desc "before restore of $Name"
    Get-ChildItem (Join-Path $Dev 'saves') -Directory -Filter '_auto-*' | Sort-Object Name -Descending | Select-Object -Skip 5 | Remove-Item -Recurse -Force
    Mirror (Join-Path $src 'SPRJ0005') $a.FullName
    if (Test-Path (Join-Path $src 'SPRJ0005.sce_sys')) { Mirror (Join-Path $src 'SPRJ0005.sce_sys') "$($a.FullName).sce_sys" }
    $p = DataPkg
    foreach ($n in 'own-world', 'bell-pending') {
        $s = Join-Path $src "bbsc-$n"
        if ($p -and (Test-Path $s)) { Mirror $s (Join-Path $p "bbsc\$n") }
    }
    "restored $Name -> $($a.FullName)"
}
'collect' {
    if (-not $RunId) { throw 'need -RunId' }
    $t = [DateTimeOffset]::FromUnixTimeSeconds($Since).LocalDateTime
    $out = Join-Path $Dev "runs\$RunId"
    if (Test-Path $out) { Remove-Item $out -Recurse -Force }
    New-Item -ItemType Directory -Force $out | Out-Null
    $u = UserDir; $p = DataPkg
    $sets = @(
        @{ dir = $u; filter = 'last_run*.log'; to = 'game' },
        @{ dir = (Join-Path $u 'log'); filter = '*'; to = 'game-log' }
    )
    if ($p) {
        $sets += @{ dir = (Join-Path $p 'bbsc\logs'); filter = '*'; to = 'bbsc-logs' }
        $sets += @{ dir = (Join-Path $p 'bbsc\captures'); filter = '*'; to = 'bbsc-captures' }
    }
    $sets += @{ dir = (Join-Path $env:LOCALAPPDATA 'CrashDumps'); filter = 'bb*.dmp'; to = 'crashdumps' }
    foreach ($s in $sets) {
        Get-ChildItem -Path $s.dir -Filter $s.filter -File -Recurse -ErrorAction SilentlyContinue |
            Where-Object { $_.LastWriteTime -ge $t -and $_.Length -lt 300MB } | ForEach-Object {
                $d = Join-Path $out $s.to; New-Item -ItemType Directory -Force $d | Out-Null
                Copy-Item $_.FullName $d
            }
    }
    Get-WinEvent -FilterHashtable @{ LogName = 'Application'; StartTime = $t; Id = 1000, 1001, 1002 } -ErrorAction SilentlyContinue |
        Where-Object { $_.Message -match 'bb-probe|bb-play|bbsc|Bloodborne|LiveKernelEvent|nvlddmkm' } |
        ForEach-Object { "[$($_.TimeCreated.ToString('s'))] id=$($_.Id)`n$($_.Message)`n" } |
        Set-Content (Join-Path $out 'windows-crash-events.txt') -Encoding UTF8
    Get-WinEvent -FilterHashtable @{ LogName = 'System'; StartTime = $t } -ErrorAction SilentlyContinue |
        Where-Object { $_.ProviderName -match '^(Display|nvlddmkm|Microsoft-Windows-WHEA-Logger)$' } |
        ForEach-Object { $_.ToXml() } |
        Set-Content (Join-Path $out 'windows-gpu-events.xml') -Encoding UTF8
    $r = GameRunning
    "game_running=$([bool]$r.Count)" | Set-Content (Join-Path $out 'state.txt')
    Get-ChildItem $out -Recurse -File | ForEach-Object { "{0,10} {1}" -f $_.Length, $_.FullName.Substring($out.Length + 1) }
    "collected=$out"
}
'set-user-dir' {
    RequireStopped
    if (Get-Process -Name 'Bloodborne', 'Play Bloodborne' -ErrorAction SilentlyContinue) { throw 'LAUNCHER_RUNNING: close the launcher first' }
    if (-not (Test-Path (Join-Path $Source 'savedata'))) { throw "no savedata in $Source" }
    $p = SettingsFile
    if (-not $p) { throw 'no launcher settings.json' }
    $raw = Get-Content $p -Raw -Encoding UTF8
    $old = (ConvertFrom-Json $raw).user_dir
    $new = ($Source -replace '\\', '/')
    $raw2 = [regex]::Replace($raw, '("user_dir"\s*:\s*")[^"]*(")', { param($m) $m.Groups[1].Value + $new + $m.Groups[2].Value })
    if ($raw2 -eq $raw -and $old -ne $new) { throw 'user_dir key not found' }
    Copy-Item $p "$p.bak-coopdev" -Force
    [IO.File]::WriteAllText($p, $raw2, (New-Object Text.UTF8Encoding $false))
    "user_dir: $old -> $new"
}
'job-start' {
    if (-not (Test-Path $Source)) { throw "no $Source" }
    $r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{
        CommandLine = "cmd.exe /c `"$Source`""; CurrentDirectory = (Split-Path $Source -Parent) }
    if ($r.ReturnValue -ne 0) { throw "Win32_Process.Create failed: $($r.ReturnValue)" }
    "pid=$($r.ProcessId)"
}
default { throw "unknown action $Action" }
}
