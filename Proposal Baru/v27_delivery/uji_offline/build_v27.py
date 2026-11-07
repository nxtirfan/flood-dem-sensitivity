"""Bangun Flood_DEM_Sensitivity_Notebook_v27.ipynb dari v26 (v26 tidak diubah).
Prinsip: perubahan lokal. Cell lama dibungkus guard (indentasi) atau dipecah, isinya tidak ditulis ulang.
"""
import json, sys, textwrap, uuid, ast, copy

SRC = sys.argv[1]
OUT = sys.argv[2]
CELLS = sys.argv[3]          # folder cell baru

nb = json.load(open(SRC, encoding='utf-8'))
old = [''.join(c['source']) for c in nb['cells']]
types = [c['cell_type'] for c in nb['cells']]
assert len(old) == 47


def rd(name):
    return open(f'{CELLS}/{name}.py', encoding='utf-8').read().rstrip('\n') + '\n'


def indent(src, n=4):
    out = []
    for ln in src.rstrip('\n').split('\n'):
        out.append((' ' * n + ln) if ln.strip() else ln)
    return '\n'.join(out) + '\n'


def guard(cond, src, extra_after=''):
    for bad in ('"""', "'''"):
        assert bad not in src, 'triple-quote dalam cell yang akan di-indent'
    return f'if {cond}:\n' + indent(src) + extra_after


def cut(src, start_marker, end_marker=None, include_end=False):
    i = src.index(start_marker)
    j = len(src) if end_marker is None else src.index(end_marker, i)
    if end_marker is not None and include_end:
        j += len(end_marker)
    return src[:i], src[i:j], src[j:]


cells = []   # list of (type, source, origin)


def code(src, origin):
    cells.append(('code', src.rstrip('\n'), origin))


def md(src, origin):
    cells.append(('markdown', src.rstrip('\n'), origin))


# ---------------------------------------------------------------- 0-3
t0 = old[0] + """

---
**Catatan v27 (reproducibility).** Notebook ini adalah refactor lokal dari v26 untuk memisahkan *pembentukan dataset* dari *eksperimen model*.
Tiga mode eksekusi (variabel `RUN_MODE`, cell konfigurasi):

| Mode | GEE | Fungsi |
|---|---|---|
| `USE_CACHED_DATA` (default) | tidak | Validasi artefak beku (checksum, baris, fitur), lalu seluruh evaluasi dari file beku. |
| `PREPARE_DATA` | ya | Sampling utama + multi-seed dari GEE, bekukan (Parquet + CSV), `manifest.json`, SHA-256. |
| `PREPARE_MAPS` | ya | Latih RF GEE (300 pohon) pada sampel utama beku, unduh GeoTIFF, status ekspor. Tidak ada sampling ulang. |

Desain eksperimen, parameter, dan metode tidak diubah dari v26. RF peta GEE (300 pohon) dan RF evaluasi sklearn (400 pohon) tetap dua model berbeda."""
md(t0, 0)
md(old[1], 1)
md(old[2], 2)
code(old[3].replace('!pip install -q earthengine-api geemap', '!pip install -q earthengine-api geemap rasterio pyarrow'), 3)

# ---------------------------------------------------------------- konfigurasi baru
md("## 1a. Mode eksekusi, lingkungan, dan path (v27)\n\nSemua path terpusat di kamus `PATHS`. Mode default `USE_CACHED_DATA` tidak menyentuh GEE.", 'new')
code(rd('cfg'), 'new')
md("## 1b. Preamble Google Colab / Drive (v27)\n\nHanya aktif di Colab. Preamble Kaggle (cell import di bawah) dipertahankan.", 'new')
code(rd('colab'), 'new')

# ---------------------------------------------------------------- 4 : preamble Kaggle (edit lokal)
s4 = old[4]
a, mid, b = cut(s4, "# Direktori output: Colab Drive jika berjalan di Colab", "os.makedirs(OUTPUT_DIR, exist_ok=True)\n", include_end=True)
s4 = a + ("# v27: OUTPUT_DIR berasal dari konfigurasi terpusat (cell 1a). Mount Drive Colab ada di cell 1b.\n"
          "# PENTING (tetap berlaku): jangan import google.colab di Kaggle, karena geemap mendeteksi\n"
          "# keberadaan modul 'google.colab' sebagai tanda lingkungan Colab dan akan mencoba mengambil secret.\n"
          "OUTPUT_DIR = PATHS['outputs']\n"
          "os.makedirs(OUTPUT_DIR, exist_ok=True)\n") + b
