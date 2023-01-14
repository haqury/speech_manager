from gtts import gTTS
import os

import speach_manager.state

LANG_RUS = 'ru'
RETURN_COMMANDS = ['скажи', 'повтори', 'the fall']

class SpeechService():
    def __init__(self, state: speach_manager.state.State):
        self.commands = RETURN_COMMANDS
        self.state = state

    def is_spec(self, str) -> bool:
        for c in self.commands:
            if str.lower().find(c.lower()) != -1:
                return True

        return False

    def run(self, str):
        return self.speech(str, speach_manager.state.get_keyboard_language())
    def speech(self, str, languages):
        audio = gTTS(text=str, lang='ru', slow=False)

        audio.save("example.mp3")
        os.system("start example.mp3")

def speech(str, languages):
    audio = gTTS(text=str, lang=languages, slow=False)

    audio.save("example.mp3")
    os.system("start example.mp3")
