import os
import sys
import signal
from parameters import *
import subprocess

sys.path.append(WORKING_DIR_PATH)


def keyboardInterruptHandler(signal, frame):
    print("KeyboardInterrupt (ID: {}) preso. Killo i sottoprocessi...".format(signal))
    p1.kill()
    p2.kill()
    # exit(0)
    try:
        print('[+] Fatto...')
        sys.exit(0)
    except SystemExit:
        print('[+] Bye')
        os._exit(0)


signal.signal(signal.SIGINT, keyboardInterruptHandler)
signal.signal(signal.SIGTERM, keyboardInterruptHandler)

p1 = subprocess.Popen(['python3', WORKING_DIR_PATH + '/GUI/main_fe.py',
                       WORKING_DIR_PATH])
p2 = subprocess.Popen(['python3', WORKING_DIR_PATH + '/back_end/main_be.py',
                       WORKING_DIR_PATH])
while True:
    pass