# import ee/geemap hanya bila GEE diperlukan
old_imp = "import ee\nimport geemap\n"
assert s4.count(old_imp) == 1
s4 = s4.replace(old_imp, "# v27: mode cached TIDAK mengimpor ee/geemap (tanpa autentikasi dan tanpa koneksi GEE).\n"
                "if GEE_REQUIRED:\n    import ee\n    import geemap\nelse:\n    ee = None\n    geemap = None\n")
# patch geemap (Kaggle) hanya saat GEE dipakai
i0 = s4.index("# Kaggle: geemap mendeteksi modul")
i1 = s4.index("import numpy as np")
patch = s4[i0:i1]
s4 = s4[:i0] + "if GEE_REQUIRED:\n" + indent(patch.rstrip('\n')) + "\n" + s4[i1:]
code(s4, 4)

code(rd('helpers'), 'new')
code(rd('maps_utils'), 'new')
code(rd('moran_utils'), 'new')

# ---------------------------------------------------------------- 5-6 : autentikasi
md(old[5], 5)
s6 = old[6]
old_c = "_key_candidates = [\n"
assert s6.count(old_c) == 1
s6 = s6.replace("_initialized = False\n",
                "_key_candidates.insert(0, PATHS['sa_json'])   # v27: path Colab/Drive dari konfigurasi terpusat\n_initialized = False\n")
s6_tail = """

# v27: periksa akses project GEE dan catat identitas/versi aset (masuk manifest).
GEE_ASSET_IDS = ['FAO/GAUL/2015/level2', 'COPERNICUS/S1_GRD', 'COPERNICUS/S2_SR_HARMONIZED',
                 'USGS/SRTMGL1_003', 'COPERNICUS/DEM/GLO30', 'JAXA/ALOS/AW3D30/V4_1',
                 'UCSB-CHG/CHIRPS/DAILY', 'ESA/WorldCover/v200', 'MERIT/Hydro/v1_0_1',
                 'JRC/GSW1_4/GlobalSurfaceWater']


def check_gee_access():
    try:
        assert ee.Number(1).add(1).getInfo() == 2
    except Exception as e:
        raise RuntimeError('Project GEE tidak bisa menjalankan komputasi. Periksa registrasi Earth Engine, '
                           f'role Service Usage Consumer, dan project "{EE_PROJECT}". Pesan: {e}')
    for aid in GEE_ASSET_IDS:
        try:
            info = ee.data.getAsset(aid)
            GEE_ASSET_INFO[aid] = {'status': 'OK', 'type': info.get('type'),
                                   'updateTime': info.get('updateTime'), 'version': info.get('version'),
                                   'title': (info.get('properties') or {}).get('title')}
        except Exception as e:
            GEE_ASSET_INFO[aid] = {'status': 'ERROR', 'error': str(e)[:300]}
        print(f'  aset {aid}: {GEE_ASSET_INFO[aid]["status"]}')


check_gee_access()
"""
code("GEE_ASSET_INFO = {}   # v27: diisi bila GEE dipakai\n" +
     guard('GEE_REQUIRED', s6 + s6_tail,
           "else:\n    print('Mode cached: autentikasi dan koneksi GEE dilewati (tidak diperlukan).')\n"), 6)

# ---------------------------------------------------------------- 7-8 : parameter
md(old[7], 7)
s8 = old[8]
pre, roi_blk, post = cut(s8, "wilayah_indonesia = ee.FeatureCollection(", "# Kejadian banjir: sama dengan baseline")
s8a = pre + post.replace("# Random Forest DIKUNCI", "# v27: daftar seed multi-seed dipindah ke sini (nilai sama dengan v26) agar tersedia di semua mode.\nSEEDS_MULTI = [42, 100, 2024, 7, 99]\n\n# Random Forest DIKUNCI", 1)
assert 'SEEDS_MULTI' in s8a
code(s8a, 8)
code("# v27: pembentukan ROI memanggil GEE -> hanya di mode GEE.\n" + guard('GEE_REQUIRED', roi_blk), '8b')
code("# v27: inisialisasi manifest (PREPARE_DATA). Mode lain tidak menulis manifest ini.\n"
     "if RUN_MODE == 'PREPARE_DATA':\n    init_prepare_manifest()\n    manifest_update(gee_assets=GEE_ASSET_INFO)\n"
     "    print('manifest.json diinisialisasi:', PATHS['manifest'])\n", 'new')

