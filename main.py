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


if os.path.exists('pyenv'):
    p1 = subprocess.Popen(['pyenv/Scripts/python', WORKING_DIR_PATH + '/GUI/main_fe.py',
                        WORKING_DIR_PATH])
    p2 = subprocess.Popen(['pyenv/Scripts/python', WORKING_DIR_PATH + '/back_end/main_be.py',
                        WORKING_DIR_PATH])
else:
    p1 = subprocess.Popen(['python3', WORKING_DIR_PATH + '/GUI/main_fe.py',
                        WORKING_DIR_PATH])
    p2 = subprocess.Popen(['python3', WORKING_DIR_PATH + '/back_end/main_be.py',
                        WORKING_DIR_PATH])
while True:
    for dir in ['GUI', 'back_end']:
        path = os.path.join(WORKING_DIR_PATH, dir, 'logs')

        def check_if_older(file):
            from datetime import date
            str = file.split('.')
            filedate = date.fromisoformat(str[0])
            days_between = date.today() - filedate
            if int(days_between.days) > 7:
                return True

        # Delete files older than X days
        for f in os.listdir(path):
            if check_if_older(f):
                f = os.path.join(path, f)
                os.remove(f)
    pass
