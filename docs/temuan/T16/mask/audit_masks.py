#!/usr/bin/env python3
"""Recompute raster metadata, risk-class areas/transitions, and mask effects.

Run from the repository root with /tmp/t16-venv/bin/python. Outputs stay beside
this script; the source rasters and frozen tables are read-only.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import zipfile
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio

ROOT = Path(__file__).resolve().parents[4]
DELIVERY = ROOT / "Proposal Baru/v27_delivery/Analisis Flood DEM Susceptibility"
ACTIVE = DELIVERY / "data/rasters"
BACKUP = DELIVERY / "data/rasters_backup_unmasked"
OLD = ROOT / "Proposal Baru/v27_delivery/old_Analisis Flood DEM Susceptibility/data/rasters"
OUT = Path(__file__).resolve().parent
DEM = ("srtm", "glo30", "aw3d30")
PAIRS = (("srtm", "glo30"), ("srtm", "aw3d30"), ("glo30", "aw3d30"))
CLASSES = range(1, 6)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def role(path: Path) -> str:
    if path.parent == ACTIVE:
        return "active_v27_masked"
    if path.parent == BACKUP:
        return "backup_unmasked_pre_surgery"
    if path.parent == OLD:
        return "old_delivery"
    return "other"


def write_rows(path: Path, rows: list[dict]) -> None:
    if rows:
        pd.DataFrame(rows).to_csv(path, index=False)
        return
    empty_headers = {
        "raster_exact_duplicates.csv": ["sha256", "n_paths", "paths"],
        "geometry_candidates.csv": ["container", "member", "candidate_type", "size"],
        "embedded_geometry_json_candidates.csv": ["container", "member", "marker"],
    }
    pd.DataFrame(columns=empty_headers.get(path.name, [])).to_csv(path, index=False)


def grid_key(ds):
    return (ds.width, ds.height, ds.crs.to_string() if ds.crs else None,
            tuple(ds.transform))


def valid_values(ds):
    arr = ds.read(1)
    valid = ds.dataset_mask() > 0
    if np.issubdtype(arr.dtype, np.floating):
        valid &= np.isfinite(arr)
    return arr, valid


def main():
    all_tifs = sorted((ROOT / "Proposal Baru/v27_delivery").rglob("*.tif"))
    metadata, arrays = [], {}
    hashes: dict[str, list[str]] = {}
    for p in all_tifs:
        with rasterio.open(p) as ds:
            arr, valid = valid_values(ds)
            counts = Counter(arr[valid].tolist()) if p.parent in (ACTIVE, OLD) else Counter()
            info = {
                "path": p.relative_to(ROOT).as_posix(), "role": role(p),
                "name": p.name, "sha256": sha256(p), "width": ds.width,
                "height": ds.height, "bands": ds.count,
                "dtype": ds.dtypes[0], "crs": ds.crs.to_string() if ds.crs else "",
                "transform": json.dumps(tuple(ds.transform)),
                "bounds": json.dumps(tuple(ds.bounds)),
                "pixel_width": ds.transform.a, "pixel_height": ds.transform.e,
                "nodata": ds.nodata, "valid_pixels_dataset_mask": int(valid.sum()),
                "masked_pixels_dataset_mask": int(valid.size - valid.sum()),
                "unique_valid_values": len(counts) if counts else "not_counted",
                "value_counts_if_integer_categories": json.dumps(
                    {str(k): v for k, v in sorted(counts.items())}
                ) if counts and len(counts) <= 16 else "",
            }
            metadata.append(info)
            hashes.setdefault(info["sha256"], []).append(info["path"])
            if p.parent in (ACTIVE, BACKUP, OLD):
                arrays[(p.parent, p.name)] = (arr, valid, grid_key(ds))
    write_rows(OUT / "raster_inventory.csv", metadata)

    duplicate_rows = [{"sha256": h, "n_paths": len(paths), "paths": " | ".join(paths)}
                      for h, paths in hashes.items() if len(paths) > 1]
    write_rows(OUT / "raster_exact_duplicates.csv", duplicate_rows)

    active_grid_rows = []
    keys = {}
    for p in sorted(ACTIVE.glob("*.tif")):
        _, _, k = arrays[(ACTIVE, p.name)]
        keys[p.name] = k
        active_grid_rows.append({"path": p.relative_to(ROOT).as_posix(), "grid_key": json.dumps(k)})
    write_rows(OUT / "active_grid_signatures.csv", active_grid_rows)

    area_rows, mask_rows = [], []
    risk = {}
    for dem in DEM:
        name = f"risk_class_{dem}.tif"
        arr, valid, _ = arrays[(ACTIVE, name)]
        cls_valid = valid & np.isin(arr, list(CLASSES))
        risk[dem] = (arr, cls_valid)
        for cl in CLASSES:
            n = int((cls_valid & (arr == cl)).sum())
            area_rows.append({"dem": dem, "class": cl, "pixels": n,
                              "pixel_area_m2": 900, "planar_area_km2": n * .0009,
                              "domain_pixels": int(cls_valid.sum()),
                              "domain_area_km2": int(cls_valid.sum()) * .0009,
                              "denominator": "pixels valid and class in 1..5 in this DEM raster"})
    write_rows(OUT / "class_area_local.csv", area_rows)

    transition_rows = []
    agreement_checks = []
    for left, right in PAIRS:
        la, lm = risk[left]; ra, rm = risk[right]
        common = lm & rm
        mat = np.zeros((5, 5), dtype=np.int64)
        for i, lc in enumerate(CLASSES):
            for j, rc in enumerate(CLASSES):
                mat[i, j] = int((common & (la == lc) & (ra == rc)).sum())
        den = int(common.sum())
        agr, agr_valid, _ = arrays[(ACTIVE, f"agreement_{left}_vs_{right}.tif")]
        raster_yes = agr_valid & (agr == 1)
        matrix_yes = int(np.trace(mat))
        agreement_checks.append({
            "pair": f"{left}_vs_{right}", "shared_class_valid_pixels": den,
            "matrix_agree_pixels": matrix_yes,
            "matrix_agreement_percent": 100 * matrix_yes / den if den else np.nan,
            "stored_agreement_valid_pixels": int(agr_valid.sum()),
            "stored_agreement_true_pixels": int(raster_yes.sum()),
            "stored_agreement_percent": 100 * raster_yes.sum() / agr_valid.sum() if agr_valid.any() else np.nan,
            "mask_difference_pixels": abs(int(agr_valid.sum()) - den),
            "agreement_true_difference_pixels": abs(int(raster_yes.sum()) - matrix_yes),
            "denominator": "shared valid class rasters vs agreement raster valid domain",
        })
        for i, lc in enumerate(CLASSES):
            row_n = int(mat[i].sum())
            for j, rc in enumerate(CLASSES):
                n = int(mat[i, j])
                transition_rows.append({
                    "from_dem": left, "to_dem": right, "from_class": lc,
                    "to_class": rc, "pixels": n, "shared_valid_domain_pixels": den,
                    "row_class_denominator_pixels": row_n,
                    "share_of_shared_domain": n / den if den else np.nan,
                    "row_percent": 100 * n / row_n if row_n else np.nan,
                    "overall_agreement_diagonal": int(np.trace(mat)),
                    "overall_agreement_percent": 100 * np.trace(mat) / den if den else np.nan,
                    "domain": "intersection of both active class rasters valid and values 1..5",
                })
    write_rows(OUT / "agreement_transition_local.csv", transition_rows)
    write_rows(OUT / "agreement_raster_check.csv", agreement_checks)

    for name in sorted(p.name for p in BACKUP.glob("*.tif")):
        if (ACTIVE, name) not in arrays:
            continue
        a, av, ak = arrays[(ACTIVE, name)]
        b, bv, bk = arrays[(BACKUP, name)]
        same_grid = ak == bk and a.shape == b.shape
        if not same_grid:
            mask_rows.append({"name": name, "comparison": "not_comparable_grid_mismatch",
                              "active_valid": int(av.sum()), "backup_valid": int(bv.sum())})
            continue
        common = av & bv
        eq = np.equal(a[common], b[common])
        mask_rows.append({
            "name": name, "comparison": "active_vs_backup_unmasked",
            "active_valid": int(av.sum()), "backup_valid": int(bv.sum()),
            "active_invalid_backup_valid": int((~av & bv).sum()),
            "active_valid_backup_invalid": int((av & ~bv).sum()),
            "common_valid": int(common.sum()),
            "unequal_values_common_valid": int((~eq).sum()),
            "max_abs_value_delta_common_valid": float(np.max(np.abs(
                a[common].astype("float64") - b[common].astype("float64")
            ))) if common.any() else np.nan,
            "same_grid": True,
            "limit": "backup raster is not an independent AOI geometry",
        })
    write_rows(OUT / "mask_effect_backup.csv", mask_rows)

    # Compare frozen GEE tables and local output copies with independently
    # recomputed counts. Identical table copies are reported as copies, not
    # independent replication.
    gee_dir = DELIVERY / "data/gee_tables"
    output_dir = DELIVERY / "outputs"
    compare_rows = []
    for tabname in ["area_per_risk_class_km2.csv", *(f"transition_{a}_vs_{b}.csv" for a, b in PAIRS)]:
        gpath, opath = gee_dir / tabname, output_dir / tabname
        if not gpath.exists() or not opath.exists():
            compare_rows.append({"table": tabname, "status": "missing table"})
            continue
        gee, out = pd.read_csv(gpath), pd.read_csv(opath)
        compare_rows.append({"table": tabname, "status": "GEE table equals local output CSV" if gee.equals(out) else "GEE/local CSV differs",
                             "gee_csv_sha256": sha256(gpath), "output_csv_sha256": sha256(opath),
                             "tables_value_equal": gee.equals(out)})
        if tabname.startswith("area_"):
            for _, row in gee.iterrows():
                cl = int(row["risk_class"])
                for dem in DEM:
                    local = next(x["planar_area_km2"] for x in area_rows if x["dem"] == dem and x["class"] == cl)
                    compare_rows.append({"table": tabname, "metric": "area", "dem": dem, "class": cl,
                                         "gee_csv_value": float(row[dem]), "local_raster_planar_km2": local,
                                         "gee_minus_local_km2": float(row[dem]) - local,
                                         "gee_csv_domain_semantics": "as exported; source reduction code must define pixel weighting/geometry"})
        else:
            left, right = re.match(r"transition_(.+)_vs_(.+)\.csv", tabname).groups()
            mat = pd.read_csv(gpath, index_col=0)
            active_mat = {(int(x["from_class"]), int(x["to_class"])): int(x["pixels"])
                          for x in transition_rows if x["from_dem"] == left and x["to_dem"] == right}
            for lc in CLASSES:
                for rc in CLASSES:
                    gee_n = int(mat.loc[str(lc), str(rc)] if str(lc) in mat.index else mat.loc[lc, str(rc)])
                    local_n = active_mat[(lc, rc)]
                    compare_rows.append({"table": tabname, "metric": "transition_pixels", "from_class": lc,
                                         "to_class": rc, "gee_csv_value": gee_n,
                                         "local_shared_mask_pixels": local_n, "gee_minus_local_pixels": gee_n-local_n})
    write_rows(OUT / "gee_vs_local.csv", compare_rows)

    # Search for possible independent vector geometries, including archive
    # members, and extract relevant AOI/reduction source locations from notebook.
    candidates = []
    vector_ext = {".shp", ".geojson", ".gpkg", ".kml", ".kmz", ".wkt"}
    embedded_json = []
    parquet_meta = []
    for p in ROOT.rglob("*"):
        if not p.is_file() or ".git" in p.parts or ".hoplite" in p.parts:
            continue
        if p.suffix.lower() in vector_ext:
            candidates.append({"container": p.relative_to(ROOT).as_posix(), "member": "",
                               "candidate_type": p.suffix.lower(), "size": p.stat().st_size})
        elif p.suffix.lower() == ".zip":
            try:
                with zipfile.ZipFile(p) as z:
                    for item in z.infolist():
                        if Path(item.filename).suffix.lower() in vector_ext:
                            candidates.append({"container": p.relative_to(ROOT).as_posix(),
                                               "member": item.filename, "candidate_type": "archive_member",
                                               "size": item.file_size})
                        elif Path(item.filename).suffix.lower() in {".json", ".geojson"} and item.file_size < 20_000_000:
                            raw = z.read(item).decode("utf-8", errors="ignore")
                            if re.search(r'"type"\s*:\s*"(FeatureCollection|Feature|Polygon|MultiPolygon)"', raw):
                                embedded_json.append({"container": p.relative_to(ROOT).as_posix(),
                                                      "member": item.filename, "marker": "GeoJSON geometry type"})
            except zipfile.BadZipFile:
                pass
        elif p.suffix.lower() == ".json" and p.stat().st_size < 20_000_000:
            try:
                raw = p.read_text(encoding="utf-8", errors="ignore")
                if re.search(r'"type"\s*:\s*"(FeatureCollection|Feature|Polygon|MultiPolygon)"', raw):
                    embedded_json.append({"container": p.relative_to(ROOT).as_posix(),
                                          "member": "", "marker": "GeoJSON geometry type"})
            except OSError:
                pass
        elif p.suffix.lower() == ".parquet":
            raw = p.read_bytes().decode("utf-8", errors="ignore")
            fields = sorted(set(re.findall(r'"name"\s*:\s*"([^"]+)"', raw)))
            geom_fields = [f for f in fields if re.search(r"geom|wkt|geojson|shape|polygon", f, re.I)]
            parquet_meta.append({"path": p.relative_to(ROOT).as_posix(),
                                 "geometry_named_fields": "|".join(geom_fields),
                                 "lat_field": "lat" in fields, "lon_field": "lon" in fields,
                                 "review_note": "sample coordinate fields are not an independent AOI boundary"})
    write_rows(OUT / "geometry_candidates.csv", candidates)
    write_rows(OUT / "embedded_geometry_json_candidates.csv", embedded_json)
    write_rows(OUT / "parquet_geometry_metadata.csv", parquet_meta)

    notebook_paths = [ROOT / "Proposal Baru/Flood_DEM_Sensitivity_Notebook_v27_maskAOI.ipynb",
                      ROOT / "Proposal Baru/v27_delivery/Flood_DEM_Sensitivity_Notebook_v27_maskAOI.ipynb"]
    evidence = []
    for npth in notebook_paths:
        if not npth.exists():
            continue
        nb = json.loads(npth.read_text(encoding="utf-8"))
        for ci, cell in enumerate(nb.get("cells", [])):
            source = "".join(cell.get("source", []))
            lines = source.splitlines()
            for li, line in enumerate(lines, 1):
                if re.search(r"AOI|pixelArea|reduceRegion|reduceRegions|area_per_risk|transition_|\.geometry\(|filterBounds|clip\(|ROI_MODE|SURROUNDING_RECTANGLE|FAO/GAUL", line, re.I):
                    evidence.append({"notebook": npth.relative_to(ROOT).as_posix(), "cell": ci,
                                     "line": li, "text": line.strip()[:500]})
    write_rows(OUT / "notebook_aoi_statistics_refs.csv", evidence)

    print(f"raster inventory={len(metadata)}; active={sum(x['role']=='active_v27_masked' for x in metadata)}; "
          f"backup={sum(x['role']=='backup_unmasked_pre_surgery' for x in metadata)}; "
          f"old={sum(x['role']=='old_delivery' for x in metadata)}")
    print("active grids unique:", len(set(keys.values())))
    for row in area_rows:
        if row["class"] == 1:
            print("domain", row["dem"], row["domain_pixels"], row["domain_area_km2"])
    for left, right in PAIRS:
        rows = [x for x in transition_rows if x["from_dem"] == left and x["to_dem"] == right]
        print("agreement", left, right, rows[0]["shared_valid_domain_pixels"], rows[0]["overall_agreement_percent"])
    print("geometry vector/archive candidates:", len(candidates), "; embedded GeoJSON candidates:",
          len(embedded_json), "; Parquet schemas reviewed:", len(parquet_meta), "; notebook refs:", len(evidence))


if __name__ == "__main__":
    main()
