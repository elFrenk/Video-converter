from __future__ import annotations

import os
import platform
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk

from export_pairs import PairExportConfig, PairExportError, build_pairs, export_pairs
from frame_exporter import ExportConfig, ExportConfigError, build_target_indices, export_frames, get_video_frame_count
from preview import PreviewError, read_preview_frame, resize_for_preview
from settings_store import load_settings, save_settings
from video_io import VideoIOError, build_default_output_dir, format_video_info, read_video_info


PRESET_MAP = {
    "Custom": None,
    "geopyv standard": {
        "format": "png",
        "naming_mode": "sequential",
        "grayscale": False,
        "resize_width": "",
        "resize_height": "",
        "jpeg_quality": "95",
        "png_compression": "3",
        "export_mode": "frames",
        "prefix": "frame",
        "overwrite": False,
    },
    "Massima qualità": {
        "format": "png",
        "naming_mode": "source_index",
        "grayscale": False,
        "resize_width": "",
        "resize_height": "",
        "jpeg_quality": "95",
        "png_compression": "1",
        "export_mode": "frames",
        "prefix": "frame",
        "overwrite": False,
    },
    "Leggero": {
        "format": "jpg",
        "naming_mode": "sequential",
        "grayscale": False,
        "resize_width": "",
        "resize_height": "",
        "jpeg_quality": "90",
        "png_compression": "3",
        "export_mode": "frames",
        "prefix": "frame",
        "overwrite": False,
    },
    "Pairs per confronto": {
        "format": "png",
        "naming_mode": "sequential",
        "grayscale": False,
        "resize_width": "",
        "resize_height": "",
        "jpeg_quality": "95",
        "png_compression": "3",
        "export_mode": "pairs",
        "prefix": "pair",
        "overwrite": False,
        "pair_mode": "consecutive",
        "pair_step": "1",
        "pair_spacing": "1",
        "create_subfolders": True,
    },
}


