# Bloodborne Co-op · mark3317

**English** · [Русский](README.ru.md) · [Download](https://github.com/mark3317/bloodborne_pc/releases/latest) · [Report an issue](https://github.com/mark3317/bloodborne_pc/issues)

A Windows launcher with the **mark3317 BBSC fork built into the release**. One download includes the launcher, game runtime, co-op client, local hosting server and Xbox / keyboard button packs.

## Get started

1. Download `bbport-coop-1.0.0-windows-x64.zip` from Releases and extract it into a new folder.
2. Run `Bloodborne.exe` and select your own decrypted **Bloodborne CUSA03173, version 1.09** game folder.
3. Choose Co-op, enter your co-op account and the host's invite code, then play. To host, use Host a session; guests must be able to reach the host, for example over Tailscale.
4. Choose PlayStation, Xbox or Keyboard in Settings → Controls → Button prompts. Both alternative packs are included; the launcher generates them from your original game texture.

No separate BBSC download or manual DLL replacement is needed. Game files are not included. Back up saves before moving from an older build. Never replace files while the game is running.

## Included

- The maintained BBSC fork, with shared progress, own Hunter's Dream and enemy scaling settings.
- Existing graphics, FPS, mouse and keyboard controls; FSR / DLSS on supported hardware.
- One-hit kill, no-death and other optional gameplay patches, disabled by default.
- English and Russian UI; stable updates from this fork only.
- Xbox prompts by Dommo and PCBButtons by JinkiJinn, bundled as small texture deltas.
- No Discord Rich Presence helper or Hunter's Atlas distribution.

## Requirements and status

Windows x64, compatible Vulkan drivers, and your own game files. Co-op is experimental. Recovery after disconnects / party deaths and chalice combat have outstanding gameplay checks; see the [BBSC backlog](https://github.com/mark3317/BBSC/blob/mark/bbport-fixes/docs/BACKLOG.md). Release notes distinguish build checks from actual in-game testing.

## Development

`main` contains released source; `develop` contains ongoing work. Stable tags use `vX.Y.Z`. The BBSC fork is pinned at `mods-src/BBSC` as a Git submodule.

[Build instructions](BUILDING.md) · [Changelog](CHANGELOG.md) · [Credits and licences](THIRD_PARTY.md)

Maintained by **mark3317**, based on the original port and BBSC. Upstream credits and licence notices are retained. Not affiliated with Sony or FromSoftware.
