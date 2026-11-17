# =========================================================
# v27 - FUNGSI BANTU: pembekuan data, checksum, manifest, validasi cached.
# Hanya JSON dan file biasa. Tidak ada koneksi GEE di cell ini.
# =========================================================
import hashlib, datetime, platform, shutil
from importlib import metadata as _md


class FrozenDataError(RuntimeError):
    """Artefak beku tidak ada, tidak lengkap, atau berubah."""


def _utcnow():
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def sha256_file(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for blk in iter(lambda: fh.read(chunk), b''):
            h.update(blk)
    return h.hexdigest()


def write_json_atomic(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False, default=str)
    os.replace(tmp, path)


def _rel(path):
    return os.path.relpath(path, PATHS['data']).replace(os.sep, '/')


def _abs(rel):
    return os.path.join(PATHS['data'], *rel.split('/'))


def _require_writable():
    if DATA_READ_ONLY:
        raise FrozenDataError('Folder data bersifat read-only (Kaggle Dataset). '
                              'Pembekuan hanya bisa dilakukan di folder kerja.')


# --- Versi dependensi (dicatat, TIDAK diubah) ---------------------------
def collect_environment():
    pk = ['numpy', 'pandas', 'scikit-learn', 'scipy', 'pyarrow', 'rasterio',
          'matplotlib', 'earthengine-api', 'geemap']
    ver = {}
    for p in pk:
        try:
            ver[p] = _md.version(p)
        except Exception:
            ver[p] = None
    return {'python': platform.python_version(), 'platform': platform.platform(),
            'environment': ENV, 'packages': ver}


RUN_ENV = collect_environment()
try:
    write_json_atomic(os.path.join(PATHS['outputs'], 'run_environment.json'),
                      {'run_mode': RUN_MODE, 'recorded_at_utc': _utcnow(), **RUN_ENV})
except Exception as _e:
    print('run_environment.json tidak tersimpan:', _e)
print('Versi dependensi:', {k: v for k, v in RUN_ENV['packages'].items() if v})


# --- Manifest -----------------------------------------------------------
def load_manifest():
    p = PATHS['manifest']
    if not os.path.isfile(p):
        return None
    with open(p, 'r', encoding='utf-8') as fh:
        return json.load(fh)


def save_manifest(m):
    _require_writable()
    m['updated_at_utc'] = _utcnow()
    write_json_atomic(PATHS['manifest'], m)


def start_new_manifest():
    return {
        'artifact_type': 'flood_dem_frozen_data',
        'schema_version': 1,
        'notebook': 'Flood_DEM_Sensitivity_Notebook_v27',
        'created_at_utc': _utcnow(),
        'updated_at_utc': _utcnow(),
        'run_mode_created': RUN_MODE,
        'random_state': RANDOM_STATE,
        'seeds_multi': list(SEEDS_MULTI),
        'environment': RUN_ENV,
        'artifact_root_note': 'Semua path artefak RELATIF terhadap folder data (lokasi manifest.json ini).',
        'created_data_root_abs': PATHS['data'],
        'config': {}, 'required_columns': [],
        'gee_assets': {}, 'gee_provenance': {},
        'datasets': {}, 'gee_tables': {}, 'maps': {},
        'notes': ['Dataset utama (main) dan dataset multi-seed dibekukan TERPISAH. '
                  'Seed 42 pada multi-seed BUKAN dataset utama: keduanya berasal dari '
                  'proses sampling berbeda (lihat audit v26).'],
    }


def guard_overwrite():
    if RUN_MODE == 'PREPARE_DATA' and os.path.isfile(PATHS['manifest']) and not OVERWRITE_FROZEN:
        raise FrozenDataError(
            'Dataset beku sudah ada di ' + PATHS['data'] + '. PREPARE_DATA dihentikan agar '
            'dataset yang sudah dipakai tidak tertimpa. Pindahkan/ganti nama folder data, atau '
            'set OVERWRITE_FROZEN = True bila memang ingin membekukan ulang.')


MANIFEST = None
FINGERPRINT_STATUS = {}
_FROZEN_CACHE = {}
if RUN_MODE == 'PREPARE_DATA':
    guard_overwrite()          # gagal cepat, sebelum cell GEE yang mahal berjalan


def init_prepare_manifest():
    # Awal PREPARE_DATA: manifest baru ditulis ke disk. Setelah ini semua pembaruan
    # selalu membaca-ulang dari disk (satu sumber kebenaran).
    global MANIFEST
    _require_writable()
    MANIFEST = start_new_manifest()
    save_manifest(MANIFEST)
    return MANIFEST


def manifest_update(**sections):
    # Perbarui bagian tingkat-atas manifest (config, gee_assets, maps, ...).
    m = load_manifest()
    if m is None:
        raise FrozenDataError('manifest.json belum ada.')
    for k, v in sections.items():
        if isinstance(v, dict) and isinstance(m.get(k), dict):
            m[k].update(v)
        else:
            m[k] = v
    save_manifest(m)
    return m


def config_snapshot():
    keys = ['ROI_MODE', 'SURROUNDING_RECTANGLE', 'BEFORE_START', 'BEFORE_END', 'AFTER_START',
            'AFTER_END', 'S2_START', 'S2_END', 'S1_POLARIZATION', 'S1_RATIO_THRESHOLD',
            'AFTER_DB_THRESHOLD', 'SLOPE_MAX_FOR_FLOOD', 'MIN_CONNECTED_PIXELS',
            'SAMPLE_PER_CLASS_TARGET', 'AUTO_BALANCE_SAMPLE', 'SAMPLE_SCALE', 'TILE_SCALE',
            'RIVER_UPA_THRESHOLD', 'DEM_CONFIGS', 'RF_SKLEARN', 'RF_GEE', 'RISK_CLASS_METHOD',
            'ANALYSIS_CRS', 'ANALYSIS_SCALE', 'APPLY_VERTICAL_OFFSET', 'SAMPLING_MODE',
            'SAMPLE_PER_CLASS', 'SAMPLE_PER_CLASS_FINAL', 'EE_PROJECT', 'fixed_bands',
            'predictor_bands_all']
    g = globals()
    return {k: g[k] for k in keys if k in g}


# --- Pembekuan tabel ------------------------------------------------------
def freeze_table(df, key, folder, extra=None):
    # Simpan tabel mentah hasil GEE: Parquet (utama) + CSV (interoperabilitas).
    # Lalu muat ulang dan BUKTIKAN identik. Metadata masuk ke manifest.
    _require_writable()
    df = df.reset_index(drop=True)
    os.makedirs(folder, exist_ok=True)
    stem = f'sample_{key}_raw'
    p_parq = os.path.join(folder, stem + '.parquet')
    p_csv = os.path.join(folder, stem + '.csv')
    df.to_parquet(p_parq, index=False, engine='pyarrow')
    df.to_csv(p_csv, index=False, float_format='%.17g')       # %.17g: float64 round-trip penuh

    back = pd.read_parquet(p_parq)
    try:
        pd.testing.assert_frame_equal(df, back, check_exact=True)
    except AssertionError as e:
        raise FrozenDataError(f'[{key}] muat ulang Parquet TIDAK identik dengan data sebelum disimpan: {e}')
    csv_ok = True
    try:
        back_csv = pd.read_csv(p_csv, dtype=df.dtypes.to_dict(), float_precision='round_trip')
        pd.testing.assert_frame_equal(df, back_csv, check_exact=True, check_dtype=False)
    except Exception as e:
        csv_ok = False
        print(f'[{key}] PERINGATAN: muat ulang CSV tidak identik ({str(e)[:200]}). Gunakan Parquet.')

    entry = {
        'file_parquet': _rel(p_parq), 'sha256_parquet': sha256_file(p_parq),
        'file_csv': _rel(p_csv), 'sha256_csv': sha256_file(p_csv),
        'csv_roundtrip_identical': csv_ok,
        'n_rows': int(len(df)), 'n_cols': int(df.shape[1]),
        'columns': [str(c) for c in df.columns],
        'dtypes': {str(c): str(t) for c, t in df.dtypes.items()},
        'null_counts': {str(c): int(n) for c, n in df.isna().sum().items()},
        'created_at_utc': _utcnow(),
    }
    entry.update(extra or {})
    m = load_manifest()
    if m is None:
        raise FrozenDataError('manifest.json belum diinisialisasi (init_prepare_manifest).')
    m['datasets'][key] = entry
    save_manifest(m)
    _FROZEN_CACHE.pop(key, None)
    print(f'[{key}] dibekukan: {entry["n_rows"]} baris x {entry["n_cols"]} kolom | '
          f'sha256 parquet {entry["sha256_parquet"][:16]}...')
    return entry


def get_frozen(key):
    # Muat tabel beku (setelah validate_artifacts). Salinan di-cache.
    if key not in _FROZEN_CACHE:
        m = load_manifest()
        if m is None or key not in m.get('datasets', {}):
            raise FrozenDataError(f'Dataset beku "{key}" tidak ada di manifest.')
        _FROZEN_CACHE[key] = pd.read_parquet(_abs(m['datasets'][key]['file_parquet']))
    return _FROZEN_CACHE[key].copy()


_MSG_ACTION = ('\nTindakan: jalankan notebook dengan RUN_MODE = \'PREPARE_DATA\' (butuh GEE) untuk '
               'membentuk dataset beku, atau pulihkan folder data beku yang benar. '
               'Notebook TIDAK akan mengambil data dari GEE secara otomatis.')


def validate_artifacts(keys='all'):
    # Cek: manifest, seed, file ada, SHA-256, jumlah baris, urutan kolom, tipe data,
    # nilai kosong, kolom wajib (prediktor ketiga DEM). Gagal -> FrozenDataError.
    global MANIFEST
    m = load_manifest()
    if m is None:
        raise FrozenDataError('ARTEFAK BEKU TIDAK DITEMUKAN: manifest.json tidak ada di '
                              + PATHS['data'] + '.' + _MSG_ACTION)
    MANIFEST = m
    problems, warns = [], []
    if m.get('artifact_type') != 'flood_dem_frozen_data':
        problems.append('manifest.json bukan manifest proyek ini (artifact_type tidak cocok).')
    if m.get('schema_version') != 1:
        problems.append(f'schema_version manifest {m.get("schema_version")} tidak didukung (diharapkan 1).')
    if m.get('random_state') != RANDOM_STATE:
        problems.append(f'random_state manifest ({m.get("random_state")}) != RANDOM_STATE notebook ({RANDOM_STATE}).')
    if list(m.get('seeds_multi', [])) != list(SEEDS_MULTI):
        problems.append(f'seeds_multi manifest {m.get("seeds_multi")} != SEEDS_MULTI notebook {list(SEEDS_MULTI)}.')

    all_keys = ['main'] + [f'seed_{s}' for s in SEEDS_MULTI]
    want = all_keys if keys == 'all' else list(keys)
    required = list(m.get('required_columns', []))
    dem_req = [f'{p}_{n}' for n in DEM_NAMES
               for p in ('elevation', 'slope', 'aspect_sin', 'aspect_cos', 'aspect_valid')]
    for key in want:
        ent = m.get('datasets', {}).get(key)
        if ent is None:
            problems.append(f'[{key}] tidak tercatat di manifest.')
            continue
        if key.startswith('seed_') and ent.get('seed') != int(key.split('_')[1]):
            problems.append(f'[{key}] seed di manifest ({ent.get("seed")}) tidak sesuai nama dataset.')
        p = _abs(ent['file_parquet'])
        if not os.path.isfile(p):
            problems.append(f'[{key}] file hilang: {p}')
            continue
        if sha256_file(p) != ent['sha256_parquet']:
            problems.append(f'[{key}] SHA-256 Parquet BERBEDA dari manifest: file berubah sejak dibekukan.')
            continue
        try:
            d = pd.read_parquet(p)
        except Exception as e:
            problems.append(f'[{key}] Parquet tidak terbaca: {e}')
            continue
        if len(d) != ent['n_rows']:
            problems.append(f'[{key}] jumlah baris {len(d)} != manifest {ent["n_rows"]}.')
        if [str(c) for c in d.columns] != ent['columns']:
            problems.append(f'[{key}] nama/urutan kolom berbeda dari manifest.')
        elif {str(c): str(t) for c, t in d.dtypes.items()} != ent['dtypes']:
            problems.append(f'[{key}] tipe data kolom berbeda dari manifest.')
        elif {str(c): int(n) for c, n in d.isna().sum().items()} != ent['null_counts']:
            problems.append(f'[{key}] jumlah nilai kosong berbeda dari manifest.')
        miss = [c for c in (['flood', 'lon', 'lat'] + required + dem_req) if c not in d.columns]
        if miss:
            problems.append(f'[{key}] kolom wajib tidak ada: {miss}')
        pc = _abs(ent['file_csv']) if ent.get('file_csv') else None
        if pc and os.path.isfile(pc):
            if sha256_file(pc) != ent['sha256_csv']:
                problems.append(f'[{key}] SHA-256 CSV berbeda dari manifest.')
        elif pc:
            warns.append(f'[{key}] salinan CSV tidak ada (tidak memengaruhi evaluasi, hanya interoperabilitas).')
        if key == 'main' or key.startswith('seed_'):
            _FROZEN_CACHE.pop(key, None)
    if problems:
        raise FrozenDataError('ARTEFAK BEKU TIDAK LENGKAP ATAU BERUBAH:\n  - '
                              + '\n  - '.join(problems) + _MSG_ACTION)
    for w in warns:
        print('Catatan:', w)
    for key in want:
        e = m['datasets'][key]
        print(f'[{key}] OK | {e["n_rows"]} baris x {e["n_cols"]} kolom | sha256 {e["sha256_parquet"][:16]}...')
    print(f'Validasi artefak beku LULUS ({len(want)} dataset).')
    return m


# --- Sidik jari data terproses (mendeteksi drift versi library/kode) ---------
def processed_fingerprint(X, y):
    h = hashlib.sha256()
    h.update('|'.join(map(str, X.columns)).encode('utf-8'))
    h.update(np.ascontiguousarray(X.to_numpy(dtype='float64')).tobytes())
    h.update(np.ascontiguousarray(y.to_numpy(dtype='int64')).tobytes())
    return h.hexdigest()


def record_or_check_fingerprint(key, X, y):
    fp = processed_fingerprint(X, y)
    m = load_manifest()
    ent = (m or {}).get('datasets', {}).get(key)
    if ent is None:
        FINGERPRINT_STATUS[key] = 'tidak ada manifest'
        return
    feat = [str(c) for c in X.columns]
    if RUN_MODE == 'PREPARE_DATA' and 'processed_fingerprint' not in ent and not DATA_READ_ONLY:
        ent['processed_fingerprint'] = fp
        ent['processed_shape'] = [int(X.shape[0]), int(X.shape[1])]
        ent['processed_feature_order'] = feat
        save_manifest(m)
        FINGERPRINT_STATUS[key] = 'dicatat'
        print(f'[{key}] sidik jari data terproses dicatat ({X.shape[0]} baris x {X.shape[1]} fitur).')
    elif ent.get('processed_fingerprint'):
        same = ent['processed_fingerprint'] == fp
        same_order = ent.get('processed_feature_order') == feat
        FINGERPRINT_STATUS[key] = 'cocok' if same else 'BEDA'
        print(f'[{key}] sidik jari data terproses: ' + ('COCOK dengan manifest.' if same else
              'BEDA dari manifest (urutan fitur ' + ('sama' if same_order else 'BEDA') +
              '). Periksa versi pandas/numpy dan kode pembersihan; evaluasi tetap berjalan.'))
    else:
        FINGERPRINT_STATUS[key] = 'tidak ada acuan'


# --- Tabel hasil GEE (statistik dll.) ---------------------------------------
def freeze_gee_table(filename, src_dir=None):
    _require_writable()
    src = os.path.join(src_dir or PATHS['outputs'], filename)
    if not os.path.isfile(src):
        print(f'freeze_gee_table: {filename} tidak ada, dilewati.')
        return None
    dst = os.path.join(PATHS['gee_tables'], filename)
    os.makedirs(PATHS['gee_tables'], exist_ok=True)
    shutil.copyfile(src, dst)
    m = load_manifest()
    if m is None:
        raise FrozenDataError('manifest.json belum ada. Jalankan PREPARE_DATA lebih dulu.')
    m['gee_tables'][filename] = {'file': _rel(dst), 'sha256': sha256_file(dst),
                                 'created_at_utc': _utcnow(), 'created_in_mode': RUN_MODE}
    save_manifest(m)
    return m['gee_tables'][filename]


def load_gee_table(filename, **read_kw):
    # Baca tabel GEE beku dan cek checksum. None + pesan jelas bila tidak tersedia.
    m = load_manifest()
    ent = (m or {}).get('gee_tables', {}).get(filename)
    if ent is None or not os.path.isfile(_abs(ent['file'])):
        print(f'Tabel GEE beku "{filename}" belum tersedia (jalankan PREPARE_DATA/PREPARE_MAPS sesuai jenisnya).')
        return None
    if sha256_file(_abs(ent['file'])) != ent['sha256']:
        raise FrozenDataError(f'Tabel GEE beku "{filename}": SHA-256 berbeda dari manifest.')
    return pd.read_csv(_abs(ent['file']), **read_kw)


print('Fungsi pembekuan/validasi siap. Mode:', RUN_MODE)
