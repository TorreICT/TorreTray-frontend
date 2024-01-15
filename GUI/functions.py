import requests
from escpos.printer import Usb
from jsonschema.compat import urlopen
from GUI.logger import *
from database import *
import time
import datetime

# Function to retrieve the unsigned queue from the database
def create_not_signed_queue():
    # Get logger for this function
    logger = get_logger('create_not_signed_queue()')
    try:
        db.connect()  # Connect to the database
        queue = []

        current_time = datetime.datetime.now().time()  # Get current time

        # Determina se l'ora corrente è tra le START_SACCHETTO:00 e le END_SACCHETTO:00
        if datetime.time(START_SACCHETTO, 0) <= current_time <= datetime.time(END_SACCHETTO, 0):
            queue = db.get_all(1, 0)  # Get unsigned queue from database
        else:
            queue = db.get_all(0, 0)  # Get unsigned queue from database
            
        db.close_connection()  # Close database connection
        return queue  # Return the unsigned queue
    except Exception as e:
        logger.error('impossibile connettersi al database: create_not_signed_queue')  # Log error if database connection fails
        logger.error(e)
        return 0

# Function to retrieve the signed queue from the database
def create_signed_queue():
    # Get logger for this function
    logger = get_logger('create_signed_queue()')
    try:
        db.connect()  # Connect to the database
        # Una coda contenenete tutti i vassoi/schiscette chiesti sull'app e stampati (tray/packed=1, done=1, valid=0)
        # La coda viene ottenuta tramite la funzione db.get_all()
        queue  = []

        # Ottieni l'ora corrente
        current_time = datetime.datetime.now().time()
        
        # Determina se l'ora corrente è tra le START_SACCHETTO:00 e le END_SACCHETTO:00
        if datetime.time(START_SACCHETTO, 0) <= current_time <= datetime.time(END_SACCHETTO, 0):
            queue = db.get_all(1, 1)  # Get signed packed queue from database
        else:
            queue = db.get_all(0, 1)  # Get signed trays queue from database
        
        db.close_connection()  # Close database connection
        return queue  # Return the signed queue
    except Exception as e:
        logger.error('impossibile connettersi al database: create_signed_queue')  # Log error if database connection fails
        logger.error(e)
        return 0  # Return 0 in case of error

# Function to mark a tray as signed
def sign_tray(name):
    # Get logger for this function
    logger = get_logger('sign_tray()')
    try:
        db.connect()  # Connect to the database
        db.set_done(name, 1)  # Mark the tray as signed in the database
        db.close_connection()  # Close database connection
    except Exception as e:
        logger.error('impossibile connettersi al database: sign_tray')  # Log error if database connection fails
        logger.error(e)
        return 0  # Return 0 in case of error

# Function to delete a tray from view
def delete_tray_from_view(name):
    # Get logger for this function
    logger = get_logger('delete_tray_from_view()')
    try:
        db.connect()  # Connect to the database
        db.set_valid(name, 1)  # Mark the tray as valid in the database
        db.close_connection()  # Close database connection
    except Exception as e:
        logger.error('impossibile connettersi al database: delete_tray_from_view')  # Log error if database connection fails
        logger.error(e)
        return 0  # Return 0 in case of error

def verify_internet():
    logger = get_logger('verify_internet()')

    try:
        with urlopen('https://www.google.it') as response:
            # The with statement ensures the connection is properly closed after usage
            return response.status == 200  # Return True if HTTP status is 200 (OK)
    except Exception as ex:
        logger.warning(f'Internet connection unavailable: {ex}')  # Log warning if internet connection fails
        return False  # Return False in case of error


def verify_db():
    logger = get_logger('verify_db()')

    try:
        # Attempt to connect to the database and execute a simple query
        db.connect().execute("SELECT 1 FROM tray_status LIMIT 1;")
        # Close the database connection
        db.close_connection()
        return True  # Return True if successful
    except sqlite3.ProgrammingError as e:
        logger.critical(f'Error connecting to the database: {e}')  # Log critical error if database connection fails
        return False  # Return False in case of error


