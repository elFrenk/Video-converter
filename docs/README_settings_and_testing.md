# Memoria impostazioni e test rapido

## Memoria delle ultime impostazioni

La GUI salva automaticamente le ultime scelte dell’utente in un file JSON locale.

Questo include, per esempio:

* ultimo video selezionato
* cartella output
* formato immagine
* modalità export
* parametri pairs
* naming mode
* resize
* qualità/compressione

Il salvataggio è gestito da:

* `settings_store.py`

## Dove vengono salvate

Le impostazioni vengono salvate in una cartella locale nella home utente, in un file JSON facilmente ispezionabile.

## Test rapido

Prima di un export completo, puoi usare il **test rapido**.

### In modalità `frames`

Esporta pochi frame di prova in una sottocartella `quick_test`.

### In modalità `pairs`

Esporta la prima coppia disponibile, sempre in `quick_test`.

Questo è utile per verificare:

* naming
* qualità file
* struttura cartelle
* compatibilità pratica con geopyv

## Popup di risultato

Al termine del test o dell’export, la GUI mostra una finestra più leggibile con:

* riepilogo operazione
* file esportati
* cartella output
* pulsante per aprire la cartella

## Note pratiche

* se un video non si apre bene, prova a convertirlo in `.mp4`
* se l’export è lungo, fai sempre prima un test rapido
* la preview usa `Pillow` per mostrare il frame in `tkinter`

## Rimandi

* quickstart → `README_enhanced_quickstart.md`
* funzioni GUI → `README_enhanced_features.md`
* preset e modalità → `README_enhanced_presets_and_modes.md`
* indice generale → `README_enhanced_index.md`
