# =========================================================
# v27 - UTILITAS RASTER PETA (semua mode, tanpa GEE saat didefinisikan)
# Grid dipatok eksplisit (EPSG:32749, 30 m, origin kelipatan 30 m) dan dipakai
# sama oleh SEMUA raster dan SEMUA tile -> tidak ada pergeseran antar tile/DEM.
# Status ekspor: PENDING -> RUNNING -> COMPLETED | FAILED (data/export_status.json).
# COMPLETED hanya jika file ada, terbaca, lolos verifikasi grid/nilai, dan SHA-256 tercatat.
# =========================================================
MAP_PAIRS = [('srtm', 'glo30'), ('srtm', 'aw3d30'), ('glo30', 'aw3d30')]
RASTER_KINDS = {'prob': (0.0, 1.0), 'delta': (0.0, 1.0), 'risk': (1, 5),
                'agreement': (0, 1), 'label': (0, 1)}


def _rio():
    try:
        import rasterio
        return rasterio
    except ImportError as e:
        raise ImportError('rasterio belum terpasang. Jalankan: pip install rasterio') from e


def status_load():
    p = PATHS['export_status']
    if os.path.isfile(p):
        with open(p, 'r', encoding='utf-8') as fh:
            return json.load(fh)
    return {'schema_version': 1, 'rasters': {}, 'grid': None, 'validation': None}


def status_save(st):
    _require_writable()
    st['updated_at_utc'] = _utcnow()
    write_json_atomic(PATHS['export_status'], st)


def status_set(name, rec):
    st = status_load()
    st['rasters'][name] = rec
    status_save(st)


def make_grid(x_min, y_min, x_max, y_max, crs='EPSG:32749', res=30.0):
    # Grid yang memuat bounding box, origin dibulatkan ke kelipatan res (sejajar grid GEE 30 m UTM).
    x0 = float(np.floor(x_min / res) * res)
    x1 = float(np.ceil(x_max / res) * res)
    y0 = float(np.floor(y_min / res) * res)
    y1 = float(np.ceil(y_max / res) * res)
    return {'crs': crs, 'res': float(res), 'x0': x0, 'y1': y1,
            'width': int(round((x1 - x0) / res)), 'height': int(round((y1 - y0) / res))}


def grid_tiles(grid, tile_px):
    tiles = []
    for r0 in range(0, grid['height'], tile_px):
        for c0 in range(0, grid['width'], tile_px):
            tiles.append({'row_off': r0, 'col_off': c0,
                          'height': min(tile_px, grid['height'] - r0),
                          'width': min(tile_px, grid['width'] - c0),
                          'x0': grid['x0'] + c0 * grid['res'],
                          'y1': grid['y1'] - r0 * grid['res']})
    return tiles


def read_tile_bytes(data, tile, grid):
    # Baca GeoTIFF satu tile dari memori dan BUKTIKAN grid-nya persis seperti yang diminta.
    rasterio = _rio()
    from rasterio.io import MemoryFile
    with MemoryFile(data) as mf:
        with mf.open() as ds:
            tr = ds.transform
            ok = (ds.count == 1 and ds.width == tile['width'] and ds.height == tile['height']
                  and abs(tr.a - grid['res']) < 1e-6 and abs(tr.e + grid['res']) < 1e-6
                  and abs(tr.c - tile['x0']) < 1e-6 and abs(tr.f - tile['y1']) < 1e-6
                  and ds.crs is not None and ds.crs.to_epsg() == int(grid['crs'].split(':')[1]))
            if not ok:
                raise RuntimeError(
                    f'Grid tile tidak sesuai permintaan: dapat (w={ds.width},h={ds.height},'
                    f'a={tr.a},e={tr.e},c={tr.c},f={tr.f},crs={ds.crs}) vs diminta '
                    f'(w={tile["width"]},h={tile["height"]},x0={tile["x0"]},y1={tile["y1"]}).')
            arr = ds.read(1).astype('float32')
    return np.where(np.isfinite(arr), arr, np.float32(EXPORT_NODATA)).astype('float32')


