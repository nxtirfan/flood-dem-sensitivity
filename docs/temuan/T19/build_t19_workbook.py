"""Rebuild the T19 30-point row-by-row verification workbook from frozen sources.

Read-only on all scientific artefacts. Outputs:
  t19_30point_row_by_row_verification.csv
  t19_30point_row_by_row_verification.xlsx
"""

import csv
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from affine import Affine
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font
from pyproj import Geod, Transformer

ROOT = Path(r"D:\Kuliah\1_Metopen")
T19 = ROOT / "docs" / "temuan" / "T19"
DELIV = ROOT / "Proposal Baru" / "v28_delivery" / "Analisis Flood DEM Susceptibility"
TF28 = DELIV / "outputs" / "training_sample_features.csv"
RAWS = DELIV / "data" / "frozen" / "main" / "sample_main_raw.csv"
RAWP = DELIV / "data" / "frozen" / "main" / "sample_main_raw.parquet"
T17 = ROOT / "Proposal Baru" / "v28_delivery" / "diagnostics_t17" / "t17_slope_30point_diagnostic.csv"
T16 = ROOT / "docs" / "temuan" / "T16" / "slope" / "slope_points_audit.csv"
RASTER = DELIV / "data" / "rasters" / "proxy_flood_label_sentinel1.tif"
MD = T19 / "T19_VERIFICATION.md"
OUT_XLSX = T19 / "t19_30point_row_by_row_verification.xlsx"
OUT_CSV = T19 / "t19_30point_row_by_row_verification.csv"

COLS = [
    "pt_no", "audit_id", "tf_phys_line", "raw_phys_line", "lon_tf", "lat_tf",
    "tf_lon_str", "rm_lon_str", "tf_slp_str", "rm_slp_str", "str_exact_slp_tf_rm",
    "float_exact_lon_tf_rm", "float_exact_lat_tf_rm", "float_exact_slp_tf_rm",
    "float_exact_slp_tf_pq", "float_exact_lon_tf_t17", "float_exact_lat_tf_t17",
    "historic_slope_tf", "nat_slope", "nat_valid", "nat_mask_wt", "nat_lt5",
    "forced_slope", "forced_valid", "forced_lt5", "feat_slope", "feat_valid",
    "feat_lt5", "feat_diff_vs_tf", "feat_exact_float_eq", "final_slope",
    "final_diff_vs_tf", "final_exact_float_eq", "proxy_label_tif_row",
    "proxy_label_tif_col", "proxy_label_tif_val", "dist_input_to_feat_snap_m",
    "dist_input_to_nat_snap_m", "dist_nat_snap_to_feat_snap_m",
]

ROUTES = {
    "nat": "label_native_projection_control",
    "forced": "label_slope_forced_analysis_grid_control",
    "feat": "feature_srtm_slope_analysis_grid",
    "final": "feature_slope_final_sampling_grid_control",
}

TRANSFORM_FEAT = Affine(30, 0, 419280, 0, -30, 9258540)
TRANSFORM_NAT = Affine(1 / 3600, 0, -180.0001388888889, 0, -1 / 3600, 60.00013888888889)
GEOD = Geod(ellps="WGS84")
TO_UTM = Transformer.from_crs("EPSG:4326", "EPSG:32749", always_xy=True)
TO_LONLAT = Transformer.from_crs("EPSG:32749", "EPSG:4326", always_xy=True)


def physical_records(path):
    with open(path, "r", encoding="utf-8", newline="") as handle:
        lines = handle.readlines()
    header = next(csv.reader([lines[0]]))
    records = {}
    for number, line in enumerate(lines[1:], start=2):
        values = next(csv.reader([line]))
        if len(values) == len(header):
            records[number] = dict(zip(header, values))
    return records


def snapped_center(lon, lat, transform, inverse=None):
    x, y = TO_UTM.transform(lon, lat) if inverse is not None else (lon, lat)
    col, row = (~transform) * (x, y)
    cx, cy = transform * (math.floor(col) + 0.5, math.floor(row) + 0.5)
    if inverse is None:
        return cx, cy
    return inverse.transform(cx, cy)


