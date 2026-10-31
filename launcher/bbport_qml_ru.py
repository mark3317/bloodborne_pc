# SPDX-License-Identifier: GPL-2.0-or-later
"""Russian texts of the Qt Quick launcher (bbport_launcher_qml.py, launcher/qml).

The English text is the key: QML shows launcher.tr("English"), the backend passes its labels,
hints, notices and statuses through tr(). Texts made with values ("... {} ...") are matched by
PATTERNS; the values themselves are translated too when they are texts of this table.
The classic Tk launcher keeps its own table (bbport_i18n.py).
"""
import re

RU = {
    "In the host's Hunter's Dream a guest sees its own Dream (own messengers, shops, Doll, workshop tools); off = the host's copy of the Dream": 'Гость видит собственный Сон охотника: своих посланников, магазины, Куклу и инструменты мастерской.',
    "Removes the summoned guest's 30% max HP cut": 'Убирает снижение максимального здоровья призванного гостя на 30%.',
    'A kept death still drops a bloodstain and echoes': 'При смерти остаются пятно крови и отголоски.',
    'The bell costs no Insight': 'Использование колокола не расходует озарение.',
    "Enemies and bosses get stronger for every guest (replaces the game's own boss buff)": 'Враги и боссы становятся сильнее за каждого гостя. Заменяет стандартное усиление боссов.',
    'Henryk, Djura and the other hostile hunters also get the enemy scaling (off = vanilla)': 'Усиление также применяется к Генрику, Джуре и другим враждебным охотникам.',
    'Extra health for normal enemies, per guest': 'Дополнительное здоровье обычных врагов за каждого гостя.',
    'Extra health for bosses, per guest': 'Дополнительное здоровье боссов за каждого гостя.',
    'Extra damage for enemies and bosses, per guest': 'Дополнительный урон врагов и боссов за каждого гостя.',
    'Harder to stagger normal enemies, per guest': 'Дополнительная устойчивость обычных врагов к ошеломлению за каждого гостя.',
    'Harder to stagger bosses, per guest': 'Дополнительная устойчивость боссов к ошеломлению за каждого гостя.',
    "When a guest goes home, bosses, shortcuts, doors and lamps the host has done are added to the guest's own world (adds only, never removes; NPC quests and your character are not touched; saves backed up first)": 'После возвращения гостя домой прогресс боссов, проходов и фонарей хоста добавляется к его миру. Квесты NPC и персонаж не заменяются; сначала создаётся копия сохранения.',
    'Extra logs for the developers (key item census, item hooks, every flag in a session). Off = faster': 'Подробные журналы для диагностики. По умолчанию выключены.',
    'Enter a whole number within the setting range.': 'Введите целое число в допустимом диапазоне.',
    'Which buttons the game shows, from the next start. Xbox (by Dommo) and Keyboard (PCBButtons by JinkiJinn) are bundled. Select your game folder, then choose the buttons; no separate download is needed. Keyboard also binds the keys its images show: E interact, Left Shift dodge, R blood vial, Q item, F transform, mouse buttons to attack.': 'Значки кнопок меняются после перезапуска игры. Xbox от Dommo и PCBButtons от JinkiJinn уже включены: выберите папку игры и нужный набор. Клавиатура также настраивает соответствующие клавиши: E — действие, Shift — уклонение, R — флакон, Q — предмет, F — трансформация, кнопки мыши — атаки.',
    'Experimental. This launcher includes the BBSC-GL fork: one session through deaths, lamps, areas and bosses, each hunter keeping their own character. Play on a co-op server (an invite code, or the one this launcher comes with), or host one on your PC for friends on Tailscale or your home network. BBSC-GL client and hosting files are included and ready to use. Your saves are backed up before every session. Normal play and online are unchanged.': 'Экспериментальный кооператив на основе форка BBSC-GL: одна сессия через смерти, фонари, области и боссов. Каждый сохраняет своего персонажа. Подключитесь по коду приглашения или создайте сервер на своём ПК. BBSC-GL включён в комплект и не требует отдельной загрузки. Перед каждой сессией создаётся копия сохранений.',

    'Prepare bundled BBSC': 'Подготовить встроенный BBSC',
    'Preparing bundled co-op…': 'Подготовка встроенного коопа…',
    'Co-op gameplay': 'Настройки кооператива',
    "Own Hunter's Dream": 'Собственный Сон охотника',
    'No guest HP cut': 'Без снижения здоровья гостя',
    'Bloodstain on death': 'Пятно крови после смерти',
    'Free Beckoning Bell': 'Колокол без расхода озарения',
    'Enemy scaling': 'Масштабирование врагов',
    'Scale NPC hunters': 'Масштабировать NPC-охотников',
    'Enemy HP per guest (%)': 'Здоровье врагов за гостя (%)',
    'Boss HP per guest (%)': 'Здоровье боссов за гостя (%)',
    'Enemy damage per guest (%)': 'Урон врагов за гостя (%)',
    'Enemy stagger resistance per guest (%)': 'Устойчивость врагов за гостя (%)',
    'Boss stagger resistance per guest (%)': 'Устойчивость боссов за гостя (%)',
    'Shared progress': 'Общий прогресс',
    'Research logs': 'Подробные диагностические логи',
    'Bundled BBSC is ready to prepare. Play co-op installs it automatically.': 'BBSC-GL включён в комплект. При запуске коопа он будет подготовлен автоматически.',

    # --- Home, rail, splash -------------------------------------------------------------------
    'Default location': 'Папка по умолчанию',
    'Browse': 'Обзор',
    'The hunt is underway': 'Охота идёт',
    'Preparing game files': 'Подготовка файлов игры',
    'Game files needed': 'Нужны файлы игры',
    'Saves need attention': 'Сохранения требуют внимания',
    'Co-op needs setting up': 'Нужно настроить совместную игру',
    'Sign in to play online': 'Войдите, чтобы играть онлайн',
    'Ready to hunt': 'Готов к охоте',
    'Ready to hunt.': 'Готов к охоте.',
    'Choose your Bloodborne folder, or install it from your own ZIP or PKG dump.':
        'Выберите папку Bloodborne или установите игру из своего дампа ZIP или PKG.',
    'The saves folder cannot be written. Choose another one.':
        'В папку сохранений нельзя записывать. Выберите другую.',
    'LAUNCHER': 'ЛАУНЧЕР',
    'Running': 'Запущена',
    'Needs attention': 'Требует внимания',
    'Ready': 'Готово',
    'Game running': 'Игра запущена',
    'Installing…': 'Установка…',
    'Set up game files': 'Настроить файлы игры',
    'Choose a saves folder': 'Выбрать папку сохранений',
    'Set up co-op': 'Настроить совместную игру',
    'Sign in with Discord': 'Войти через Discord',
    'Play co-op': 'Играть вместе',
    'Play online': 'Играть онлайн',
    'Play offline': 'Играть офлайн',
    'Stop': 'Остановить',
    'Offline': 'Офлайн',
    "Online · The Hunter's Dream": "The Hunter's Dream",
    'Online · Seamless co-op': 'Совместная игра',
    'A new version is ready': 'Готова новая версия',
    'Install': 'Установить',
    'Graphics': 'Графика',
    'Custom': 'Свой',
    ' preset': ' (пресет)',
    'Visuals': 'Изображение',
    'Controls': 'Управление',
    ' prompts': ' (подсказки)',
    'Button prompts': 'Подсказки кнопок',
    'Game files & saves': 'Файлы игры и сохранения',
    'Game & Saves': 'Игра и сохранения',
    'Your data': 'Ваши данные',
    'Game files': 'Файлы игры',
    'Mods & patches': 'Моды и патчи',
    'None enabled': 'Не включены',
    ' mod enabled': ' мод включён',
    ' mods enabled': ' мод. включено',
    'Mods & Patches': 'Моды и патчи',
    'Installed mods': 'Установленные моды',
    'Hold Shift while starting to open this launcher  ·  Insert or L3+R3 opens the guide in game':
        'Удерживайте Shift при запуске, чтобы открыть лаунчер  ·  Insert или L3+R3 открывает меню в игре',
    'Home': 'Главная',
    'Game files need attention': 'Файлы игры требуют внимания',
    'Ready to play': 'Можно играть',
    'Bloodborne is running.': 'Bloodborne запущена.',
    'Installation is in progress.': 'Идёт установка.',
    'Choose a writable saves folder.': 'Выберите папку сохранений, доступную для записи.',
    'Everything required is ready.': 'Всё необходимое готово.',
    'Setup': 'Настройка',
    'Settings': 'Настройки',
    'Log': 'Журнал',
    'System': 'Система',
    'Logs': 'Журналы',
    'Game': 'Игра',
    'Play': 'Играть',
    'Bloodborne starts in ': 'Bloodborne запустится через ',
    'Launching Bloodborne…': 'Запуск Bloodborne…',
    'Hold Shift or click here for the launcher': 'Удерживайте Shift или нажмите здесь, чтобы открыть лаунчер',
    'Bloodborne — Windows': 'Bloodborne — Windows',

    # --- Settings workspace -------------------------------------------------------------------
    'Graphics, display & frame rate': 'Графика, экран и FPS',
    'Prompts, mouse & keyboard': 'Подсказки, мышь и клавиатура',
    'Game files, saves & language': 'Файлы, сохранения, язык',
    'Online': 'Онлайн',
    "The Hunter's Dream sign-in": "Вход в The Hunter's Dream",
    'Co-op': 'Совместная игра',
    'Seamless co-op: host or join': 'Создать или присоединиться',
    'Mods, enhancements & tweaks': 'Моды, улучшения и настройки',
    'Startup, updates & diagnostics': 'Запуск, обновления, журнал',
    'SETTINGS': 'НАСТРОЙКИ',
    'Find a setting': 'Найти настройку',
    'Changes save as you make them. Some take effect the next time the game starts.':
        'Изменения сохраняются сразу. Некоторые вступят в силу при следующем запуске игры.',
    'Results': 'Результаты',
    'Nothing matches “': 'Ничего не найдено по запросу «',
    'Preset': 'Пресет',
    '  ★ Suggested for ': '  ★ Рекомендуется для ',
    'Keyboard': 'Клавиатура',
    'Which buttons the game shows, from the next start. Xbox (by Dommo) and Keyboard (PCBButtons by JinkiJinn) '
    'are mods from Nexus Mods, not part of the launcher: the first time you choose one, its Nexus page opens and '
    'you pick the file you downloaded (.zip, .7z or .rar). Keyboard also binds the keys its images show: E '
    'interact, Left Shift dodge, R blood vial, Q item, F transform, mouse buttons to attack.':
        'Какие кнопки показывает игра (со следующего запуска). Xbox (от Dommo) и Клавиатура (PCBButtons от '
        'JinkiJinn) — моды с Nexus Mods, они не входят в лаунчер: при первом выборе откроется их страница на '
        'Nexus, затем выберите скачанный файл (.zip, .7z или .rar). Клавиатура также назначает клавиши с её '
        'картинок: E — действие, Левый Shift — уклонение, R — флакон крови, Q — предмет, F — трансформация, '
        'кнопки мыши — атака.',
    "Hunter's Atlas (map)": "Hunter's Atlas (карта)",
    'Prepare maps': 'Подготовить карты',
    "Hunter's Atlas by MikeTat1988 (GPL-2.0): a full-screen map with your position, floors, lamps and NPCs. Its "
    "maps are made from your own game files, once. In the game, open the quick menu and choose Map (the tile "
    "beside the first row), or click it.":
        "Hunter's Atlas от MikeTat1988 (GPL-2.0): полноэкранная карта с вашим положением, этажами, лампами и "
        "NPC. Карты один раз создаются из ваших файлов игры. В игре откройте быстрое меню и выберите «Карта» "
        "(плитка рядом с первым рядом) или щёлкните по ней.",
    'Upscaling': 'Масштабирование',
    'Download FSR 4 assets': 'Скачать ресурсы FSR 4',
    'Install from ZIP / PKG': 'Установить из ZIP / PKG',
    'Check again': 'Проверить снова',
    'Setup wizard': 'Мастер настройки',
    'Import trophy keys': 'Импорт ключей трофеев',
    'Open saves folder': 'Открыть папку сохранений',
    "The Hunter's Dream": "The Hunter's Dream",
    "The Hunter's Dream (thehuntersdream.com) is the public online server: messages, bloodstains, summons and "
    "invasions with players on bbhost and the other Bloodborne ports. Sign in once with Discord: press the "
    "button, sign in with Discord on the page that opens, and approve the code. Then choose \"Online · The "
    "Hunter's Dream\" under Play on the Home page. Seamless co-op with your friends is separate: Settings → Co-op.":
        "The Hunter's Dream (thehuntersdream.com) — общий онлайн-сервер: послания, пятна крови, призывы и "
        "вторжения с игроками bbhost и других портов Bloodborne. Войдите один раз через Discord: нажмите кнопку, "
        "войдите в Discord на открывшейся странице и подтвердите код. Затем на главной под «Играть» выберите "
        "«Онлайн · The Hunter's Dream». Бесшовная совместная игра с друзьями — отдельно: Настройки → Совместная игра.",
    'Copy code': 'Скопировать код',
    'Waiting for Discord…': 'Ожидание Discord…',
    'Sign in again': 'Войти снова',
    'Cancel': 'Отмена',
    'Sign out': 'Выйти',
    'Test connection': 'Проверить соединение',
    "The connection to The Hunter's Dream is Awaken's port of bbhost's network code (GPL-3.0), as Supermedo's "
    "port took it in; bbhost and The Hunter's Dream are by droogie and its team. Seamless co-op (the Co-op page) "
    "does not use it.":
        "Подключение к The Hunter's Dream — это порт сетевого кода bbhost от Awaken (GPL-3.0) в том виде, в "
        "каком его взял порт Supermedo; bbhost и The Hunter's Dream созданы droogie и его командой. Бесшовная "
        "совместная игра (страница «Совместная игра») его не использует.",
    'Seamless co-op': 'Бесшовная совместная игра',
    'Experimental. Seamless co-op is BBSC by CLS_AMG (Bloodborne Seamless Co-op): one session through deaths, '
    'lamps, areas and bosses, each hunter keeping their own character. Play on a co-op server (an invite code, '
    'or the one this launcher comes with), or host one on your PC for friends on Tailscale or your home network. '
    'Set up / update BBSC installs the newest BBSC release. Your saves are backed up before every session. '
    'Normal play and online are unchanged.':
        'Экспериментально. Бесшовная совместная игра — это BBSC от CLS_AMG (Bloodborne Seamless Co-op): одна '
        'сессия через смерти, лампы, локации и боссов, у каждого охотника свой персонаж. Играйте на сервере '
        'совместной игры (по коду приглашения или на сервере, который идёт с этим лаунчером) или создайте сервер '
        'на своём ПК для друзей в Tailscale или вашей домашней сети. «Установить / обновить BBSC» ставит новейший '
        'релиз BBSC. Перед каждой сессией делается копия сохранений. Обычная игра и онлайн не меняются.',
    'Host a session': 'Создать сессию',
    'Join a host': 'Присоединиться к хосту',
    'Set up / update BBSC': 'Установить / обновить BBSC',
    'BBSC from ZIP': 'BBSC из ZIP',
    'About BBSC': 'О BBSC',
    "Starts BBSC's two servers on this PC (the first time, Windows asks once to open the firewall for Tailscale "
    "and your home network only). Keep this launcher open while you play; closing it stops the servers.":
        'Запускает два сервера BBSC на этом ПК (в первый раз Windows один раз попросит открыть брандмауэр — '
        'только для Tailscale и вашей домашней сети). Не закрывайте лаунчер во время игры: это остановит серверы.',
    'Restart hosting': 'Перезапустить сервер',
    'Start hosting': 'Запустить сервер',
    'Copy invite code': 'Скопировать код приглашения',
    'Stop hosting': 'Остановить сервер',
    'Paste the invite code from your host, then Play co-op. The host rings the Hunt Bell; you ring the Kin Bell.':
        'Вставьте код приглашения от хоста и нажмите «Играть вместе». Хост звонит в Колокол охоты, вы — в '
        'Колокол родства.',
    'Gameplay patches': 'Патчи геймплея',
    'Optional gameplay changes. All are off by default and apply the next time the game starts.':
        'Необязательные изменения геймплея. По умолчанию все выключены, применяются при следующем запуске игры.',
    'No mods in the mods folder yet. Put each mod in its own folder there, then refresh.':
        'В папке модов пока пусто. Положите каждый мод в отдельную папку и обновите список.',
    'Refresh': 'Обновить',
    'Open mods folder': 'Открыть папку модов',
    'External patches': 'Внешние патчи',
    'Launch': 'Запуск',
    'Start the game directly': 'Сразу запускать игру',
    'Opening Bloodborne starts the game; hold Shift or Ctrl to open the launcher instead.':
        'Bloodborne сразу запускает игру; удерживайте Shift или Ctrl, чтобы открыть лаунчер.',
    'Close the launcher after Play': 'Закрывать лаунчер после запуска игры',
    'Desktop shortcut': 'Ярлык на рабочем столе',
    'Add to Steam': 'Добавить в Steam',
    'Updates': 'Обновления',
    'Check for updates': 'Проверять обновления',
    'Also checks quietly when the game starts directly, and shows the result here and on Play.':
        'Также тихо проверяет при прямом запуске игры и показывает результат здесь и на кнопке «Играть».',
    'Install the new version': 'Установить новую версию',
    'Check now': 'Проверить сейчас',
    'Releases ↗': 'Релизы ↗',
    'Maintenance': 'Обслуживание',
    'Open port folder': 'Открыть папку порта',
    'Open bbport.ini': 'Открыть bbport.ini',
    'Clear shader cache': 'Очистить кэш шейдеров',
    'Copy log': 'Скопировать журнал',
    'Clear log': 'Очистить журнал',

    # --- Setup wizard -------------------------------------------------------------------------
    'Skip setup?': 'Пропустить настройку?',
    'Any missing game files or unwritable saves will still block Play. You can finish setup later in Game & '
    'Saves.\n\nSkip setup anyway?':
        'Без файлов игры или доступной для записи папки сохранений играть не получится. Закончить настройку '
        'можно позже в разделе «Игра и сохранения».\n\nВсё равно пропустить?',
    'FIRST-TIME SETUP': 'ПЕРВАЯ НАСТРОЙКА',
    'Step ': 'Шаг ',
    ' of 4': ' из 4',
    'Welcome to Yharnam': 'Добро пожаловать в Ярнам',
    'Add your game files': 'Добавьте файлы игры',
    'Welcome': 'Начало',
    'Finish': 'Готово',
    'This guide sets up your own copy of Bloodborne, checks the trophy pack and keeps your saves in the right '
    'place. It takes about two minutes.':
        'Этот мастер настроит вашу копию Bloodborne, проверит пакет трофеев и разместит сохранения в нужном '
        'месте. Это займёт около двух минут.',
    'The game files and trophy key are not included in this download. You can skip setup and use the launcher '
    'straight away.':
        'Файлы игры и ключ трофеев не входят в эту загрузку. Можно пропустить настройку и сразу пользоваться '
        'лаунчером.',
    'Have cusa-03173.zip? The next step can unpack it and apply update 1.09. Already have a CUSA03173 folder? '
    'Point the launcher to the folder that contains eboot.bin.':
        'Есть cusa-03173.zip? Следующий шаг распакует его и установит обновление 1.09. Уже есть папка CUSA03173? '
        'Укажите лаунчеру папку, в которой лежит eboot.bin.',
    'Choose how to add Bloodborne 1.09. The installer creates a new game folder and never replaces an existing one.':
        'Выберите, как добавить Bloodborne 1.09. Установщик создаёт новую папку игры и никогда не заменяет '
        'существующую.',
    'Choose a game folder': 'Выбрать папку игры',
    'For cusa-03173.zip, choose the ZIP and then where the game should go, such as C:\\Games\\Bloodborne. For an '
    'extracted game, choose the folder with eboot.bin directly inside it.':
        'Для cusa-03173.zip выберите ZIP, затем место для игры, например C:\\Games\\Bloodborne. Для '
        'распакованной игры выберите папку, где прямо внутри лежит eboot.bin.',
    "A writable saves folder is required to play. Trophy keys are optional and add trophy names. Saves stay in the "
    "launcher's own user folder unless you choose another.":
        'Для игры нужна папка сохранений, доступная для записи. Ключи трофеев необязательны и добавляют названия '
        'трофеев. Сохранения лежат в папке user лаунчера, если вы не выберете другую.',
    'Trophies': 'Трофеи',
    'Optional': 'Необязательно',
    'Required': 'Обязательно',
    'Your game files and saves are ready. Choose a graphics preset, then start playing or open the launcher.':
        'Файлы игры и сохранения готовы. Выберите пресет графики, затем начните игру или откройте лаунчер.',
    'A required check needs attention. Go back to Game files or Your data to fix it.':
        'Обязательная проверка не пройдена. Вернитесь к шагу «Файлы игры» или «Ваши данные», чтобы исправить.',
    '  ★ Suggested for your graphics card.': '  ★ Рекомендуется для вашей видеокарты.',
    'Start the game directly next time': 'В следующий раз сразу запускать игру',
    'Hold Shift while starting to open the launcher instead. In the game, Insert or L3+R3 opens the guide. Setup '
    'can be run again from Game & Saves.':
        'Удерживайте Shift при запуске, чтобы открыть лаунчер. В игре Insert или L3+R3 открывает меню. Мастер '
        'можно запустить снова в разделе «Игра и сохранения».',
    'Start setup': 'Начать настройку',
    'Skip for now': 'Пока пропустить',
    'Back': 'Назад',
    'Continue': 'Далее',
    'Open launcher': 'Открыть лаунчер',
    'Add valid game files to continue.': 'Добавьте правильные файлы игры, чтобы продолжить.',
    'Skip setup': 'Пропустить настройку',

    # --- Settings pages, sections, rows (backend FIELDS / SETTINGS_SECTIONS) -------------------
    'Display': 'Экран',
    'Display & frame rate': 'Экран и частота кадров',
    'Image effects': 'Эффекты изображения',
    'Video memory': 'Видеопамять',
    'Controller': 'Контроллер',
    'Mouse': 'Мышь',
    'Xbox and PlayStation prompts': 'Подсказки Xbox и PlayStation',
    'In-game preferences': 'Настройки в игре',
    'Cheats': 'Читы',
    'Mods': 'Моды',
    'Enhancements': 'Улучшения',
    'Built-in enhancements': 'Встроенные улучшения',
    'Atlas': 'Атлас',
    'Advanced': 'Дополнительно',
    'Diagnostics': 'Диагностика',
    'Overlay': 'Оверлей',
    'Engine': 'Движок',
    'Developer': 'Для разработчиков',
    'Online connection': 'Онлайн-подключение',
    'Upscaler': 'Масштабирование',
    'Renders below the output size and rebuilds a sharp image. DLSS needs an NVIDIA RTX card; FSR 3.1 works on any.':
        'Отрисовывает кадр в меньшем разрешении и восстанавливает чёткое изображение. DLSS требует видеокарту '
        'NVIDIA RTX, FSR 3.1 работает на любой.',
    'Upscaling preset': 'Пресет масштабирования',
    'How far below the output the game renders: higher factors are faster and softer.':
        'Насколько ниже выходного разрешения рисует игра: больший множитель быстрее, но мягче.',
    'Output resolution': 'Выходное разрешение',
    "The final image size, usually your display's.": 'Итоговый размер изображения, обычно как у вашего экрана.',
    'Frame generation': 'Генерация кадров',
    "Makes frames between two of the game's: 60 FPS on screen becomes 120. Needs a display that fast; adds a "
    "little input latency. DLSS needs a GeForce RTX 40/50 and its frame generation files.":
        'Создаёт кадры между кадрами игры: 60 FPS на экране становятся 120. Нужен экран с такой частотой; '
        'немного увеличивает задержку ввода. DLSS требует GeForce RTX 40/50 и файлы генерации кадров.',
    'Frame generation multiplier': 'Множитель генерации кадров',
    '3× and 4× need DLSS on a GeForce RTX 50.': '3× и 4× требуют DLSS на GeForce RTX 50.',
    'Fit frame generation to the display': 'Подстраивать генерацию кадров под экран',
    "Generates only the frames your display's refresh rate can show.":
        'Создаёт только те кадры, которые может показать частота обновления экрана.',
    'HUD position (ultrawide)': 'Положение интерфейса (сверхширокий экран)',
    '21:9 and 32:9 outputs: health, items and Blood Echoes at the screen edges, or in the centred 16:9 area as on '
    'a 16:9 screen. Applies at the next start.':
        'Для 21:9 и 32:9: здоровье, предметы и Отголоски крови по краям экрана или в центральной области 16:9, '
        'как на экране 16:9. Применяется при следующем запуске.',
    'Live resolution changes': 'Смена разрешения на лету',
    'Lets the in-game menu change the upscaling preset without a restart, at some cost in speed.':
        'Позволяет менять пресет масштабирования в меню игры без перезапуска, ценой небольшой потери скорости.',
    'Model detail': 'Детализация моделей',
    'How soon distant models switch to simpler versions. Highest costs GPU time.':
        'Как скоро дальние модели заменяются упрощёнными. «Максимальная» нагружает видеокарту.',
    'Video memory pressure target': 'Порог использования видеопамяти',
    'Starts clearing old textures and buffers before the chosen amount. This is not a hard VRAM cap; lower values '
    'may cause stutter. Restart the game to apply.':
        'Начинает выгружать старые текстуры и буферы до выбранного объёма. Это не жёсткий лимит видеопамяти; '
        'меньшие значения могут вызывать подтормаживания. Применяется после перезапуска игры.',
    'Chromatic aberration': 'Хроматическая аберрация',
    'Colour fringes at the screen edges. Look only.': 'Цветная кайма по краям экрана. Только внешний вид.',
    'Depth of field': 'Глубина резкости',
    'Blurs the background in cutscenes and close-ups. Look only.':
        'Размывает фон в катсценах и на крупных планах. Только внешний вид.',
    'Motion blur': 'Размытие в движении',
    'Blur while turning the camera. Look only.': 'Размытие при повороте камеры. Только внешний вид.',
    'Ambient occlusion (SSAO)': 'Затенение окружения (SSAO)',
    'Soft shadows in corners and creases. Costs GPU time.': 'Мягкие тени в углах и складках. Нагружает видеокарту.',
    "The game's own anti-aliasing": 'Сглаживание самой игры',
    "The game's own edge smoothing, under the upscaler. Look only.":
        'Собственное сглаживание краёв игры, под масштабированием. Только внешний вид.',
    'Shadows of dynamic lights': 'Тени от динамического света',
    'Shadows cast by lamps, torches and other moving lights. Costs GPU time.':
        'Тени от ламп, факелов и других подвижных источников света. Нагружает видеокарту.',
    'Screen-space reflections (not in the original)': 'Отражения в экранном пространстве (нет в оригинале)',
    'Reflections on wet streets; not in the original game. Costs GPU time.':
        'Отражения на мокрых улицах; в оригинальной игре их нет. Нагружает видеокарту.',
    'Sharpening (RCAS)': 'Повышение резкости (RCAS)',
    'Sharpens the upscaled image.': 'Делает масштабированное изображение резче.',
    'Sharpness (0.00–1.00)': 'Резкость (0.00–1.00)',
    'Object motion vectors': 'Векторы движения объектов',
    'Motion data for moving characters: fewer ghosting trails with an upscaler.':
        'Данные о движении персонажей: меньше шлейфов при масштабировании.',
    'Show FPS counter': 'Показывать счётчик FPS',
    'Frame rate': 'Частота кадров',
    'Frames ahead': 'Кадров наперёд',
    'Unlocked mode limit': 'Предел в режиме без ограничения',
    'Fullscreen': 'Полноэкранный режим',
    'Fullscreen type': 'Тип полноэкранного режима',
    'Exclusive switches the display to its own mode: notifications and other windows do not show over the game.':
        'Эксклюзивный переключает экран в собственный режим: уведомления и другие окна не появляются поверх игры.',
    'Monitor': 'Монитор',
    'The monitor the game window and fullscreen go to, in the order the game log lists them.':
        'Монитор для окна игры и полноэкранного режима, в порядке, как они перечислены в журнале игры.',
    'Primary monitor': 'Основной монитор',
    'Monitor 1': 'Монитор 1', 'Monitor 2': 'Монитор 2', 'Monitor 3': 'Монитор 3', 'Monitor 4': 'Монитор 4',
    'HDR output': 'Вывод HDR',
    'Presentation mode': 'Режим вывода кадров',
    'Draw pipeline': 'Конвейер отрисовки',
    'GPU readbacks': 'Чтение данных с видеокарты',
    'Frame statistics': 'Статистика кадров',
    'GPU profiling': 'Профилирование видеокарты',
    'Vulkan validation': 'Проверка Vulkan',
    'Extra environment variables': 'Дополнительные переменные окружения',
    'Game folder (contains eboot.bin)': 'Папка игры (с eboot.bin)',
    'DLC folder (base-game dumps only, e.g. SPEXPANSIONDLC03)':
        'Папка DLC (только для дампов базовой игры, например SPEXPANSIONDLC03)',
    'Saves folder': 'Папка сохранений',
    'Game language': 'Язык игры',
    'Voice language': 'Язык озвучки',
    'As in the game uses the original voice setting; other choices use available tracks.':
        '«Как в игре» оставляет исходную озвучку; другие варианты используют доступные дорожки.',
    'Hunter name': 'Имя охотника',
    'Skip the intro logos and movie': 'Пропускать логотипы и вступительный ролик',
    'Mouse camera (click the game window to use it)': 'Камера мышью (щёлкните по окну игры, чтобы включить)',
    'Mouse sensitivity': 'Чувствительность мыши',
    'Invert mouse Y': 'Инвертировать мышь по вертикали',
    "Mouse pointer in the game's menus (hover, click, right-click back)":
        'Указатель мыши в меню игры (наведение, щелчок, правый щелчок — назад)',
    'Hide the mouse cursor in the game (for mouse-to-controller tools)':
        'Скрывать курсор мыши в игре (для программ эмуляции контроллера)',
    'Keyboard movement smoothing (WASD direction changes)': 'Сглаживание движения с клавиатуры (смена направления WASD)',
    'Free camera': 'Свободная камера',
    'Debug menu': 'Меню отладки',
    'Never die (health stops at 1 HP)': 'Бессмертие (здоровье не опускается ниже 1)',
    'Enemies do not see you (unless attacked)': 'Враги не видят вас (пока вы не атакуете)',
    'Enemies do not hear you': 'Враги не слышат вас',
    'Rally never fades': 'Восстановление здоровья не угасает',
    'Control the targeted enemy (R3; L3 to go back; not with the free camera)':
        'Управлять выбранным врагом (R3; L3 — вернуться; не со свободной камерой)',
    'No stamina use': 'Выносливость не тратится',
    'No stamina use out of combat (8 s after your last attack or hit)':
        'Выносливость не тратится вне боя (через 8 с после последней атаки или удара)',
    'No Rally (hits do not give health back)': 'Без восстановления (удары не возвращают здоровье)',
    'Camera further from the character': 'Камера дальше от персонажа',
    'No camera auto-rotation while moving': 'Без автоповорота камеры при движении',
    'Run with less stick tilt (about 70%)': 'Бег при меньшем наклоне стика (около 70%)',
    'Japanese/Asian buttons: Circle confirms and interacts, Cross dodges':
        'Японская раскладка: Круг подтверждает и взаимодействует, Крест — уклонение',
    'Dark Souls-style ragdoll physics (corpses fly further)': 'Физика тел как в Dark Souls (тела отлетают дальше)',
    'UPnP': 'UPnP',
    'Opens a port on your router for summons. Turn it off on Tailscale or another VPN.':
        'Открывает порт на роутере для призывов. Выключите при Tailscale или другом VPN.',
    'Co-op name': 'Имя в совместной игре',
    'Your name in co-op, 3-16 letters, numbers, - or _.': 'Ваше имя в совместной игре: 3–16 букв, цифр, - или _.',
    'Co-op password': 'Пароль совместной игры',
    "For your co-op account on the host's server. Use one you use nowhere else.":
        'Для вашего аккаунта на сервере хоста. Используйте пароль, который больше нигде не используете.',
    'Host invite code': 'Код приглашения хоста',
    "Paste the BBCOOP- code your host sent you. Leave empty when you host, or to use this launcher's own co-op "
    "server (coop-server.json).":
        'Вставьте код BBCOOP-, присланный хостом. Оставьте пустым, если хост — вы, или чтобы играть на сервере '
        'этого лаунчера (coop-server.json).',
    'Co-op game program': 'Программа игры для совместной игры',
    "Which bb-probe.exe co-op runs. This launcher's has frame generation, the mouse settings and the rest; BBSC's "
    "is the one BBSC tests with.":
        'Какой bb-probe.exe запускать для совместной игры. У этого лаунчера есть генерация кадров, настройки мыши '
        'и остальное; эмулятор BBSC — тот, на котором BBSC тестируют.',
    "This launcher's (all its settings; BBSC relay built in)": 'Этого лаунчера (все настройки; relay BBSC встроен)',
    "BBSC's own BBport build (BBport 1.7.2 features only)": 'Собственная сборка BBport от BBSC (только возможности BBport 1.7.2)',
    'Enable mods': 'Включить моды',
    'Mods folder': 'Папка модов',
    'Refresh mods': 'Обновить список модов',
    'External patches folder': 'Папка внешних патчей',
    "Hunter's Dream mirror: change appearance": 'Зеркало во Сне Охотника: смена внешности',
    'Two invaders in the late areas (every player needs it)': 'Два захватчика в поздних локациях (нужно всем игрокам)',
    'Rebirth in the Nightmare at the Altar of Despair': 'Перерождение в Кошмаре у Алтаря отчаяния',
    'Lamps: Level Up and Storage at every lit lamp': 'Лампы: повышение уровня и хранилище у каждой зажжённой лампы',
    'Boss rematches at their lamps (experimental; back up your saves)':
        'Повторные бои с боссами у их ламп (экспериментально; сделайте копию сохранений)',
    "Hunter's Atlas: full-screen map (Map in the game's quick menu)":
        "Hunter's Atlas: полноэкранная карта («Карта» в быстром меню игры)",
    'Fast travel to discovered lamps from the map': 'Быстрое перемещение к открытым лампам с карты',
    "Reveal an area's map only after its boss": 'Показывать карту локации только после её босса',
    'Pickup markers (vials, Insight, equipment, Coldblood)': 'Метки предметов (флаконы, Озарение, снаряжение, Холодная кровь)',
    'NPC markers': 'Метки NPC',
    'All NPCs': 'Все NPC',
    'Only NPCs with new dialogue': 'Только NPC с новыми репликами',
    'Hidden': 'Скрыты',
    'Launcher language': 'Язык лаунчера',
    'System default': 'Как в системе',

    # --- Graphics presets (core.GRAPHICS_PRESET_INFO), setup facts -----------------------------
    'Low': 'Низкий', 'Balanced': 'Баланс', 'High': 'Высокий', 'Ultra': 'Ультра',
    'Unlocked': 'Без ограничения', 'Windowed': 'В окне',
    'Performance upscaling (×2), lower model detail, no SSAO or dynamic-light shadows, 60 FPS. For integrated '
    'graphics, the Steam Deck and cards with under 4 GB.':
        'Масштабирование «Производительность» (×2), упрощённые модели, без SSAO и теней от динамического '
        'света, 60 FPS. Для встроенной графики, Steam Deck и видеокарт с памятью меньше 4 ГБ.',
    "Balanced upscaling (×1.7) and the game's own detail, 120 FPS. The default; for cards with 4-8 GB.":
        'Масштабирование «Баланс» (×1.7) и исходная детализация игры, 120 FPS. По умолчанию; для видеокарт '
        'с 4–8 ГБ.',
    "Quality upscaling (×1.5) and the game's own detail, 120 FPS. For cards with 8-12 GB.":
        'Масштабирование «Качество» (×1.5) и исходная детализация игры, 120 FPS. Для видеокарт с 8–12 ГБ.',
    'Native resolution, highest model detail and screen-space reflections (not in the original game), 120 FPS. '
    'For cards with 12 GB or more.':
        'Родное разрешение, максимальная детализация моделей и отражения в экранном пространстве (нет в '
        'оригинальной игре), 120 FPS. Для видеокарт с 12 ГБ и больше.',
    'Your own combination. Choosing a preset changes only upscaling, model detail, SSAO, dynamic-light shadows, '
    'reflections and the frame rate.':
        'Ваша собственная комбинация. Выбор пресета меняет только масштабирование, детализацию моделей, SSAO, '
        'тени от динамического света, отражения и частоту кадров.',

    # --- Option labels without a Russian label in the launcher core ----------------------------
    'Off': 'Выключено', 'On': 'Включено',
    'TAA (native resolution anti-aliasing)': 'TAA (сглаживание в родном разрешении)',
    'AMD FSR 3.1 Frame Generation (any GPU)': 'Генерация кадров AMD FSR 3.1 (любая видеокарта)',
    'NVIDIA DLSS Frame Generation (GeForce RTX 40/50)': 'Генерация кадров NVIDIA DLSS (GeForce RTX 40/50)',
    '2× (one generated frame)': '2× (один созданный кадр)',
    '3× (DLSS on GeForce RTX 50)': '3× (DLSS на GeForce RTX 50)',
    '4× (DLSS on GeForce RTX 50)': '4× (DLSS на GeForce RTX 50)',
    'Screen edges': 'По краям экрана', 'Halfway': 'Посередине', 'Centred (16:9)': 'В центре (16:9)',
    'Automatic (recommended)': 'Автоматически (рекомендуется)',
    'No limit  ⚠': 'Без ограничения  ⚠',
    '1 (default)': '1 (по умолчанию)',
    'Unbounded': 'Без ограничения',
    'Borderless (default)': 'Без рамки (по умолчанию)',
    'Exclusive': 'Эксклюзивный',
    'Mailbox (low latency, no tearing)': 'Mailbox (малая задержка, без разрывов)',
    'Immediate (tearing)': 'Immediate (с разрывами)',
    'Light': 'Слабое', 'Medium (default)': 'Среднее (по умолчанию)', 'Strong': 'Сильное',
    'Auto (8+ threads)': 'Авто (8+ потоков)',
    'Off (more stable)': 'Выключено (стабильнее)',
    'Relaxed (default)': 'Мягкий (по умолчанию)',
    'Precise': 'Точный',
    "The Hunter's Dream (Discord sign-in)": "The Hunter's Dream (вход через Discord)",
    'shadNet server (address below)': 'Сервер shadNet (адрес ниже)',
    'Performance (×2)': 'Производительность (×2)',
    'Balanced (×1.7)': 'Баланс (×1.7)',
    'Quality (×1.5)': 'Качество (×1.5)',
    'Native AA (×1.0)': 'Родное сглаживание (×1.0)',
    'Ultra Performance (×3)': 'Макс. производительность (×3)',
    'Russian': 'Русский', 'Japanese': 'Японский', 'French': 'Французский', 'Spanish': 'Испанский',
    'German': 'Немецкий', 'Italian': 'Итальянский', 'Portuguese (Brazil)': 'Португальский (Бразилия)',
    'Portuguese (Portugal)': 'Португальский (Португалия)', 'Spanish (Latin America)': 'Испанский (Латинская Америка)',
    'English (UK)': 'Английский (Великобритания)', 'Dutch': 'Нидерландский', 'Polish': 'Польский',
    'Turkish': 'Турецкий', 'Finnish': 'Финский', 'Swedish': 'Шведский', 'Danish': 'Датский',
    'Norwegian': 'Норвежский', 'Korean': 'Корейский', 'Chinese (Traditional)': 'Китайский (традиционный)',
    'Chinese (Simplified)': 'Китайский (упрощённый)',

    # --- Notices, statuses, errors (backend) --------------------------------------------------
    'Bloodborne was added to your Steam library.': 'Bloodborne добавлена в вашу библиотеку Steam.',
    'Bloodborne.exe is missing from the download': 'В загрузке нет Bloodborne.exe',
    'Checking BBSC releases…': 'Проверка релизов BBSC…',
    'Checking graphics card…': 'Проверка видеокарты…',
    'Choose a BBSC package (BBSC-<version>-BBport.zip)': 'Выберите пакет BBSC (BBSC-<версия>-BBport.zip)',
    'Choose a writable saves folder before playing.': 'Перед игрой выберите папку сохранений, доступную для записи.',
    'Choose the game folder containing eboot.bin first.': 'Сначала выберите папку игры с eboot.bin.',
    'Choose your game folder to begin': 'Выберите папку игры, чтобы начать',
    'Close the game before clearing its cache.': 'Закройте игру перед очисткой её кэша.',
    'Close the game before updating.': 'Закройте игру перед обновлением.',
    'Close the game or wait for the current setup to finish.': 'Закройте игру или дождитесь окончания текущей установки.',
    'Desktop and Start Menu shortcuts created.': 'Ярлыки на рабочем столе и в меню «Пуск» созданы.',
    'Entering original x86-64 code': 'Переход к исходному коду x86-64',
    'FSR 4 assets are already installed.': 'Ресурсы FSR 4 уже установлены.',
    'FSR 4 assets installed.': 'Ресурсы FSR 4 установлены.',
    'FSR 4 assets ready': 'Ресурсы FSR 4 готовы',
    'Fill in your co-op name and password first.': 'Сначала укажите имя и пароль для совместной игры.',
    'Fill in your co-op name and password first; they make your account on your server.':
        'Сначала укажите имя и пароль для совместной игры: с ними создаётся ваш аккаунт на вашем сервере.',
    'First time: say Yes to the Windows prompt (firewall and C++ runtime)…':
        'В первый раз: ответьте «Да» на запрос Windows (брандмауэр и библиотеки C++)…',
    'First time: say Yes to the Windows prompt (firewall)…': 'В первый раз: ответьте «Да» на запрос Windows (брандмауэр)…',
    'Game archive or base PKG (*.zip *.pkg)': 'Архив игры или базовый PKG (*.zip *.pkg)',
    'Game folder already exists': 'Папка игры уже существует',
    'Game installation could not finish': 'Не удалось завершить установку игры',
    'Game installed and version 1.09 verified. Press PLAY.': 'Игра установлена, версия 1.09 подтверждена. Нажмите «Играть».',
    'Game installed. Check that the launcher reports version 1.09 before playing.':
        'Игра установлена. Перед игрой проверьте, что лаунчер показывает версию 1.09.',
    'Getting co-op ready…': 'Подготовка совместной игры…',
    'Graphics card check unavailable': 'Проверка видеокарты недоступна',
    "Hunter's Atlas maps ready. Turn the map on and play: Map is in the game's quick menu.":
        "Карты Hunter's Atlas готовы. Включите карту и играйте: «Карта» — в быстром меню игры.",
    'Import failed': 'Импорт не удался',
    'Installing BBSC…': 'Установка BBSC…',
    'Invalid trophy keys': 'Неверные ключи трофеев',
    'Invite code copied. Send it to your friend in a private message.':
        'Код приглашения скопирован. Отправьте его другу в личном сообщении.',
    'JSON files (*.json)': 'Файлы JSON (*.json)',
    'Last step: choose where to create the CUSA03173 game folder': 'Последний шаг: выберите, где создать папку игры CUSA03173',
    'Log copied to clipboard.': 'Журнал скопирован в буфер обмена.',
    'Maps not prepared yet: Prepare maps makes them from your game (5-15 minutes, once).':
        'Карты ещё не подготовлены: «Подготовить карты» создаст их из вашей игры (5–15 минут, один раз).',
    'Maps ready.': 'Карты готовы.',
    'Mod change saved. Restart the game to apply it.': 'Изменение модов сохранено. Перезапустите игру, чтобы применить.',
    'No network found. Connect Tailscale, then try again.': 'Сеть не найдена. Подключите Tailscale и попробуйте снова.',
    'No update PKG': 'Нет PKG обновления',
    'Not set up yet: Set up / update BBSC downloads the newest BBSC from its GitHub releases (about 100 MB), or '
    'Play co-op does it for you.':
        'Ещё не настроено: «Установить / обновить BBSC» скачает новейший BBSC из его релизов на GitHub (около '
        '100 МБ), или это сделает «Играть вместе».',
    "Not signed in to The Hunter's Dream.": "Вход в The Hunter's Dream не выполнен.",
    'Offline: your own world, no servers.': 'Офлайн: ваш собственный мир, без серверов.',
    'On the page that opened, sign in with Discord and approve this code (not in its "code from the game" box):':
        'На открывшейся странице войдите через Discord и подтвердите этот код (не в поле «код из игры»):',
    'Online ID must be your account name, not an email address.': 'Онлайн-ID — это имя аккаунта, а не адрес почты.',
    'Online connection test finished.': 'Проверка онлайн-подключения завершена.',
    "Online on The Hunter's Dream: sign in with Discord first (Settings → Online).":
        "Онлайн на The Hunter's Dream: сначала войдите через Discord (Настройки → Онлайн).",
    'Preparing maps…': 'Подготовка карт…',
    'Preparing the game…': 'Подготовка игры…',
    'Preparing your game files. Keep the launcher open…': 'Подготовка файлов игры. Не закрывайте лаунчер…',
    'Prompt mod download (*.zip *.7z *.rar common.tpf.dcx);;All files (*)':
        'Загрузка мода подсказок (*.zip *.7z *.rar common.tpf.dcx);;Все файлы (*)',
    'ReleaseTrophyKey must be 32 hexadecimal characters': 'ReleaseTrophyKey должен состоять из 32 шестнадцатеричных символов',
    'Replace trophy keys?': 'Заменить ключи трофеев?',
    'Restarting with the new settings…': 'Перезапуск с новыми настройками…',
    'Seamless co-op: choose a co-op name and password first (Settings → Co-op).':
        'Бесшовная совместная игра: сначала укажите имя и пароль (Настройки → Совместная игра).',
    "Seamless co-op: joining your host's server from the invite code.":
        'Бесшовная совместная игра: подключение к серверу хоста по коду приглашения.',
    "Seamless co-op: start hosting, or paste a host's invite code (Settings → Co-op).":
        'Бесшовная совместная игра: запустите сервер или вставьте код приглашения хоста (Настройки → Совместная игра).',
    'Shader cache cleared. The next launch will rebuild it.': 'Кэш шейдеров очищен. Следующий запуск создаст его заново.',
    'Sign-in code copied.': 'Код входа скопирован.',
    "Signed out of The Hunter's Dream on this PC.": "Выход из The Hunter's Dream на этом ПК выполнен.",
    'Starting the co-op servers…': 'Запуск серверов совместной игры…',
    'Starting the sign-in…': 'Начало входа…',
    'Steam did not close. Close it yourself and try again.': 'Steam не закрылся. Закройте его сами и попробуйте снова.',
    'Steam must close while the game is added. Close Steam now?': 'Пока игра добавляется, Steam нужно закрыть. Закрыть Steam сейчас?',
    'Steam was not found on this PC or no account has signed in.': 'Steam не найден на этом ПК, или в нём не выполнен вход.',
    'Step 1: choose the game ZIP or the BASE game PKG (CUSA03173.pkg, not the update)':
        'Шаг 1: выберите ZIP игры или PKG БАЗОВОЙ игры (CUSA03173.pkg, не обновление)',
    'Step 2: choose the plain 1.09 UPDATE PKG (not 720p or 1080p)':
        'Шаг 2: выберите обычный PKG ОБНОВЛЕНИЯ 1.09 (не 720p и не 1080p)',
    'Stopped hosting.': 'Сервер остановлен.',
    "Testing The Hunter's Dream…": "Проверка The Hunter's Dream…",
    "The Hunter's Dream: sign in with Discord on the Online page first.":
        "The Hunter's Dream: сначала войдите через Discord на странице «Онлайн».",
    'The game is running.': 'Игра запущена.',
    'This folder already contains keys.json. Replace it?': 'В этой папке уже есть keys.json. Заменить его?',
    'Trophy keys are already installed.': 'Ключи трофеев уже установлены.',
    'Trophy keys copied to the new saves folder.': 'Ключи трофеев скопированы в новую папку сохранений.',
    'Trophy keys installed successfully.': 'Ключи трофеев установлены.',
    'Update PKG (*.pkg)': 'PKG обновления (*.pkg)',
    'Vulkan graphics card not detected': 'Видеокарта с Vulkan не обнаружена',
    'Wait for the game files to finish installing.': 'Дождитесь окончания установки файлов игры.',
    'Game files not found': 'Файлы игры не найдены',
    'Saves folder is not writable': 'В папку сохранений нельзя записывать',
    # co-op (bbport_coop.py)
    'A co-op name is 3-16 letters, numbers, - or _.': 'Имя в совместной игре — 3–16 букв, цифр, - или _.',
    'Choose a password of at least 4 characters (one you use nowhere else).':
        'Выберите пароль не короче 4 символов (который больше нигде не используете).',
    'Co-op needs a Yes on the Windows administrator prompt (firewall rules); the answer was No. Try Start hosting again.':
        'Для совместной игры нужно ответить «Да» на запрос администратора Windows (правила брандмауэра), а ответ '
        'был «Нет». Попробуйте «Запустить сервер» снова.',
    'Set up co-op first (the BBSC package is missing).': 'Сначала настройте совместную игру (нет пакета BBSC).',
    'That invite code is damaged; ask the host to copy it again.':
        'Код приглашения повреждён; попросите хоста скопировать его ещё раз.',
    "The invite code does not match the host's server: it is from an older session or another host. Ask the host "
    "to copy the invite code again.":
        'Код приглашения не подходит к серверу хоста: он от прошлой сессии или другого хоста. Попросите хоста '
        'скопировать код ещё раз.',
    # pkg setup (bbport_pkg_setup.py)
    'Applying the update to the game folder…': 'Установка обновления в папку игры…',
    'Checking the base game and 1.09 update…': 'Проверка базовой игры и обновления 1.09…',
    'Checking the game PKG…': 'Проверка PKG игры…',
    'Choose an existing destination folder.': 'Выберите существующую папку назначения.',
    'Choose an existing game ZIP or base PKG.': 'Выберите существующий ZIP игры или базовый PKG.',
    'Choose cusa-03173.zip or CUSA03173.pkg.': 'Выберите cusa-03173.zip или CUSA03173.pkg.',
    'Choose the plain 1.09 update PKG too.': 'Выберите также обычный PKG обновления 1.09.',
    'Extracting the 1.09 update…': 'Распаковка обновления 1.09…',
    'Extracting the base game. This can take a while…': 'Распаковка базовой игры. Это может занять время…',
    'Game files installed. Ready to play.': 'Файлы игры установлены. Можно играть.',
    'The PKG extractor is missing from the launcher package.': 'В пакете лаунчера нет распаковщика PKG.',
    'The ZIP must contain CUSA03173.pkg and the plain 1.09 update PKG (not the 720p or 1080p 60fps one).':
        'ZIP должен содержать CUSA03173.pkg и обычный PKG обновления 1.09 (не версию 720p или 1080p 60fps).',
    'The completed game folder is missing eboot.bin.': 'В готовой папке игры нет eboot.bin.',
    'Unpacking the 1.09 update from the ZIP…': 'Распаковка обновления 1.09 из ZIP…',
    'Unpacking the base PKG from the ZIP…': 'Распаковка базового PKG из ZIP…',
    # readiness (bbport_readiness.py)
    'Bloodborne 1.09 and required folders found.': 'Bloodborne 1.09 и нужные папки найдены.',
    'Choose the extracted CUSA03173 folder containing eboot.bin.': 'Выберите распакованную папку CUSA03173 с eboot.bin.',
    'Missing: ': 'Не хватает: ',
    'No trophy pack found; achievements can show IDs only.': 'Пакет трофеев не найден; достижения будут показаны только номерами.',
    'Pack and key format found; launch the game to verify decryption.':
        'Пакет и формат ключа найдены; запустите игру, чтобы проверить расшифровку.',
    'Pack found; import a valid keys.json to show trophy names.': 'Пакет найден; импортируйте правильный keys.json, чтобы видеть названия трофеев.',
    'Save folder is not writable.': 'В папку сохранений нельзя записывать.',
    'Save folder will be created on first launch.': 'Папка сохранений будет создана при первом запуске.',
    'Save path is a file, not a folder.': 'Путь сохранений указывает на файл, а не на папку.',
    'Trophy names have been loaded by the game.': 'Игра загрузила названия трофеев.',
    'Trophy pack cannot be read or has an invalid header.': 'Пакет трофеев не читается или у него неверный заголовок.',
}

