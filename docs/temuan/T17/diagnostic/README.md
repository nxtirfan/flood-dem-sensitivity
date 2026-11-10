# T17 diagnostic files

- `t17_slope_diagnostic.js` — standalone Google Earth Engine Code Editor script for the exact 30 fixed T16 audit coordinates. It separates native label slope, forced-grid label control, reproject-before-slope feature calculation, and final feature sampling-grid control. It preserves masked points with sentinel values plus validity columns. No sample regeneration, label edits, or training.
- `build_t17_diagnostic.py` — rebuilds the JS input list from the frozen T16 audit CSV and checks for exactly 30 positive, unique coordinates.
- `PROVENANCE_AND_LIMITS.md` — inspected notebook/manifest provenance, route interpretation, and unverified historical facts.

Verification performed locally: builder ran and `node --check t17_slope_diagnostic.js` passed. The script was not run in Earth Engine in this delegated task; therefore there is no GEE result CSV or finding about the cause of the 30 discrepant values yet. See parent handoff.

**Access:** Parent confirmed Google sign-in / Earth Engine authentication is blocked in the current environment. The script is **NOT_EXECUTED**. The JS uses one `FeatureCollection.evaluate` call to return the 120 expected rows as console JSON; no GEE results are claimed. Manifest S1 provenance contains counts and hashes of sorted image IDs, not the full IDs. See `PROVENANCE_AND_LIMITS.md` for the hash algorithm, parent-reported asset metadata timestamps, and the Sentinel-1 projection caveat.

The frozen lon/lat properties were added to stage-1 stratified sample points before historical `sampleRegions`; that call specified `scale: 30` but no CRS. The T17 routes explicitly specify their evaluation projection to make route comparisons interpretable, so they do not prove the historical implicit projection choice. Details are in `PROVENANCE_AND_LIMITS.md`.