def mosaic_tiles(tile_arrays, grid):
    # Gabungkan tile ke satu array penuh dan buktikan: tidak ada celah, tidak ada tumpang tindih.
    H, W = grid['height'], grid['width']
    mosaic = np.full((H, W), np.nan, dtype='float32')
    cover = np.zeros((H, W), dtype='uint8')
    for tile, arr in tile_arrays:
        r0, c0, th, tw = tile['row_off'], tile['col_off'], tile['height'], tile['width']
        if arr.shape != (th, tw):
            raise RuntimeError(f'Ukuran array tile {arr.shape} != ({th}, {tw}).')
        mosaic[r0:r0 + th, c0:c0 + tw] = arr
        cover[r0:r0 + th, c0:c0 + tw] += 1
    gaps, overlaps = int((cover == 0).sum()), int((cover > 1).sum())
    if gaps or overlaps:
        raise RuntimeError(f'Mosaik tile tidak sempurna: celah={gaps} piksel, tumpang tindih={overlaps} piksel.')
    return mosaic


def write_geotiff(path, arr, grid, tags=None, description=None):
    rasterio = _rio()
    from rasterio.transform import from_origin
    os.makedirs(os.path.dirname(path), exist_ok=True)
    profile = dict(driver='GTiff', height=grid['height'], width=grid['width'], count=1,
                   dtype='float32', crs=grid['crs'],
                   transform=from_origin(grid['x0'], grid['y1'], grid['res'], grid['res']),
                   nodata=EXPORT_NODATA, compress='deflate', tiled=True,
                   blockxsize=256, blockysize=256)
    with rasterio.open(path, 'w', **profile) as dst:
        dst.write(arr.astype('float32'), 1)
        if description:
            dst.set_band_description(1, description)
        dst.update_tags(**{k: str(v) for k, v in (tags or {}).items()})


def verify_raster(path, grid, kind):
    # Periksa CRS, transform, ukuran, resolusi, tipe, NoData, dan rentang nilai. Raise bila ada pelanggaran.
    rasterio = _rio()
    from rasterio.transform import from_origin
    errs, info = [], {}
    if not os.path.isfile(path):
        raise RuntimeError(f'file tidak ditemukan: {path}')
    with rasterio.open(path) as ds:
        exp = from_origin(grid['x0'], grid['y1'], grid['res'], grid['res'])
        if ds.crs is None or ds.crs.to_epsg() != int(grid['crs'].split(':')[1]):
            errs.append(f'CRS {ds.crs} != {grid["crs"]}')
        if not np.allclose(tuple(ds.transform)[:6], tuple(exp)[:6], atol=1e-9):
            errs.append(f'transform {tuple(ds.transform)[:6]} != {tuple(exp)[:6]}')
        if (ds.width, ds.height) != (grid['width'], grid['height']):
            errs.append(f'ukuran {(ds.width, ds.height)} != {(grid["width"], grid["height"])}')
        if ds.res != (grid['res'], grid['res']):
            errs.append(f'resolusi {ds.res} != {(grid["res"], grid["res"])}')
        if ds.count != 1 or ds.dtypes[0] != 'float32':
            errs.append(f'band/tipe {ds.count}/{ds.dtypes} != 1/float32')
        if ds.nodata != EXPORT_NODATA:
            errs.append(f'NoData {ds.nodata} != {EXPORT_NODATA}')
        arr = ds.read(1)
        info['bounds'] = tuple(ds.bounds)
    valid = np.isfinite(arr) & (arr != EXPORT_NODATA)
    info['n_valid'] = int(valid.sum())
    info['n_nodata'] = int(arr.size - valid.sum())
    if info['n_valid'] == 0:
        errs.append('tidak ada piksel valid (raster kosong)')
    else:
        v = arr[valid]
        lo, hi = RASTER_KINDS[kind]
        info['min'], info['max'] = float(v.min()), float(v.max())
        if v.min() < lo - 1e-6 or v.max() > hi + 1e-6:
            errs.append(f'rentang nilai [{v.min():.6g}, {v.max():.6g}] di luar [{lo}, {hi}]')
        if kind in ('risk', 'agreement', 'label') and not np.all(v == np.round(v)):
            errs.append('nilai kelas tidak bulat')
    if errs:
        raise RuntimeError('Verifikasi raster gagal: ' + ' | '.join(errs))
    return info


