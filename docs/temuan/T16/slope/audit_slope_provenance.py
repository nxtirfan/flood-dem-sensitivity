#!/usr/bin/env python3
"""Read-only provenance audit for the 30 frozen positive samples with SRTM slope >= 5°.

Run from any working directory with /tmp/t16-venv/bin/python. Writes only
docs/temuan/T16/slope/slope_points_audit.csv.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


def repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "Proposal Baru/Flood_DEM_Sensitivity_Notebook_v27_maskAOI.ipynb").exists():
            return parent
    raise FileNotFoundError("Cannot locate repository root")


ROOT = repo_root()
NOTEBOOK = ROOT / "Proposal Baru/Flood_DEM_Sensitivity_Notebook_v27_maskAOI.ipynb"
DELIVERY = ROOT / "Proposal Baru/v27_delivery/Analisis Flood DEM Susceptibility"
TRAINING = ROOT / "Proposal Baru/hasil_kaggle/training_sample_features.csv"
DELIVERY_TRAINING = DELIVERY / "outputs/training_sample_features.csv"
RAW = DELIVERY / "data/frozen/main/sample_main_raw.csv"
OUT = ROOT / "docs/temuan/T16/slope/slope_points_audit.csv"


def read(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def point_key(row: pd.Series) -> tuple[float, float]:
    return round(float(row["lon"]), 12), round(float(row["lat"]), 12)


def main() -> None:
    training = read(TRAINING)
    delivery_training = read(DELIVERY_TRAINING)
    raw = read(RAW)
    positive = training["flood"].astype(int).eq(1)
    high = pd.to_numeric(training["slope_srtm"], errors="coerce").ge(5)
    points = training.loc[positive & high].copy()

    # Match frozen raw rows by exact exported coordinates, not an assumed ID.
    raw_by_key: dict[tuple[float, float], list[tuple[int, pd.Series]]] = {}
    for position, (_, row) in enumerate(raw.iterrows(), start=2):
        raw_by_key.setdefault(point_key(row), []).append((position, row))

    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    nb_text = "\n".join(
        f"CELL {i + 1}\n{''.join(cell.get('source', []))}"
        for i, cell in enumerate(notebook["cells"])
    )
    raster_dir = DELIVERY / "data/rasters"
    raster_names = sorted(p.name for p in raster_dir.glob("*.tif"))
    slope_dem_rasters = [n for n in raster_names if "slope" in n.lower() or "dem" in n.lower()]

    # The CSV has no persistent sample ID; row numbers are locators only.
    output_rows = []
    for index, row in points.iterrows():
        position = int(index) + 2
        matches = raw_by_key.get(point_key(row), [])
        raw_position, raw_row = matches[0] if len(matches) == 1 else (None, None)
        raw_slope = float(raw_row["slope_srtm"]) if raw_row is not None else None
        sample_slope = float(row["slope_srtm"])
        output_rows.append({
            "locator_id": f"training_sample_features.csv:physical_line_{position}",
            "training_csv_physical_line_1based": position,
            "raw_main_csv_physical_line_1based": raw_position if raw_position is not None else "NA",
            "raw_coordinate_match_count": len(matches),
            "flood": int(row["flood"]),
            "lon": format(float(row["lon"]), ".15g"),
            "lat": format(float(row["lat"]), ".15g"),
            "coordinate_crs": "geographic degrees inferred from lon/lat columns; CRS not declared in CSV",
            "slope_srtm_training_export_deg": format(sample_slope, ".15g"),
            "slope_srtm_raw_frozen_deg": format(raw_slope, ".15g") if raw_slope is not None else "NA",
            "sample_vs_raw_slope_equal": raw_slope == sample_slope if raw_slope is not None else "BLOCKED",
            "slope_at_label_filter_deg": "NA_BLOCKED_no_saved_filter-intermediate_or_GEE_access",
            "label_filter_dem": "USGS/SRTMGL1_003 per canon notebook cell 22",
            "label_filter_rule": "slope < 5 degrees (cell 22; SLOPE_MAX_FOR_FLOOD=5 in cell 16)",
            "label_filter_crs_resolution_affine_resampling_mask": "NA_BLOCKED_not recorded in exported data; requires source GEE computation/assets",
            "predictor_source_raster_path": "NA_BLOCKED_no DEM or slope GeoTIFF in v27 raster delivery",
            "predictor_source_raster_slope_deg": "NA_BLOCKED_source slope raster absent",
            "predictor_source_crs_resolution_affine_resampling_mask": "NA_BLOCKED_source raster/grid metadata absent",
            "predictor_processing_grid_from_notebook": "EPSG:32749, nominal scale 30 m (cell 28 lines 33-36; shared stack reprojection cell 28 lines 82-84)",
            "predictor_resampling_method": "not explicitly set in notebook; cannot infer exact sampling kernel",
            "predictor_mask": "DEM clipped to ROI; exact per-pixel SRTM/ROI mask not exportable from available files",
            "available_raster_names": ";".join(raster_names),
            "matching_dem_or_slope_rasters": ";".join(slope_dem_rasters) if slope_dem_rasters else "NONE",
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output_rows[0]))
        writer.writeheader()
        writer.writerows(output_rows)

    # Report checks for reproducibility without writing outside the T16 slope directory.
    raw_equal = sum(r["sample_vs_raw_slope_equal"] is True for r in output_rows)
    raw_matched = sum(r["raw_coordinate_match_count"] == 1 for r in output_rows)
    point_cols = ["flood", "lon", "lat", "slope_srtm"]
    delivery_matches = sum(
        training.loc[points.index, c].reset_index(drop=True).equals(
            delivery_training.loc[points.index, c].reset_index(drop=True)
        ) for c in point_cols
    )
    print(f"training_rows={len(training)} positives={(training['flood'].astype(int) == 1).sum()}")
    print(f"candidate_count={len(points)} max_slope={points['slope_srtm'].max():.15g}")
    print(f"candidate_flood_coord_slope_columns_equal_in_delivery_export={delivery_matches}/{len(point_cols)}")
    print(f"candidate_raw_coordinate_matches={raw_matched}/{len(points)} raw_slope_equal={raw_equal}/{len(points)}")
    print(f"v27_raster_files={len(raster_names)} DEM_or_slope_rasters={len(slope_dem_rasters)}")
    print(f"notebook_cells={len(notebook['cells'])} has_label_filter={('slope_for_label.lt(SLOPE_MAX_FOR_FLOOD)' in nb_text)}")
    print(f"wrote={OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
