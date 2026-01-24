## What's New in v1.1.3

### New Features
- **📁 Portable Configuration**: The application now looks for and creates `config.json` in the folder with the .exe file, not in the source folder
- **📋 Auto-create Config**: On first run, if `config.json` is not found, the application automatically creates it with default values
- **📝 Copy config.json.example**: During build, `config.json.example` is automatically copied to the `dist` folder for users

### Improvements
- **🔧 Config Loading Logic**: Config is now searched in the folder with the executable file (for .exe) or in the current working directory (for Python script)
- **📊 Log File**: `speech_manager.log` is now also created in the folder with the .exe file
- **🪟 Adaptive Window Width**: Window width automatically adjusts to the length of the longest text in messages

### Bug Fixes
- **🐛 Fixed**: Config was being searched in the wrong directory when running from .exe

### Technical Changes
- Added `get_config_dir()` and `get_config_path()` methods to `Config` class
- Updated `Config.load()` to try loading from `config.json.example` if `config.json` is not found
- Updated `build.bat` to copy `config.json.example` to `dist` folder
- Updated logging to use the same directory as config

Full changelog: https://github.com/haqury/speech_manager/blob/main/CHANGELOG.md
