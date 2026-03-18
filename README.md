# Video to Frames Exporter — Enhanced Docs

Questa documentazione è divisa in file brevi per essere più leggibile.

## Indice

- [Quick start](docs/readme/README_quickstart.md) — avvio rapido e uso consigliato
- [Features](docs/readme/README_features.md) — funzioni principali della GUI enhanced
- [Presets and modes](docs/readme/README_presets_and_modes.md) — preset, modalità `frames/pairs` e naming mode
- [Settings and testing](docs/readme/README_settings_and_testing.md) — memoria impostazioni, test rapido e note pratiche

## File principali del progetto

- [`video_to_frames_gui.py`](video_to_frames_gui_enhanced.py) — interfaccia grafica principale
- [`settings_store.py`](settings_store.py) — salvataggio e caricamento impostazioni
- [`preview.py`](preview.py) — anteprima video/frame
- [`frame_exporter.py`](frame_exporter.py) — esportazione dei frame
- [`export_pairs.py`](export_pairs.py) — esportazione in modalità coppie
- [`video_io.py`](video_io.py) — lettura e gestione dei file video
