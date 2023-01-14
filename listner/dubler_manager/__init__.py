import speach_manager.state
from gtts import gTTS
import os

LANG_RETURN_COMMANDS = ['повторяй', 'osteria']
LISTNER = ['dublin', 'дублёр']

class DublerManager():

    def __init__(self, state, manager):
        self.state = state
        self.current_manager = "дублёр"
        self.speech_service = manager
        self.manager = manager
        self.commands = LANG_RETURN_COMMANDS
        self.process = LISTNER

    def is_spec(self, str) -> bool:
        for c in self.commands:
            if str.lower().find(c.lower()) != -1:
                return True

        return False
    def is_spec_proc(self, name) -> bool:
        for c in self.process:
            if c.find(name) != -1:
                return True

        return False

    def run(self):
        self.speech_service.run('дублёр активирован')
        self.manager.current_manager = self.current_manager

    def process_to_run(self, str):
        self.speech_service.run(str)