# Texts with values: {} in the English template, {0}, {1}, ... in the Russian one.
PATTERNS = [
    ('A co-op server stopped at start; see {}.', 'Сервер совместной игры остановился при запуске; см. {0}.'),
    ('An invite code starts with {}', 'Код приглашения начинается с {0}'),
    ('No BBSC release has a {} package ({}).', 'Ни в одном релизе BBSC нет пакета {0} ({1}).'),
    ('No answer from the co-op server at {}. Is the host hosting, and are you both on Tailscale?',
     'Сервер совместной игры {0} не отвечает. Хост запустил сервер, и вы оба в Tailscale?'),
    ('No answer from the co-op server at {}. The host must be hosting (launcher open), and both of you on '
     'Tailscale or the same network.',
     'Сервер совместной игры {0} не отвечает. Хост должен запустить сервер (лаунчер открыт), а вы оба — быть '
     'в Tailscale или одной сети.'),
    ('The firewall rules were not made although Windows allowed the setup. A firewall program other than Windows '
     'Defender Firewall may manage them; the setup script is {}.',
     'Правила брандмауэра не созданы, хотя Windows разрешила настройку. Возможно, ими управляет другой '
     'брандмауэр, а не Защитник Windows; сценарий настройки: {0}.'),
    ("The host's server did not create the account ({}).", 'Сервер хоста не создал аккаунт ({0}).'),
    ("The host's server does not accept the name {}; choose another.", 'Сервер хоста не принимает имя {0}; выберите другое.'),
    ('Unsafe path in the package: {}', 'Небезопасный путь в пакете: {0}'),
    ('Windows could not run the co-op setup: {}', 'Windows не смогла выполнить настройку совместной игры: {0}'),
    ('{} does not match the checksum BBSC published; not installed.',
     '{0} не совпадает с контрольной суммой, опубликованной BBSC; не установлено.'),
    ("{} is already taken on the host's server, with another password. Use the password you chose with this name "
     "before, or another co-op name.",
     'Имя {0} на сервере хоста уже занято с другим паролем. Введите пароль, который вы выбрали с этим именем, '
     'или другое имя.'),
    ("{} is signed in on the host's server right now. Every player needs their own co-op name; if it is yours, "
     "close the game that uses it first.",
     '{0} сейчас уже в сети на сервере хоста. У каждого игрока должно быть своё имя; если это ваше, сначала '
     'закройте игру, где оно используется.'),
    (' Saves backed up to {}.', ' Копия сохранений: {0}.'),
    ('BBSC {} ({}) installed from {}.', 'BBSC {0} ({1}) установлен из {2}.'),
    ('BBSC {} is the newest release.', 'BBSC {0} — новейший релиз.'),
    ('BBSC {} installed ({}).', 'BBSC {0} установлен ({1}).'),
    ('BBSC {}. Hosting on {}. Send your friend the invite code.', 'BBSC {0}. Сервер на {1}. Отправьте другу код приглашения.'),
    ("BBSC {}. Ready. Host a session, or paste a host's invite code and play.",
     'BBSC {0}. Готово. Создайте сессию или вставьте код приглашения хоста и играйте.'),
    ('BBSC {}. Ready: Play co-op joins {}.', 'BBSC {0}. Готово: «Играть вместе» подключит к серверу {1}.'),
    ('Choose your {} download (by {}, opened on Nexus Mods)', 'Выберите скачанный {0} (от {1}, открыт на Nexus Mods)'),
    ('Copy keys.json to the new saves folder yourself: {}', 'Скопируйте keys.json в новую папку сохранений сами: {0}'),
    ('Could not add the game to Steam: {}', 'Не удалось добавить игру в Steam: {0}'),
    ('Could not check for updates: {}', 'Не удалось проверить обновления: {0}'),
    ('Could not start: {}', 'Не удалось запустить: {0}'),
    ('Downloading version {}…', 'Загрузка версии {0}…'),
    ('Downloading {}: {}%', 'Загрузка {0}: {1}%'),
    ('Installing BBSC {}…', 'Установка BBSC {0}…'),
    ('Installing {}…', 'Установка {0}…'),
    ('FSR 4 download failed: {}', 'Не удалось скачать FSR 4: {0}'),
    ('Game ready · version {}', 'Игра готова · версия {0}'),
    ('Hosting on {} ({}); your account is {}. Copy the invite code for your friend, then press Play co-op. Keep this '
     'launcher open while you play.',
     'Сервер запущен: {0} ({1}); ваш аккаунт: {2}. Скопируйте код приглашения для друга и нажмите «Играть '
     'вместе». Не закрывайте лаунчер во время игры.'),
    ('Install version {} now? Saves, settings and mods are kept.',
     'Установить версию {0} сейчас? Сохранения, настройки и моды останутся.'),
    ('Now: the game renders at the output size, {} × {}.', 'Сейчас: игра рисует в выходном разрешении, {0} × {1}.'),
    ('Now: the game renders at {} × {} and upscales it to {} × {}.',
     'Сейчас: игра рисует в {0} × {1} и масштабирует до {2} × {3}.'),
    ("Online on The Hunter's Dream as {}: messages, bloodstains and summons with everyone.",
     "Онлайн на The Hunter's Dream как {0}: послания, пятна крови и призывы со всеми."),
    ('Preparing maps: {}% · {}', 'Подготовка карт: {0}% · {1}'),
    ('Preparing the maps failed: {}', 'Не удалось подготовить карты: {0}'),
    ('Seamless co-op: you host on {}; send your friends the invite code.',
     'Бесшовная совместная игра: вы хост на {0}; отправьте друзьям код приглашения.'),
    ("Signed in to The Hunter's Dream as {}.", "Вход в The Hunter's Dream выполнен как {0}."),
    ('Starting co-op with {}. Host: ring the Hunt Bell. Guest: ring the Kin Bell.{}',
     'Запуск совместной игры с {0}. Хост: звоните в Колокол охоты. Гость: в Колокол родства.{1}'),
    ('The game could not start (exit code {}). See the log for details.',
     'Игра не запустилась (код выхода {0}). Подробности — в журнале.'),
    ('This is not a valid trophy keys.json: {}', 'Это не правильный keys.json трофеев: {0}'),
    ('Unexpected installer error: {}', 'Неожиданная ошибка установщика: {0}'),
    ('Update failed: {}', 'Обновление не удалось: {0}'),
    ('You have the latest version ({}).', 'У вас последняя версия ({0}).'),
    ('{} FSR 4 assets missing', 'Не хватает ресурсов FSR 4: {0}'),
    ('{} already exists. Choose another location so no game files are replaced.',
     '{0} уже существует. Выберите другое место, чтобы не заменить файлы игры.'),
    ('{} button prompts selected. Restart the game to apply them.',
     'Выбраны подсказки кнопок: {0}. Перезапустите игру, чтобы применить.'),
    ('{} preset chosen. It applies the next time the game starts.', 'Выбран пресет «{0}». Применится при следующем запуске игры.'),
    ('{} preset chosen. Restart the game to apply it.', 'Выбран пресет «{0}». Перезапустите игру, чтобы применить.'),
    ('{} prompts are a separate download: get {} by {} from {}, then choose {} again and pick the downloaded file.',
     'Подсказки {0} скачиваются отдельно: возьмите {1} от {2} с {3}, затем снова выберите {4} и укажите скачанный файл.'),
    ('{}. Or host a session yourself.', '{0}. Или создайте сессию сами.'),
    ('— The game exited (code {}) —', '— Игра завершилась (код {0}) —'),
    ('Could not load Qt Quick launcher: {}', 'Не удалось загрузить лаунчер Qt Quick: {0}'),
    ('Could not extract {}. {}', 'Не удалось распаковать {0}. {1}'),
    ('Could not inspect {}: {}', 'Не удалось проверить {0}: {1}'),
    ('Could not start the PKG extractor: {}', 'Не удалось запустить распаковщик PKG: {0}'),
    ('Game installation failed: {}', 'Установка игры не удалась: {0}'),
    ('Not enough free space here. Allow about {} GB for setup.', 'Здесь мало места. Для установки нужно около {0} ГБ.'),
    ('The ZIP has more than one {}.', 'В ZIP больше одного {0}.'),
    ('{} You chose {} as the base game and {} as the update.', '{0} Вы выбрали {1} как базовую игру и {2} как обновление.'),
    ('{} already exists. Choose another destination so your game files stay safe.',
     '{0} уже существует. Выберите другое место, чтобы файлы игры не пострадали.'),
    ('{} appeared during setup. No files were replaced.', '{0} появилась во время установки. Файлы не заменены.'),
    ('{} holds game version {}, not 1.09. Choose the plain 1.09 update PKG as well.',
     'В {0} версия игры {1}, а не 1.09. Выберите также обычный PKG обновления 1.09.'),
    ('{} is the 1.09 update. Choose the base game PKG (the large CUSA03173.pkg) first, then this update.',
     '{0} — это обновление 1.09. Сначала выберите PKG базовой игры (большой CUSA03173.pkg), затем это обновление.'),
    ('{} looks like the 720p or 1080p 60fps update. Choose the plain 1.09 update PKG instead.',
     '{0} похож на обновление 720p или 1080p 60fps. Выберите вместо него обычный PKG обновления 1.09.'),
    ('{} is not a valid {} PKG. Check that you selected the right file.',
     '{0} — неправильный PKG ({1}). Проверьте, что выбран нужный файл.'),
    (' {} local unlocks recorded.', ' Записано разблокировок: {0}.'),
    ('Save folder is writable; no {} save yet.', 'Папка сохранений доступна для записи; сохранения {0} пока нет.'),
    ('Save folder is writable; {} save data found.', 'Папка сохранений доступна для записи; найдены сохранения {0}.'),
    ('Extracting file {} of {}', 'Распаковка файла {0} из {1}'),
]

_COMPILED = None


def _compiled():
    global _COMPILED
    if _COMPILED is None:
        _COMPILED = []
        for english, russian in PATTERNS:
            regex = '^' + re.escape(english).replace(r'\{\}', '(.*?)') + '$'
            _COMPILED.append((re.compile(regex, re.S), russian))
    return _COMPILED


def tr(text):
    """The Russian text for an English launcher text, or the text itself."""
    if not text:
        return text
    found = RU.get(text)
    if found is not None:
        return found
    for regex, russian in _compiled():
        match = regex.match(text)
        if match:
            return russian.format(*(tr(value) for value in match.groups()))
    return text
