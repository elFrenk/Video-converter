# Video to Frames Exporter

Tool desktop Python per convertire video in immagini pronte per workflow **geopyv**, PIV o image-correlation.

Il progetto è organizzato in moduli separati per mantenere chiara la distinzione tra:

* interfaccia grafica
* lettura e validazione video
* esportazione frame
* esportazione coppie
* preview
* salvataggio impostazioni

---

## Stato del progetto

La struttura attuale è buona e già abbastanza professionale:

* **GUI principale unica**: `video_to_frames_gui.py`
* **logica separata** in moduli dedicati
* **entry point** pulito con `run_gui.py`
* **documentazione modulare** in README brevi
* **persistenza impostazioni** con `settings_store.py`
* **supporto a sequenze e coppie di frame**

In pratica, non è più uno script monolitico: è già un piccolo progetto software vero.

---

## Struttura principale

* `video_to_frames_gui.py` — GUI principale
* `run_gui.py` — avvio rapido dell'app
* `frame_exporter.py` — export di sequenze di frame
* `export_pairs.py` — export di coppie di frame
* `video_io.py` — metadati e validazione video
* `preview.py` — lettura/resize frame per anteprima
* `settings_store.py` — memoria delle ultime impostazioni
* `requirements.txt` — dipendenze Python

Documentazione:

* `README_quickstart.md`
* `README_features.md`
* `README_preset_and_modes.md`
* `README_settings_and_testing.md`

---

## Avvio rapido

Installa le dipendenze:

```bash
pip install -r requirements.txt
```

Avvia l'app:

```bash
python video_to_frames_gui.py
```

Oppure:

```bash
python run_gui.py
```

---

## Da dove partire

Per leggere la documentazione nel modo più utile:

### 1. Partenza veloce

Apri prima:

[`README_quickstart.md`](README_quickstart.md)

### 2. Funzioni della GUI

Poi:

[`README_features.md`](README_features.md)

### 3. Preset e modalità

Per capire preset, `frames/pairs`, naming mode:

[`README_preset_and_modes.md`](README_preset_and_modes.md)

### 4. Memoria impostazioni e quick test

Per salvataggio automatico, test rapido e popup risultati:

[`README_settings_and_testing.md`](README_settings_and_testing.md)

---

## Considerazioni sulla struttura attuale

La struttura che hai ora ha diversi punti forti:

* **moduli ben separati**
* **nomi chiari** e leggibili
* **GUI centrale** senza dispersione eccessiva
* **README spezzati bene** invece di un unico file enorme
* **presenza di `run_gui.py`** utile per packaging futuro

Le uniche rifiniture che potresti fare più avanti sono:

* spostare i README secondari in una cartella `docs/`
* ignorare bene `Exports/` e `__pycache__`
* in futuro aggiungere una cartella `tests/`

Ma già così la base è ordinata e sensata.

---

## Documenti collegati

* [`README_quickstart.md`](README_quickstart.md)
* [`README_features.md`](README_features.md)
* [`README_preset_and_modes.md`](README_preset_and_modes.md)
* [`README_settings_and_testing.md`](README_settings_and_testing.md)

---

## Uso consigliato per geopyv

Workflow pratico consigliato:

1. seleziona il video
2. leggi i metadati
3. controlla la preview
4. applica il preset **geopyv standard**
5. fai un **test rapido**
6. verifica i file esportati
7. lancia l'export completo

---

## Nota finale

La struttura attuale è già più che dignitosa per un tool personale serio, e abbastanza pulita da poter crescere senza diventare subito ingestibile.