def export_raster(name, kind, image, grid, fetch, tile_px=None):
    # fetch(image, tile) -> bytes GeoTIFF. Dipisah agar logika ini bisa diuji tanpa GEE.
    tile_px = tile_px or MAP_TILE_PX
    path = os.path.join(PATHS['rasters'], name + '.tif')
    st = status_load().get('rasters', {}).get(name, {})
    if (not OVERWRITE_RASTERS and st.get('status') == 'COMPLETED' and os.path.isfile(path)
            and sha256_file(path) == st.get('sha256')):
        print(f'{name}: COMPLETED sebelumnya (checksum cocok), dilewati.')
        return st
    rec = {'status': 'PENDING', 'kind': kind, 'file': _rel(path), 'tile_px': tile_px,
           'pending_at_utc': _utcnow()}
    status_set(name, rec)
    try:
        rec['status'] = 'RUNNING'
        rec['started_at_utc'] = _utcnow()
        status_set(name, rec)
        tiles = grid_tiles(grid, tile_px)
        arrays = []
        for i, tile in enumerate(tiles, 1):
            t0 = time.time()
            data = None
            for attempt in range(1, 4):
                try:
                    data = fetch(image, tile)
                    break
                except Exception as e:
                    txt = f'{type(e).__name__}: {e}'
                    body = getattr(e, 'content', None)
                    if body:
                        txt += ' | ' + (body.decode('utf-8', 'replace') if isinstance(body, bytes) else str(body))[:2000]
                    print(f'  {name} tile {i}/{len(tiles)} percobaan {attempt}/3 gagal: {txt[:500]}')
                    last_err = txt
                    if attempt < 3:
                        time.sleep(5 * attempt)
            if data is None:
                raise RuntimeError(f'tile {i}/{len(tiles)} gagal 3x. Pesan terakhir: {last_err}')
            arrays.append((tile, read_tile_bytes(data, tile, grid)))
            print(f'  {name} tile {i}/{len(tiles)} OK ({time.time() - t0:.0f} s)')
        mosaic = mosaic_tiles(arrays, grid)
        write_geotiff(path, mosaic, grid, description=name, tags={
            'name': name, 'kind': kind, 'created_at_utc': _utcnow(),
            'source': 'GEE computePixels', 'notebook': 'Flood_DEM_Sensitivity_Notebook_v27',
            'grid_crs': grid['crs'], 'grid_res_m': grid['res'], 'nodata': EXPORT_NODATA,
            'risk_class_breaks': json.dumps(globals().get('BREAKS')),
            'rf_gee_trees': (globals().get('RF_GEE') or {}).get('numberOfTrees')})
        info = verify_raster(path, grid, kind)
        rec.update({'status': 'COMPLETED', 'finished_at_utc': _utcnow(), 'sha256': sha256_file(path),
                    'size_bytes': os.path.getsize(path), 'n_valid': info['n_valid'],
                    'n_nodata': info['n_nodata'], 'min': info['min'], 'max': info['max']})
        status_set(name, rec)
        print(f'{name}: COMPLETED | valid={info["n_valid"]} nodata={info["n_nodata"]} '
              f'rentang=[{info["min"]:.4g}, {info["max"]:.4g}]')
    except Exception as e:
        rec.update({'status': 'FAILED', 'finished_at_utc': _utcnow(),
                    'error': f'{type(e).__name__}: {e}'})
        status_set(name, rec)
        print(f'{name}: FAILED -> {rec["error"]}')
    return rec


def _raster_array(name):
    rasterio = _rio()
    with rasterio.open(os.path.join(PATHS['rasters'], name + '.tif')) as ds:
        arr = ds.read(1)
    return arr, (np.isfinite(arr) & (arr != EXPORT_NODATA))


def _gee_table_any(filename, **kw):
    t = None
    try:
        t = load_gee_table(filename, **kw)
    except FrozenDataError as e:
        print(e)
    if t is None:
        p = os.path.join(PATHS['outputs'], filename)
        if os.path.isfile(p):
            t = pd.read_csv(p, **kw)
    return t


