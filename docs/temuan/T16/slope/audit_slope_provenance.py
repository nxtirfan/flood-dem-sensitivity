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
    # CSV matching uses coordinates rounded to 12 decimal places; raw exact
    # numeric equality is checked and reported separately for each match.
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
    delivery_by_key: dict[tuple[float, float], list[pd.Series]] = {}
    for _, row in delivery_training.iterrows():
        delivery_by_key.setdefault(point_key(row), []).append(row)

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
        raw_lon_equal = float(row["lon"]) == float(raw_row["lon"]) if raw_row is not None else "BLOCKED"
        raw_lat_equal = float(row["lat"]) == float(raw_row["lat"]) if raw_row is not None else "BLOCKED"
        raw_flood_equal = int(row["flood"]) == int(raw_row["flood"]) if raw_row is not None else "BLOCKED"
        output_rows.append({
            "locator_id": f"training_sample_features.csv:physical_line_{position}",
            "locator_note": "physical CSV line only; source has no stable sample ID",
            "training_csv_physical_line_1based": position,
            "raw_main_csv_physical_line_1based": raw_position if raw_position is not None else "NA",
            "coordinate_match_method": "lon/lat rounded to 12 decimal places; exact numeric equality separately checked",
            "raw_coordinate_match_count": len(matches),
            "raw_lon_exact_equal": raw_lon_equal,
            "raw_lat_exact_equal": raw_lat_equal,
            "raw_flood_equal": raw_flood_equal,
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
            "filter_crs": "NA_BLOCKED_not recorded for evaluated slope image; source SRTM asset is USGS/SRTMGL1_003",
            "filter_nominal_resolution_m": "NA_BLOCKED_not explicitly set for filter slope calculation",
            "filter_affine": "NA_BLOCKED_filter-image grid transform unavailable",
            "filter_resampling": "no explicit override in label code; Earth Engine reprojection default is nearest neighbor when invoked, but actual implicit evaluation path at these points is unverified",
            "filter_mask": "filter slope/pixel mask at each point unavailable; flood mask also combines Sentinel-1 and permanent-water conditions",
            "predictor_source_raster_path": "NA_BLOCKED_no DEM or slope GeoTIFF in v27 raster delivery",
            "predictor_source_raster_slope_deg": "NA_BLOCKED_source slope raster absent",
            "predictor_crs_from_code": "EPSG:32749",
            "predictor_nominal_scale_m_from_code": 30,
            "predictor_affine": "NA_BLOCKED_source raster transform unavailable",
            "predictor_source_resolution_affine_resampling_mask": "source raster resolution/affine unavailable; per-point mask unavailable",
            "predictor_processing_grid_from_notebook": "EPSG:32749, nominal scale 30 m (cell 28 lines 33-36; shared stack reprojection cell 28 lines 82-84)",
            "predictor_resampling_method": "no explicit override in notebook; Earth Engine reprojection default is nearest neighbor when invoked, but actual implicit per-point reprojection/sampling path is unverified",
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
    raw_lon_equal = sum(r["raw_lon_exact_equal"] is True for r in output_rows)
    raw_lat_equal = sum(r["raw_lat_exact_equal"] is True for r in output_rows)
    raw_flood_equal = sum(r["raw_flood_equal"] is True for r in output_rows)
    point_cols = ["flood", "lon", "lat", "slope_srtm"]
    delivery_coordinate_matches = 0
    delivery_field_matches = {c: 0 for c in point_cols}
    for _, row in points.iterrows():
        matches = delivery_by_key.get(point_key(row), [])
        if len(matches) != 1:
            continue
        delivery_coordinate_matches += 1
        for column in point_cols:
            if row[column] == matches[0][column]:
                delivery_field_matches[column] += 1
    print(f"training_rows={len(training)} positives={(training['flood'].astype(int) == 1).sum()}")
    print(f"candidate_count={len(points)} max_slope={points['slope_srtm'].max():.15g}")
    print(f"candidate_delivery_coordinate_matches={delivery_coordinate_matches}/{len(points)}")
    print(f"candidate_delivery_flood_lon_lat_slope_matches={delivery_field_matches}")
    print(f"candidate_raw_coordinate_matches={raw_matched}/{len(points)} raw_slope_equal={raw_equal}/{len(points)}")
    print(f"candidate_raw_exact_lon_equal={raw_lon_equal}/{len(points)} exact_lat_equal={raw_lat_equal}/{len(points)} flood_equal={raw_flood_equal}/{len(points)}")
    if not (len(points) == 30 and raw_matched == raw_lon_equal == raw_lat_equal == raw_flood_equal == raw_equal == 30):
        raise AssertionError("Expected 30 uniquely matched points with exact lon/lat, flood, and slope equality")
    print(f"v27_raster_files={len(raster_names)} DEM_or_slope_rasters={len(slope_dem_rasters)}")
    print(f"notebook_cells={len(notebook['cells'])} has_label_filter={('slope_for_label.lt(SLOPE_MAX_FOR_FLOOD)' in nb_text)}")
    print(f"wrote={OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
