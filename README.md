# Video to Frames Exporter for geopyv

Piccola applicazione Python per convertire un video in una sequenza ordinata di immagini, pensata per preparare dataset da usare con **geopyv** o workflow simili di image correlation / PIV.

---

## Obiettivo

L'app permette di:

* selezionare un video
* leggere i metadati principali
* esportare i fotogrammi in una cartella
* scegliere il formato delle immagini
* controllare il naming dei file
* fare resize e conversione in scala di grigi
* evitare o permettere la sovrascrittura

---

## Struttura del progetto

### File principali

* `video_to_frames_gui.py`
  GUI principale dell'applicazione

* `frame_exporter.py`
  Logica di esportazione dei fotogrammi

* `video_io.py`
  Lettura metadati, validazione video, utility di input/output

* `run_gui.py`
  Entry point pulito per avviare l'app

### File di supporto

* `requirements.txt`
  Dipendenze Python minime

* `README.md`
  Documentazione del progetto

---

## Requisiti

* Python 3.10 o superiore consigliato
* OpenCV
* Tkinter disponibile nella tua installazione Python

Installazione dipendenze:

```bash
pip install -r requirements.txt
```

Se preferisci installare manualmente:

```bash
pip install opencv-python
```

---

## Avvio dell'app

Il modo consigliato è:

```bash
python run_gui.py
```

In alternativa, puoi lanciare direttamente la GUI:

```bash
python video_to_frames_gui.py
```

---

## Funzionalità attuali

### Input video

* selezione file video da finestra
* lettura metadati:

  * risoluzione
  * FPS
  * numero frame
  * durata stimata

### Export fotogrammi

* formati supportati:

  * PNG
  * JPG / JPEG
  * BMP
  * TIF / TIFF
* frame iniziale e finale
* passo di campionamento
* prefisso del nome file
* zero padding configurabile
* scala di grigi opzionale
* resize opzionale
* qualità JPEG e compressione PNG
* gestione overwrite

### Naming mode

Sono disponibili due modalità:

#### `source_index`

Mantiene l'indice reale del frame nel video.

Esempio:

* `frame_00015.png`
* `frame_00020.png`
* `frame_00025.png`

#### `sequential`

Rinumera i frame esportati in modo compatto.

Esempio:

* `frame_00001.png`
* `frame_00002.png`
* `frame_00003.png`

---

## Uso consigliato per geopyv

Per un workflow pulito con geopyv:

* usa **PNG** se vuoi massima fedeltà
* usa **JPG** se vuoi ridurre peso su disco
* usa `sequential` se vuoi una sequenza ordinata semplice da leggere negli script
* usa `source_index` se vuoi mantenere il legame col frame originale del video
* usa `step > 1` se vuoi esportare un frame ogni N frame
* evita il resize se non hai una ragione precisa

---

## Esempio di workflow

1. apri l'app
2. seleziona il video
3. controlla i metadati
4. scegli cartella output
5. imposta formato e naming mode
6. imposta intervallo frame e passo
7. esporta
8. usa la cartella di immagini risultante in geopyv

---

## Stato del progetto

### Già implementato

* separazione tra GUI e logica di export
* modulo dedicato ai metadati video
* entry point pulito
* report finale dell'export

### Miglioramenti futuri possibili

* anteprima del primo frame
* export di coppie di frame per analisi
* salvataggio ultime impostazioni
* packaging come eseguibile
* log più dettagliato
* test automatici

---

## Note

* `tkinter` è normalmente incluso in molte installazioni Python desktop, ma in alcuni ambienti Linux può essere necessario installarlo separatamente.
* Alcuni codec video possono dipendere da come OpenCV è stato compilato sul sistema.
* Se un file video non si apre, prova a convertirlo in `.mp4` con codec standard prima dell'import.

---

## Stato da verificare manualmente

Conviene fare un test rapido su un video reale per verificare:

* corretto export dei frame
* compatibilità pratica con geopyv
* comportamento del naming scelto
* corretto funzionamento di grayscale e resize
