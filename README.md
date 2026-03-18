# Video to Frames Exporter for geopyv

Piccola applicazione Python per convertire un video in una sequenza ordinata di immagini, pensata per preparare dataset da usare con **geopyv** o workflow simili di image correlation / PIV.

---

## Obiettivo

L'app permette di:
- selezionare un video
- leggere i metadati principali
- visualizzare l'anteprima del primo frame
- esportare i fotogrammi in una cartella
- scegliere il formato delle immagini
- controllare il naming dei file
- fare resize e conversione in scala di grigi
- evitare o permettere la sovrascrittura
- esportare sia sequenze normali sia coppie di frame

---

## Struttura del progetto

### File principali
- `video_to_frames_gui.py`  
  GUI principale dell'applicazione

- `video_to_frames_gui_with_preview.py`  
  Variante della GUI con anteprima del primo frame integrata

- `frame_exporter.py`  
  Logica di esportazione dei fotogrammi

- `video_io.py`  
  Lettura metadati, validazione video, utility di input/output

- `preview.py`  
  Lettura e ridimensionamento del frame usato per l'anteprima

- `export_pairs.py`  
  Esportazione controllata di coppie di frame

- `run_gui.py`  
  Entry point pulito per avviare l'app

### File di supporto
- `requirements.txt`  
  Dipendenze Python minime

- `README.md`  
  Documentazione del progetto

---

## Requisiti

- Python 3.10 o superiore consigliato
- OpenCV
- Pillow per la GUI con anteprima
- Tkinter disponibile nella tua installazione Python

Installazione dipendenze:

```bash
pip install -r requirements.txt
```

Installazione manuale tipica:

```bash
pip install opencv-python Pillow
```

---

## Avvio dell'app

### Versione standard

```bash
python run_gui.py
```

oppure:

```bash
python video_to_frames_gui.py
```

### Versione con anteprima integrata

```bash
python video_to_frames_gui_with_preview.py
```

---

## Funzionalità attuali

### Input video
- selezione file video da finestra
- lettura metadati:
  - risoluzione
  - FPS
  - numero frame
  - durata stimata

### Anteprima
- anteprima del primo frame del video
- ridimensionamento automatico per la visualizzazione
- utile per verificare rapidamente:
  - che il video sia quello giusto
  - che OpenCV lo stia leggendo correttamente
  - che il contenuto sia adatto all'analisi successiva

### Export fotogrammi
- formati supportati:
  - PNG
  - JPG / JPEG
  - BMP
  - TIF / TIFF
- frame iniziale e finale
- passo di campionamento
- prefisso del nome file
- zero padding configurabile
- scala di grigi opzionale
- resize opzionale
- gestione overwrite

### Naming mode
Sono disponibili due modalità:

#### `source_index`
Mantiene l'indice reale del frame nel video.

Esempio:
- `frame_00015.png`
- `frame_00020.png`
- `frame_00025.png`

#### `sequential`
Rinumera i frame esportati in modo compatto.

Esempio:
- `frame_00001.png`
- `frame_00002.png`
- `frame_00003.png`

### Export mode
Sono disponibili due modalità principali:

#### `frames`
Esporta una sequenza normale di immagini.

#### `pairs`
Esporta coppie di frame controllate, utili per workflow geopyv o confronti frame-frame.

Modalità disponibili per le coppie:
- `consecutive`
- `stride`
- `custom_step`

Opzioni aggiuntive per le coppie:
- distanza tra i frame della coppia
- passo tra coppie successive
- creazione opzionale di sottocartelle dedicate per ogni coppia

---

## Uso consigliato per geopyv

Per un workflow pulito con geopyv:

- usa **PNG** se vuoi massima fedeltà
- usa **JPG** se vuoi ridurre peso su disco
- usa `sequential` se vuoi una sequenza ordinata semplice da leggere negli script
- usa `source_index` se vuoi mantenere il legame col frame originale del video
- usa `frames` se vuoi esportare tutto o un sottoinsieme regolare
- usa `pairs` se vuoi controllare esplicitamente le immagini confrontate
- usa `step > 1` o `pair_spacing > 1` se vuoi diradare il dataset
- evita il resize se non hai una ragione precisa
- controlla sempre l'anteprima del primo frame prima di lanciare export lunghi

---

## Esempio di workflow

1. apri l'app
2. seleziona il video
3. controlla i metadati
4. apri l'anteprima del primo frame
5. scegli cartella output
6. imposta formato e naming mode
7. scegli se esportare `frames` oppure `pairs`
8. imposta intervallo frame e passo
9. esporta
10. usa la cartella di immagini risultante in geopyv

---

## Stato del progetto

### Già implementato
- separazione tra GUI e logica di export
- modulo dedicato ai metadati video
- modulo di anteprima del primo frame
- supporto per export di sequenze e coppie
- entry point pulito
- report finale dell'export

### Miglioramenti futuri possibili
- anteprima di un frame arbitrario, non solo del primo
- salvataggio ultime impostazioni
- packaging come eseguibile
- log più dettagliato
- test automatici
- abilitazione/disabilitazione dinamica dei controlli GUI in base alla modalità scelta

---

## Note

- `tkinter` è normalmente incluso in molte installazioni Python desktop, ma in alcuni ambienti Linux può essere necessario installarlo separatamente.
- Alcuni codec video possono dipendere da come OpenCV è stato compilato sul sistema.
- Se un file video non si apre, prova a convertirlo in `.mp4` con codec standard prima dell'import.
- La GUI con anteprima usa Pillow per convertire l'immagine OpenCV in un formato visualizzabile in tkinter.

---

## Stato da verificare manualmente

Conviene fare un test rapido su un video reale per verificare:
- corretto export dei frame
- corretto export delle coppie
- compatibilità pratica con geopyv
- funzionamento dell'anteprima
- comportamento del naming scelto
- corretto funzionamento di grayscale e resize