def verify_all_rasters(grid=None, aoi_pixel_count=None):
    # Verifikasi menyeluruh: grid identik untuk SEMUA raster (termasuk ketiga DEM), NoData, nilai,
    # konsistensi probabilitas-kelas-delta-agreement, dan statistik vs tabel GEE.
    st = status_load()
    grid = grid or st.get('grid')
    checks = []

    def add(name, status, detail):
        checks.append({'check': name, 'status': status, 'detail': detail})

    names = sorted(st['rasters'])
    done = [n for n in names if st['rasters'][n]['status'] == 'COMPLETED']
    bad = [n for n in names if st['rasters'][n]['status'] != 'COMPLETED']
    add('status_ekspor', 'PASS' if not bad else 'FAIL',
        f'{len(done)} COMPLETED' + (f' | belum selesai/gagal: {bad}' if bad else ''))
    if not done or grid is None:
        return checks

    infos = {}
    for n in done:
        rec = st['rasters'][n]
        p = os.path.join(PATHS['rasters'], n + '.tif')
        try:
            if sha256_file(p) != rec['sha256']:
                raise RuntimeError('SHA-256 berbeda dari export_status.json')
            infos[n] = verify_raster(p, grid, rec['kind'])
        except Exception as e:
            add(f'raster:{n}', 'FAIL', str(e))
    if infos:
        add('grid_identik_semua_raster', 'PASS' if len(infos) == len(done) else 'FAIL',
            f'{len(infos)}/{len(done)} raster lolos CRS/transform/ukuran/resolusi/NoData/rentang '
            f'terhadap grid yang sama; extent={next(iter(infos.values()))["bounds"]}')

    def have(*ns):
        return all(n in infos for n in ns)

    # NoData antar DEM
    for kind_prefix in ('prob', 'risk_class'):
        ns = [f'{kind_prefix}_{d}' for d in DEM_NAMES]
        if have(*ns):
            masks = [_raster_array(n)[1] for n in ns]
            diff = [int((masks[0] != m).sum()) for m in masks[1:]]
            add(f'nodata_antar_DEM:{kind_prefix}', 'PASS' if not any(diff) else 'INFO',
                f'valid per DEM={[int(m.sum()) for m in masks]} | piksel beda mask vs {ns[0]}: {diff}')
    if aoi_pixel_count and have(f'prob_{DEM_NAMES[0]}'):
        nv = infos[f'prob_{DEM_NAMES[0]}']['n_valid']
        add('piksel_valid_vs_hitungan_GEE', 'PASS' if abs(nv - aoi_pixel_count) / aoi_pixel_count < 1e-3 else 'INFO',
            f'raster={nv} | GEE={aoi_pixel_count} | selisih relatif={(nv - aoi_pixel_count) / aoi_pixel_count:+.2e}')

    # konsistensi prob -> kelas
    brk = globals().get('BREAKS') or (load_manifest() or {}).get('maps', {}).get('breaks')
    for d in DEM_NAMES:
        if have(f'prob_{d}', f'risk_class_{d}') and brk:
            p, pm = _raster_array(f'prob_{d}')
            r, rm = _raster_array(f'risk_class_{d}')
            exp = 1 + (p > brk[0]).astype(int) + (p > brk[1]) + (p > brk[2]) + (p > brk[3])
            both = pm & rm
            mism = both & (exp != r)
            near = np.min(np.abs(p[..., None] - np.array(brk)), axis=-1) <= 1e-6
            real = int((mism & ~near).sum())
            add(f'prob_vs_kelas:{d}', 'PASS' if real == 0 else 'FAIL',
                f'selisih di luar tepi batas kelas={real} | di tepi batas (presisi float32)={int((mism & near).sum())}')

    # delta & agreement vs hitungan lokal
    for a, b in MAP_PAIRS:
        if have(f'prob_{a}', f'prob_{b}', f'delta_abs_{a}_vs_{b}'):
            pa, ma = _raster_array(f'prob_{a}')
            pb, mb = _raster_array(f'prob_{b}')
            dd, md = _raster_array(f'delta_abs_{a}_vs_{b}')
            both = ma & mb & md
            mx = float(np.abs(np.abs(pa - pb)[both] - dd[both]).max()) if both.any() else float('nan')
            add(f'delta_lokal:{a}_vs_{b}', 'PASS' if mx < 1e-6 else 'FAIL', f'maks |selisih| = {mx:.3e}')
        if have(f'risk_class_{a}', f'risk_class_{b}', f'agreement_{a}_vs_{b}'):
            ra, mra = _raster_array(f'risk_class_{a}')
            rb, mrb = _raster_array(f'risk_class_{b}')
            ag, mag = _raster_array(f'agreement_{a}_vs_{b}')
            both = mra & mrb & mag
            mism = int(((ra == rb)[both].astype(float) != ag[both]).sum())
            add(f'agreement_lokal:{a}_vs_{b}', 'PASS' if mism == 0 else 'FAIL', f'piksel beda = {mism}')

    # statistik dari raster vs tabel GEE
    ss = _gee_table_any('sensitivity_summary.csv')
    for a, b in MAP_PAIRS:
        lab = f'{a} vs {b}'
        if ss is not None and have(f'delta_abs_{a}_vs_{b}', f'agreement_{a}_vs_{b}'):
            dd, md = _raster_array(f'delta_abs_{a}_vs_{b}')
            ag, mag = _raster_array(f'agreement_{a}_vs_{b}')
            row = ss[ss['pair'] == lab]
            if len(row):
                g_d, g_a = float(row['mean_abs_delta_prob'].iloc[0]), float(row['agreement_rate'].iloc[0])
                l_d, l_a = float(dd[md].mean()), float(ag[mag].mean())
                ok = abs(l_d - g_d) < 1e-3 and abs(l_a - g_a) < 1e-3
                add(f'statistik_vs_GEE:{lab}', 'PASS' if ok else 'INFO',
                    f'mean|dP| raster={l_d:.5f} GEE={g_d:.5f} | agreement raster={l_a:.5f} GEE={g_a:.5f}')
        tt = _gee_table_any(f'transition_{a}_vs_{b}.csv', index_col=0)
        if tt is not None and have(f'risk_class_{a}', f'risk_class_{b}'):
            ra, mra = _raster_array(f'risk_class_{a}')
            rb, mrb = _raster_array(f'risk_class_{b}')
            both = mra & mrb
            M = np.zeros((5, 5), dtype='int64')
            np.add.at(M, (ra[both].astype(int) - 1, rb[both].astype(int) - 1), 1)
            G = tt.to_numpy(dtype='int64')
            rel = float(np.abs(M - G).sum() / max(G.sum(), 1))
            add(f'transisi_vs_GEE:{lab}', 'PASS' if rel == 0 else ('INFO' if rel < 1e-3 else 'FAIL'),
                f'total |selisih sel| / total piksel = {rel:.2e}')
    at = _gee_table_any('area_per_risk_class_km2.csv', index_col=0)
    if at is not None:
        for d in DEM_NAMES:
            if have(f'risk_class_{d}') and d in at.columns:
                r, mr = _raster_array(f'risk_class_{d}')
                loc = np.array([(r[mr] == c).sum() for c in range(1, 6)]) * (grid['res'] ** 2) / 1e6
                g = at[d].reindex(range(1, 6)).fillna(0).to_numpy()
                rel = float(np.abs(loc - g).sum() / max(g.sum(), 1e-9))
                add(f'luas_vs_GEE:{d}', 'PASS' if rel < 2e-3 else 'INFO',
                    f'selisih relatif total = {rel:.2e} (lokal memakai 900 m2/piksel, GEE memakai pixelArea)')
    return checks


def print_checks(checks):
    for c in checks:
        print(f'[{c["status"]:<4}] {c["check"]}: {c["detail"]}')
    n_fail = sum(c['status'] == 'FAIL' for c in checks)
    print(f'Ringkasan: {sum(c["status"] == "PASS" for c in checks)} PASS, '
          f'{sum(c["status"] == "INFO" for c in checks)} INFO, {n_fail} FAIL')
    return n_fail

print('Utilitas raster siap. Verifikasi memakai grid yang dipatok eksplisit.')
