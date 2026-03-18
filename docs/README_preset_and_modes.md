# Preset e modalità

## Preset rapidi

La GUI enhanced include questi preset:

* `Custom`
* `geopyv standard`
* `Massima qualità`
* `Leggero`
* `Pairs per confronto`

## Preset consigliato: geopyv standard

Imposta una configurazione pulita e pratica:

* formato `png`
* naming `sequential`
* niente grayscale
* niente resize
* export mode `frames`
* prefisso `frame`

## Export mode

### `frames`

Esporta una sequenza normale di immagini.

Parametri principali:

* frame iniziale
* frame finale
* passo
* formato
* prefisso
* naming mode

### `pairs`

Esporta coppie controllate di frame.

Modalità disponibili:

* `consecutive`
* `stride`
* `custom_step`

Parametri principali:

* `pair_mode`
* `pair_step`
* `pair_spacing`
* `create_subfolders`

In modalità `pairs`, il `step` della sequenza normale viene disabilitato per evitare ambiguità.

## Naming mode

### `source_index`

Mantiene il numero reale del frame nel video.

Esempio:

* `frame_00120.png`
* `frame_00125.png`

### `sequential`

Rinumera solo i frame esportati.

Esempio:

* `frame_00001.png`
* `frame_00002.png`

Per geopyv, spesso `sequential` è più comodo.

## Rimandi

* quickstart → `README_enhanced_quickstart.md`
* funzioni GUI → `README_enhanced_features.md`
* impostazioni e quick test → `README_enhanced_settings_and_testing.md`
* indice generale → `README_enhanced_index.md`
