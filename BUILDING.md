# Build and release

Use Windows x64, Visual Studio C++ Build Tools (with Clang), Windows Python 3.10+ and MSYS2 CLANG64. Install the port dependencies described in [the Windows toolchain guide](packaging/windows/README.md).

```sh
git clone https://github.com/mark3317/bbgl.git
cd bbgl
git checkout develop
git submodule update --init gpu/third_party/fsr-vulkan gpu/third_party/imgui third_party/LibAtrac9 gpu/third_party/magic_enum gpu/third_party/miniz gpu/third_party/xbyak mods-src/BBSC
bash packaging/windows/build-coop-package.sh
```

The command builds the pinned BBSC-GL submodule, the port, freezes the launcher and fork game server, assembles the complete co-op payload and verifies its manifest and release hygiene. shadNet account/runtime dependencies are cached in `out/vendor`; their upstream archives are SHA-256 pinned in `bundle-coop.py`. These are build-time dependencies: players do not download a separate BBSC package.

The two button packs are binary deltas under `bundled-mods/prompts`, applied to the player's original 1.09 texture. No game folder is needed to build the release. Build outputs live in `out/`; release ZIP and SHA-256 file live in `dist/`.

`SKIP_BUILD=1` skips rebuilding the port only, for verified launcher-only iterations. BBSC is still built from its pinned source. A public release should use the full command.

## Branches

- `develop`: daily work and fixes.
- `main`: tested release source.
- `v1.0.0`: refreshed BBGL release on `main` (replaces the initial test release). Future published release tags should be immutable.

Before releasing: run Python checks, build, verify the ZIP, smoke-test the frozen launcher and bundled account/server programs, and perform the relevant in-game co-op test. Document any untested gameplay changes in release notes. Publish the ZIP and `.sha256` together; do not upload a working installation, settings, accounts, server database or saves.
