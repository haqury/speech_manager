from gtts import gTTS
import os
import pyglet

import state as state

LANG_RUS = 'ru'
PATH_FILE_SPEECH = 'downloads/example.mp3'
RETURN_COMMANDS = ['повтори', 'the fall', 'double or']

class SpeechService():
    def __init__(self):
        self.commands = RETURN_COMMANDS
        self.lang_rus = 'ru'

    def is_spec(self, str) -> bool:
        for c in self.commands:
            if str.lower().find(c.lower()) != -1:
                return True

        return False

    def run(self, str):
        return self.speech(str, state.get_keyboard_language())

    def speech(self, str, languages):
        audio = gTTS(text=str, lang='ru', slow=False)

        audio.save("example.mp3")
        os.system("start example.mp3")

def speech(str, languages):
    audio = gTTS(text=str, lang=languages, slow=False)

    audio.save(PATH_FILE_SPEECH)
    song = pyglet.media.load(PATH_FILE_SPEECH)
    song.play()
    os.remove(PATH_FILE_SPEECH)

def list_file(path):
    song = pyglet.media.load(path)
    song.play()

def speechOld(str, languages):
    audio = gTTS(text=str, lang=languages, slow=False)

    audio.save(PATH_FILE_SPEECH)
    os.system("start "+PATH_FILE_SPEECH)
