

class ProjectManager():
    def __init__(self):
        self.commands = ['product', 'project', 'проект', 'прожектор']

    def is_spec(self, name):
        for c in self.commands:
            if name.find(c) != -1:
                return name

        return False