# ---------------------------------------------------------------- 9-22
md(old[9], 9)
code(old[10], 10)
md(old[11], 11)
code(guard('GEE_REQUIRED', old[12]), 12)
md(old[13], 13)
code(guard("RUN_MODE == 'PREPARE_DATA'", old[14]), 14)
md(old[15], 15)
code(guard('GEE_REQUIRED', old[16]), 16)
md(old[17], 17)
code(guard('GEE_REQUIRED', old[18]), 18)
md(old[19], 19)
code(guard("RUN_MODE == 'PREPARE_DATA'", old[20], "    freeze_gee_table('dem_stats.csv')   # v27: bekukan tabel statistik DEM hasil GEE\n"), 20)
md(old[21], 21)
code(guard("RUN_MODE == 'PREPARE_DATA'", old[22]), 22)
md(old[23], 23)

# ---------------------------------------------------------------- 24 : unduh+bekukan vs bersihkan
s24 = old[24]
i_df = s24.index("df = geemap.ee_to_df(sample_fc)\n")
part1 = s24[:i_df]
part2 = s24[i_df + len("df = geemap.ee_to_df(sample_fc)\n"):]
s24a = part1 + """df = geemap.ee_to_df(sample_fc)

# v27: PEMBEKUAN tabel mentah hasil GEE (urutan baris GEE dipertahankan).
def gee_provenance():
    # Identitas koleksi yang dipakai: jumlah dan hash daftar ID (mendeteksi drift aset GEE).
    def _ids(col):
        ids = col.aggregate_array('system:index').getInfo()
        return {'n': len(ids), 'ids_sha256': hashlib.sha256('|'.join(sorted(ids)).encode()).hexdigest()}
    def _s1(a, b):
        return (ee.ImageCollection('COPERNICUS/S1_GRD').filterBounds(roi).filterDate(a, b)
                .filter(ee.Filter.eq('instrumentMode', 'IW'))
                .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
                .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH')))
    prov = {'s1_before': _ids(_s1(BEFORE_START, BEFORE_END)),
            's1_after': _ids(_s1(AFTER_START, AFTER_END)),
            's2_composite': _ids(ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').filterBounds(roi)
                                 .filterDate(S2_START, S2_END)
                                 .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 60)))}
    for k, d in (('chirps_7d', 7), ('chirps_30d', 30)):
        prov[k] = _ids(ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY')
                       .filterDate(ee.Date(AFTER_START).advance(-d, 'day'), AFTER_START).filterBounds(roi))
    return prov

manifest_update(config=config_snapshot(),
                required_columns=list(predictor_bands_all),
                gee_provenance=gee_provenance())
freeze_table(df, 'main', PATHS['frozen_main'], extra={
    'kind': 'main_evaluation', 'seed': RANDOM_STATE,
    'source': 'sample_fc (balancing di GEE) -> geemap.ee_to_df; urutan baris GEE dipertahankan',
    'gee_counts': {'raw_hist': raw_hist, 'final_hist': final_hist,
                   'sample_per_class_final': int(SAMPLE_PER_CLASS_FINAL)}})
validate_artifacts(['main'])
"""
code(guard("RUN_MODE == 'PREPARE_DATA'", s24a), '24a')
code("# =====================================================================\n"
     "# v27 - VALIDASI ARTEFAK BEKU sebelum evaluasi (file ada, SHA-256, baris, kolom, tipe, nilai kosong).\n"
     "# Gagal -> berhenti dengan pesan jelas. TIDAK ada pengambilan data GEE otomatis.\n"
     "# =====================================================================\n"
     "if RUN_MODE == 'USE_CACHED_DATA':\n    validate_artifacts('all')\n"
     "else:\n    print('Validasi penuh dilakukan di akhir PREPARE_DATA (setelah multi-seed) atau tidak diperlukan (PREPARE_MAPS).')\n", 'new')
