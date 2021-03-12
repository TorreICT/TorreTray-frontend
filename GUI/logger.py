from loggerpy import *
from parameters import *
import os

path = os.path.join(WORKING_DIR_PATH, 'GUI', 'logs')

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

configure(print_level=Level.DEBUG,
          save_level=Level.DEBUG,
          path=WORKING_DIR_PATH + "/GUI/",
          info=True)
