## What's New in v1.1.1

### Bug Fixes
- **Fixed dynamic language detection**: Status messages now update in real-time when keyboard layout changes during listening or processing
- Improved `update_status()` function to automatically detect language on every status update

### Technical Changes
- Language is now determined dynamically inside `update_status()` function instead of once at the start
- Status messages will immediately reflect the current keyboard layout language

Full changelog: https://github.com/haqury/speech_manager/blob/main/CHANGELOG.md
