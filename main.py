import os
import sys
sys.path.append("/home/pietro/Documenti/Python/torre_tray_official")
from parameters import *

os.system("lxterminal -e 'tmux new-session -s \"torretray_backend\" python3 " + WORKING_DIR_PATH + "back_end/main_be.py' &")
os.system("lxterminal -e 'tmux new-session -s \"torret  ray_GUI\" python3 " + WORKING_DIR_PATH + "GUI/main_fe.py' &")
# cmd1 = "lxterminal -e 'tmux new-session -s \"torretray\" \"python3 " + WORKING_DIR_PATH + "back_end/main_be.py\"; " + \
#                           "tmux split-window \"python3 " + WORKING_DIR_PATH + "GUI/main_fe.py\" '"ain_be.py\"; " + \
# cmd1 = "lxterminal -e 'tmux new-session -s \"torretray\" \"python3 /home/pietro/Documenti/Python/torre_tray_official/back_end/main_be.py\" ; tmux split-window \"python3 /home/pietro/Documenti/Python/torre_tray_official/GUI/main_fe.py\"' "
# print(cmd1)
# os.system(cmd1)
# os.system("lxterminal -e 'tmux new-session -s \"torretray\" \"python3 " + WORKING_DIR_PATH + "back_end/main_be.py\"; " + \
#                           "tmux split-window \"python3 " + WORKING_DIR_PATH + "GUI/main_be.py\" '")