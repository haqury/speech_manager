import string

import pyperclip as pc
import tkinter as tk
import speach_manager.speech_service as speach_service
from speach_manager.listner import project_manager, case_manager, dubler_manager, config_manager
import telegram
import pyautogui
import speach_manager.manager.gpt as gpt


class ListnerManger():
    def __init__(self, state, window):
        self.base_commands = ['система вернись', 'gorilla cup', 'говорилка', 'горилка', 'говорил']
        self.current_manager = "write"
        self.commands = ['поговори со мной', 'theresa may', 'play some movie']
        self.commands_state = ['case', 'keys', 'gypsy rose', 'айз', 'smokies', 'is up', 'is ap', 'activate', 'gpt подскажи']
        self.state = state
        self.window = window
        self.his = []
        self.his_arr = []
        self.managers = [
            case_manager.CaseManager(self),
            speach_service.SpeechService(),
            dubler_manager.DublerManager(),
            config_manager.ConfigManger(self),
            gpt.GptManager()
        ]
        self.managers_process = [
            self,
            dubler_manager.DublerManager()
        ]



    def process(self, speach_resul):
        str = self.get_string(speach_resul=speach_resul)
        if not str:
            return False
        print("Listner:" + self.state.listner)
        self.process_write(str)

    def process_write(self, str: str):
        str = self.state.getStr(str)
        self.save(self.concat_str(str))
        self.write()

    def is_command_write(self, str):
        for i in self.base_commands:
            print(i)
            print(str.find(i) and str.find(i) != -1)
            if str.find(i) != -1:
                speach_service.speech('Базовый режим', speach_service.LANG_RUS)
                return True
        return False

    def concat_str(self, str):
        if not self.his:
            return str
        str_arr = str.split(" ")
        i = None
        for s in list(reversed(str_arr)):
            rindex = "".join(list(reversed(self.his[0]))).find(''.join(list(reversed(s))))
            if rindex != -1:
                i = len(self.his[0]) - rindex - len(s)
                break
        if i and str.find(self.his[0][i:]) != -1:
            str = self.his[0][:i] + str
        return str

    def get_string(self, speach_resul):
        return speach_resul['alternative'][0]['transcript'].lower() if speach_resul and speach_resul['alternative'][0] else  None

    def to_console(self, string):
        print(string)

    def save(self, str):
        try:
            pc.copy(str)
        except:
            pyautogui.typewrite(str)

        if self.state.fastWrite:
            pyautogui.typewrite(str)

        rhis = list(reversed(self.his))
        rhis.append(str)
        if len(rhis) > 3:
            rhis.pop(0)
        self.his = list(reversed(rhis))

    def write(self):
        string = "\n".join(list(reversed(self.his)))
        self.window.lable.setText(string)

        # self.window.addAnswer(string)

    def last_rebuld(self):
        for h in self.his:
            h = self.state.getStr(h)
            self.save(h)
            self.write()

    def is_commands(self, str):
        for c in self.commands:
            if str.find(c) != -1:
                return str
        return False
    def is_commands_state(self, str):
        for c in self.commands_state:
            if str.find(c) != -1:
                return str
        return False

    def get_command_secification(self, str):
        for m in self.managers:
            print(self, m, str, m.is_spec(str))
            if m.is_spec(str):
                m.run(str)
                return m

    def is_process(self):
        if self.state != self.current_manager:
            return True
        return False

    def get_process_secification(self):
        for m in self.managers_process:
            if m.is_spec_proc(self.state.current_manager):
                return m.run()

    def send_to_telegram(self):
        bot = telegram.Bot(token='5911315799:AAGwigQbxl_t2Q-Tm10bK671Gcq3-PXAEp4')

        code = '''
        def greet(name):
            print("Hello, " + name + "!")

        greet("John")
        '''

        bot.send_message(chat_id='YOUR_CHAT_ID', text=code)

