import pyperclip as pc
COMMANDS = ['fast', 'фаст', 'first']

true = ['true', 'тру', 'room']


class ConfigManger:
    def __init__(self, listner_manager):
        self.commands = COMMANDS
        self.listner_manager = listner_manager

    def is_spec(self, str) -> bool:
        for c in self.commands:
            if str.lower().find(c.lower()) != -1:
                print('is_spec')
                return True

        return False

    def run(self, str):
        for t in true:
            if str.find(t) != -1:
                self.change_state(True)
                return True

    def change_state(self, state):
        self.listner_manager.state.fastWrite = state

