from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Literal

import cv2

ImageFormat = Literal["png", "jpg", "jpeg", "bmp", "tif", "tiff"]
NamingMode = Literal["source_index", "sequential"]
ProgressCallback = Callable[[int, int, str], None]


@dataclass(slots=True)
class ExportConfig:
    video_path: str
    output_dir: str
    image_format: ImageFormat = "png"
    prefix: str = "frame"
    start_frame: int = 0
    end_frame: int | None = None
    step: int = 1
    jpeg_quality: int = 95
    png_compression: int = 3
    resize_width: int | None = None
    resize_height: int | None = None
    grayscale: bool = False
    overwrite: bool = False
    naming_mode: NamingMode = "source_index"
    zero_padding: int = 5


@dataclass(slots=True)
class ExportReport:
    requested_frames: int
    exported_frames: int
    skipped_existing: int
    failed_reads: int
    failed_writes: int
    output_dir: str
    first_output: str | None = None
    last_output: str | None = None


class ExportConfigError(ValueError):
    pass


SUPPORTED_FORMATS = {"png", "jpg", "jpeg", "bmp", "tif", "tiff"}


def validate_config(config: ExportConfig) -> None:
    video_path = Path(config.video_path)
    if not video_path.is_file():
        raise ExportConfigError(f"Video non trovato: {video_path}")

    if config.image_format.lower() not in SUPPORTED_FORMATS:
        raise ExportConfigError(f"Formato non supportato: {config.image_format}")

    if config.start_frame < 0:
        raise ExportConfigError("start_frame deve essere >= 0")

    if config.end_frame is not None and config.end_frame < config.start_frame:
        raise ExportConfigError("end_frame deve essere >= start_frame")

    if config.step < 1:
        raise ExportConfigError("step deve essere >= 1")

    if not (0 <= config.jpeg_quality <= 100):
        raise ExportConfigError("jpeg_quality deve essere tra 0 e 100")

    if not (0 <= config.png_compression <= 9):
        raise ExportConfigError("png_compression deve essere tra 0 e 9")

    if (config.resize_width is None) != (config.resize_height is None):
        raise ExportConfigError(
            "resize_width e resize_height devono essere entrambi valorizzati oppure entrambi None"
        )

    if config.resize_width is not None and config.resize_width <= 0:
        raise ExportConfigError("resize_width deve essere > 0")

    if config.resize_height is not None and config.resize_height <= 0:
        raise ExportConfigError("resize_height deve essere > 0")

    if config.zero_padding < 1:
        raise ExportConfigError("zero_padding deve essere >= 1")

    if config.naming_mode not in {"source_index", "sequential"}:
        raise ExportConfigError(f"naming_mode non valido: {config.naming_mode}")



def get_video_frame_count(video_path: str) -> int:
    cap = cv2.VideoCapture(video_path)
    try:
        if not cap.isOpened():
            raise ExportConfigError(f"Impossibile aprire il video: {video_path}")
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if frame_count <= 0:
            raise ExportConfigError("Numero frame non valido o non disponibile")
        return frame_count
    finally:
        cap.release()



def build_target_indices(config: ExportConfig, frame_count: int) -> list[int]:
    end_frame = config.end_frame if config.end_frame is not None else frame_count - 1
    end_frame = min(end_frame, frame_count - 1)

    if config.start_frame >= frame_count:
        return []

    return list(range(config.start_frame, end_frame + 1, config.step))



def export_frames(
    config: ExportConfig,
    progress_callback: ProgressCallback | None = None,
) -> ExportReport:
    validate_config(config)

    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    frame_count = get_video_frame_count(config.video_path)
    target_indices = build_target_indices(config, frame_count)
    if not target_indices:
        return ExportReport(
            requested_frames=0,
            exported_frames=0,
            skipped_existing=0,
            failed_reads=0,
            failed_writes=0,
            output_dir=str(output_dir),
        )

    ext = normalize_extension(config.image_format)
    imwrite_params = build_imwrite_params(config, ext)
    padding = max(config.zero_padding, len(str(max(target_indices))))

    cap = cv2.VideoCapture(config.video_path)
    if not cap.isOpened():
        raise ExportConfigError(f"Impossibile aprire il video: {config.video_path}")

    exported = 0
    skipped_existing = 0
    failed_reads = 0
    failed_writes = 0
    first_output = None
    last_output = None

    try:
        for sequence_idx, source_idx in enumerate(target_indices, start=1):
            cap.set(cv2.CAP_PROP_POS_FRAMES, source_idx)
            ok, frame = cap.read()
            if not ok:
                failed_reads += 1
                if progress_callback is not None:
                    progress_callback(sequence_idx, len(target_indices), f"Lettura fallita al frame {source_idx}")
                continue

            frame = transform_frame(frame, config)
            output_name = build_output_name(
                prefix=config.prefix,
                source_idx=source_idx,
                sequence_idx=sequence_idx,
                ext=ext,
                padding=padding,
                naming_mode=config.naming_mode,
            )
            output_path = output_dir / output_name

            if output_path.exists() and not config.overwrite:
                skipped_existing += 1
                if progress_callback is not None:
                    progress_callback(sequence_idx, len(target_indices), f"Saltato esistente: {output_name}")
                continue

            success = cv2.imwrite(str(output_path), frame, imwrite_params)
            if not success:
                failed_writes += 1
                if progress_callback is not None:
                    progress_callback(sequence_idx, len(target_indices), f"Errore scrittura: {output_name}")
                continue

            exported += 1
            if first_output is None:
                first_output = str(output_path)
            last_output = str(output_path)

            if progress_callback is not None:
                progress_callback(sequence_idx, len(target_indices), f"Esportato: {output_name}")
    finally:
        cap.release()

    return ExportReport(
        requested_frames=len(target_indices),
        exported_frames=exported,
        skipped_existing=skipped_existing,
        failed_reads=failed_reads,
        failed_writes=failed_writes,
        output_dir=str(output_dir),
        first_output=first_output,
        last_output=last_output,
    )



def normalize_extension(image_format: str) -> str:
    fmt = image_format.lower()
    if fmt == "jpeg":
        return "jpg"
    if fmt == "tiff":
        return "tif"
    return fmt



def build_imwrite_params(config: ExportConfig, ext: str) -> list[int]:
    if ext == "jpg":
        return [cv2.IMWRITE_JPEG_QUALITY, config.jpeg_quality]
    if ext == "png":
        return [cv2.IMWRITE_PNG_COMPRESSION, config.png_compression]
    return []



def transform_frame(frame, config: ExportConfig):
    out = frame
    if config.grayscale:
        out = cv2.cvtColor(out, cv2.COLOR_BGR2GRAY)

    if config.resize_width is not None and config.resize_height is not None:
        out = cv2.resize(
            out,
            (config.resize_width, config.resize_height),
            interpolation=cv2.INTER_AREA,
        )
    return out



def build_output_name(
    prefix: str,
    source_idx: int,
    sequence_idx: int,
    ext: str,
    padding: int,
    naming_mode: NamingMode,
) -> str:
    if naming_mode == "sequential":
        idx = sequence_idx
    else:
        idx = source_idx
    return f"{prefix}_{idx:0{padding}d}.{ext}"