s24b = "df = get_frozen('main')   # v27: tabel mentah GEE dari file beku (bukan dari GEE)\n" + part2.rstrip('\n') + \
       "\n\nrecord_or_check_fingerprint('main', X_all, y)   # v27: sidik jari data terproses\n"
code(guard('RUN_EVALUATION', s24b), '24b')

# ---------------------------------------------------------------- 25-30
md(old[25], 25)
code(guard('RUN_EVALUATION', old[26]), 26)
md(old[27], 27)
code(guard('RUN_EVALUATION', old[28]), 28)
md(old[29], 29)
code(guard('RUN_EVALUATION', old[30]), 30)
md("""## 13b. Diagnostik autokorelasi spasial: Global Moran's I (v27)

Dua analisis pendukung pada **titik sampel** (bukan 16 blok): (a) probabilitas OOF dan (b) residual OOF
(label aktual dikurangi probabilitas OOF) dari spatial CV evaluasi utama. Weights: kNN (k = 8), row-standardized,
jarak dalam meter (UTM 49S), **satu definisi yang sama untuk ketiga DEM**. p-value berbasis permutasi kondisional
(9.999 permutasi, seed 42). Ini diagnostik pendukung. Moran's I tidak menghilangkan dan tidak membuktikan
ketiadaan *spatial leakage*, karena pencegahan leakage bergantung pada desain evaluasi spasial.""", 'new')
code(guard('RUN_EVALUATION', rd('moran_oof')), 'new')

# ---------------------------------------------------------------- 31 : multi-seed
s31 = old[31]
assert s31.count("SEEDS_MULTI = [42, 100, 2024, 7, 99]\n") == 1
s31 = s31.replace("SEEDS_MULTI = [42, 100, 2024, 7, 99]\n", "# SEEDS_MULTI didefinisikan di cell parameter (v27).\n")
# 31a: ekstraksi GEE + pembekuan
m0 = "        locs_s = (label_for_sampling.rename('flood').stratifiedSample("
m1 = "        df_s = geemap.ee_to_df(sample_fc_s)\n"
i0 = s31.index(m0)
i1 = s31.index(m1) + len(m1)
extract = s31[i0:i1]
s31a = ("_seed_failed = {}\nfor _sd in SEEDS_MULTI:\n    try:\n" + extract +
        "        freeze_table(df_s, f'seed_{_sd}', PATHS['frozen_multiseed'], extra={\n"
        "            'kind': 'multiseed', 'seed': int(_sd),\n"
        "            'source': 'stratifiedSample(seed) + sampleRegions + notNull -> geemap.ee_to_df (tanpa balancing; balancing di pandas saat evaluasi)',\n"
        "            'gee_counts': {'flood_raw': _n1, 'nonflood_raw': _n0}})\n"
        "    except Exception as e:\n"
        "        _seed_failed[_sd] = str(e)\n"
        "        print(f'[seed {_sd}] GAGAL dibekukan: {e}')\n"
        "if _seed_failed:\n"
        "    print('SEED GAGAL:', list(_seed_failed), '-> artefak multi-seed TIDAK lengkap; validasi di bawah akan menolak.')\n"
        "validate_artifacts('all')   # seluruh dataset beku (main + 5 seed) harus utuh sebelum evaluasi\n")
code("# ------------------------------------------------------------------\n"
     "# v27 - EKSTRAKSI GEE MULTI-SEED + PEMBEKUAN (hanya PREPARE_DATA).\n"
     "# Kode sampling di bawah disalin dari cell multi-seed v26 tanpa perubahan.\n"
     "# ------------------------------------------------------------------\n" +
     guard("RUN_MODE == 'PREPARE_DATA'", s31a), '31a')
# 31b: evaluasi dari tabel beku
new_load = ("        df_s = get_frozen(f'seed_{_sd}')   # v27: tabel mentah GEE seed ini dari file beku\n"
            "        print(f'[seed {_sd}] baris beku mentah: {len(df_s)} | catatan GEE: '\n"
            "              f'{MANIFEST[\"datasets\"][f\"seed_{_sd}\"].get(\"gee_counts\")}')\n")
