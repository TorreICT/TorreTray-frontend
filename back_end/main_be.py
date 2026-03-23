# Decommentare se si vuole runnare singolarmente
import sys
if len(sys.argv) > 1:
    sys.path.append(sys.argv[1])

from back_end.functions import *
from parameters import *
import schedule
import time
import datetime


sched_times = create_scheduler_time()

schedule.every().day.at(LUNCH_END_TIME).do(reset_session)
schedule.every().day.at("00:01").do(reset_session)
schedule.every().day.at("00:02").do(reboot_sys)

# Ogni 5 minuti controlla se ci sono nuovi vassoi e fa suonare la campanella
now = datetime.datetime.now().time()
current_time = now.time()
if datetime.time(12,45) <= current_time <= datetime.time(13,40) or datetime.time(19,30) <= current_time <= datetime.time(20,25):
    schedule.every(5).minutes.do(run_play_sound)

schedule.every().monday.at(DB_RESET_TIME).do(reset_db)

for i in sched_times:
    schedule.every().day.at(i).do(db_update)

while True:
    schedule.run_pending()
    time.sleep(1)
