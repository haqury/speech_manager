import speech_service
import state
from gtts import gTTS
import os

from speech_service import SpeechService

LANG_RETURN_COMMANDS = ['повторяй', 'osteria']
LISTNER = ['dublin', 'дублёр']

class DublerManager():

    def __init__(self):
        self.current_manager = "дублёр"
        self.speech_service = SpeechService()
        self.commands = LANG_RETURN_COMMANDS
        self.process = LISTNER

    def start(self):
        self.speech_service.speech('дублёр менеджер', speech_service.LANG_RUS)

    def is_spec(self, str) -> bool:
        for c in self.commands:
            if str.lower().find(c.lower()) != -1:
                return True

        return False
    def is_spec_proc(self, str) -> bool:
        for c in self.process:
            if str.lower().find(c.lower()) != -1:
                return True

        return False

    def run(self):
        return self

    def process_to_run(self, str):
        self.speech_service.run(str)

