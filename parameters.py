from local import *
# ############ PATHS ##############
WORKING_DIR_PATH = LOCALE_WORKING_DIR_PATH
IMG_DIR_PATH = WORKING_DIR_PATH + 'res/img/'
DB_FILE_PATH = WORKING_DIR_PATH + 'database_tray.db'

# ############ DATABASE ##############
TRAY_DB_CREATE_QUERY = """CREATE TABLE IF NOT EXISTS "tray_status" (
             "name" varchar(50) PRIMARY KEY NOT NULL,
             "diet" varchar(50),
             "tray" INTEGER DEFAULT 0,
             "done" INTEGER DEFAULT 0,
             "valid" INTEGER DEFAULT 0
           );"""

CLOCK_DB_CREATE_QUERY = """CREATE TABLE IF NOT EXISTS "clock" (
             "last_update" varchar(50)
           );"""

# ############ PARAMETERS ##############
URL = 'https://mycollegeapp.rui.it/jsonapi?residenza=dG9ycmVzY2FsbGE-'
URL_PARAM = 'data'

LUNCH_START_TIME = "12:45"
# Per calcolare l'orario seguente sottrarre all'orario di fine pranzo (non LUNCH_END_TIME)  il DELTA_VASSOI (settato su mycollege) + 1 minuto
LAST_LUNCH_UPDATE_TIME = "13:50"
LUNCH_END_TIME = "14:30"

DINNER_START_TIME = "19:30"
# Per calcolare l'orario seguente sottrarre all'orario di fine cena (non DINNER_END_TIME) il DELTA_VASSOI (settato su mycollege) + 1 minuto
LAST_DINNER_UPDATE_TIME = "20:35"
DINNER_END_TIME = "21:30"

DELTA_VASSOI = "00:40"
UPDATE_INTERVAL_MINUTES = "2"

DB_RESET_TIME = "02:00"

# ###### GUI RELATED PARAMETERS ########
FONT = "DejaVu Sans"
FONT_SIZE = 12
STATUS_BAR_TIMEOUT = 5000
NO_INTERNET_TIMEOUT = 30000
UPDATE_GUI_TABLES_INTERVAL = 5000

# ############# PRINTER ################
VENDOR_ID = 0x1fc9
PRODUCT_ID = 0x2016
INTERFACE = 0
