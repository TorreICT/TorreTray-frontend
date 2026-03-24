# TorreTray Pi App

Interfaccia PyQt5 per Raspberry Pi dedicata alla gestione operativa e alla
stampa dei ticket TorreTray.

Questa app mantiene il flusso visuale del tray storico, ma non usa piu' il
vecchio database SQLite locale ne' un backend embedded: legge direttamente da
`TorreTray-backend`, usa il programma pasti definito dal backend e aggiorna via
API lo stato operativo delle prenotazioni.

## Cosa fa

- mostra le prenotazioni operative della fascia attiva divise in `Da stampare`
  e `Gia stampati`
- usa gli orari backend di `breakfast`, `lunch` e `dinner` per capire quando
  precaricare e quando aggiornare i dati
- esegue il caricamento automatico alcuni minuti prima del pasto e il refresh
  periodico durante la fascia attiva
- permette di stampare ticket singoli o in blocco
- permette di ristampare ticket gia' stampati senza cambiarne lo stato
- permette di annullare singole prenotazioni non ancora stampate
- suona una campanella quando ci sono ticket da gestire, con mute e intervallo configurabili
- salva localmente alcune impostazioni runtime modificabili dall'operatore

## Struttura

- `main.py`: entrypoint con supporto a `--test-time`
- `src/torretray_pi/app.py`: bootstrap PyQt5
- `src/torretray_pi/config.py`: lettura `.env`, schedule locale runtime, salvataggio impostazioni
- `src/torretray_pi/backend_client.py`: chiamate HTTP verso il backend
- `src/torretray_pi/services.py`: orchestrazione refresh, stampa e annullamento
- `src/torretray_pi/printing.py`: integrazione con stampante USB ESC/POS
- `src/torretray_pi/audio.py`: gestione campanella
- `src/torretray_pi/ui/`: finestra principale, dialog e widget PyQt5
- `res/img/`: asset grafici

## Configurazione

Crea un file `.env` nella root del progetto partendo da `.env.example`.

Variabili correnti:

- `TORRETRAY_API_BASE_URL=http://127.0.0.1:8000`
- `TORRETRAY_REQUEST_TIMEOUT_SECONDS=10`
- `TORRETRAY_AUTO_REFRESH_MINUTES=5`
- `TORRETRAY_PRELOAD_MINUTES=5`
- `TORRETRAY_SCHEDULE_LOOKAHEAD_DAYS=7`
- `TORRETRAY_BELL_INTERVAL_SECONDS=60`
- `TORRETRAY_BELL_MUTED=false`
- `TORRETRAY_START_FULLSCREEN=true`
- `TORRETRAY_PRINTER_VENDOR_ID=0x1fc9`
- `TORRETRAY_PRINTER_PRODUCT_ID=0x2016`
- `TORRETRAY_PRINTER_INTERFACE=0`

Gli orari dei pasti non vengono piu' definiti nel `.env` locale: arrivano dal
backend, che e' la singola fonte di verita' del programma pasti.

## Installazione

1. Crea e attiva un virtual environment.
2. Installa le dipendenze con `pip install -r requirements.txt`.
3. Avvia `TorreTray-backend` e verifica che sia raggiungibile dal Raspberry Pi.
4. Avvia l'app con `python main.py`.

Per simulare una data/ora specifica senza cambiare l'orologio del sistema:

```powershell
python main.py --test-time 2026-03-23T13:00:00
```

## Note operative

- All'avvio l'app carica gli orari dal backend e decide se si trova in
  precaricamento, in fascia attiva o fuori fascia.
- Il refresh manuale ricarica prima gli orari dal backend e poi, se esiste una
  fascia attiva, esegue la sync e aggiorna la lista delle prenotazioni.
- Se non c'e' una fascia attiva, il refresh manuale esegue comunque la sync
  giornaliera del backend ma lascia vuote le liste operative.
- La stampa dei ticket pendenti li marca come stampati via API.
- La ristampa dei ticket gia' stampati non cambia lo stato operativo.
- L'annullamento e' disponibile solo per prenotazioni non ancora stampate.
- Il pulsante `Impostazioni` salva nel `.env` locale: refresh automatico,
  precaricamento, lookahead schedule, intervallo campanella e mute campanella.

## Dipendenze runtime

- `PyQt5`
- `requests`
- `python-escpos`

Su Raspberry Pi la stampa richiede che la stampante USB ESC/POS sia accessibile
con vendor id, product id e interface configurati correttamente.
