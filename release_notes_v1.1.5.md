## What's New in v1.1.5

### Bug Fixes
- **🐛 Clipboard Fix**: Fixed issue where text was copied to clipboard even when "Clipboard" setting was disabled
- **🔧 Clipboard Restoration**: When "Clipboard" is disabled but "Text Cursor" is enabled, previous clipboard content is now restored after paste

### Technical Changes
- Added logic to save and restore previous clipboard content
- Improved handling when `output_clipboard` is disabled but `output_text_cursor` is enabled

Full changelog: https://github.com/haqury/speech_manager/blob/main/CHANGELOG.md

---

## Что нового в v1.1.5

### Исправления
- **🐛 Исправление буфера обмена**: Исправлена проблема, когда текст попадал в буфер обмена даже при выключенной настройке "Буфер обмена"
- **🔧 Восстановление буфера**: При выключенной настройке "Буфер обмена" и включенной "Вставка в курсор", предыдущее содержимое буфера обмена теперь восстанавливается после вставки

### Технические изменения
- Добавлена логика сохранения и восстановления предыдущего содержимого буфера обмена
- Улучшена обработка случая, когда `output_clipboard` выключен, но `output_text_cursor` включен

Полный список изменений: https://github.com/haqury/speech_manager/blob/main/CHANGELOG.md
