from escpos.printer import Usb
from jsonschema.compat import urlopen
from .logger import *
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
                p.text('    Data: ' + datetime.datetime.now().strftime('%d/%m/%y') + '\n')
                p.text('    Ora: ' + datetime.datetime.now().time().strftime('%H:%M') + '\n\n\n')
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