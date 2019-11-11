from database_functions import *
from parameters import *
import datetime

db = Database(DB_FILE_PATH)

db.create_database(TRAY_DB_CREATE_QUERY)
db.connect()
db.clear_clock()
db.create_database(CLOCK_DB_CREATE_QUERY)
db.create_clock(datetime.datetime.now().strftime('%d/%m/%y %H:%M'))
db.close_connection()
