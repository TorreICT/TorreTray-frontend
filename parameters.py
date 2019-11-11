# ############ PATHS ##############
WORKING_DIR_PATH = '/home/peppetort/Scrivania/Programmazione/Projects/torretray_release/'
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

# TODO: mettere nel codice
SELECT_SIGNED_TRAYS_QUERY = """SELECT * FROM tray_status WHERE
                            "tray"=1 AND
                            "done"=1 AND
                            "valid"=0;"""

SELECT_NOT_SIGNED_TRAYS_QUERY = """SELECT * FROM tray_status WHERE
                                "tray"=1 AND
                                "done"=0 AND
                                "valid"=0;"""

SELECT_CLOCK_QUERY = """SELECT * FROM clock;"""

# ############ PARAMETERS ##############
URL = 'https://mycollegeapp.rui.it/jsonapi?residenza=dG9ycmVzY2FsbGE-'
URL_PARAM = 'data'

LUNCH_START_TIME = "12:45"
LAST_LUNCH_UPDATE_TIME = "13:31"
LUNCH_END_TIME = "13:45"
DINNER_START_TIME = "20:00"
LAST_DINNER_UPDATE_TIME = "20:21"
DINNER_END_TIME = "21:00"


MINUTES_FROM_THE_END_DINNER = "39"
MINUTES_FROM_THE_END_LUNCH = "14"

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
