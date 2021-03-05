import os, sys
# sys.path.append("/home/pi/torre_tray_official")
sys.path.append(os.path.join(os.path.dirname(__file__), "GUI"))

from parameters import *

#os.system("lxterminal -e 'tmux new-session -s \"torretray_backend\" python3 " + WORKING_DIR_PATH + "back_end/main_be.py' &")
#os.system("lxterminal -e 'tmux new-session -s \"torret  ray_GUI\" python3 " + WORKING_DIR_PATH + "GUI/main_fe.py' &")
# os.system("lxterminal -e 'tmux new-session -d -s \"torretray\" \"python3 " + WORKING_DIR_PATH + "back_end/main_be.py\"; tmux split-window \"python3 " + WORKING_DIR_PATH + "GUI/main_fe.py\"' ")

# Siccome execfile non funziona con python3 uso questa alternativa
def execfile(filepath, globals=None, locals=None):
    if globals is None:
        globals = {}
    globals.update({
        "__file__": filepath,
        "__name__": "__main__",
    })
    with open(filepath, 'rb') as file:
        exec(compile(file.read(), filepath, 'exec'), globals, locals)


execfile('back_end/main_be.py')
execfile('GUI/main_fe.py')

