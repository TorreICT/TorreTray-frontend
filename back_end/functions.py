import requests
import datetime
from urllib.request import urlopen
from back_end.logger import *
from database import *
import simpleaudio as sa
import threading
import os
import time


def reboot_sys():
    logger = get_logger('reboot_sys()')
    logger.info('reboot tra 5 secondi')
    time.sleep(5)
    os.system("sudo reboot")


def play_sound():
    wave_obj = sa.WaveObject.from_wave_file(
        WORKING_DIR_PATH + '/res/glass_ping.wav')
    play_obj = wave_obj.play()
    play_obj.wait_done()

# Emette un suono se ci sono vassoi non stampati in coda
def run_play_sound():
    logger = get_logger('run_play_sound()')

    # Se la coda dei vassoi non stampati NON è vuota
    if len(create_not_signed_queue()) != 0:
        try:
            logger.info("Campanella")

            # Emetti suono
            threading.Thread(target=play_sound).start()
        except:
            logger.error('impossibile spawnare il thread del suono')


def create_scheduler_time():
    sched_times = []

    lunch_start_time = datetime.datetime.strptime(LUNCH_START_TIME, '%H:%M')
    dinner_start_time = datetime.datetime.strptime(DINNER_START_TIME, '%H:%M')

    max_lunch_sched = datetime.datetime.strptime(
        LAST_LUNCH_UPDATE_TIME, '%H:%M')
    max_dinner_sched = datetime.datetime.strptime(
        LAST_DINNER_UPDATE_TIME, '%H:%M')

    update_interval = datetime.datetime.strptime(
        UPDATE_INTERVAL_MINUTES, '%M').minute

    i = lunch_start_time + datetime.timedelta(
        minutes=update_interval)
    while i < max_lunch_sched:
        sched_times.append(i.strftime("%H:%M"))
        i = i + datetime.timedelta(
            minutes=update_interval)
    sched_times.append(max_lunch_sched.strftime("%H:%M"))
    i = dinner_start_time + datetime.timedelta(
        minutes=update_interval)
    while i < max_dinner_sched:
        sched_times.append(i.strftime("%H:%M"))
        i = i + datetime.timedelta(
            minutes=update_interval)
    sched_times.append(max_dinner_sched.strftime("%H:%M"))

    return sched_times


def get_registro_pasti():
    logger = get_logger('get_registro_pasti()')
    try:
        params = [(URL_PARAM, datetime.datetime.now().date())]
        response = requests.get(URL, params=params)
        data = response.json()
        # Correzione dei nomi in Mycollege su database
        for i in data["nomi"]["Pranzo"]:
            i["nome"] = i["nome"].replace("&agrave;", "à")
            i["nome"] = i["nome"].replace("o&#039;", "ò")
            i["nome"] = i["nome"].replace("&atilde;", "a")
            i["nome"] = i["nome"].replace("ã", "a")
            i["nome"] = i["nome"].replace("ñ", "n")
            i["nome"] = i["nome"].replace("&ntilde", "n")
            i["nome"] = i["nome"].replace("&ograve;", "ò")
	for i in data["nomi"]["Cena"]:
            i["nome"] = i["nome"].replace("&agrave;", "à")
            i["nome"] = i["nome"].replace("o&#039;", "ò")
            i["nome"] = i["nome"].replace("&atilde;", "a")
            i["nome"] = i["nome"].replace("ã", "a")
            i["nome"] = i["nome"].replace("ñ", "n")
            i["nome"] = i["nome"].replace("&ntilde", "n")
            i["nome"] = i["nome"].replace("&ograve;", "ò")
	return data
    except:
        logger.error('impossibile fare il get del json')
        return 0


def set_db():
    json_data = get_registro_pasti()
    logger = get_logger('set_db()')
    if json_data != 0:
        json_data = json_data['nomi']['Pranzo']
        try:
            db.connect()
            for i in json_data:
                db.set_name(i['nome'])
                if i['dieta'] != "":
                    db.set_dieta(i['nome'], i['dieta'])
            db.close_connection()
            logger.info('database compilato')
            return 1
        except Exception as e:
            logger.error('impossibile connettersi al database: set_db')
            logger.error(e)
            return 0


def db_update():
    logger = get_logger('db_update()')
    try:
        db.connect()
        time = datetime.datetime.now().time()
        if datetime.datetime.strptime("00:01", '%H:%M').time() <= time < datetime.datetime.strptime(LUNCH_END_TIME, '%H:%M').time():
            json_data = get_registro_pasti()
            if json_data != 0:
                json_data = json_data['nomi']['Pranzo']
                logger.info('aggiornamento dati pranzo')
            else:
                logger.warning('impossibile aggiornare')
                return 0
        else:
            json_data = get_registro_pasti()
            if json_data != 0:
                json_data = json_data['nomi']['Cena']
                logger.info('aggiornamento dati cena')
            else:
                logger.warning('impossibile aggiornare')
                return 0
        for i in json_data:

            valid_status = db.get_valid(i['nome'])

            if valid_status is None:
                db.set_name(i['nome'])
                if i['dieta'] != "":
                    db.set_dieta(i['nome'], i['dieta'])
                valid_status = 0
                logger.info(
                    'aggiunto utente non presente nel database: ' + i['nome'])
            else:
                valid_status = valid_status[0]

            if valid_status == 0:
                tray_status = db.get_tray(i['nome'])[0]  # Get tray status for user
                packed_lunch_status = db.get_packed(i['nome'])[0]  # Get packed lunch status for user

                # If the user has a tray
                if tray_status == 0 and i['stato'] == 'vassoio':
                    db.set_tray(i['nome'], 1)  # Set tray status to 1 in the database
                elif tray_status == 1 and i['stato'] != 'vassoio':
                    db.set_tray(i['nome'], 0)  # Set tray status to 0 in the database

                # If the user has a packed lunch
                if packed_lunch_status == 0 and i['stato'] == 'sacco':
                    db.set_packed(i['nome'], 1)  # Set packed lunch status to 1 in the database
                elif tray_status == 1 and i['stato'] != 'sacco':
                    db.set_packed(i['nome'], 0)  # Set packed lunch status to 0 in the database

            # Valid status = 1 <=> tray or packed lunch already printed
            else:
                db.set_packed(i['nome'], 0)  # Set tray status to 0 in the database
                db.set_tray(i['nome'], 0)  # Set tray status to 0 in the database
                db.set_done(i['nome'], 0)  # Set done status to 0 in the database

        db.set_last_update(datetime.datetime.now().strftime('%d/%m/%y %H:%M'))
        db.close_connection()

        return 1
    except:
        logger.error('impossibile connettersi al database: db_update BE')
        return 0


