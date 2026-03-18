from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from frame_exporter import ExportConfig, ExportReport, export_frames, get_video_frame_count

PairMode = Literal["consecutive", "stride", "custom_step"]
NamingMode = Literal["source_index", "sequential"]


@dataclass(slots=True)
class PairExportConfig:
    video_path: str
    output_dir: str
    image_format: str = "png"
    prefix: str = "pair"
    start_frame: int = 0
    end_frame: int | None = None
    pair_mode: PairMode = "consecutive"
    pair_step: int = 1
    pair_spacing: int = 1
    jpeg_quality: int = 95
    png_compression: int = 3
    resize_width: int | None = None
    resize_height: int | None = None
    grayscale: bool = False
    overwrite: bool = False
    naming_mode: NamingMode = "sequential"
    zero_padding: int = 5
    create_subfolders: bool = True


@dataclass(slots=True)
class PairDefinition:
    first_index: int
    second_index: int
    pair_number: int


@dataclass(slots=True)
class PairExportReport:
    total_pairs: int
    exported_pairs: int
    output_dir: str
    pair_reports: list[tuple[PairDefinition, ExportReport, ExportReport]]


class PairExportError(ValueError):
    pass



def build_pairs(config: PairExportConfig) -> list[PairDefinition]:
    if config.pair_step < 1:
        raise PairExportError("pair_step deve essere >= 1")
    if config.pair_spacing < 1:
        raise PairExportError("pair_spacing deve essere >= 1")

    frame_count = get_video_frame_count(config.video_path)
    end_frame = config.end_frame if config.end_frame is not None else frame_count - 1
    end_frame = min(end_frame, frame_count - 1)

    pairs: list[PairDefinition] = []
    pair_number = 1

    if config.start_frame >= frame_count:
        return pairs

    if config.pair_mode == "consecutive":
        i = config.start_frame
        while i + 1 <= end_frame:
            pairs.append(PairDefinition(i, i + 1, pair_number))
            pair_number += 1
            i += 2
    elif config.pair_mode == "stride":
        i = config.start_frame
        while i + config.pair_spacing <= end_frame:
            pairs.append(PairDefinition(i, i + config.pair_spacing, pair_number))
            pair_number += 1
            i += config.pair_spacing
    elif config.pair_mode == "custom_step":
        i = config.start_frame
        while i + config.pair_spacing <= end_frame:
            pairs.append(PairDefinition(i, i + config.pair_spacing, pair_number))
            pair_number += 1
            i += config.pair_step
    else:
        raise PairExportError(f"pair_mode non valido: {config.pair_mode}")

    return pairs



def export_pairs(config: PairExportConfig) -> PairExportReport:
    pairs = build_pairs(config)
    output_root = Path(config.output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    pair_reports: list[tuple[PairDefinition, ExportReport, ExportReport]] = []
    exported_pairs = 0

    for pair in pairs:
        if config.create_subfolders:
            pair_dir = output_root / f"{config.prefix}_{pair.pair_number:0{config.zero_padding}d}"
        else:
            pair_dir = output_root

        first_prefix = f"{config.prefix}_A"
        second_prefix = f"{config.prefix}_B"

        first_cfg = ExportConfig(
            video_path=config.video_path,
            output_dir=str(pair_dir),
            image_format=config.image_format,
            prefix=first_prefix,
            start_frame=pair.first_index,
            end_frame=pair.first_index,
            step=1,
            jpeg_quality=config.jpeg_quality,
            png_compression=config.png_compression,
            resize_width=config.resize_width,
            resize_height=config.resize_height,
            grayscale=config.grayscale,
            overwrite=config.overwrite,
            naming_mode=config.naming_mode,
            zero_padding=config.zero_padding,
        )

        second_cfg = ExportConfig(
            video_path=config.video_path,
            output_dir=str(pair_dir),
            image_format=config.image_format,
            prefix=second_prefix,
            start_frame=pair.second_index,
            end_frame=pair.second_index,
            step=1,
            jpeg_quality=config.jpeg_quality,
            png_compression=config.png_compression,
            resize_width=config.resize_width,
            resize_height=config.resize_height,
            grayscale=config.grayscale,
            overwrite=config.overwrite,
            naming_mode=config.naming_mode,
            zero_padding=config.zero_padding,
        )

        first_report = export_frames(first_cfg)
        second_report = export_frames(second_cfg)

        if first_report.exported_frames == 1 and second_report.exported_frames == 1:
            exported_pairs += 1

        pair_reports.append((pair, first_report, second_report))

    return PairExportReport(
        total_pairs=len(pairs),
        exported_pairs=exported_pairs,
        output_dir=str(output_root),
        pair_reports=pair_reports,
    )
