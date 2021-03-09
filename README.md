# torre_tray_official
Gestione e stampa dei ticket vassoi

## Preparation & Install

1. Installare i requirements: `pip3 install -r requirements.txt` [TODO: completare `requirements.txt`]
2. Installare [PyQt5][https://pythonbasics.org/install-pyqt/]

~3. Creare il file `local.py` nella root folder del progetto. Specificare la variabile `LOCALE_WORKING_DIR_PATH = "/path/to/torre_tray_official/` come ad es.:~

~LOCALE_WORKING_DIR_PATH = "/home/projects/torre_tray_official/"~

## TODO
- [ ] Ripulire il codice
  - [ ] Ottimizzare imports: ossia fare in modo che ogni `from package import module` si riferisca al percorso corretto del package e importi solo le funzioni necessarie così rendiamo più facile in futuro il lavoro di debug
  - [ ] Definire le librerie effettivamente utilizzate
  - [ ] Scrivere documentazione partendo da come è strutturato il progetto. Struttura BE+FE e organizzazione database.
- [ ] Aggiungere modifica dei parametri da GUI
- [ ] Modalità turno singolo
