import requests
from escpos.printer import Usb
from jsonschema.compat import urlopen
from GUI.logger import *
from database import *
import time


def create_not_signed_queue():
    logger = get_logger('create_not_signed_queue()')
    try:
        db.connect()
        queue = db.get_all(1, 0)
        db.close_connection()
        return queue
    except:
        logger.error('impossibile connettersi al database')
        return 0


def create_signed_queue():
    logger = get_logger('create_signed_queue()')
    try:
        db.connect()
        queue = db.get_all(1, 1)
        db.close_connection()
        return queue
    except:
        logger.error('impossibile connettersi al database')
        return 0


def sign_tray(name):
    logger = get_logger('sign_tray()')
    try:
        db.connect()
        db.set_done(name, 1)
        db.close_connection()
    except:
        logger.error('impossibile connettersi al database')
        return 0


def delete_tray_from_view(name):
    logger = get_logger('delete_tray_from_view()')
    try:
        db.connect()
        db.set_valid(name, 1)
        db.close_connection()
    except:
        logger.error('impossibile connettersi al database')
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
                tray_status = db.get_tray(i['nome'])[0]

                if tray_status == 0 and i['stato'] == 'Vassoio':
                    db.set_tray(i['nome'], 1)
                elif tray_status == 1 and i['stato'] != 'Vassoio':
                    db.set_tray(i['nome'], 0)
            else:
                db.set_tray(i['nome'], 0)
                db.set_done(i['nome'], 0)

        db.set_last_update(datetime.datetime.now().strftime('%d/%m/%y %H:%M'))
        db.close_connection()

        return 1
    except:
        logger.error('impossibile connettersi al database')
        return 0


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
        for i in data["nomi"]["Cena"]:
            i["nome"] = i["nome"].replace("&agrave;", "à")
            i["nome"] = i["nome"].replace("o&#039;", "ò")
            i["nome"] = i["nome"].replace("&atilde;", "a")
        return data
    except:
        logger.error('impossibile fare il get del json')
        return 0


def start_print_process(print_queque):
    logger = get_logger('start_print_process()')
    try:
        p = Usb(VENDOR_ID, PRODUCT_ID, INTERFACE)
        p.charcode("USA")
        if print_queque:
            for i in range(0, len(print_queque)):
                p.set(height=2, width=2, align='center')
                p.image(IMG_DIR_PATH + 'logo-torre-mono-medium.png')
                time.sleep(0.1)
                p.text('Vassoi Torrescalla\n\n\n')
                p.set(height=1, width=1, align='left')
                time.sleep(0.1)
                p.text('    Data: ' +
                       datetime.datetime.now().strftime('%d/%m/%y') + '\n')
                p.text(
                    '    Ora: ' + datetime.datetime.now().time().strftime('%H:%M') + '\n\n\n')
                p.set(height=2, width=2, align='center')
                time.sleep(0.1)
                p.text(print_queque[0][0] + '\n')
                if print_queque[0][1] is not None:
                    p.set(height=1, width=1, align='center')
                    time.sleep(0.1)
                    p.text(print_queque[0][1] + '\n')
                p.text('\n\n\n')
                p.cut()
                print_queque.pop(0)
                time.sleep(0.3)
    except:
        logger.error('impossibile connettersi alla stampante')
        return 0
