import os
import sys
from parameters import *
sys.path.append(WORKING_DIR_PATH)

#os.system("lxterminal -e 'tmux new-session -s \"torretray_backend\" python3 " + WORKING_DIR_PATH + "back_end/main_be.py' &")
#os.system("lxterminal -e 'tmux new-session -s \"torret  ray_GUI\" python3 " + WORKING_DIR_PATH + "GUI/main_fe.py' &")
# os.system("lxterminal -e 'tmux new-session -d -s \"torretray\" \"python3 " + WORKING_DIR_PATH + "back_end/main_be.py\"; tmux split-window \"python3 " + WORKING_DIR_PATH + "GUI/main_fe.py\"' ")


import subprocess
# subprocess.call(['python', WORKING_DIR_PATH + '/GUI/main_fe.py', WORKING_DIR_PATH]) # Just run the program
# subprocess.check_output(['python', './GUI/main_fe.py']) # Just run the program

if os.path.exists('pyenv/'):
	myProc = subprocess.Popen(['pyenv/Scripts/python', WORKING_DIR_PATH + '/GUI/main_fe.py', WORKING_DIR_PATH], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	[outStream, errStream] = myProc.communicate()
else:
	myProc = subprocess.Popen(['python', WORKING_DIR_PATH + '/GUI/main_fe.py', WORKING_DIR_PATH], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	[outStream, errStream] = myProc.communicate()

