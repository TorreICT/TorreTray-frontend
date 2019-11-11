# STATUS BAR #

STATBAR_INIT_MES = "ultimo aggiornamento: N/D"
STATBAR_NO_INTERNET_MES = u'\u26a0 errore connessione a internet'
STATBAR_DB_CONN_ERROR_MES = u'\u26a0 errore connessione a database'
STATBAR_TRAY_PRINT_REQUEST_MES = u"\u231b stampa vassoio in coda per {}"
STATBAR_PRINT_SUCCESS_MES = u"\u2714 stampa avvenuta correttamente"
STATBAR_PRINT_ERROR_MES = u"\u26a0 errore di stampa"
STATBAR_TRAY_CANCEL_MES = u"\u2714 cancellazione vassoio per {}"
STATBAR_TRAY_CANCEL_ABORT_MES = u"\u2718 cancellazione annullata"
STATBAR_PRINT_REQUEST_MES = u"\u231b richiesta di stampa"
STATBAR_PRINT_ABORTED_MES = u"\u2718 stampa cancellata"
STATBAR_UPDATE_MES = u"\u2714 aggiornato"
STATBAR_LAST_UPDATE_TEMPLATE = "ultimo aggiornamento: "

# QUERIES ##
SELECT_SIGNED_TRAYS_QUERY = """SELECT * FROM tray_status WHERE
                            "tray"=1 AND
                            "done"=1 AND
                            "valid"=0;"""

SELECT_NOT_SIGNED_TRAYS_QUERY = """SELECT * FROM tray_status WHERE
                                "tray"=1 AND
                                "done"=0 AND
                                "valid"=0;"""

SELECT_CLOCK_QUERY = """SELECT * FROM clock;"""

# TODO: aggiunger labels dei logs
# LOGS #