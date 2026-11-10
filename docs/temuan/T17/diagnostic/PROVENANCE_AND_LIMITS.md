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

The JS requests four route rows per input point (120 rows expected if evaluation succeeds):

1. `label_native_projection_control`: current SRTM label slope and strict `<5` mask sampled on its native slope projection. It is a current native-projection control only, not the effective historical label grid; the Sentinel-1-dependent `flood_raw` graph is not rebuilt.
2. `label_slope_forced_analysis_grid_control`: native label slope explicitly reprojected to the analysis grid before sampling. This is a control, not the label-code path.
3. `feature_srtm_slope_analysis_grid`: SRTM elevation reprojected first to EPSG:32749/30 m, then slope computed, matching the DEM feature branch.
4. `feature_slope_final_sampling_grid_control`: feature slope explicitly set to the final analysis sampling grid. This isolates final stack sampling-grid effects; the other predictor bands are not needed to evaluate this single band.

Each row carries source/evaluation/sampling CRS, transform, nominal scale, route name, strict-threshold output, and separate validity flags. Masked values use `-9999`; interpret a slope or threshold only when its corresponding validity flag is 1. All bands are unmasked with expanded footprint to keep masked/out-of-footprint points in the table. No resampling override is imposed; any reprojection uses Earth Engine's default behavior. The returned FeatureCollection contains four route rows per fixed coordinate rather than dropping points that fail a mask; optional CSV export is disabled by default.

The comparison can establish whether current code paths produce different values/masks at these coordinates. It cannot, by itself, prove why the historical training feature export contains the 30 values ≥5°, because historical per-point label-filter values, grid transforms, and server-side execution provenance were not saved.

## Running / exporting

Open `t17_slope_diagnostic.js` in the Google Earth Engine Code Editor. Inspect the console and route fields. By default no Drive export is created; set `EXPORT_TO_DRIVE = true` only to create the diagnostic CSV. This does not change any labels, samples, training, or source notebook. Retain the generated CSV and console evidence as a current diagnostic result and record the run date/account/project separately; do not call it a historic replay.

## Access status and additional manifest provenance

The parent reports that Code Editor access is **blocked** at Google sign-in and that `ee.Initialize` requires authentication; the expected `GOOGLE_APPLICATION_CREDENTIALS` and `GEE_SERVICE_ACCOUNT_JSON` variables and the inspected candidate credential files are absent. This delegated task did not try to authenticate or evaluate the script. Consequently, there is intentionally no result CSV and no simulated output.

The parent also reports these asset `updateTime` metadata values: `USGS/SRTMGL1_003` — `2022-01-12T12:32:47.055141Z`; `FAO/GAUL/2015/level2` — `2023-12-04T09:37:14.012831Z`; `COPERNICUS/S1_GRD` — `2026-11-05T11:24:23.189041Z`. These are parent-provided metadata observations, not independently re-queried here, and they identify collection/asset metadata—not the exact historical per-point pixels or effective projections.

The current manifest's `gee_provenance` does not store full image IDs. It stores counts and SHA-256 digests for sorted IDs joined by the literal `|`, encoded as UTF-8, then hashed (`sha256('|'.join(sorted(ids)).encode())`). S1 digests are: before-event, `n=2`, `ab9b9e1d6943585b35fdc70a509eed1e0d78051102068d62e263df492413baa8`; after-event, `n=3`, `f6e5e0609364e0e31acd295d1531d2d08117d91e607363a6ef3e01cb2e4e40ce`. The full IDs cannot be recovered from these hashes. A future authorized comparison must list the filtered IDs under the same ROI/date/configuration and compare the resulting digest; collection `updateTime` alone does not establish that the historical composite inputs match.

