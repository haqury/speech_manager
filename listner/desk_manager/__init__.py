import pyperclip as pc
SNAKE_CASE = ['snake', 'make', 'снейк', 'smokies']
CAMEL_CASE = ['camel', 'como', 'кому', 'хаббл', 'kamo']
DEFAULT_CASE = ['default', 'the fault', 'the fall', 'дефолт_кейс', 'стандарт_кейс']
IS_UP = ['is up', 'из opt', 'is app', 'is apt']

WORK = ['давай рабатать']
FREE_CODING = ['чем занятся']


class DeskManager:
    def __init__(self, listner_manager):
        self.commands = WORK
        self.listner_manager = listner_manager

    def is_spec(self, str) -> bool:
        for c in self.commands:
            if str.lower().find(c.lower()) != -1:
                return True

        return False

    def run(self, str):
        return



    def change_case(self, type):
        self.listner_manager.state.case = type
        self.listner_manager.last_rebuld()

    def change_uper(self, type):
        print('upper case', type)
        self.listner_manager.state.is_up = type
        self.listner_manager.last_rebuld()
