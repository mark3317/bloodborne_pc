# bloodborne_pc / bbport (форк mark3317) — заметки для Claude

Windows-порт Bloodborne (bbport) + Qt/QML-лаунчер на Python, в нашем форке — сборка «bbport-coop»
с кооперативом BBSC. Цель: релизный кооп (см. CLAUDE.md в `../BBSC`) и лаунчер с минимумом настроек:
запустил → указал игру/сейвы/графику → играешь; моды, сервер, BBSC настраиваются автоматически и скрыто.

Общайся по-русски. Пользователь — Android/Kotlin-разработчик, Linux/macOS знает.

## Рабочие папки (mark-pc, Windows)
| Путь | Что |
|---|---|
| `C:\Users\markn\CLionProjects\bloodborne_pc` | этот репо |
| `C:\Users\markn\CLionProjects\BBSC` | форк мода BBSC; его `build\mod` кладётся в пакет |
| `D:\Games\Bloodborne\bbport-coop` | установленный лаунчер на этом ПК (сюда деплоим) |
| `D:\Games\Bloodborne\game` | файлы игры CUSA03173 v1.09 (только чтение!) |

Тестовые машины: этот ПК, ноутбук `local_pc` (192.168.88.233, Windows 10, ssh `markn`),
VPS `remote_server` (77.73.67.175, Ubuntu 24, ssh `root`) — co-op сервер (shadNet/BBSC gameserver).

## Git
- Remotes: `mark` = github.com/mark3317/bloodborne_pc (push сюда), `origin` = Jgamrot/bloodborne_pc (апстрим, только fetch).
- Рабочая ветка: `mark/coop-relay`. Не пушить в `origin`, без force-push без явной просьбы.
- Стиль коммитов: `<область>: <что сделано>` (например `bbnet event filter: ...`).

## Структура
- `src/` — C-код порта/хуков (probe.c — загрузчик, engine_hooks, pc_menu, mouse_camera, ...).
- `gpu/` — видеоядро shadPS4 (CMake), там же `gpu/shadps4` и сеть/bbnet.
- `launcher/` — лаунчер: `bbport_launcher*.py`, `bbport_coop.py` (кооп, сервер, invite), `bbport_pkg_setup.py` (мастер установки), `qml/`.
- `packaging/windows/` — `package.sh`, `build-coop-package.sh`, `build_coop_server.sh` (shadnet-p2p + патчи), `play.c`.
- `tests/` — pytest + C-тесты. `docs/` — ROADMAP, CHANGELOG, DEVELOPMENT_LOG.ru.md.

## Сборка (только MSYS2 CLANG64: `C:\msys64\msys2_shell.cmd -clang64` или `bash` с `source msys2-env.sh`)
- Порт: `bash build.sh` → `out/bb-probe.exe`, `bb-play.exe`, `bb-gpu-capabilities.exe` (лог `out/gpu-build.log`).
- Полный кооп-пакет: `bash packaging/windows/build-coop-package.sh`
  (`SKIP_BUILD=1` — без пересборки exe; `COOP_BBSC_BUILD` по умолчанию `../BBSC/build/mod`;
  `COOP_INVITE`/`COOP_NAME` — сервер по умолчанию). Результат: `out/stage/bbport-windows/` и `dist/bbport-coop-windows.zip`.
- Co-op сервер (shadnet) для Windows-хоста: `bash packaging/windows/build_coop_server.sh`.

## Деплой на этот ПК / ноут
- Источник — `out/stage/bbport-windows/`. Копировать поверх установки, НЕ затирая пользовательское:
  `user/`, `mods/`, `bbport.ini`, `input.ini`, `mods.json`, `patches.json`, `coop-server.json` (если там свой сервер).
- Перед заменой — бэкап заменяемых exe/dll (`*.bak-YYYYMMDD`, как `bin/bb-probe.exe.bak-20261027`).
- Ноут: `scp`/`ssh local_pc` (Windows, cmd/PowerShell), путь установки на ноуте уточнить у пользователя, если не записан.

## Цикл разработки и теста (tools/coop-dev в bloodborne_pc)
`bloodborne_pc/tools/coop-dev/coopdev.sh` (из Linux-VM Claude, по ssh) + `coopdev.ps1` (Windows-сторона):
status · commit bbsc|port · build mod|port|package · job · deploy mod|launcher pc|laptop|all · deploy server ·
save list|snap|restore pc|laptop · test begin|collect. Логи прогонов: `bloodborne_pc/out/coop-dev/runs/<id>/{pc,laptop,vps}`.
Снимки сейвов: `<D:|C:>\Games\Bloodborne\coop-dev\saves\<имя>` (SPRJ0005 + BBSC own-world/bell-pending).
На ноуте: установка `C:\Games\Bloodborne\bbport-coop`, user_dir `C:\Games\Bloodborne\test`. На ПК user_dir `D:\Games\Bloodborne\ddd`.
Логи BBSC: `%LOCALAPPDATA%\bbport-coop\BBSC-0.0.1-BBport\bbsc\logs` (+ captures), лог игры `<user_dir>\last_run*.log`.
VPS: `/opt/bbsc/{gameserver,shadnet,logs,data,backups}`, сервисы `bbsc-gameserver`, `bbsc-shadnet` (пользователь bbsc).

## Правила
- Сейвы — только копии. Файлы игры не изменять.
- Лаунчер: любую новую настройку мода/кооператива по возможности делать автоматической, а не ещё одним полем для пользователя.