Notebook cell 19 defines `db_to_power(img_db)` as `ee.Image(10).pow(img_db.divide(10))`; `get_s1_median` uses the filtered `COPERNICUS/S1_GRD` collection's `.median().clip(roi)`. Composite/expression projection behavior can affect the effective flood-label operation's lazy evaluation. The T17 script deliberately does not reconstruct or assert the effective Sentinel-1 projection, does not rerun the label-generation chain, and does not claim that any slope-grid difference caused the discrepancy. Its slope-only routes are deliberately limited to the requested comparison.

The script uses small synchronous `getInfo()` calls for current ROI/projection metadata, then one `results.evaluate(...)` request for the bounded FeatureCollection JSON (expected 120 route rows); the optional Drive export remains disabled by default. This is ready to paste/run after authorized Code Editor access is available, but remains **NOT_EXECUTED**.

## Saved-coordinate and sampling-grid semantics

Notebook cell 31 creates `locs_stage1` with `stratifiedSample(scale: 30, geometries: true)` and then maps `add_lon_lat`, which copies longitude/latitude from that feature geometry into properties **before** calling `predictor_stack_all.sampleRegions({collection: locs_stage1, scale: 30, ...})`. Since the extraction uses `geometries: false` by default, the frozen CSV lon/lat fields derive from the saved stage-1 point properties; they are not a saved record of the exact final pixel transform or mask used for every predictor band. The historical `sampleRegions` call supplies no `projection`, so this notebook code alone does not record the effective projection selected during that extraction.

T17 intentionally samples each saved coordinate in explicitly named projection routes to compare paths and controls. This is not byte-for-byte reproduction of the historical extraction call's implicit projection selection. The CSV audit's coordinate CRS is inferred as geographic lon/lat (EPSG:4326); the original audit data does not declare a CRS field.

## Final review: projection API, masks, point centers, and access boundary

- The JS records `projection.getInfo().transform` as the six-value affine array when present, along with CRS and nominal scale. It records `projection.transform().getInfo()` separately as `transform_wkt`; it does **not** call `.join()` on that method. The official `ee.Projection.transform()` reference states its return type is a WKT `String`: https://developers.google.com/earth-engine/apidocs/ee-projection-transform . This corrects the earlier invalid assumption that it returned a list.
- Each route retains both mask weights (`slope_mask_weight`, `lt5_mask_weight`) and explicit validity flags. Slope/threshold bands use `.unmask(SENTINEL, false)`; mask bands use `.unmask(0, false)`, so unmasking expands the footprint rather than silently dropping points outside the original footprint. Sentinel values are meaningful only with their weights/validity fields.
- `sampleRegions` uses only the 30 saved point features and `geometries: true`. Its returned geometry is the sampled pixel center; the script records that center as `snapped_pixel_center_lon/lat` while retaining `input_lon/input_lat` from the audit feature. The official API documents that returned geometries are snapped to pixel centers: https://developers.google.com/earth-engine/apidocs/ee-image-sampleregions . These explicit route projections and centers are diagnostic controls, not proof of the historic `sampleRegions` implicit projection.
- The script reports whether primary or fallback GAUL names were selected and the actual selected names. It queries current projection metadata separately using small `getInfo()` metadata requests; it does not query asset update times or reconstruct the Sentinel-1 graph. The `label_native_projection_control` is explicitly **not** the effective historic label grid: flood_raw also depends on the Sentinel-1 ratio expressions, and T17 does not rebuild that graph.
- With authenticated access, a separate metadata check should (1) inspect `ee.data.getAsset()` metadata/updateTime for the configured asset IDs and record the check time; (2) reproduce the notebook's ROI/date filters for before/after S1; (3) list `system:index` values, sort lexically, join with literal `|`, UTF-8 encode, and SHA-256 hash; and (4) compare counts/digests with manifest `gee_provenance`. The manifest stores only count/hash, not IDs. None of these checks proves historical effective per-pixel projection or filter-time values without a retained execution record.

`node --check` verifies only JavaScript syntax. No Code Editor execution, Earth Engine `getInfo()`/`evaluate()`, metadata request, or result export was performed here; runtime semantics remain unverified because authentication is blocked.
