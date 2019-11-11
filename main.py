import os
from parameters import *

os.system("konsole -e 'python3 " + WORKING_DIR_PATH + "back_end/main_be.py' &")
os.system("konsole -e 'python3 " + WORKING_DIR_PATH + "GUI/main_fe.py' &")