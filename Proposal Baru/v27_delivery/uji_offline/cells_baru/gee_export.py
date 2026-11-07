# =========================================================
# v27 - EKSPOR PETA KE GeoTIFF (mode PREPARE_MAPS)
# Pengganti Export.toDrive v26. Alasannya:
#  - task toDrive oleh service account mendarat di Drive milik service account,
#    bukan Drive pengguna, dan v26 hanya mencetak "Export started" tanpa memeriksa hasil.
#  - Di sini raster diunduh langsung per tile (ee.data.computePixels) pada grid yang dipatok
#    eksplisit, ditulis ke folder data, diverifikasi, baru berstatus COMPLETED.
# Kode Export.toDrive v26 tetap ada di cell berikutnya (nonaktif secara default).
# =========================================================
def build_grid_from_roi():
    bb = roi.bounds(1, ANALYSIS_CRS).getInfo()
    ring = bb['coordinates'][0]
    xs, ys = [c[0] for c in ring], [c[1] for c in ring]
    if max(abs(v) for v in xs + ys) < 1000:
        raise RuntimeError('Koordinat bounding box bukan meter UTM (nilai terlalu kecil). '
                           'Periksa roi.bounds(maxError, proj).')
    return make_grid(min(xs), min(ys), max(xs), max(ys), crs=ANALYSIS_CRS, res=ANALYSIS_SCALE)


def fetch_tile_gee(image, tile):
    # Satu tile GeoTIFF pada grid persis yang diminta (dimensi + affine + CRS).
    params = {
        'expression': image,
        'fileFormat': 'GEO_TIFF',
        'grid': {
            'dimensions': {'width': tile['width'], 'height': tile['height']},
            'affineTransform': {'scaleX': GRID['res'], 'shearX': 0, 'translateX': tile['x0'],
                                'shearY': 0, 'scaleY': -GRID['res'], 'translateY': tile['y1']},
            'crsCode': GRID['crs'],
        },
    }
    return ee.data.computePixels(params)


if RUN_MODE == 'PREPARE_MAPS':
    # 1. Bekukan tabel statistik spasial hasil GEE (sudah dihitung di cell 39, 40, 42).
    for _f in ['sensitivity_summary.csv', 'area_per_risk_class_km2.csv', 'worldcover_sensitivity.csv',
               'transition_srtm_vs_glo30.csv', 'transition_srtm_vs_aw3d30.csv',
               'transition_glo30_vs_aw3d30.csv']:
        freeze_gee_table(_f)

    # 2. Grid dan daftar raster.
    GRID = build_grid_from_roi()
    print('Grid ekspor:', GRID)
    _aoi_px = None
    try:
        _aoi_px = int(round(float(prob_map[DEM_NAMES[0]].mask().rename('m').reduceRegion(
            reducer=ee.Reducer.sum(), geometry=roi, scale=ANALYSIS_SCALE,
            maxPixels=1e13, tileScale=TILE_SCALE).get('m').getInfo())))
        print('Piksel valid peta (GEE, grid asli):', _aoi_px)
    except Exception as _e:
        print('Hitungan piksel valid GEE dilewati:', _e)
    _st = status_load()
    _st['grid'] = GRID
    _st['aoi_pixel_count_gee'] = _aoi_px
    status_save(_st)

    _jobs = []
    for _d in DEM_NAMES:
        _jobs.append((f'prob_{_d}', 'prob', prob_map[_d]))
        _jobs.append((f'risk_class_{_d}', 'risk', risk_class[_d]))
    for _p in pairs:
        _jobs.append((f'delta_abs_{_p[0]}_vs_{_p[1]}', 'delta', delta_abs[_p]))
        _jobs.append((f'agreement_{_p[0]}_vs_{_p[1]}', 'agreement', agreement_map[_p]))
    _jobs.append(('proxy_flood_label_sentinel1', 'label', flood_label))

    # 3. Unduh, mosaik, tulis, verifikasi. Satu raster gagal tidak menghentikan yang lain.
    for _name, _kind, _img in _jobs:
        print(f'== {_name} ({_kind})')
        export_raster(_name, _kind, _img.toFloat().unmask(EXPORT_NODATA), GRID, fetch_tile_gee)

    # 4. Verifikasi menyeluruh dan catat ke manifest/status.
    EXPORT_CHECKS = verify_all_rasters(GRID, _aoi_px)
    _nfail = print_checks(EXPORT_CHECKS)
    _st = status_load()
    _st['validation'] = {'checked_at_utc': _utcnow(), 'checks': EXPORT_CHECKS}
    status_save(_st)
    _stm = status_load()['rasters']
    manifest_update(maps={
        'grid': GRID, 'nodata': EXPORT_NODATA, 'breaks': [float(b) for b in BREAKS],
        'risk_class_method': RISK_CLASS_METHOD, 'rf_gee': RF_GEE,
        'note_models': 'Peta: ee.Classifier.smileRandomForest 300 pohon (GEE). Evaluasi: sklearn RandomForest 400 pohon. Dua model berbeda.',
        'rasters': {n: {'status': r['status'], 'sha256': r.get('sha256')} for n, r in _stm.items()},
        'created_at_utc': _utcnow()})
    _failed = [n for n, r in _stm.items() if r['status'] != 'COMPLETED']
    if _failed or _nfail:
        print('\nPERHATIAN: ada raster belum COMPLETED atau verifikasi FAIL. Lihat pesan di atas dan '
              'data/export_status.json. Jalankan ulang cell ini untuk melanjutkan (raster COMPLETED dilewati).')
    else:
        print('\nSemua raster COMPLETED dan lolos verifikasi.')
else:
    print('Ekspor peta dilewati (RUN_MODE != PREPARE_MAPS).')
