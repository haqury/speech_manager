## What's New in v1.1.6

### Bug Fixes
- **🐛 UI freezes**: Fixed periodic application freezes caused by updating the UI from a non-main Qt thread
- **🔧 QMetaObject.invokeMethod**: Replaced with Qt signals — status, window, and volume updates now run on the main thread

### Improvements
- **Threading**: Hotkey handler now runs speech recognition in a separate thread, so the keyboard library thread is not blocked
- **MainWindow signals**: Added `status_update_requested`, `show_window_requested`, `show_volume_bar_requested`, `volume_update_requested` for thread-safe UI updates
- **.gitignore**: Added `.vscode/` and `.atom8n/`

Full changelog: https://github.com/haqury/speech_manager/blob/main/CHANGELOG.md

---

## Что нового в v1.1.6

### Исправления
- **🐛 Зависания интерфейса**: Устранены периодические подвисания из-за обновления UI не из главного потока Qt
- **🔧 QMetaObject.invokeMethod**: Заменены на сигналы Qt — обновление статуса, окна и громкости выполняется в главном потоке

### Улучшения
- **Поток распознавания**: Горячая клавиша запускает распознавание в отдельном потоке, не блокируя поток keyboard
- **Сигналы MainWindow**: Добавлены сигналы для потокобезопасного обновления UI
- **.gitignore**: Добавлены `.vscode/` и `.atom8n/`

Полный список изменений: https://github.com/haqury/speech_manager/blob/main/CHANGELOG.md
