import array

import pyperclip as pc
import tkinter as tk

SNAKE_CASE = ['snake', 'снейк', 'smokies']
CAMEL_CASE = ['camel', 'кому', 'хаббл', 'kamo']
DEFAULT_CASE = ['default']

class ListnerManger():
    def __init__(self, state, window):
        self.commands = ['getservice', 'manger', 'case', 'keys', 'менеджер', 'gypsy rose', 'айз', 'smokies']
        self.state = state
        self.window = window
        self.his = []

    def process(self, speach_resul):
        if not speach_resul:
            return False

        self.to_console(speach_resul['alternative'][0]['transcript'])
        c = self.is_commands(speach_resul)
        if c:
            self.get_command_secification(c)
            return False

        str = self.get_string(speach_resul=speach_resul)
        str = self.state.getStr(str)
        self.save_to_buffer(str)
        self.save(str)
        self.write()

    def get_string(self, speach_resul):
        if self.state.is_up == False:
            return speach_resul['alternative'][0]['transcript'].lower()

        return speach_resul['alternative'][0]['transcript'].upper()

    def to_console(self, string):
        print(string)

    def save(self, str):
        self.his.append(str)
        if len(self.his) > 3:
            self.his.pop(0)

    def save_to_buffer(self, string):
        pc.copy(string)


    def write(self):
        string = "\n".join(self.his)
        root = tk.Tk()
        a = pc.paste()
        self.window.lable.setText(string)

    def is_commands(self, speach_resul):
        for alternative in speach_resul['alternative']:
            for c in self.commands:
                if alternative['transcript'].find(c) != -1:
                    return alternative['transcript']

        return False

    def get_command_secification(self, str):
        if str.find(self.commands[3]) or str.find(self.commands[4]):
            self.state.case = self.get_case(str)
        if str.find('is up'):
            if (str.find('true')):
                self.state.is_up = True
            self.state.is_up = False

    def get_case(self, str):
        for case in SNAKE_CASE:
            if str.find(case) != -1:
                return 2

        for case in CAMEL_CASE:
            if str.find(case) != -1:
                return 1

        for case in DEFAULT_CASE:
            if str.find(case) != -1:
                return 0
        return self.state.case