# BBGL changelog

## 1.0.0 — refreshed release, 2026-10-31

- Rename the launcher to Bloodborne Game Launcher (BBGL), repository to `bbgl`, and bundled mod fork to BBSC-GL (`bbsc-gl`).
- Extract into `Bloodborne Game Launcher`; store the writable profile in `%LOCALAPPDATA%\bbgl`, importing previous Local/Roaming profiles without overwriting existing files.
- Include the latest pinned client and server, profile storage changes and ready-to-use button packs.
- Replace the initial test 1.0.0 package. This is still version 1.0.0; existing 1.0.0 installs need a manual download.
- Rewrite player documentation and explain upstream attribution and fork architecture. Gameplay limitations remain tracked in BBSC-GL.


## 1.0.0

- First version of the mark3317 launcher distribution.
- BBSC fork pinned as a Git submodule and bundled with its matching client and server.
- Removed the official BBSC download / DLL override installation sequence.
- Built-in Xbox and PCBButtons texture patches.
- BBSC gameplay settings alongside existing one-hit kill and other gameplay patches.
- Updates use mark3317/bbgl stable releases.
- Removed optional Discord Rich Presence packaging and Hunter's Atlas distribution.
- English / Russian getting-started documentation, release checks and development branch.

Gameplay validation of this packaging change is separate from the existing BBSC test history; see the release notes for the actual checks performed.
