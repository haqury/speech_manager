import speech_service
from listner import dubler_manager
import manager.gpt as gpt

call = ["менеджер "]
PATH_FILE_SPEECH_FIRST = 'downloads/Warcraft III – Я жажду служить_(mp3phoenix.ru).mp3'

class Managers():
    def __init__(self, window):
        self.window = window
        self.managers_process = [
            dubler_manager.DublerManager(),
            gpt.GptManager()
        ]

    def start(self):
        speech_service.list_file(PATH_FILE_SPEECH_FIRST)

    def spec(self, str):
        for m in self.managers_process:
            print(self, str, m, 0 if m.is_spec_proc(str) else 1)
            if str and m.is_spec_proc(str):
                return m

        return False

    def process_to_run(self, str):
        return self.spec(str)


    def write(self, result):
        self.window.lables.insertPlainText(result)