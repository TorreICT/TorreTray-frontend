# torre_tray_official
Gestione e stampa dei ticket vassoi

## Preparation & Install

1. Installare i requirements: `pip3 install -r requirements.txt` [TODO: completare `requirements.txt`]
2. Installare [PyQt5][https://pythonbasics.org/install-pyqt/]
- [OPZIONALE] Creare un virtual environment es. `python3 -m venv pyenv`

~3. Creare il file `local.py` nella root folder del progetto. Specificare la variabile `LOCALE_WORKING_DIR_PATH = "/path/to/torre_tray_official/` come ad es.:~

~LOCALE_WORKING_DIR_PATH = "/home/projects/torre_tray_official/"~

3. Avviare da terminale `python3 main.py`


## TODO
- [ ] Ripulire il codice
  - [x] Ottimizzare imports: ossia fare in modo che ogni `from package import module` si riferisca al percorso corretto 
    del package e importi solo le funzioni necessarie così rendiamo più facile in futuro il lavoro di debug
  - [x] Definire le librerie effettivamente utilizzate
  - [ ] Scrivere documentazione partendo da come è strutturato il progetto. Struttura BE+FE e organizzazione database.
- [x] Avviare Front End e Back End come processi distinti dal main ed in parallelo
- [ ] Risolvere problemi con loggerpy
  - [x] File di log creati incorrettamente
  - [ ] Ripulire i log più vecchi di una settimana
- [ ] Aggiungere modifica dei parametri da GUI
- [ ] Modalità turno singolo