class VideoToFramesAppEnhanced:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Video to Frames Exporter — Enhanced")
        self.root.geometry("1120x860")
        self.root.minsize(980, 760)

        self._settings = load_settings()
        self._preview_window = None
        self._preview_photo = None
        self._preview_label = None
        self._preview_info_label = None
        self._frame_count_cache = None
        self._video_info_cache = None
        self._validation_labels: dict[str, ttk.Label] = {}
        self._field_widgets: dict[str, tk.Widget] = {}

        self.video_path = tk.StringVar(value=self._settings.get("video_path", ""))
        self.output_dir = tk.StringVar(value=self._settings.get("output_dir", ""))
        self.format_var = tk.StringVar(value=self._settings.get("format", "png"))
        self.prefix_var = tk.StringVar(value=self._settings.get("prefix", "frame"))
        self.start_frame_var = tk.StringVar(value=str(self._settings.get("start_frame", 0)))
        self.end_frame_var = tk.StringVar(value=self._settings.get("end_frame", ""))
        self.step_var = tk.StringVar(value=str(self._settings.get("step", 1)))
        self.jpeg_quality_var = tk.StringVar(value=str(self._settings.get("jpeg_quality", 95)))
        self.png_compression_var = tk.StringVar(value=str(self._settings.get("png_compression", 3)))
        self.resize_width_var = tk.StringVar(value=str(self._settings.get("resize_width", "")))
        self.resize_height_var = tk.StringVar(value=str(self._settings.get("resize_height", "")))
        self.gray_var = tk.BooleanVar(value=bool(self._settings.get("grayscale", False)))
        self.overwrite_var = tk.BooleanVar(value=bool(self._settings.get("overwrite", False)))
        self.naming_mode_var = tk.StringVar(value=self._settings.get("naming_mode", "source_index"))
        self.padding_var = tk.StringVar(value=str(self._settings.get("zero_padding", 5)))

        self.export_mode_var = tk.StringVar(value=self._settings.get("export_mode", "frames"))
        self.pair_mode_var = tk.StringVar(value=self._settings.get("pair_mode", "consecutive"))
        self.pair_step_var = tk.StringVar(value=str(self._settings.get("pair_step", 1)))
        self.pair_spacing_var = tk.StringVar(value=str(self._settings.get("pair_spacing", 1)))
        self.create_subfolders_var = tk.BooleanVar(value=bool(self._settings.get("create_subfolders", True)))
        self.preset_var = tk.StringVar(value="Custom")

        self.video_info_text = tk.StringVar(value="Nessun video selezionato.")
        self.progress_var = tk.DoubleVar(value=0.0)
        self.status_var = tk.StringVar(value="Pronto.")
        self.summary_text = tk.StringVar(value="Nessun riepilogo disponibile.")
        self.preview_frame_var = tk.IntVar(value=0)

        self._build_ui()
        self._bind_events()
        self._load_initial_video_state()
        self._update_mode_ui()
        self.validate_all_fields()
        self.update_summary()

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill="both", expand=True)

        header = ttk.Frame(main)
        header.pack(fill="x", pady=(0, 8))
        ttk.Label(header, text="Video to Frames Exporter", font=("Segoe UI", 18, "bold")).pack(side="left")
        ttk.Label(header, text="UX enhanced for geopyv", font=("Segoe UI", 10)).pack(side="left", padx=(10, 0))

        content = ttk.Frame(main)
        content.pack(fill="both", expand=True)
        content.columnconfigure(0, weight=3)
        content.columnconfigure(1, weight=2)

        left = ttk.Frame(content)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        right = ttk.Frame(content)
        right.grid(row=0, column=1, sticky="nsew")

        self._build_video_section(left)
        self._build_export_section(left)
        self._build_pair_section(left)
        self._build_actions_section(left)

        self._build_preview_section(right)
        self._build_summary_section(right)
        self._build_progress_section(right)

    def _build_video_section(self, parent):
        sec = ttk.LabelFrame(parent, text="Video e output", padding=10)
        sec.pack(fill="x", pady=6)

        r1 = ttk.Frame(sec)
        r1.pack(fill="x", pady=3)
        ttk.Label(r1, text="Video:", width=12).pack(side="left")
        e = ttk.Entry(r1, textvariable=self.video_path)
        e.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._field_widgets["video_path"] = e
        ttk.Button(r1, text="Sfoglia", command=self.browse_video).pack(side="left")

        self._add_validation_line(sec, "video_path")

        r2 = ttk.Frame(sec)
        r2.pack(fill="x", pady=3)
        ttk.Label(r2, text="Output:", width=12).pack(side="left")
        e2 = ttk.Entry(r2, textvariable=self.output_dir)
        e2.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._field_widgets["output_dir"] = e2
        ttk.Button(r2, text="Sfoglia", command=self.browse_output).pack(side="left")
        ttk.Button(r2, text="Apri cartella", command=self.open_output_dir).pack(side="left", padx=(8, 0))

        self._add_validation_line(sec, "output_dir")

        info = ttk.LabelFrame(sec, text="Info video", padding=8)
        info.pack(fill="x", pady=(6, 0))
        ttk.Label(info, textvariable=self.video_info_text, justify="left").pack(anchor="w")

    def _build_export_section(self, parent):
        sec = ttk.LabelFrame(parent, text="Export base", padding=10)
        sec.pack(fill="x", pady=6)

        r0 = ttk.Frame(sec)
        r0.pack(fill="x", pady=3)
        ttk.Label(r0, text="Preset:", width=12).pack(side="left")
        preset_combo = ttk.Combobox(r0, textvariable=self.preset_var, values=list(PRESET_MAP.keys()), state="readonly", width=24)
        preset_combo.pack(side="left")
        ttk.Button(r0, text="Applica", command=self.apply_preset).pack(side="left", padx=(8, 0))

        r1 = ttk.Frame(sec)
        r1.pack(fill="x", pady=3)
        ttk.Label(r1, text="Formato:", width=12).pack(side="left")
        ttk.Combobox(r1, textvariable=self.format_var, values=["png", "jpg", "jpeg", "bmp", "tif", "tiff"], state="readonly", width=10).pack(side="left", padx=(0, 16))
        ttk.Label(r1, text="Prefisso:", width=10).pack(side="left")
        e = ttk.Entry(r1, textvariable=self.prefix_var, width=14)
        e.pack(side="left", padx=(0, 16))
        self._field_widgets["prefix"] = e
        ttk.Label(r1, text="Padding:", width=8).pack(side="left")
        e2 = ttk.Entry(r1, textvariable=self.padding_var, width=6)
        e2.pack(side="left")
        self._field_widgets["padding"] = e2

        self._add_validation_line(sec, "prefix")
        self._add_validation_line(sec, "padding")

        r2 = ttk.Frame(sec)
        r2.pack(fill="x", pady=3)
        ttk.Label(r2, text="Modalità:", width=12).pack(side="left")
        ttk.Combobox(r2, textvariable=self.export_mode_var, values=["frames", "pairs"], state="readonly", width=12).pack(side="left", padx=(0, 16))
        ttk.Label(r2, text="Naming:", width=10).pack(side="left")
        ttk.Combobox(r2, textvariable=self.naming_mode_var, values=["source_index", "sequential"], state="readonly", width=16).pack(side="left")

        r3 = ttk.Frame(sec)
        r3.pack(fill="x", pady=3)
        ttk.Label(r3, text="Frame iniziale:", width=12).pack(side="left")
        e3 = ttk.Entry(r3, textvariable=self.start_frame_var, width=10)
        e3.pack(side="left", padx=(0, 16))
        self._field_widgets["start_frame"] = e3
        ttk.Label(r3, text="Frame finale:", width=10).pack(side="left")
        e4 = ttk.Entry(r3, textvariable=self.end_frame_var, width=10)
        e4.pack(side="left", padx=(0, 16))
        self._field_widgets["end_frame"] = e4
        ttk.Label(r3, text="Passo:", width=8).pack(side="left")
        e5 = ttk.Entry(r3, textvariable=self.step_var, width=8)
        e5.pack(side="left")
        self._field_widgets["step"] = e5

        self._add_validation_line(sec, "frame_range")

        r4 = ttk.Frame(sec)
        r4.pack(fill="x", pady=3)
        ttk.Label(r4, text="Resize w:", width=12).pack(side="left")
        e6 = ttk.Entry(r4, textvariable=self.resize_width_var, width=10)
        e6.pack(side="left", padx=(0, 16))
        self._field_widgets["resize_width"] = e6
        ttk.Label(r4, text="Resize h:", width=10).pack(side="left")
        e7 = ttk.Entry(r4, textvariable=self.resize_height_var, width=10)
        e7.pack(side="left", padx=(0, 16))
        self._field_widgets["resize_height"] = e7
        ttk.Checkbutton(r4, text="Grayscale", variable=self.gray_var).pack(side="left", padx=(0, 16))
        ttk.Checkbutton(r4, text="Overwrite", variable=self.overwrite_var).pack(side="left")

        self._add_validation_line(sec, "resize")

        r5 = ttk.Frame(sec)
        r5.pack(fill="x", pady=3)
        ttk.Label(r5, text="JPEG quality:", width=12).pack(side="left")
        e8 = ttk.Entry(r5, textvariable=self.jpeg_quality_var, width=10)
        e8.pack(side="left", padx=(0, 16))
        self._field_widgets["jpeg_quality"] = e8
        ttk.Label(r5, text="PNG compr.:", width=10).pack(side="left")
        e9 = ttk.Entry(r5, textvariable=self.png_compression_var, width=10)
        e9.pack(side="left")
        self._field_widgets["png_compression"] = e9

        self._add_validation_line(sec, "format_params")

    def _build_pair_section(self, parent):
        sec = ttk.LabelFrame(parent, text="Coppie di frame", padding=10)
        sec.pack(fill="x", pady=6)
        self.pair_section = sec

        r1 = ttk.Frame(sec)
        r1.pack(fill="x", pady=3)
        ttk.Label(r1, text="Pair mode:", width=12).pack(side="left")
        ttk.Combobox(r1, textvariable=self.pair_mode_var, values=["consecutive", "stride", "custom_step"], state="readonly", width=16).pack(side="left", padx=(0, 16))
        ttk.Label(r1, text="Pair step:", width=10).pack(side="left")
        e1 = ttk.Entry(r1, textvariable=self.pair_step_var, width=10)
        e1.pack(side="left", padx=(0, 16))
        self._field_widgets["pair_step"] = e1
        ttk.Label(r1, text="Spacing:", width=8).pack(side="left")
        e2 = ttk.Entry(r1, textvariable=self.pair_spacing_var, width=10)
        e2.pack(side="left")
        self._field_widgets["pair_spacing"] = e2

        self._add_validation_line(sec, "pairs")

        r2 = ttk.Frame(sec)
        r2.pack(fill="x", pady=3)
        ttk.Checkbutton(r2, text="Crea sottocartelle per coppia", variable=self.create_subfolders_var).pack(side="left")

    def _build_actions_section(self, parent):
        sec = ttk.LabelFrame(parent, text="Azioni", padding=10)
        sec.pack(fill="x", pady=6)

        row = ttk.Frame(sec)
        row.pack(fill="x")
        ttk.Button(row, text="Leggi info video", command=self.load_video_info).pack(side="left")
        ttk.Button(row, text="Test rapido", command=self.run_quick_test).pack(side="left", padx=(8, 0))
        ttk.Button(row, text="Esporta", command=self.start_export_thread).pack(side="right")

    def _build_preview_section(self, parent):
        sec = ttk.LabelFrame(parent, text="Anteprima", padding=10)
        sec.pack(fill="both", expand=False, pady=6)

        top = ttk.Frame(sec)
        top.pack(fill="x", pady=(0, 6))
        ttk.Button(top, text="Mostra frame selezionato", command=self.show_preview).pack(side="left")
        ttk.Button(top, text="Primo frame", command=lambda: self._set_preview_frame(0)).pack(side="left", padx=(8, 0))
        ttk.Button(top, text="Frame iniziale", command=self._set_preview_start_frame).pack(side="left", padx=(8, 0))
        ttk.Button(top, text="Frame finale", command=self._set_preview_end_frame).pack(side="left", padx=(8, 0))

        slider_row = ttk.Frame(sec)
        slider_row.pack(fill="x", pady=(0, 6))
        ttk.Label(slider_row, text="Frame preview:").pack(side="left")
        self.preview_slider = ttk.Scale(slider_row, from_=0, to=0, orient="horizontal", command=self._on_slider_move)
        self.preview_slider.pack(side="left", fill="x", expand=True, padx=8)
        self.preview_value_label = ttk.Label(slider_row, text="0")
        self.preview_value_label.pack(side="left")

        self.inline_preview_info = ttk.Label(sec, text="Nessuna anteprima caricata.", justify="left")
        self.inline_preview_info.pack(anchor="w", pady=(0, 6))
        self.inline_preview_image = ttk.Label(sec)
        self.inline_preview_image.pack(anchor="center")

    def _build_summary_section(self, parent):
        sec = ttk.LabelFrame(parent, text="Riepilogo export previsto", padding=10)
        sec.pack(fill="x", pady=6)
        ttk.Label(sec, textvariable=self.summary_text, justify="left", wraplength=360).pack(anchor="w")

    def _build_progress_section(self, parent):
        sec = ttk.LabelFrame(parent, text="Stato", padding=10)
        sec.pack(fill="x", pady=6)
        ttk.Progressbar(sec, variable=self.progress_var, maximum=100).pack(fill="x", pady=(0, 8))
        ttk.Label(sec, textvariable=self.status_var, justify="left", wraplength=360).pack(anchor="w")

    def _add_validation_line(self, parent, key: str):
        label = ttk.Label(parent, text="", foreground="#9a1b1b")
        label.pack(anchor="w")
        self._validation_labels[key] = label

    def _bind_events(self):
        vars_to_watch = [
            self.video_path, self.output_dir, self.format_var, self.prefix_var,
            self.start_frame_var, self.end_frame_var, self.step_var,
            self.jpeg_quality_var, self.png_compression_var,
            self.resize_width_var, self.resize_height_var,
            self.naming_mode_var, self.padding_var,
            self.export_mode_var, self.pair_mode_var,
            self.pair_step_var, self.pair_spacing_var,
        ]
        for var in vars_to_watch:
            var.trace_add("write", self._on_settings_changed)
        for var in [self.gray_var, self.overwrite_var, self.create_subfolders_var]:
            var.trace_add("write", self._on_settings_changed)

    def _load_initial_video_state(self):
        path = self.video_path.get().strip()
        if path and os.path.isfile(path):
            try:
                self.load_video_info(silent=True)
            except Exception:
                pass

    def _on_settings_changed(self, *args):
        self._update_mode_ui()
        self.validate_all_fields()
        self.update_summary()
        self._save_current_settings()

    def _save_current_settings(self):
        settings = {
            "video_path": self.video_path.get().strip(),
            "output_dir": self.output_dir.get().strip(),
            "format": self.format_var.get().strip(),
            "prefix": self.prefix_var.get().strip(),
            "start_frame": self.start_frame_var.get().strip(),
            "end_frame": self.end_frame_var.get().strip(),
            "step": self.step_var.get().strip(),
            "jpeg_quality": self.jpeg_quality_var.get().strip(),
            "png_compression": self.png_compression_var.get().strip(),
            "resize_width": self.resize_width_var.get().strip(),
            "resize_height": self.resize_height_var.get().strip(),
            "grayscale": self.gray_var.get(),
            "overwrite": self.overwrite_var.get(),
            "naming_mode": self.naming_mode_var.get().strip(),
            "zero_padding": self.padding_var.get().strip(),
            "export_mode": self.export_mode_var.get().strip(),
            "pair_mode": self.pair_mode_var.get().strip(),
            "pair_step": self.pair_step_var.get().strip(),
            "pair_spacing": self.pair_spacing_var.get().strip(),
            "create_subfolders": self.create_subfolders_var.get(),
        }
        save_settings(settings)

    def _update_mode_ui(self):
        pairs_enabled = self.export_mode_var.get().strip() == "pairs"
        state = "normal" if pairs_enabled else "disabled"
        for key in ["pair_step", "pair_spacing"]:
            widget = self._field_widgets.get(key)
            if widget is not None:
                widget.configure(state=state)
        for child in self.pair_section.winfo_children():
            for grand in getattr(child, "winfo_children", lambda: [])():
                try:
                    if isinstance(grand, ttk.Entry) or isinstance(grand, ttk.Combobox) or isinstance(grand, ttk.Checkbutton):
                        grand.configure(state=state)
                except Exception:
                    pass
        # keep frame step disabled in pairs mode to avoid ambiguity
        step_widget = self._field_widgets.get("step")
        if step_widget is not None:
            step_widget.configure(state="disabled" if pairs_enabled else "normal")

    def apply_preset(self):
        preset = PRESET_MAP.get(self.preset_var.get())
        if not preset:
            return
        self.format_var.set(preset.get("format", self.format_var.get()))
        self.naming_mode_var.set(preset.get("naming_mode", self.naming_mode_var.get()))
        self.gray_var.set(preset.get("grayscale", self.gray_var.get()))
        self.resize_width_var.set(preset.get("resize_width", self.resize_width_var.get()))
        self.resize_height_var.set(preset.get("resize_height", self.resize_height_var.get()))
        self.jpeg_quality_var.set(preset.get("jpeg_quality", self.jpeg_quality_var.get()))
        self.png_compression_var.set(preset.get("png_compression", self.png_compression_var.get()))
        self.export_mode_var.set(preset.get("export_mode", self.export_mode_var.get()))
        self.prefix_var.set(preset.get("prefix", self.prefix_var.get()))
        self.overwrite_var.set(preset.get("overwrite", self.overwrite_var.get()))
        if "pair_mode" in preset:
            self.pair_mode_var.set(preset["pair_mode"])
        if "pair_step" in preset:
            self.pair_step_var.set(preset["pair_step"])
        if "pair_spacing" in preset:
            self.pair_spacing_var.set(preset["pair_spacing"])
        if "create_subfolders" in preset:
            self.create_subfolders_var.set(preset["create_subfolders"])
        self.status_var.set(f"Preset applicato: {self.preset_var.get()}")

    def browse_video(self):
        path = filedialog.askopenfilename(
            title="Seleziona un video",
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv *.m4v *.mpg *.mpeg"), ("All files", "*.*")],
        )
        if path:
            self.video_path.set(path)
            if not self.output_dir.get().strip():
                try:
                    self.output_dir.set(build_default_output_dir(path))
                except VideoIOError:
                    pass
            self.load_video_info()

    def browse_output(self):
        path = filedialog.askdirectory(title="Seleziona cartella di output")
        if path:
            self.output_dir.set(path)

    def open_output_dir(self):
        output_dir = self.output_dir.get().strip()
        if not output_dir:
            messagebox.showwarning("Attenzione", "Nessuna cartella output impostata.")
            return
        os.makedirs(output_dir, exist_ok=True)
        try:
            system = platform.system()
            if system == "Windows":
                os.startfile(output_dir)  # type: ignore[attr-defined]
            elif system == "Darwin":
                subprocess.run(["open", output_dir], check=False)
            else:
                subprocess.run(["xdg-open", output_dir], check=False)
        except Exception as exc:
            messagebox.showerror("Errore", f"Impossibile aprire la cartella: {exc}")

    def load_video_info(self, silent: bool = False):
        video = self.video_path.get().strip()
        if not video:
            if not silent:
                messagebox.showwarning("Attenzione", "Seleziona prima un video.")
            return
        try:
            info = read_video_info(video)
        except VideoIOError as exc:
            if not silent:
                messagebox.showerror("Errore", str(exc))
            return
        self._video_info_cache = info
        self._frame_count_cache = info.frame_count
        self.video_info_text.set(format_video_info(info))
        if not self.end_frame_var.get().strip() and info.frame_count > 0:
            self.end_frame_var.set(str(info.frame_count - 1))
        self.preview_slider.configure(to=max(info.frame_count - 1, 0))
        self.preview_frame_var.set(min(self.preview_frame_var.get(), max(info.frame_count - 1, 0)))
        self.preview_slider.set(self.preview_frame_var.get())
        self.preview_value_label.configure(text=str(self.preview_frame_var.get()))

    def _on_slider_move(self, value):
        idx = int(float(value))
        self.preview_frame_var.set(idx)
        self.preview_value_label.configure(text=str(idx))

    def _set_preview_frame(self, idx: int):
        self.preview_frame_var.set(max(0, idx))
        self.preview_slider.set(self.preview_frame_var.get())
        self.preview_value_label.configure(text=str(self.preview_frame_var.get()))
        self.show_preview()

    def _set_preview_start_frame(self):
        idx = self._safe_int(self.start_frame_var.get().strip(), 0)
        self._set_preview_frame(idx)

    def _set_preview_end_frame(self):
        if self.end_frame_var.get().strip():
            idx = self._safe_int(self.end_frame_var.get().strip(), 0)
        elif self._frame_count_cache:
            idx = self._frame_count_cache - 1
        else:
            idx = 0
        self._set_preview_frame(idx)

    def show_preview(self):
        video = self.video_path.get().strip()
        if not video:
            messagebox.showwarning("Attenzione", "Seleziona prima un video.")
            return
        frame_index = self.preview_frame_var.get()
        try:
            preview = read_preview_frame(video, frame_index=frame_index)
            frame_bgr = resize_for_preview(preview.image_bgr, max_width=560, max_height=320)
            frame_rgb = frame_bgr[:, :, ::-1]
            pil_image = Image.fromarray(frame_rgb)
            self._preview_photo = ImageTk.PhotoImage(pil_image)
        except (PreviewError, OSError) as exc:
            messagebox.showerror("Errore anteprima", str(exc))
            return

        info_text = (
            f"Video: {os.path.basename(preview.video_path)}\n"
            f"Frame mostrato: {preview.frame_index}\n"
            f"Dimensioni originali: {preview.width} x {preview.height}"
        )
        self.inline_preview_info.configure(text=info_text)
        self.inline_preview_image.configure(image=self._preview_photo)
        self.inline_preview_image.image = self._preview_photo

    def validate_all_fields(self) -> bool:
        errors = {}

        video = self.video_path.get().strip()
        if not video:
            errors["video_path"] = "Seleziona un video."
        elif not os.path.isfile(video):
            errors["video_path"] = "Il file video non esiste."

        output_dir = self.output_dir.get().strip()
        if not output_dir:
            errors["output_dir"] = "Seleziona una cartella output."

        if not self.prefix_var.get().strip():
            errors["prefix"] = "Il prefisso non può essere vuoto."

        pad = self._safe_int(self.padding_var.get().strip(), None)
        if pad is None or pad < 1:
            errors["padding"] = "Padding deve essere un intero >= 1."

        start = self._safe_int(self.start_frame_var.get().strip(), None)
        end_text = self.end_frame_var.get().strip()
        end = self._safe_int(end_text, None) if end_text else None
        step = self._safe_int(self.step_var.get().strip(), None)
        if start is None or start < 0:
            errors["frame_range"] = "Frame iniziale non valido."
        elif end is not None and end < start:
            errors["frame_range"] = "Frame finale deve essere >= iniziale."
        elif self.export_mode_var.get().strip() == "frames" and (step is None or step < 1):
            errors["frame_range"] = "Passo deve essere >= 1."

        rw = self.resize_width_var.get().strip()
        rh = self.resize_height_var.get().strip()
        if bool(rw) ^ bool(rh):
            errors["resize"] = "Inserisci sia resize width sia resize height."
        else:
            if rw and (self._safe_int(rw, None) is None or self._safe_int(rw, None) <= 0):
                errors["resize"] = "Resize width deve essere > 0."
            if rh and (self._safe_int(rh, None) is None or self._safe_int(rh, None) <= 0):
                errors["resize"] = "Resize height deve essere > 0."

        jpg_q = self._safe_int(self.jpeg_quality_var.get().strip(), None)
        png_c = self._safe_int(self.png_compression_var.get().strip(), None)
        if jpg_q is None or not (0 <= jpg_q <= 100):
            errors["format_params"] = "JPEG quality deve essere tra 0 e 100."
        elif png_c is None or not (0 <= png_c <= 9):
            errors["format_params"] = "PNG compression deve essere tra 0 e 9."

        if self.export_mode_var.get().strip() == "pairs":
            ps = self._safe_int(self.pair_step_var.get().strip(), None)
            sp = self._safe_int(self.pair_spacing_var.get().strip(), None)
            if ps is None or ps < 1 or sp is None or sp < 1:
                errors["pairs"] = "Pair step e spacing devono essere >= 1."

        for key, label in self._validation_labels.items():
            label.configure(text=errors.get(key, ""))

        return len(errors) == 0

    def update_summary(self):
        if not self.validate_all_fields():
            self.summary_text.set("Correggi i campi evidenziati per vedere un riepilogo affidabile.")
            return

        try:
            frame_count = self._frame_count_cache or get_video_frame_count(self.video_path.get().strip())
            if self.export_mode_var.get().strip() == "pairs":
                config = self._build_pair_config_from_ui()
                pairs = build_pairs(config)
                nfiles = len(pairs) * 2
                msg = (
                    f"Modalità: coppie\n"
                    f"Coppie previste: {len(pairs)}\n"
                    f"File immagine previsti: {nfiles}\n"
                    f"Output: {config.output_dir}\n"
                    f"Naming: {config.naming_mode}\n"
                    f"Sottocartelle per coppia: {'sì' if config.create_subfolders else 'no'}\n"
                    f"Frame video disponibili: {frame_count}"
                )
            else:
                config = self._build_config_from_ui()
                targets = build_target_indices(config, frame_count)
                msg = (
                    f"Modalità: sequenza frame\n"
                    f"Frame previsti: {len(targets)}\n"
                    f"Output: {config.output_dir}\n"
                    f"Naming: {config.naming_mode}\n"
                    f"Formato: {config.image_format}\n"
                    f"Frame video disponibili: {frame_count}"
                )
            self.summary_text.set(msg)
        except Exception:
            self.summary_text.set("Riepilogo non disponibile finché il video non è leggibile.")

    def run_quick_test(self):
        if not self.validate_all_fields():
            messagebox.showwarning("Campi non validi", "Correggi i campi evidenziati prima del test rapido.")
            return
        try:
            quick_root = os.path.join(self.output_dir.get().strip(), "quick_test")
            if self.export_mode_var.get().strip() == "pairs":
                config = self._build_pair_config_from_ui()
                config.output_dir = quick_root
                pairs = build_pairs(config)
                if not pairs:
                    raise PairExportError("Nessuna coppia disponibile per il test rapido.")
                config.end_frame = pairs[0].second_index
                report = export_pairs(config)
                self._show_result_dialog(
                    title="Test rapido completato",
                    body=(
                        f"È stata esportata la prima coppia disponibile.\n\n"
                        f"Coppie esportate correttamente: {report.exported_pairs}/{report.total_pairs}\n"
                        f"Cartella: {report.output_dir}"
                    ),
                )
            else:
                config = self._build_config_from_ui()
                config.output_dir = quick_root
                start = config.start_frame
                config.end_frame = min(start + max(2, config.step * 2), int(self.end_frame_var.get().strip()) if self.end_frame_var.get().strip() else start + max(2, config.step * 2))
                report = export_frames(config)
                self._show_result_dialog(
                    title="Test rapido completato",
                    body=(
                        f"Sono stati esportati alcuni frame di prova.\n\n"
                        f"Frame esportati: {report.exported_frames}/{report.requested_frames}\n"
                        f"Cartella: {report.output_dir}"
                    ),
                )
        except (ExportConfigError, PairExportError, VideoIOError, ValueError) as exc:
            messagebox.showerror("Errore test rapido", str(exc))

    def start_export_thread(self):
        if not self.validate_all_fields():
            messagebox.showwarning("Campi non validi", "Correggi i campi evidenziati prima di esportare.")
            return
        self.progress_var.set(0.0)
        self.status_var.set("Avvio export...")
        thread = threading.Thread(target=self.export_worker, daemon=True)
        thread.start()

    def export_worker(self):
        try:
            if self.export_mode_var.get().strip() == "pairs":
                config = self._build_pair_config_from_ui()
                report = export_pairs(config)
                self.root.after(0, self.progress_var.set, 100.0)
                self.root.after(0, self.status_var.set, f"Completato. Esportate {report.exported_pairs}/{report.total_pairs} coppie.")
                self.root.after(0, lambda: self._show_result_dialog(
                    title="Export completato",
                    body=self._build_pair_report_message(report),
                ))
            else:
                config = self._build_config_from_ui()
                report = export_frames(config, progress_callback=self._progress_callback)
                self.root.after(0, self.progress_var.set, 100.0)
                self.root.after(0, self.status_var.set, f"Completato. Esportati {report.exported_frames}/{report.requested_frames} frame.")
                self.root.after(0, lambda: self._show_result_dialog(
                    title="Export completato",
                    body=self._build_report_message(report),
                ))
        except (ValueError, ExportConfigError, VideoIOError, PairExportError) as exc:
            self.root.after(0, self.status_var.set, f"Errore: {exc}")
            self.root.after(0, lambda: messagebox.showerror("Errore", str(exc)))
        except Exception as exc:
            self.root.after(0, self.status_var.set, f"Errore inatteso: {exc}")
            self.root.after(0, lambda: messagebox.showerror("Errore inatteso", str(exc)))

    def _build_config_from_ui(self) -> ExportConfig:
        end_frame_text = self.end_frame_var.get().strip()
        resize_w_text = self.resize_width_var.get().strip()
        resize_h_text = self.resize_height_var.get().strip()
        return ExportConfig(
            video_path=self.video_path.get().strip(),
            output_dir=self.output_dir.get().strip(),
            image_format=self.format_var.get().strip().lower(),
            prefix=self.prefix_var.get().strip() or "frame",
            start_frame=int(self.start_frame_var.get().strip()),
            end_frame=int(end_frame_text) if end_frame_text else None,
            step=int(self.step_var.get().strip()),
            jpeg_quality=int(self.jpeg_quality_var.get().strip()),
            png_compression=int(self.png_compression_var.get().strip()),
            resize_width=int(resize_w_text) if resize_w_text else None,
            resize_height=int(resize_h_text) if resize_h_text else None,
            grayscale=self.gray_var.get(),
            overwrite=self.overwrite_var.get(),
            naming_mode=self.naming_mode_var.get().strip(),
            zero_padding=int(self.padding_var.get().strip()),
        )

    def _build_pair_config_from_ui(self) -> PairExportConfig:
        end_frame_text = self.end_frame_var.get().strip()
        resize_w_text = self.resize_width_var.get().strip()
        resize_h_text = self.resize_height_var.get().strip()
        return PairExportConfig(
            video_path=self.video_path.get().strip(),
            output_dir=self.output_dir.get().strip(),
            image_format=self.format_var.get().strip().lower(),
            prefix=self.prefix_var.get().strip() or "pair",
            start_frame=int(self.start_frame_var.get().strip()),
            end_frame=int(end_frame_text) if end_frame_text else None,
            pair_mode=self.pair_mode_var.get().strip(),
            pair_step=int(self.pair_step_var.get().strip()),
            pair_spacing=int(self.pair_spacing_var.get().strip()),
            jpeg_quality=int(self.jpeg_quality_var.get().strip()),
            png_compression=int(self.png_compression_var.get().strip()),
            resize_width=int(resize_w_text) if resize_w_text else None,
            resize_height=int(resize_h_text) if resize_h_text else None,
            grayscale=self.gray_var.get(),
            overwrite=self.overwrite_var.get(),
            naming_mode=self.naming_mode_var.get().strip(),
            zero_padding=int(self.padding_var.get().strip()),
            create_subfolders=self.create_subfolders_var.get(),
        )

    def _progress_callback(self, current: int, total: int, message: str):
        progress = 0.0 if total <= 0 else 100.0 * current / total
        self.root.after(0, self.progress_var.set, progress)
        self.root.after(0, self.status_var.set, message)

    def _show_result_dialog(self, title: str, body: str):
        dlg = tk.Toplevel(self.root)
        dlg.title(title)
        dlg.transient(self.root)
        dlg.grab_set()
        frm = ttk.Frame(dlg, padding=14)
        frm.pack(fill="both", expand=True)
        ttk.Label(frm, text=title, font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 8))
        text = tk.Text(frm, width=68, height=12, wrap="word")
        text.pack(fill="both", expand=True)
        text.insert("1.0", body)
        text.configure(state="disabled")
        btns = ttk.Frame(frm)
        btns.pack(fill="x", pady=(10, 0))
        ttk.Button(btns, text="Apri cartella output", command=self.open_output_dir).pack(side="left")
        ttk.Button(btns, text="Chiudi", command=dlg.destroy).pack(side="right")

    @staticmethod
    def _build_report_message(report) -> str:
        lines = [
            f"Frame richiesti: {report.requested_frames}",
            f"Frame esportati: {report.exported_frames}",
            f"File esistenti saltati: {report.skipped_existing}",
            f"Letture fallite: {report.failed_reads}",
            f"Scritture fallite: {report.failed_writes}",
            f"Cartella output: {report.output_dir}",
        ]
        if report.first_output:
            lines.append(f"Primo file: {report.first_output}")
        if report.last_output:
            lines.append(f"Ultimo file: {report.last_output}")
        return "\n".join(lines)

    @staticmethod
    def _build_pair_report_message(report) -> str:
        lines = [
            f"Coppie totali: {report.total_pairs}",
            f"Coppie esportate correttamente: {report.exported_pairs}",
            f"Cartella output: {report.output_dir}",
        ]
        if report.pair_reports:
            first_pair, first_a, first_b = report.pair_reports[0]
            lines.append(f"Prima coppia: ({first_pair.first_index}, {first_pair.second_index})")
            lines.append(f"File A: {first_a.first_output}")
            lines.append(f"File B: {first_b.first_output}")
        return "\n".join(lines)

    @staticmethod
    def _safe_int(text: str, default):
        try:
            return int(text)
        except Exception:
            return default


def main():
    root = tk.Tk()
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass
    VideoToFramesAppEnhanced(root)
    root.mainloop()


if __name__ == "__main__":
    main()
