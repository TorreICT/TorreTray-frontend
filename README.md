# TorreTray Pi App

Interfaccia PyQt5 per Raspberry Pi 3 dedicata alla stampa dei ticket TorreTray.

Questa versione mantiene il layout generale dell'app storica, ma rimuove il vecchio
database SQLite locale e il backend embedded: l'interfaccia legge direttamente dal
nuovo backend `TorreTray-backend` e aggiorna lo stato di stampa tramite API.

## Cosa fa

- mostra le prenotazioni di oggi divise in `Da stampare` e `Già stampati`
- permette di filtrare per `Pranzo` / `Cena`
- permette di filtrare per `Vassoi` / `Schiscette`
- stampa ticket singoli o in blocco
- marca come stampati i ticket confermati dal backend

## Struttura

- `main.py`: entrypoint minimale
- `src/torretray_pi/config.py`: configurazione da environment / `.env`
- `src/torretray_pi/backend_client.py`: chiamate HTTP al backend
- `src/torretray_pi/printing.py`: integrazione con la stampante USB
- `src/torretray_pi/services.py`: orchestrazione refresh e stampa
- `src/torretray_pi/ui/`: componenti PyQt5
- `res/img/`: asset grafici originali

## Configurazione

Crea un file `.env` nella root del progetto partendo da `.env.example`.

Variabili principali:

- `TORRETRAY_API_BASE_URL=http://127.0.0.1:8000`
- `TORRETRAY_REQUEST_TIMEOUT_SECONDS=10`
- `TORRETRAY_AUTO_REFRESH_MINUTES=5`
- `TORRETRAY_START_FULLSCREEN=true`
- `TORRETRAY_PRINTER_VENDOR_ID=0x1fc9`
- `TORRETRAY_PRINTER_PRODUCT_ID=0x2016`
- `TORRETRAY_PRINTER_INTERFACE=0`

## Installazione

1. Crea e attiva un virtual environment.
2. Installa i requirements con `pip install -r requirements.txt`.
3. Avvia il backend `TorreTray-backend`.
4. Avvia l'app con `python main.py`.

## Note operative

- Il backend deve essere raggiungibile dal Raspberry Pi.
- Il refresh manuale esegue una sync giornaliera sul backend prima di leggere le prenotazioni.
- La ristampa non modifica lo stato `printed`; la stampa dei ticket non ancora stampati invece lo aggiorna tramite API.
