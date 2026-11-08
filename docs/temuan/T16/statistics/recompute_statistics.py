#!/usr/bin/env python3
"""Recompute frozen v27 OOF Moran, raster Moran-I, and block-bootstrap diagnostics.

Read-only inputs: notebook-derived CSVs, frozen prediction CSV copies, and
probability GeoTIFFs. Outputs are restricted to this script's directory.
"""
from __future__ import annotations

import hashlib
import importlib.util
import importlib.metadata
import json
import platform
from pathlib import Path
import re
import sys

import numpy as np
import pandas as pd
import rasterio
import scipy
import sklearn
from rasterio.warp import transform
from sklearn.metrics import roc_auc_score

sys.dont_write_bytecode = True


ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
PROJECT = ROOT / "Proposal Baru"
DELIVERY = PROJECT / "v27_delivery/Analisis Flood DEM Susceptibility"
OUTPUTS = DELIVERY / "outputs"
RASTERS = DELIVERY / "data/rasters"
BACKUP = DELIVERY / "data/rasters_backup_unmasked"
DEM_NAMES = ("srtm", "glo30", "aw3d30")
POINT_PREDICTION_FILES = {
    "hasil_kaggle": PROJECT / "hasil_kaggle/spatial_cv_test_predictions.csv",
    "v27_delivery": OUTPUTS / "spatial_cv_test_predictions.csv",
}
BOOTSTRAP_FILES = {
    "hasil_kaggle": PROJECT / "hasil_kaggle/spatial_cv_delta_auc_bootstrap.csv",
    "v27_delivery": OUTPUTS / "spatial_cv_delta_auc_bootstrap.csv",
}
OOF_POINTS = OUTPUTS / "moran_oof_points.csv"
OOF_STORED = OUTPUTS / "moran_oof_global.csv"
MAP_STORED = OUTPUTS / "moran_prob_map_global.csv"
NOTEBOOK = PROJECT / "Flood_DEM_Sensitivity_Notebook_v27_maskAOI.ipynb"
MANIFEST = DELIVERY / "data/manifest.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def source_moran_module():
    """Load the frozen Moran utility with its notebook-provided NumPy global."""
    source = PROJECT / "v27_delivery/uji_offline/cells_baru/moran_utils.py"
    spec = importlib.util.spec_from_file_location("frozen_v27_moran_utils", source)
    module = importlib.util.module_from_spec(spec)
    module.np = np
    spec.loader.exec_module(module)
    return module


