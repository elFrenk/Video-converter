from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2


@dataclass(slots=True)
class PreviewFrame:
    image_bgr: object
    width: int
    height: int
    frame_index: int
    video_path: str


class PreviewError(ValueError):
    pass



def read_preview_frame(video_path: str, frame_index: int = 0) -> PreviewFrame:
    path = Path(video_path)
    if not path.exists() or not path.is_file():
        raise PreviewError(f"File video non trovato: {path}")

    cap = cv2.VideoCapture(str(path))
    try:
        if not cap.isOpened():
            raise PreviewError(f"Impossibile aprire il video: {path}")

        if frame_index < 0:
            raise PreviewError("frame_index deve essere >= 0")

        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ok, frame = cap.read()
        if not ok or frame is None:
            raise PreviewError(f"Impossibile leggere il frame {frame_index}")

        height, width = frame.shape[:2]
        return PreviewFrame(
            image_bgr=frame,
            width=width,
            height=height,
            frame_index=frame_index,
            video_path=str(path),
        )
    finally:
        cap.release()



def resize_for_preview(image_bgr, max_width: int = 720, max_height: int = 420):
    if max_width <= 0 or max_height <= 0:
        raise PreviewError("max_width e max_height devono essere > 0")

    h, w = image_bgr.shape[:2]
    scale = min(max_width / w, max_height / h, 1.0)
    new_w = max(1, int(round(w * scale)))
    new_h = max(1, int(round(h * scale)))

    if new_w == w and new_h == h:
        return image_bgr

    return cv2.resize(image_bgr, (new_w, new_h), interpolation=cv2.INTER_AREA)
