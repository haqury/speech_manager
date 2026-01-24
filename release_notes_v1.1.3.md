## What's New in v1.1.3

### New Features
- **📁 Portable Configuration**: The application now looks for and creates `config.json` in the folder with the .exe file, not in the source folder
- **📋 Auto-create Config**: On first run, if `config.json` is not found, the application automatically creates it with default values
- **📝 Copy config.json.example**: During build, `config.json.example` is automatically copied to the `dist` folder for users

### Bug Fixes
- **🐛 Fixed**: Config was being searched in the wrong directory when running from .exe

### Technical Changes
- Added `get_config_dir()` and `get_config_path()` methods to `Config` class
- Updated `Config.load()` to try loading from `config.json.example` if `config.json` is not found
- Updated `build.bat` to copy `config.json.example` to `dist` folder
- Updated logging to use the same directory as config

Full changelog: https://github.com/haqury/speech_manager/blob/main/CHANGELOG.md

---

## Что нового в v1.1.3

### Новые возможности
- **📁 Портативная конфигурация**: Приложение теперь ищет и создает `config.json` в папке с .exe файлом, а не в папке исходников
- **📋 Автоматическое создание конфига**: При первом запуске, если `config.json` не найден, приложение автоматически создает его с дефолтными значениями
- **📝 Копирование config.json.example**: При сборке `config.json.example` автоматически копируется в папку `dist` для пользователей

### Исправления
- **🐛 Исправлено**: Конфиг искался в неправильной директории при запуске из .exe

### Технические изменения
- Добавлены методы `get_config_dir()` и `get_config_path()` в класс `Config`
- Обновлен `Config.load()` для попытки загрузки из `config.json.example`, если `config.json` не найден
- Обновлен `build.bat` для копирования `config.json.example` в папку `dist`
- Обновлено логирование для использования той же директории, что и конфиг

Полный список изменений: https://github.com/haqury/speech_manager/blob/main/CHANGELOG.md
