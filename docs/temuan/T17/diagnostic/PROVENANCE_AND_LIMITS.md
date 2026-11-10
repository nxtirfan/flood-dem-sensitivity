# T17 — provenance and limits for the 30-point slope diagnostic

## Result status

No Google Earth Engine request was run in this delegated task. The files here are a reproducible Code Editor diagnostic request, not exported measurements. No historical filter-time slope, mask, grid transform, or causal explanation is asserted. The parent task handles any authorized Code Editor access and must treat results from this script as a current evaluation unless an independent historical execution record establishes otherwise.

## Saved point set

The sole coordinate source is `../../T16/slope/slope_points_audit.csv` (30 rows, all `flood=1`). The builder validates the count, positive label, and unique coordinate pairs, then embeds the exact decimal coordinates and the stored training-export slope values in `t17_slope_diagnostic.js`. Audit CSV SHA-256: `0bbde44413c754eab7831244335b08237996e1bdd5cc94a3e065e23b5409da88`. The point rows are fixed input features; the diagnostic does not call `stratifiedSample` or generate replacement points.

## Notebook and frozen-run evidence inspected

- Canon notebook: `Proposal Baru/Flood_DEM_Sensitivity_Notebook_v27_maskAOI.ipynb`; SHA-256 `c40308146e2cc0bca08ddf7f9b34a81b3e1653666f7be4ebd9b780b1a578e748`. Its delivery copy has the same hash.
- Cell 15: `ROI_MODE='SEMDEMAK_ONLY'`, event dates, `SLOPE_MAX_FOR_FLOOD=5`, `SAMPLE_SCALE=30`, SRTM asset/band, and DEM configuration.
- Cell 16: GAUL level-2 Semarang/Demak ROI selection and fallback.
- Cell 21: label route loads `USGS/SRTMGL1_003` band `elevation`, clips to ROI, calls `ee.Terrain.slope`, and applies `slope_for_label.lt(5)` in `flood_raw` before connected-pixel filtering. It does not explicitly reproject this label DEM.
- Cell 27: predictor route clips SRTM, explicitly reprojects DEM to `EPSG:32749` at 30 m, computes terrain slope, and the predictor stack is explicitly reprojected to the same CRS/scale.
- Cell 31: v24 sampling path uses `label_for_sampling.stratifiedSample(... scale: 30, geometries: true)` and then `predictor_stack_all.sampleRegions({collection: locs_stage1, scale: 30, ...})`; `add_lon_lat` records coordinates before predictor extraction. Neither call specifies a CRS. Cell 44 duplicates this sequence in the multiseed `PREPARE_DATA` path.
- Current v27 manifest: `Proposal Baru/v27_delivery/Analisis Flood DEM Susceptibility/data/manifest.json`; SHA-256 `cb3eb7d34be9eb82438ffb5278bbe0fb184b80eb00aa30eeae0eb64f706e8dbd`. It records notebook `Flood_DEM_Sensitivity_Notebook_v27`, mode `PREPARE_DATA`, ROI `SEMDEMAK_ONLY`, `EPSG:32749`/30 m analysis grid, v24 sampling, target 3,000/class and final 2,978. The older delivery manifest is dated earlier and must not be substituted for the current one.

These sources identify the saved code/configuration and frozen sample context. They do **not** prove which lazy Earth Engine projection/resampling evaluation was effective at each historical point, or preserve the label-filter slope/mask values. The manifest's asset status is recorded provenance, not an independent verification of current asset availability or the exact historical server response.

## Diagnostic routes and interpretation

The JS produces four rows per input point (120 rows expected if evaluation succeeds):

1. `label_native_filter_eval`: current SRTM label slope and strict `<5` mask sampled on its native slope projection. It is the closest code-path diagnostic, but is not the historical effective value.
2. `label_slope_forced_analysis_grid_control`: native label slope explicitly reprojected to the analysis grid before sampling. This is a control, not the label-code path.
3. `feature_srtm_slope_analysis_grid`: SRTM elevation reprojected first to EPSG:32749/30 m, then slope computed, matching the DEM feature branch.
4. `feature_slope_final_sampling_grid_control`: feature slope explicitly set to the final analysis sampling grid. This isolates final stack sampling-grid effects; the other predictor bands are not needed to evaluate this single band.

Each row carries source/evaluation/sampling CRS, transform, nominal scale, route name, strict-threshold output, and separate validity flags. Masked values use `-9999`; interpret a slope or threshold only when its corresponding validity flag is 1. All bands are unmasked with expanded footprint to keep masked/out-of-footprint points in the table. No resampling override is imposed; any reprojection uses Earth Engine's default behavior. The CSV contains four route rows per fixed coordinate rather than dropping points that fail a mask.

The comparison can establish whether current code paths produce different values/masks at these coordinates. It cannot, by itself, prove why the historical training feature export contains the 30 values ≥5°, because historical per-point label-filter values, grid transforms, and server-side execution provenance were not saved.

## Running / exporting

Open `t17_slope_diagnostic.js` in the Google Earth Engine Code Editor. Inspect the console and route fields. By default no Drive export is created; set `EXPORT_TO_DRIVE = true` only to create the diagnostic CSV. This does not change any labels, samples, training, or source notebook. Retain the generated CSV and console evidence as a current diagnostic result and record the run date/account/project separately; do not call it a historic replay.
