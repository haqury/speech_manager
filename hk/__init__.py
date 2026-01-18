import keyboard
import Th

def loadToList(){
    keyboard.add_hotkey('Ctrl + 1', lambda: listed())
}

def listed():
    print('listed write')
    if state.listner != 'write':
        return
    tll = Thread(target=list, args=())
    tll.start()
    time.sleep(2.8)