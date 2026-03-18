from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2


@dataclass(slots=True)
class VideoInfo:
    path: str
    filename: str
    width: int
    height: int
    fps: float
    frame_count: int
    duration_seconds: float
    is_openable: bool


class VideoIOError(ValueError):
    pass


SUPPORTED_VIDEO_EXTENSIONS = {
    ".mp4",
    ".avi",
    ".mov",
    ".mkv",
    ".wmv",
    ".m4v",
    ".mpg",
    ".mpeg",
}



def validate_video_path(video_path: str) -> Path:
    path = Path(video_path)
    if not path.exists():
        raise VideoIOError(f"File video non trovato: {path}")
    if not path.is_file():
        raise VideoIOError(f"Il percorso non è un file: {path}")
    return path



def has_supported_extension(video_path: str) -> bool:
    return Path(video_path).suffix.lower() in SUPPORTED_VIDEO_EXTENSIONS



def can_open_video(video_path: str) -> bool:
    cap = cv2.VideoCapture(video_path)
    try:
        return bool(cap.isOpened())
    finally:
        cap.release()



def read_video_info(video_path: str) -> VideoInfo:
    path = validate_video_path(video_path)

    cap = cv2.VideoCapture(str(path))
    try:
        if not cap.isOpened():
            raise VideoIOError(f"Impossibile aprire il video: {path}")

        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = float(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        if frame_count < 0:
            raise VideoIOError("Numero frame non valido")
        if width <= 0 or height <= 0:
            raise VideoIOError("Risoluzione video non valida")

        duration_seconds = frame_count / fps if fps > 0 else 0.0

        return VideoInfo(
            path=str(path),
            filename=path.name,
            width=width,
            height=height,
            fps=fps,
            frame_count=frame_count,
            duration_seconds=duration_seconds,
            is_openable=True,
        )
    finally:
        cap.release()



def build_default_output_dir(video_path: str) -> str:
    path = validate_video_path(video_path)
    return str(path.with_suffix("")) + "_frames"



def format_video_info(info: VideoInfo) -> str:
    fps_text = f"{info.fps:.3f}" if info.fps > 0 else "non disponibile"
    duration_text = f"{info.duration_seconds:.2f} s"
    return (
        f"File: {info.filename}\n"
        f"Risoluzione: {info.width} x {info.height}\n"
        f"FPS: {fps_text}\n"
        f"Numero frame: {info.frame_count}\n"
        f"Durata stimata: {duration_text}"
    )



def suggest_end_frame(video_path: str) -> int:
    info = read_video_info(video_path)
    if info.frame_count <= 0:
        raise VideoIOError("Il video non contiene frame utilizzabili")
    return info.frame_count - 1
