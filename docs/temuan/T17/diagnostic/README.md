# T17 diagnostic files

- `t17_slope_diagnostic.js` — standalone Google Earth Engine Code Editor script for the exact 30 fixed T16 audit coordinates. It separates native label slope, forced-grid label control, reproject-before-slope feature calculation, and final feature sampling-grid control. It preserves masked points with sentinel values plus validity columns. No sample regeneration, label edits, or training.
- `build_t17_diagnostic.py` — rebuilds the JS input list from the frozen T16 audit CSV and checks for exactly 30 positive, unique coordinates.
- `PROVENANCE_AND_LIMITS.md` — inspected notebook/manifest provenance, route interpretation, and unverified historical facts.

Verification performed locally: builder ran and `node --check t17_slope_diagnostic.js` passed. The script was not run in Earth Engine in this delegated task; therefore there is no GEE result CSV or finding about the cause of the 30 discrepant values yet. See parent handoff.