# Function to update the database
def db_update():
    # Get logger for this function
    logger = get_logger('db_update()')
    try:
        db.connect()  # Connect to the database
        time = datetime.datetime.now().time()  # Get current time
        # Check if it's lunch time or dinner time
        if datetime.datetime.strptime("00:01", '%H:%M').time() <= time < datetime.datetime.strptime(LUNCH_END_TIME, '%H:%M').time():
            json_data = get_registro_pasti()  # Get meal data
            if json_data != 0:
                json_data = json_data['nomi']['Pranzo']  # Extract lunch data
                logger.info('aggiornamento dati pranzo')  # Log info message
            else:
                logger.warning('impossibile aggiornare')  # Log warning if data retrieval fails
                return 0  # Return 0 in case of error
        else:
            json_data = get_registro_pasti()  # Get meal data
            if json_data != 0:
                json_data = json_data['nomi']['Cena']  # Extract dinner data
                logger.info('aggiornamento dati cena')  # Log info message
            else:
                logger.warning('impossibile aggiornare')  # Log warning if data retrieval fails
                return 0  # Return 0 in case of error
        for i in json_data:
            valid_status = db.get_valid(i['nome'])  # Get validity status of user

            if valid_status is None:
                db.set_name(i['nome'])  # Set user name in the database
                if i['dieta'] != "":
                    db.set_dieta(i['nome'], i['dieta'])  # Set user diet in the database
                valid_status = 0  # Set validity status to 0
                logger.info('aggiunto utente non presente nel database: ' + i['nome'])  # Log info message
            else:
                valid_status = valid_status[0]

            # Valid status = 0 <=> tray or packed lunch not printed yet
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

        db.set_last_update(datetime.datetime.now().strftime('%d/%m/%y %H:%M'))  # Set last update time in the database
        db.close_connection()  # Close database connection

        return 1  # Return 1 if successful
    except Exception as e:
        logger.error('impossibile connettersi al database: db_update')  # Log error if database connection fails
        logger.error(e)
        return 0  # Return 0 in case of error

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

    except requests.exceptions.RequestException as e:
        logger.error(f'Error making GET request: {e}')
        return 0

    except ValueError as e:
        logger.error(f'Error parsing JSON response: {e}')
        return 0

def start_print_process(print_queue):
    # Ottieni un logger specifico per questa funzione
    logger = get_logger('start_print_process()')

    try:
        # Inizializza la connessione alla stampante USB
        p = Usb(VENDOR_ID, PRODUCT_ID, INTERFACE)
        p.charcode("USA")
        
        # Ottieni l'ora corrente
        current_time = datetime.datetime.now().time()
        
        # Determina se l'ora corrente è tra le START_SACCHETTO:00 e le END_SACCHETTO:00
        if datetime.time(START_SACCHETTO, 0) <= current_time <= datetime.time(END_SACCHETTO, 0):
            title = "Schiscette Torrescalla"
        else:
            title = "Vassoi Torrescalla"

        # Verifica se c'è qualcosa nella coda di stampa
        if print_queue:
            # Ciclo sulla coda di stampa
            for i in range(0, len(print_queue)):
                # Configura i parametri della stampa
                p.set(height=2, width=2, align='center')
                p.image(IMG_DIR_PATH + '/logo-torre-mono-medium.png')
                time.sleep(0.1)
                
                # Stampa il nome della query
                p.text(title + '\n\n\n')
                
                # Configura ulteriori parametri della stampa
                p.set(height=1, width=1, align='left')
                time.sleep(0.1)
                p.text('    Data: ' +
                       datetime.datetime.now().strftime('%d/%m/%y') + '\n')
                p.text(
                    '    Ora: ' + datetime.datetime.now().time().strftime('%H:%M') + '\n\n\n')
                p.set(height=2, width=2, align='center')
                time.sleep(0.1)
                
                # Stampa il nome e, se disponibile, l'altro valore
                p.text(print_queue[0][0] + '\n')
                if print_queue[0][1] is not None:
                    p.set(height=1, width=1, align='center')
                    time.sleep(0.1)
                    p.text(print_queue[0][1] + '\n')
                p.text('\n\n\n')

                # Logga il vassoio stampato
                logger.info(f'{print_queue[0][0]}: vassoio stampato')

                # Esegue il taglio della carta
                p.cut()
                
                # Rimuove il vassoio dalla coda di stampa
                print_queue.pop(0)
                
                # Attende prima di passare al prossimo vassoio
                time.sleep(0.3)
    except Exception as e:
        # Gestisce le eccezioni nel caso di errori
        logger.error('Impossibile connettersi alla stampante')
        logger.error(e)
        return 0