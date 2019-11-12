from .functions import *
from parameters import *
import schedule
import time

sched_times = create_scheduler_time()

schedule.every().day.at(LUNCH_END_TIME).do(reset_session)
schedule.every().day.at("00:01").do(reset_session)
schedule.every().day.at("00:02").do(reboot_sys)

schedule.every().day.at("13:15").do(run_play_sound)
schedule.every().day.at(LAST_LUNCH_UPDATE_TIME).do(run_play_sound)
schedule.every().day.at("20:15").do(run_play_sound)
schedule.every().day.at(LAST_DINNER_UPDATE_TIME).do(run_play_sound)

schedule.every().monday.at(DB_RESET_TIME).do(reset_db)

for i in sched_times:
    schedule.every().day.at(i).do(db_update)

while True:
    schedule.run_pending()
    time.sleep(1)