def reset_db():
    # Initialize logger for this function
    logger = get_logger('reset_db()')
    
    try:
        db.connect()
        # Clear the database
        db.clear_db()
        # Create a new database using a specific query
        db.create_database(TRAY_DB_CREATE_QUERY)
        # Close the connection after operations are complete
        db.close_connection()
        # Set the database
        set_result = set_db()
        # Check if setting the database was successful
        if set_result != 0:
            # If successful, try to update the database
            update_result = db_update()
            
            # Check if the update was successful
            if update_result == 0:
                # Log a warning if update fails and return 0
                logger.warning('Unable to update database')
                return 0
        else:
            # Log a warning if setting the database fails and return 0
            logger.warning('Unable to set database')
            return 0
        # Log an info message indicating successful database reset
        logger.info('Database reset successful')
        return 1
    
    except Exception as e:
        # Log an error if unable to connect to the database
        logger.error('Unable to connect to database: reset BE')
        # Log the specific error that occurred
        logger.error(e)
        # Return 0 to indicate an error occurred
        return 0


def reset_session():
    # Initialize logger for this function
    logger = get_logger('reset_session()')
    try:
        db.connect()
        # Get a list of all names from the database
        names = db.get_all_name()
        
        for i in names:
            # Get the 'done' status for the current name
            done_status = db.get_done(i[0])

            # Check if 'done' status is not None
            if done_status is not None:
                # Reset various attributes for the current name
                db.set_tray(i[0], 0)
                db.set_done(i[0], 0)
                db.set_valid(i[0], 0)
                db.set_packed(i[0], 0)

        db.close_connection()
        # Log an info message indicating successful session reset
        logger.info('Session reset successful')
        return 1

    except Exception as e:
        logger.error('Unable to connect to database: reset_session BE')
        logger.error(e)

        return 0


def create_not_signed_queue():
    logger = get_logger('create_not_signed_queue()')
    try:
        db.connect()
        # Una coda contenenete tutti i vassoi/schiscette chiesti sull'app ma NON stampati (tray/packed=1, done=0, valid=0)
        # La coda viene ottenuta tramite la funzione db.get_all()
        queue  = []

        # Ottieni l'ora corrente
        current_time = datetime.datetime.now().time()
        # Determina se l'ora corrente è tra le START_SACCHETTO:00 e le END_SACCHETTO:00
        if datetime.time(START_SACCHETTO, 0) <= current_time <= datetime.time(END_SACCHETTO, 0):
            queue = db.get_all(1, 0)
        else:
            queue = db.get_all(0, 0)
        db.close_connection()
        return queue
    except Exception as e:
        logger.error('impossibile connettersi al database: create_not_signed_queue BE')
        logger.error(e)
        return 0


def create_signed_queue():
    logger = get_logger('create_signed_queue()')
    try:
        db.connect()
        # Una coda contenenete tutti i vassoi/schiscette chiesti sull'app e stampati (tray/packed=1, done=1, valid=0)
        # La coda viene ottenuta tramite la funzione db.get_all()
        queue  = []

        # Ottieni l'ora corrente
        current_time = datetime.datetime.now().time()
        # Determina se l'ora corrente è tra le START_SACCHETTO:00 e le END_SACCHETTO:00
        if datetime.time(START_SACCHETTO, 0) <= current_time <= datetime.time(END_SACCHETTO, 0):
            queue = db.get_all(1, 1)
        else:
            queue = db.get_all(0, 1)
        db.close_connection()
        return queue
    except:
        logger.error('impossibile connettersi al database: create_signed_queue BE')
        return 0


def sign_tray(name):
    logger = get_logger('sign_tray()')
    try:
        db.connect()
        db.set_done(name, 1)
        db.close_connection()
    except:
        logger.error('impossibile connettersi al database: sign_tray BE')
        return 0


def delete_tray_from_view(name):
    logger = get_logger('delete_tray_from_view()')
    try:
        db.connect()
        db.set_valid(name, 1)
        db.close_connection()
    except:
        logger.error('impossibile connettersi al database: delete_tray_from_view BE')
        return 0


def verify_internet():
    logger = get_logger('verify_internet()')
    try:
        with urlopen('https://www.google.it'):
            return True
    except BaseException as ex:
        logger.warning('connessione internet assente: ' + str(ex))
        return False


def verify_db():
    logger = get_logger('verify_db()')
    try:
        db.connect().execute("SELECT 1 FROM tray_status LIMIT 1;")
        db.close_connection()
        return True
    except sqlite3.ProgrammingError as e:
        logger.critical('impossibile connettersi al database ' + str(e))
        return False
