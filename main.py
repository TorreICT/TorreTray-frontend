import os
import sys
sys.path.append("/home/pi/torre_tray_official")
from parameters import *

#os.system("lxterminal -e 'tmux new-session -s \"torretray_backend\" python3 " + WORKING_DIR_PATH + "back_end/main_be.py' &")
#os.system("lxterminal -e 'tmux new-session -s \"torret  ray_GUI\" python3 " + WORKING_DIR_PATH + "GUI/main_fe.py' &")
os.system("lxterminal -e 'tmux new-session -d -s \"torretray\" \"python3 " + WORKING_DIR_PATH + "back_end/main_be.py\"; tmux split-window \"python3 " + WORKING_DIR_PATH + "GUI/main_fe.py\"' ")

