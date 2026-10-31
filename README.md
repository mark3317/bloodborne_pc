# Bloodborne Game Launcher (BBGL)

**English** · [Русский](README.ru.md) · [Download 1.0.0](https://github.com/mark3317/bbgl/releases/latest) · [Report a problem](https://github.com/mark3317/bbgl/issues)

A Windows launcher for playing Bloodborne alone or with friends. BBGL builds on [yharnam-pc](https://github.com/Jgamrot/yharnam-pc) and includes **[BBSC-GL](https://github.com/mark3317/bbsc-gl)**, our fork of Bloodborne Seamless Co-op. The co-op client and hosting tools come with the download: no separate mod installation or DLL replacement.

## Start playing

1. Download `bbgl-1.0.0-windows-x64.zip` from Releases and extract it. Open the **Bloodborne Game Launcher** folder.
2. Run **Bloodborne.exe** and select your own decrypted Bloodborne **CUSA03173, update 1.09** files. Game files are not included.
3. For solo play, launch the game normally. For co-op, choose Co-op, enter your account and the host's invite code. One player can choose **Host a session**; friends need network access to that PC, for example through Tailscale.
4. Use the in-game co-op bells to gather your party. Keep everyone on the same BBGL release.

Windows x64 and a compatible Vulkan driver are required. For graphics, hardware, controls, extracting your game and other port details, use the **[original yharnam-pc README](https://github.com/Jgamrot/yharnam-pc#readme)**.

## What this fork adds

- A matched launcher, BBSC-GL client and hosting server in one package, pinned to known source revisions.
- Co-op focused on playing through the game together, with guest world recovery, personal NPC rewards and an own Hunter's Dream option. See [how BBSC-GL differs from BBSC](https://github.com/mark3317/bbsc-gl#readme).
- PlayStation, Xbox and keyboard button prompts; the alternative packs are included.
- Updates from **mark3317/bbgl**. Settings, saves managed by the launcher, co-op journals and host data live in `%LOCALAPPDATA%\bbgl`; existing launcher profiles are imported automatically without deleting the originals. A manually selected save folder remains where you chose it.

Co-op is experimental. Chalice combat latency, uncommon death/disconnect recovery and larger parties still need further checks. Keep save backups; automatic backups do not replace them. [Current issues and test status](https://github.com/mark3317/bbsc-gl/blob/mark/bbport-fixes/docs/BACKLOG.md).

## Source and credits

[Build BBGL](BUILDING.md) · [Changes](CHANGELOG.md) · [Credits and licences](THIRD_PARTY.md)

`main` is the release source; `develop` is ongoing work. BBSC-GL is pinned as a submodule. Internal `bbport` / `bbsc` executable names and protocol identifiers are retained for compatibility.

Based on yharnam-pc / bbport and [BBSC by CLS_AMG and contributors](https://github.com/CLSAMG22/BBSC). Their licences and attribution remain included. Bloodborne belongs to FromSoftware and Sony Interactive Entertainment; this is an independent fan project.