s31b = s31[:i0] + new_load + s31[i1:]
marker = "        X_s, y_s, dd_s = _clean_sample_df(df_s, _sd)\n"
assert s31b.count(marker) == 1
s31b = s31b.replace(marker, marker + "        record_or_check_fingerprint(f'seed_{_sd}', X_s, y_s)   # v27\n")
code(guard('RUN_EVALUATION', s31b), '31b')

# ---------------------------------------------------------------- 32-33
md(old[32], 32)
code(guard('RUN_EVALUATION', old[33]), 33)

# ---------------------------------------------------------------- 34-35 : peta GEE
md(old[34] + "\n\n**v27:** hanya di mode `PREPARE_MAPS`. RF GEE dilatih pada `sample_fc` yang DIBENTUK ULANG dari tabel mentah utama yang dibekukan (koordinat, label, fitur, urutan baris), bukan dari sampling baru.", 34)
s35_pre = '''validate_artifacts(['main'])
_raw_main = get_frozen('main')

def build_sample_fc_from_frozen(df):
    # Bentuk ee.FeatureCollection dari tabel beku. Nilai dikirim sebagai daftar angka (ringkas),
    # urutan baris dipertahankan. TIDAK ada sampling/ekstraksi GEE.
    prop_cols = [c for c in df.columns if c not in ('system:index', '.geo')]
    needed = ['flood', 'lon', 'lat'] + list(fixed_bands) + [c for n in DEM_NAMES for c in dem_cols(n)]
    miss = [c for c in needed if c not in prop_cols]
    if miss:
        raise FrozenDataError(f'Tabel beku utama tidak memuat kolom yang dibutuhkan peta: {miss}')
    if df[prop_cols].isna().any().any():
        raise FrozenDataError('Tabel beku utama memuat nilai kosong pada kolom properti (tidak sesuai sample_fc v26).')
    int_cols = {'flood', 'landcover'}
    rows = [[int(v) if c in int_cols else float(v) for c, v in zip(prop_cols, rec)]
            for rec in df[prop_cols].itertuples(index=False, name=None)]
    names = ee.List(prop_cols)
    fc = ee.FeatureCollection(ee.List(rows).map(
        lambda r: ee.Feature(None, ee.Dictionary.fromLists(names, ee.List(r)))))
    return fc, prop_cols

sample_fc, _prop_cols = build_sample_fc_from_frozen(_raw_main)

# Bukti identitas observasi: jumlah, dan SEMUA kolom (koordinat, label, fitur) persis sama dan berurutan sama.
_n_fc = int(sample_fc.size().getInfo())
if _n_fc != len(_raw_main):
    raise FrozenDataError(f'sample_fc GEE {_n_fc} baris != tabel beku {len(_raw_main)} baris.')
_bad_cols = []
for _c in _prop_cols:
    _srv = np.array(sample_fc.aggregate_array(_c).getInfo(), dtype='float64')
    if not np.array_equal(_srv, _raw_main[_c].to_numpy(dtype='float64')):
        _bad_cols.append(_c)
if _bad_cols:
    raise FrozenDataError(f'sample_fc GEE tidak identik dengan tabel beku pada kolom: {_bad_cols}')
print(f'sample_fc terverifikasi identik dengan tabel beku utama: {_n_fc} baris, '
      f'{len(_prop_cols)} kolom (koordinat, label, fitur, urutan baris).')
SAMPLE_FC_VERIFICATION = {'n_rows': _n_fc, 'n_columns_verified': len(_prop_cols),
                          'order_preserved': True,
                          'frozen_main_sha256': MANIFEST['datasets']['main']['sha256_parquet']}

'''
s35_post = "\nmanifest_update(maps={'breaks': [float(b) for b in BREAKS], 'risk_class_method': RISK_CLASS_METHOD,\n                      'rf_gee': RF_GEE, 'sample_fc_verification': SAMPLE_FC_VERIFICATION})\n"
code(guard("RUN_MODE == 'PREPARE_MAPS'", s35_pre + old[35] + s35_post), 35)

