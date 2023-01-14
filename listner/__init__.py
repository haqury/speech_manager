import string

import pyperclip as pc
import tkinter as tk
import speach_manager.speech_service as speach_service
from speach_manager.listner import project_manager, case_manager, dubler_manager


class ListnerManger():
    def __init__(self, state, window):
        self.base_commands = ['система вернись', 'sistema']
        self.current_manager = "write"
        self.commands = ['getservice', 'manger', 'case', 'keys', 'менеджер', 'gypsy rose', 'айз', 'smokies', 'is up', 'is ap']
        self.state = state
        self.window = window
        self.his = []
        self.his_arr = []
        self.managers = [
            case_manager.CaseManager(self),
            speach_service.SpeechService(state),
            dubler_manager.DublerManager(state, speach_service.SpeechService(state), )
        ]
        self.managers_process = [
            dubler_manager.DublerManager(state, speach_service.SpeechService(state), )
        ]



    def process(self, speach_resul):
        if not speach_resul:
            return False
        str = self.get_string(speach_resul=speach_resul)
        if not str:
            return False
        print(self.state.listner)
        c = self.is_commands(str)
        if c:
            self.get_command_secification(c.lower())
        # manager_name = self.get_process_secification()
        # if manager_name:
        #     self.process(manager_name)
        if self.state.listner != self.current_manager:
            self.command_spec(str)
        self.process_write(str)

    def process_write(self, str: str):
        print(self.state.case)
        str = self.state.getStr(str)
        self.save(self.concat_str(str))
        self.write()

    def command_spec(self, str: str):
        if self.current_manager != self.state.listner:
            for i in self.base_commands:
                if str.find(i) and str.find(i) != -1:
                    self.current_manager = self.state.listner
                    speach_service.speech('Базовый режим', speach_service.LANG_RUS)
                    return False
            if self.current_manager != self.state.listner:
                return
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
        if self.state.is_up == False:
            return speach_resul['alternative'][0]['transcript'].lower()

        return speach_resul['alternative'][0]['transcript'].upper()

    def to_console(self, string):
        print(string)

    def save(self, str):
        pc.copy(str)
        rhis = list(reversed(self.his))
        rhis.append(str)
        if len(rhis) > 3:
            rhis.pop(0)
        self.his = list(reversed(rhis))

    def write(self):
        string = "\n".join(list(reversed(self.his)))
        self.window.lable.setText(string)

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

    def get_command_secification(self, str):
        for m in self.managers:
            if m.is_spec(str):
                m.run(str)

    def is_process(self):
        if self.state != self.current_manager:
            return True
        return False

    def get_process_secification(self):
        for m in self.managers_process:
            if m.is_spec_proc(self.state.current_manager):
                return m.run()