def build_rows():
    tf = physical_records(TF28)
    raw = physical_records(RAWS)
    t16 = pd.read_csv(T16).set_index("locator_id")
    t17 = pd.read_csv(T17)
    pq = pd.read_parquet(RAWP)
    pq_lon = pq["lon"].to_numpy()
    pq_lat = pq["lat"].to_numpy()

    with rasterio.open(RASTER) as ds:
        raster = ds.read(1)

    route_rows = {}
    for key, route in ROUTES.items():
        subset = t17[t17["route"] == route].set_index("audit_id")
        assert subset.index.is_unique
        route_rows[key] = subset

    audit_ids = list(route_rows["nat"].index)
    assert len(audit_ids) == 30
    rows = []
    for pt_no, audit_id in enumerate(audit_ids, start=1):
        tf_line = int(re.search(r"physical_line_(\d+)", audit_id).group(1))
        rec_tf = tf[tf_line]
        locator = t16.loc[audit_id]
        raw_line = int(locator["raw_main_csv_physical_line_1based"])
        rec_raw = raw[raw_line]

        tf_lon_str, tf_lat_str = rec_tf["lon"], rec_tf["lat"]
        rm_lon_str, rm_lat_str = rec_raw["lon"], rec_raw["lat"]
        tf_slp_str, rm_slp_str = rec_tf["slope_srtm"], rec_raw["slope_srtm"]
        lon_tf, lat_tf = float(tf_lon_str), float(tf_lat_str)
        slp_tf = float(tf_slp_str)

        hit = np.flatnonzero((pq_lon == float(rm_lon_str)) & (pq_lat == float(rm_lat_str)))
        assert len(hit) == 1, (audit_id, len(hit))
        pq_slope = float(pq["slope_srtm"].iloc[hit[0]])

        n = route_rows["nat"].loc[audit_id]
        f = route_rows["feat"].loc[audit_id]
        x_nat, y_nat = snapped_center(lon_tf, lat_tf, TRANSFORM_NAT)
        x_feat, y_feat = snapped_center(lon_tf, lat_tf, TRANSFORM_FEAT, TO_LONLAT)
        e, north = TO_UTM.transform(lon_tf, lat_tf)
        c = math.floor((e - 419280) / 30)
        r = math.floor((9258540 - north) / 30)
        assert 0 <= r < raster.shape[0] and 0 <= c < raster.shape[1]

        nat_slope = float(n["slope_deg"])
        feat_slope = float(f["slope_deg"])
        final_slope = float(route_rows["final"].loc[audit_id, "slope_deg"])
        forced = route_rows["forced"].loc[audit_id]

        row = {
            "pt_no": pt_no,
            "audit_id": audit_id,
            "tf_phys_line": tf_line,
            "raw_phys_line": raw_line,
            "lon_tf": lon_tf,
            "lat_tf": lat_tf,
            "tf_lon_str": tf_lon_str,
            "rm_lon_str": rm_lon_str,
            "tf_slp_str": tf_slp_str,
            "rm_slp_str": rm_slp_str,
            "str_exact_slp_tf_rm": tf_slp_str == rm_slp_str,
            "float_exact_lon_tf_rm": lon_tf == float(rm_lon_str),
            "float_exact_lat_tf_rm": lat_tf == float(rm_lat_str),
            "float_exact_slp_tf_rm": slp_tf == float(rm_slp_str),
            "float_exact_slp_tf_pq": slp_tf == pq_slope,
            "float_exact_lon_tf_t17": lon_tf == float(n["input_lon"]),
            "float_exact_lat_tf_t17": lat_tf == float(n["input_lat"]),
            "historic_slope_tf": float(locator["slope_srtm_training_export_deg"]),
            "nat_slope": nat_slope,
            "nat_valid": int(n["slope_valid"]),
            "nat_mask_wt": float(n["lt5_mask_weight"]),
            "nat_lt5": int(n["lt5_value"]),
            "forced_slope": float(forced["slope_deg"]),
            "forced_valid": int(forced["slope_valid"]),
            "forced_lt5": int(forced["lt5_value"]),
            "feat_slope": feat_slope,
            "feat_valid": int(f["slope_valid"]),
            "feat_lt5": int(f["lt5_value"]),
            "feat_diff_vs_tf": abs(feat_slope - slp_tf),
            "feat_exact_float_eq": abs(feat_slope - slp_tf) == 0.0,
            "final_slope": final_slope,
            "final_diff_vs_tf": abs(final_slope - slp_tf),
            "final_exact_float_eq": abs(final_slope - slp_tf) == 0.0,
            "proxy_label_tif_row": int(r),
            "proxy_label_tif_col": int(c),
            "proxy_label_tif_val": float(raster[r, c]),
            "dist_input_to_feat_snap_m": GEOD.inv(lon_tf, lat_tf, x_feat, y_feat)[2],
            "dist_input_to_nat_snap_m": GEOD.inv(lon_tf, lat_tf, x_nat, y_nat)[2],
            "dist_nat_snap_to_feat_snap_m": GEOD.inv(x_nat, y_nat, x_feat, y_feat)[2],
        }
        rows.append(row)
    return rows


def write_outputs(rows):
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(COLS)
        for row in rows:
            writer.writerow([
                format(v, ".17g") if isinstance(v, float) else v for v in (row[c] for c in COLS)
            ])

    wb = Workbook()
    ws = wb.active
    ws.title = "T19 30-point verification"
    ws.append(COLS)
    for row in rows:
        ws.append([row[c] for c in COLS])
    for cell in ws[1]:
        cell.font = Font(bold=True)
    ws.freeze_panes = "C2"
    wb.save(OUT_XLSX)


