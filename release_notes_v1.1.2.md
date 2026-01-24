## What's New in v1.1.2

### New Features
- **⏹️ Stop Recording with Hotkey**: You can now stop the current recording by pressing the same hotkey again during recording
- **⚙️ Recording Stop Toggle**: New setting in the Appearance section to enable/disable hotkey stop recording feature
- **📝 Maximum Message Length**: New setting to control the maximum length of text displayed in messages (default: 500 characters)

### Improvements
- When recording is stopped via hotkey, the already captured audio is processed and sent for recognition
- Better recording state management with thread-safe locking

### Technical Changes
- Added `enable_hotkey_stop_recording` configuration option (default: `true`)
- Added `max_message_length` configuration option (default: 500)
- Improved `AudioRecorder` class with `should_stop` flag for manual recording termination
- Added `stop_recording()` and `is_recording()` methods to `MicrophoneStream` class

Full changelog: https://github.com/haqury/speech_manager/blob/main/CHANGELOG.md