md(old[36], 36)
# 37 : widget interaktif geemap + thumbnail (default MATI)
s37 = old[37]
_i = s37.index("# Bonus: figure statis PNG untuk artikel.")
a37, b37 = s37[:_i], s37[_i:].rstrip()
assert b37.endswith("Map2"); b37 = b37[:-4]
code("# v27: peta interaktif geemap dan thumbnail dimatikan secara default (ENABLE_GEE_INTERACTIVE / ENABLE_GEE_THUMBNAILS).\n"
     "# v26: widget tidak tersimpan di output Kaggle dan getThumbURL gagal HTTP 400 untuk citra hasil RF.\n"
     "# Peta final dibaca lokal dari GeoTIFF (cell visualisasi lokal di bawah).\n" +
     guard("RUN_MODE == 'PREPARE_MAPS' and ENABLE_GEE_INTERACTIVE",
           a37 + "if ENABLE_GEE_THUMBNAILS:\n" + indent(b37.rstrip('\n')) + "\nMap2\n"), 37)

# ---------------------------------------------------------------- 38-42
md(old[38], 38)
code(guard("RUN_MODE == 'PREPARE_MAPS'", old[39]), 39)
s40 = old[40]
a40, b40, _ = cut(s40, "# --- Peta interaktif delta probabilitas dan kesesuaian ---")
_j = b40.index("# Bonus: figure statis PNG untuk artikel.")
c0, c1 = b40[:_j], b40[_j:].rstrip()
assert c1.endswith("Map3"); c1 = c1[:-4]
code(guard("RUN_MODE == 'PREPARE_MAPS'", a40) +
     "\n" + guard("RUN_MODE == 'PREPARE_MAPS' and ENABLE_GEE_INTERACTIVE",
                  c0 + "if ENABLE_GEE_THUMBNAILS:\n" + indent(c1.rstrip('\n')) + "\nMap3\n"), 40)
md(old[41], 41)
code(guard("RUN_MODE == 'PREPARE_MAPS'", old[42]), 42)
code("# v27: mode cached menampilkan tabel statistik spasial BEKU (hasil GEE dari PREPARE_MAPS), checksum diperiksa.\n"
     "if RUN_MODE == 'USE_CACHED_DATA':\n"
     "    for _f in ['sensitivity_summary.csv', 'area_per_risk_class_km2.csv', 'worldcover_sensitivity.csv',\n"
     "               'transition_srtm_vs_glo30.csv', 'transition_srtm_vs_aw3d30.csv', 'transition_glo30_vs_aw3d30.csv']:\n"
     "        _t = load_gee_table(_f)\n"
     "        if _t is not None:\n"
     "            print('==', _f)\n"
     "            print(_t.head(12).to_string(index=False))\n", 'new')

# ---------------------------------------------------------------- 43-44 : ekspor
md(old[43] + "\n\n**v27:** ekspor peta memakai unduhan langsung per tile (`computePixels`) dengan status `PENDING/RUNNING/COMPLETED/FAILED` di `data/export_status.json`. Kode `Export.toDrive` v26 dipertahankan di cell berikutnya, nonaktif secara default.", 43)
code(rd('gee_export'), 'new')
code("# v26 (LEGACY, nonaktif): Export.toDrive oleh service account. Aktifkan hanya dengan EXPORT_TO_DRIVE_LEGACY = True.\n" +
     guard("EXPORT_TO_DRIVE_LEGACY and RUN_MODE == 'PREPARE_MAPS'", old[44]), 44)
md("## 18b. Visualisasi lokal peta dari GeoTIFF (v27)\n\nMembaca `data/rasters/*.tif`. Tidak memanggil GEE dan bekerja di Kaggle maupun Colab.", 'new')
code(rd('viz'), 'new')
md("## 18c. Global Moran's I pada peta probabilitas (v27)\n\nMembaca GeoTIFF probabilitas per DEM. Jika raster belum tersedia, hasil dinyatakan belum tersedia (tidak dihitung).", 'new')
code(rd('moran_map'), 'new')