def read_csv_checked(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def reconstruct_oof(pred: pd.DataFrame, points: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    required = {"fold", "config", "block", "y_true", "proba"}
    if not required.issubset(pred.columns):
        raise ValueError(f"Prediction CSV missing {required - set(pred.columns)}")
    if not {"lon", "lat", "block", "fold", "y"}.issubset(points.columns):
        raise ValueError("moran_oof_points.csv lacks the coordinate/label fields")
    points = points.reset_index(drop=True).copy()
    points["fold"] = points["fold"].astype(int)
    checks = []
    probs = {name: np.full(len(points), np.nan) for name in DEM_NAMES}
    for fold in sorted(points["fold"].unique()):
        idx = np.flatnonzero(points["fold"].to_numpy() == fold)
        target = points.iloc[idx]
        for dem in DEM_NAMES:
            rows = pred[(pred.fold.astype(int) == fold) & (pred.config == dem)]
            align = (len(rows) == len(idx)
                     and np.array_equal(rows.y_true.to_numpy(), target.y.to_numpy())
                     and np.array_equal(rows.block.to_numpy(), target.block.to_numpy()))
            checks.append({"check": "fold_label_block_order", "source": dem,
                           "fold": int(fold), "n_points": len(idx),
                           "n_predictions": len(rows), "pass": bool(align),
                           "max_abs_probability_delta": (
                               float(np.max(np.abs(rows.proba.to_numpy() -
                                                   target[f"oof_prob_{dem}"].to_numpy())))
                               if len(rows) == len(idx) else np.nan)})
            if not align:
                raise ValueError(f"OOF fold/config row alignment failed: {fold}/{dem}")
            probs[dem][idx] = rows.proba.to_numpy(dtype="float64")
    if any(np.isnan(v).any() for v in probs.values()):
        raise ValueError("At least one point lacks an OOF prediction")
    for dem in DEM_NAMES:
        checks.append({"check": "stored_probability_match", "source": dem,
                       "fold": "all", "n_points": len(points),
                       "n_predictions": len(points), "pass": True,
                       "max_abs_probability_delta": float(np.max(np.abs(
                           probs[dem] - points[f"oof_prob_{dem}"].to_numpy())))})
    points["fold"] = points.fold.astype(int)
    return points, checks


def compute_oof(points: pd.DataFrame, moran) -> tuple[pd.DataFrame, pd.DataFrame]:
    xy = moran.project_to_utm(points.lon.to_numpy(), points.lat.to_numpy(), "EPSG:32749")
    fold_id = points.fold.to_numpy(dtype=int)
    labels = points.y.to_numpy(dtype="float64")
    variables = [("label_acuan", "flood", labels)]
    for dem in DEM_NAMES:
        probability = points[f"oof_prob_{dem}"].to_numpy(dtype="float64")
        variables.extend((("oof_probability", dem, probability),
                          ("oof_residual", dem, labels - probability)))
    result = []
    neighbor_summary = []
    for k in (moran.MORAN_K_PRIMARY, *moran.MORAN_K_SENSITIVITY):
        nbr, dist = moran.knn_neighbors(xy, k)
        cross = float((fold_id[nbr] != fold_id[:, None]).mean())
        neighbor_summary.append({"k": k, "n_points": len(points),
                                 "neighbor_edges": len(points) * k,
                                 "cross_fold_edge_share": cross,
                                 "median_kth_neighbor_m": float(np.median(dist[:, -1])),
                                 "p95_kth_neighbor_m": float(np.percentile(dist[:, -1], 95)),
                                 "max_kth_neighbor_m": float(np.max(dist[:, -1])),
                                 "crs": "EPSG:32749"})
        for scope, dem, values in variables:
            row = moran.moran_points(values, nbr)
            row.update({"scope": scope, "dem": dem, "k": k,
                        "weights": f"kNN k={k}, row-standardized, UTM 49S",
                        "seed": moran.MORAN_SEED,
                        "permutation_method": "conditional value permutation"})
            result.append(row)
    return pd.DataFrame(result), pd.DataFrame(neighbor_summary)


def shift_sum(a: np.ndarray) -> np.ndarray:
    out = np.zeros_like(a)
    out[1:, :] += a[:-1, :]
    out[:-1, :] += a[1:, :]
    out[:, 1:] += a[:, :-1]
    out[:, :-1] += a[:, 1:]
    out[1:, 1:] += a[:-1, :-1]
    out[1:, :-1] += a[:-1, 1:]
    out[:-1, 1:] += a[1:, :-1]
    out[:-1, :-1] += a[1:, 1:]
    return out


def raster_observed_i(path: Path, role: str, stored: pd.DataFrame,
                      manifest: dict, cache: dict) -> dict:
    with rasterio.open(path) as ds:
        arr = ds.read(1)
        valid = np.isfinite(arr) & (arr != -9999)
        transform6 = tuple(ds.transform)[:6]
        crs = ds.crs.to_string() if ds.crs else ""
        shape = ds.shape
        nodata = ds.nodata
    # Match frozen moran_raster(): float32 values/mask and row-standardized queen neighbors.
    v = np.where(valid, arr, 0).astype("float32")
    m = valid.astype("float32")
    cnt = shift_sum(m)
    cnt_safe = np.where(cnt > 0, cnt, 1).astype("float32")

    def observed_for(use: np.ndarray) -> float:
        vals = v[use].astype("float64")
        zfull = np.zeros_like(v)
        zfull[use] = (vals - vals.mean()).astype("float32")
        ss = float((zfull[use].astype("float64") ** 2).sum())
        lag = shift_sum(zfull) / cnt_safe
        return float((zfull[use].astype("float64") * lag[use].astype("float64")).sum() / ss)

    use = valid & (cnt > 0)
    n = int(use.sum())
    observed = observed_for(use)
    all_valid_i = observed_for(valid)
    dem = path.stem.removeprefix("prob_")
    ref = stored[stored.dem == dem]
    stored_i = float(ref.iloc[0]["I"]) if len(ref) else np.nan
    stored_n = int(ref.iloc[0]["n"]) if len(ref) else np.nan
    manifest_record = manifest.get("maps", {}).get("rasters", {}).get(f"prob_{dem}", {})
    expected_sha = manifest_record.get("sha256", "")
    cached_i, cached_n = cache.get(dem, (np.nan, np.nan))
    return {"dem": dem, "role": role, "path": str(path.relative_to(ROOT)),
            "sha256": sha256(path), "crs": crs, "height": shape[0], "width": shape[1],
            "transform": json.dumps(transform6), "nodata": nodata,
            "manifest_sha256": expected_sha,
            "sha256_matches_manifest": bool(expected_sha and sha256(path) == expected_sha),
            "valid_pixels": int(valid.sum()), "isolated_valid_pixels_excluded": int(valid.sum() - n),
            "moran_n": n, "moran_i_recomputed": observed, "stored_active_i": stored_i,
            "delta_vs_stored_active_i": observed - stored_i,
            "stored_active_n": stored_n, "delta_n_vs_stored_active": n - stored_n,
            "moran_n_if_isolated_included": int(valid.sum()),
            "moran_i_if_isolated_included": all_valid_i,
            "delta_all_valid_i_vs_stored": all_valid_i - stored_i,
            "notebook_cell64_cached_i": cached_i, "notebook_cell64_cached_n": cached_n,
            "delta_recomputed_i_vs_notebook_cache": observed - cached_i,
            "permutations_recomputed": 0,
            "permutation_source_note": "stored p-values are compared in findings; not recomputed"}


def notebook_map_cache() -> dict:
    nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    cell = nb["cells"][64]
    text = "\n".join("".join(o.get("text", [])) or
                     "".join(o.get("data", {}).get("text/plain", []))
                     for o in cell.get("outputs", []))
    result = {}
    for dem, value, n in re.findall(r"(srtm|glo30|aw3d30): I=([0-9.]+).*?n=(\d+)", text):
        result[dem] = (float(value), int(n))
    return result


def bootstrap(pred: pd.DataFrame, source_name: str) -> pd.DataFrame:
    pred = pred.copy()
    pred["fold"] = pred.fold.astype(int)
    blocks = np.sort(pred.block.unique())
    configs = ("srtm", "glo30", "aw3d30")
    by_config = {c: pred[pred.config == c] for c in configs}
    if len(blocks) != 16 or any(len(by_config[c]) == 0 for c in configs):
        raise ValueError("Unexpected block/config coverage for block bootstrap")
    # Mirrors notebook cell 41: paired 16-block resampling with RandomState(42).
    rng = np.random.RandomState(42)
    aucs = {c: np.empty(1000) for c in configs}
    for i in range(1000):
        draw = rng.choice(blocks, size=len(blocks), replace=True)
        for config in configs:
            parts = [by_config[config][by_config[config].block == block]
                     for block in draw]
            ys = np.concatenate([p.y_true.to_numpy() for p in parts])
            ps = np.concatenate([p.proba.to_numpy() for p in parts])
            aucs[config][i] = roc_auc_score(ys, ps)
    rows = []
    for a, b, pair in (("srtm", "glo30", "srtm-minus-glo30"),
                       ("srtm", "aw3d30", "srtm-minus-aw3d30"),
                       ("glo30", "aw3d30", "glo30-minus-aw3d30")):
        delta = aucs[a] - aucs[b]
        rows.append({"source": source_name, "pair": pair, "method": "block16",
                     "auc_a_mean": float(aucs[a].mean()), "auc_b_mean": float(aucs[b].mean()),
                     "delta_auc_mean": float(delta.mean()),
                     "delta_auc_std_ddof1": float(delta.std(ddof=1)),
                     "ci_low_percentile": float(np.percentile(delta, 2.5)),
                     "ci_high_percentile": float(np.percentile(delta, 97.5)),
                     "n_iter": 1000, "n_blocks": len(blocks), "seed": 42,
                     "rng": "numpy.random.RandomState(MT19937)",
                     "auc": "sklearn.metrics.roc_auc_score"})
    return pd.DataFrame(rows)


def main() -> None:
    moran = source_moran_module()
    points = read_csv_checked(OOF_POINTS)
    pred_frames = {name: read_csv_checked(path) for name, path in POINT_PREDICTION_FILES.items()}
    # Both copies must have the same row keys and numerically equivalent saved predictions.
    left, right = pred_frames["hasil_kaggle"], pred_frames["v27_delivery"]
    if not left[["fold", "config", "block", "y_true"]].equals(
            right[["fold", "config", "block", "y_true"]]):
        raise ValueError("Prediction-copy row keys/labels differ")
    probability_delta = np.abs(left.proba.to_numpy() - right.proba.to_numpy())
    provenance = [{"check": "prediction_copy_comparison", "pass": True,
                   "left_sha256": sha256(POINT_PREDICTION_FILES["hasil_kaggle"]),
                   "right_sha256": sha256(POINT_PREDICTION_FILES["v27_delivery"]),
                   "rows": len(left), "exact_probability_differences": int(np.sum(probability_delta != 0)),
                   "max_abs_probability_delta": float(probability_delta.max()),
                   "left_bootstrap_sha256": sha256(BOOTSTRAP_FILES["hasil_kaggle"]),
                   "right_bootstrap_sha256": sha256(BOOTSTRAP_FILES["v27_delivery"])}]
    pred = pred_frames["v27_delivery"]
    aligned_points, align_checks = reconstruct_oof(pred, points)
    provenance.extend(align_checks)

    oof, neighbors = compute_oof(aligned_points, moran)
    stored_oof = read_csv_checked(OOF_STORED)
    key = ["scope", "dem", "k"]
    merged = oof.merge(stored_oof, on=key, suffixes=("_recomputed", "_stored"), validate="one_to_one")
    merged["delta_i"] = merged.I_recomputed - merged.I_stored
    merged["delta_p_two_sided"] = merged.p_two_sided_recomputed - merged.p_two_sided_stored
    merged["stored_match_i_1e-12"] = merged.delta_i.abs() <= 1e-12

    map_stored = read_csv_checked(MAP_STORED)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    cache = notebook_map_cache()
    raster_rows = []
    for role, directory in (("active_postmask", RASTERS), ("backup_unmasked", BACKUP)):
        for dem in DEM_NAMES:
            raster_rows.append(raster_observed_i(directory / f"prob_{dem}.tif", role,
                                                 map_stored, manifest, cache))
    raster_results = pd.DataFrame(raster_rows)

    boot_results = pd.concat([bootstrap(pred_frames[name], name)
                              for name in ("hasil_kaggle", "v27_delivery")], ignore_index=True)
    stored_boot = read_csv_checked(BOOTSTRAP_FILES["v27_delivery"])
    boot_results = boot_results.merge(stored_boot, on=["pair", "method"],
                                      suffixes=("_recomputed", "_stored"), validate="many_to_one")
    boot_results["delta_mean_vs_stored"] = (boot_results.delta_auc_mean_recomputed -
                                               boot_results.delta_auc_mean_stored)
    boot_results["ci_low_vs_stored"] = boot_results.ci_low_percentile - boot_results.ci_low
    boot_results["ci_high_vs_stored"] = boot_results.ci_high_percentile - boot_results.ci_high

    local_versions = {
        "python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__,
        "scipy": scipy.__version__, "scikit_learn": sklearn.__version__,
        "rasterio": rasterio.__version__, "libpysal": importlib.util.find_spec("libpysal") is not None,
        "esda": importlib.util.find_spec("esda") is not None,
    }
    for package in ("libpysal", "esda"):
        try:
            local_versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            local_versions[package] = "not-installed"
    manifest_env = json.loads(MANIFEST.read_text(encoding="utf-8"))["environment"]
    versions = pd.DataFrame([
        {"item": key, "local_version": str(value),
         "manifest_version": str(manifest_env.get("python", "")) if key == "python" else
                            str(manifest_env.get("packages", {}).get(key.replace("_", "-"),
                                                                  manifest_env.get("packages", {}).get(key, "")))}
        for key, value in local_versions.items()
    ])
    pd.DataFrame(provenance).to_csv(OUT / "source_provenance.csv", index=False)
    merged.to_csv(OUT / "moran_oof_recomputed.csv", index=False)
    neighbors.to_csv(OUT / "moran_oof_neighbors.csv", index=False)
    raster_results.to_csv(OUT / "moran_raster_recomputed.csv", index=False)
    boot_results.to_csv(OUT / "block_bootstrap_recomputed.csv", index=False)
    versions.to_csv(OUT / "runtime_versions.csv", index=False)
    print(f"Wrote diagnostics to {OUT}")
    print(f"OOF rows: {len(merged)}; I matches at 1e-12: {int(merged['stored_match_i_1e-12'].sum())}/{len(merged)}")
    print(f"Raster rows: {len(raster_results)}; bootstrap rows: {len(boot_results)}")
    print("Max paired CSV prediction delta:", float(probability_delta.max()))


if __name__ == "__main__":
    main()
