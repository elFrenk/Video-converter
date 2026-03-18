import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from frame_exporter import ExportConfig, ExportConfigError, export_frames
from video_io import (
    VideoIOError,
    build_default_output_dir,
    format_video_info,
    read_video_info,
)


class VideoToFramesApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Video to Frames Exporter")
        self.root.geometry("780x620")
        self.root.minsize(740, 560)

        self.video_path = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.format_var = tk.StringVar(value="png")
        self.prefix_var = tk.StringVar(value="frame")
        self.start_frame_var = tk.StringVar(value="0")
        self.end_frame_var = tk.StringVar(value="")
        self.step_var = tk.StringVar(value="1")
        self.jpeg_quality_var = tk.StringVar(value="95")
        self.png_compression_var = tk.StringVar(value="3")
        self.resize_width_var = tk.StringVar(value="")
        self.resize_height_var = tk.StringVar(value="")
        self.gray_var = tk.BooleanVar(value=False)
        self.overwrite_var = tk.BooleanVar(value=False)
        self.naming_mode_var = tk.StringVar(value="source_index")
        self.padding_var = tk.StringVar(value="5")

        self.video_info_text = tk.StringVar(value="Nessun video selezionato.")
        self.progress_var = tk.DoubleVar(value=0.0)
        self.status_var = tk.StringVar(value="Pronto.")

        self._build_ui()

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill="both", expand=True)

        title = ttk.Label(main, text="Esporta video in fotogrammi", font=("Segoe UI", 16, "bold"))
        title.pack(anchor="w", pady=(0, 10))

        video_frame = ttk.LabelFrame(main, text="Input video", padding=10)
        video_frame.pack(fill="x", pady=6)
        ttk.Entry(video_frame, textvariable=self.video_path).pack(side="left", fill="x", expand=True, padx=(0, 8))
        ttk.Button(video_frame, text="Sfoglia", command=self.browse_video).pack(side="left")

        output_frame = ttk.LabelFrame(main, text="Cartella output", padding=10)
        output_frame.pack(fill="x", pady=6)
        ttk.Entry(output_frame, textvariable=self.output_dir).pack(side="left", fill="x", expand=True, padx=(0, 8))
        ttk.Button(output_frame, text="Sfoglia", command=self.browse_output).pack(side="left")

        info_frame = ttk.LabelFrame(main, text="Info video", padding=10)
        info_frame.pack(fill="x", pady=6)
        ttk.Label(info_frame, textvariable=self.video_info_text, justify="left").pack(anchor="w")

        settings = ttk.LabelFrame(main, text="Impostazioni export", padding=10)
        settings.pack(fill="x", pady=6)

        row1 = ttk.Frame(settings)
        row1.pack(fill="x", pady=3)
        ttk.Label(row1, text="Formato:", width=16).pack(side="left")
        ttk.Combobox(
            row1,
            textvariable=self.format_var,
            values=["png", "jpg", "jpeg", "bmp", "tif", "tiff"],
            state="readonly",
            width=12,
        ).pack(side="left", padx=(0, 20))
        ttk.Label(row1, text="Prefisso:", width=10).pack(side="left")
        ttk.Entry(row1, textvariable=self.prefix_var, width=16).pack(side="left")
        ttk.Label(row1, text="Padding:", width=10).pack(side="left", padx=(20, 0))
        ttk.Entry(row1, textvariable=self.padding_var, width=8).pack(side="left")

        row2 = ttk.Frame(settings)
        row2.pack(fill="x", pady=3)
        ttk.Label(row2, text="Frame iniziale:", width=16).pack(side="left")
        ttk.Entry(row2, textvariable=self.start_frame_var, width=12).pack(side="left", padx=(0, 20))
        ttk.Label(row2, text="Frame finale:", width=10).pack(side="left")
        ttk.Entry(row2, textvariable=self.end_frame_var, width=12).pack(side="left", padx=(0, 20))
        ttk.Label(row2, text="Passo:", width=8).pack(side="left")
        ttk.Entry(row2, textvariable=self.step_var, width=8).pack(side="left")

        row3 = ttk.Frame(settings)
        row3.pack(fill="x", pady=3)
        ttk.Label(row3, text="Resize width:", width=16).pack(side="left")
        ttk.Entry(row3, textvariable=self.resize_width_var, width=12).pack(side="left", padx=(0, 20))
        ttk.Label(row3, text="Resize height:", width=10).pack(side="left")
        ttk.Entry(row3, textvariable=self.resize_height_var, width=12).pack(side="left")

        row4 = ttk.Frame(settings)
        row4.pack(fill="x", pady=3)
        ttk.Label(row4, text="JPEG quality:", width=16).pack(side="left")
        ttk.Entry(row4, textvariable=self.jpeg_quality_var, width=12).pack(side="left", padx=(0, 20))
        ttk.Label(row4, text="PNG compression:", width=14).pack(side="left")
        ttk.Entry(row4, textvariable=self.png_compression_var, width=12).pack(side="left")

        row5 = ttk.Frame(settings)
        row5.pack(fill="x", pady=3)
        ttk.Checkbutton(row5, text="Converti in scala di grigi", variable=self.gray_var).pack(side="left", padx=(0, 20))
        ttk.Checkbutton(row5, text="Sovrascrivi file esistenti", variable=self.overwrite_var).pack(side="left")

        row6 = ttk.Frame(settings)
        row6.pack(fill="x", pady=3)
        ttk.Label(row6, text="Naming mode:", width=16).pack(side="left")
        ttk.Combobox(
            row6,
            textvariable=self.naming_mode_var,
            values=["source_index", "sequential"],
            state="readonly",
            width=16,
        ).pack(side="left")

        tips = ttk.LabelFrame(main, text="Suggerimenti per geopyv", padding=10)
        tips.pack(fill="x", pady=6)
        ttk.Label(
            tips,
            text=(
                "• Per geopyv in genere conviene PNG o JPG.\n"
                "• Usa source_index se vuoi mantenere il riferimento al frame originale.\n"
                "• Usa sequential se vuoi una sequenza compatta: frame_00001, frame_00002, ...\n"
                "• Se il video è lungo, usa passo > 1 per esportare un frame ogni N frame."
            ),
            justify="left",
        ).pack(anchor="w")

        progress_frame = ttk.LabelFrame(main, text="Avanzamento", padding=10)
        progress_frame.pack(fill="x", pady=6)
        ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100).pack(fill="x", pady=(0, 8))
        ttk.Label(progress_frame, textvariable=self.status_var).pack(anchor="w")

        buttons = ttk.Frame(main)
        buttons.pack(fill="x", pady=(10, 0))
        ttk.Button(buttons, text="Leggi info video", command=self.load_video_info).pack(side="left")
        ttk.Button(buttons, text="Esporta fotogrammi", command=self.start_export_thread).pack(side="right")

    def browse_video(self):
        path = filedialog.askopenfilename(
            title="Seleziona un video",
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv *.m4v *.mpg *.mpeg"),
                ("All files", "*.*"),
            ],
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

    def load_video_info(self):
        video = self.video_path.get().strip()
        if not video:
            messagebox.showwarning("Attenzione", "Seleziona prima un video.")
            return

        try:
            info = read_video_info(video)
        except VideoIOError as exc:
            messagebox.showerror("Errore", str(exc))
            return

        self.video_info_text.set(format_video_info(info))
        if not self.end_frame_var.get().strip() and info.frame_count > 0:
            self.end_frame_var.set(str(info.frame_count - 1))

    def start_export_thread(self):
        self.progress_var.set(0.0)
        self.status_var.set("Avvio export...")
        thread = threading.Thread(target=self.export_frames_worker, daemon=True)
        thread.start()

    def export_frames_worker(self):
        try:
            config = self._build_config_from_ui()
            report = export_frames(config, progress_callback=self._progress_callback)
            self.root.after(0, self.progress_var.set, 100.0)
            self.root.after(
                0,
                self.status_var.set,
                (
                    f"Completato. Esportati {report.exported_frames}/{report.requested_frames} frame "
                    f"in: {report.output_dir}"
                ),
            )
            self.root.after(0, lambda: messagebox.showinfo("Completato", self._build_report_message(report)))
        except (ValueError, ExportConfigError, VideoIOError) as exc:
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

    def _progress_callback(self, current: int, total: int, message: str):
        progress = 0.0 if total <= 0 else 100.0 * current / total
        self.root.after(0, self.progress_var.set, progress)
        self.root.after(0, self.status_var.set, message)

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


def main():
    root = tk.Tk()
    try:
        root.iconbitmap(default="")
    except Exception:
        pass
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass
    VideoToFramesApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