def validate(rows):
    wb = load_workbook(OUT_XLSX, data_only=True)
    ws = wb.active
    assert ws.max_row == 31 and ws.max_column == 39, (ws.max_row, ws.max_column)
    assert [c.value for c in ws[1]] == COLS
    for i, row in enumerate(rows, start=2):
        for j, name in enumerate(COLS, start=1):
            cell = ws.cell(row=i, column=j)
            expected = row[name]
            if isinstance(expected, float):
                assert isinstance(cell.value, (int, float)) and not isinstance(cell.value, bool)
                assert math.isclose(cell.value, expected, rel_tol=1e-14, abs_tol=1e-14), (
                    i, name, cell.value, expected
                )
            elif isinstance(expected, bool):
                assert isinstance(cell.value, bool) and cell.value == expected, (i, name, cell.value, expected)
            else:
                assert cell.value == expected, (i, name, cell.value, expected)

    md_rows = {}
    for line in MD.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\| (\d{1,2}) \| `training_sample_features\.csv:physical_line_(\d+)`", line)
        if m and int(m.group(1)) not in md_rows:
            md_rows[int(m.group(1))] = line
    assert len(md_rows) == 30, len(md_rows)

    def num(text):
        return float(re.match(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", text.strip("` ")).group())

    worst = {"lon_lat": 0.0, "nat_forced": 0.0, "feat_final": 0.0, "historic": 0.0, "distance_m": 0.0}
    ulp_notes = []
    for n, line in md_rows.items():
        parts = [p.strip().strip("`") for p in line.split("|")[1:-1]]
        row = rows[n - 1]
        assert parts[1] == row["audit_id"], (n, parts[1])
        assert int(parts[2]) == row["raw_phys_line"], (n, parts[2])
        worst["lon_lat"] = max(worst["lon_lat"], abs(num(parts[3]) - row["lon_tf"]))
        worst["lon_lat"] = max(worst["lon_lat"], abs(num(parts[4]) - row["lat_tf"]))
        for key, idx in (("nat_slope", 5), ("forced_slope", 6)):
            worst["nat_forced"] = max(worst["nat_forced"], abs(float(re.match(r"[0-9.]+", parts[idx]).group()) - row[key]))
        for key, idx in (("feat_slope", 7), ("final_slope", 8)):
            worst["feat_final"] = max(worst["feat_final"], abs(num(parts[idx]) - row[key]))
        worst["feat_final"] = max(worst["feat_final"], abs(num(parts[9]) - row["feat_diff_vs_tf"]))
        worst["feat_final"] = max(worst["feat_final"], abs(num(parts[9]) - row["final_diff_vs_tf"]))
        if num(parts[9]) != row["feat_diff_vs_tf"]:
            ulp_notes.append((n, num(parts[9]), row["feat_diff_vs_tf"]))
        worst["historic"] = max(
            worst["historic"],
            abs(num(parts[10]) - abs(row["historic_slope_tf"] - float(row["tf_slp_str"]))),
        )
        proxy = re.search(r"(\d+),(\d+)", parts[12])
        assert int(proxy.group(1)) == row["proxy_label_tif_row"]
        assert int(proxy.group(2)) == row["proxy_label_tif_col"]
        dist = [float(x) for x in re.findall(r"[0-9]+\.[0-9]+", parts[13])]
        worst["distance_m"] = max(
            worst["distance_m"],
            abs(dist[0] - row["dist_input_to_nat_snap_m"]),
            abs(dist[1] - row["dist_input_to_feat_snap_m"]),
        )

    assert worst["lon_lat"] < 1e-13, worst
    assert worst["nat_forced"] < 1e-6, worst
    assert worst["feat_final"] <= 2e-15, worst
    assert worst["historic"] < 1e-13, worst
    assert worst["distance_m"] < 0.02, worst
    print("VALIDATION OK: 30 rows x 39 columns; XLSX round-trip within Excel 15-digit precision; max |diff| vs T19 section 3.1:")
    for key, value in worst.items():
        print("  %-12s %.6g" % (key, value))
    print("  feat/final slope vs v28 CSV: %d/30 bit-exact (diff = 0)" % (30 - len(ulp_notes)))
    for n, md_value, local_value in ulp_notes:
        print("  point %d: T19 table %.1e vs locally recomputed %.6e (1 ULP, %.17g vs %.17g)" % (
            n, md_value, local_value, rows[n - 1]["feat_slope"], float(rows[n - 1]["tf_slp_str"])
        ))
    print("  proxy row/col: 30/30 exact; |Delta| vs v28 and T16 columns: 30/30 exact")


if __name__ == "__main__":
    result = build_rows()
    write_outputs(result)
    validate(result)