# ---------------------------------------------------------------- 45-46 + laporan
md(old[45], 45)
md(old[46], 46)
md(r"""## 20b. Metodologi tambahan: autokorelasi spasial, spatial leakage, dan Global Moran's I (v27)

**Autokorelasi spasial.** Nilai pada lokasi yang berdekatan cenderung lebih mirip daripada lokasi yang berjauhan. Pada data banjir hal ini wajar, karena genangan, elevasi, dan jarak ke sungai berubah secara kontinu di ruang. Akibatnya amatan tidak saling bebas dan pembagian data acak (random split) cenderung memberi estimasi kinerja yang terlalu optimistis.

**Spatial leakage.** Kebocoran spasial terjadi saat data uji berdekatan dengan data latih sehingga model dapat "mengingat" lingkungan lokasi uji dan bukan mempelajari hubungan yang dapat digeneralisasi. **Spatial cross-validation** (16 blok kuantil lon/lat, 4 fold, retrain per fold) mengurangi risiko ini dengan memisahkan blok uji dari blok latih. Pencegahan leakage bergantung pada rancangan pembagian spasial itu, bukan pada uji statistik apa pun. Blok yang bersebelahan tidak diberi zona penyangga (buffer), sehingga titik di tepi blok tetap dapat dekat dengan data latih.

**Global Moran's I (diagnostik pendukung).** Untuk nilai $x_i$ pada $n$ lokasi dengan bobot spasial $w_{ij}$ (distandardisasi baris, $S_0=\sum_{ij}w_{ij}=n$) dan $z_i=x_i-\bar{x}$:

$$I=\frac{n}{S_0}\,\frac{\sum_{i}\sum_{j}w_{ij}z_iz_j}{\sum_i z_i^2},\qquad E[I]=-\frac{1}{n-1}.$$

* Hipotesis: $H_0$: nilai tersebar acak secara spasial (tidak ada autokorelasi spasial), $H_1$: ada autokorelasi spasial (dua sisi).
* Taraf signifikansi $\alpha=0{,}05$. **Tolak $H_0$ jika $p$-value lebih kecil dari $\alpha$.**
* $p$-value berbasis **permutasi kondisional**: nilai diacak lintas lokasi tetap sebanyak $B=9.999$ kali (seed 42), $p=\dfrac{1+\#\{|I_{perm}-E[I]|\ge|I_{obs}-E[I]|\}}{B+1}$, sehingga $p$ terkecil yang dapat dilaporkan adalah $1/(B+1)=0{,}0001$. Untuk peta raster dipakai $B=999$.
* Data yang dianalisis: (a) probabilitas OOF dan (b) residual OOF $r_i=y_i-\hat{p}^{OOF}_i$ pada titik sampel, serta (c) peta probabilitas raster per DEM. Prediksi data latih tidak dipakai.
* Unit analisis adalah titik sampel, bukan 16 blok (satu blok hanya berisi 1 titik dan beberapa blok tidak memuat salah satu kelas, sehingga agregasi ke 16 unit tidak layak). Weights kNN ($k=8$, uji kepekaan $k=5,12$) dipilih karena titik tersebar tidak beraturan dengan kepadatan berbeda dan kNN menjamin tidak ada titik tanpa tetangga. Definisi weights **sama** untuk ketiga DEM.
* Hasil tidak signifikan tidak boleh dibaca sebagai bukti tidak ada autokorelasi. Moran's I tidak menghilangkan dan tidak membuktikan ketiadaan spatial leakage.""", 'new')
md("## 21. Laporan pembanding v26 vs v27 (v27)\n\nMembandingkan `outputs/` dengan `data/reference_v26/` per komponen. Komponen tanpa hasil dinyatakan **BELUM DIUJI**, bukan lolos.", 'new')
code(rd('report'), 'new')

# ---------------------------------------------------------------- rakit
out = copy.deepcopy(nb)
out['cells'] = []
used = set()
for typ, src, origin in cells:
    cid = uuid.uuid5(uuid.NAMESPACE_URL, f'{len(out["cells"])}-{origin}').hex[:12]
    assert cid not in used
    used.add(cid)
    c = {'cell_type': typ, 'id': cid, 'metadata': {}, 'source': src.splitlines(keepends=True)}
    if typ == 'code':
        c['execution_count'] = None
        c['outputs'] = []
    out['cells'].append(c)
out['nbformat'], out['nbformat_minor'] = 4, 5
json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('cells v26:', len(old), '-> v27:', len(out['cells']))
json.dump([(t, o) for t, _, o in cells], open(OUT + '.map.json', 'w'))
