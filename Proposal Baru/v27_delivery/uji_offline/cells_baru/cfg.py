# =========================================================
# v27 - KONFIGURASI TERPUSAT: lingkungan, mode eksekusi, path.
# Semua path dibaca dari kamus PATHS. Jangan menulis path di cell lain.
# =========================================================
import os, sys, json, glob

# --- 1. MODE EKSEKUSI ------------------------------------------------
#   'USE_CACHED_DATA' : DEFAULT. Membaca dataset beku dan menjalankan seluruh
#                       evaluasi. TIDAK ada autentikasi dan TIDAK ada koneksi GEE.
#   'PREPARE_DATA'    : GEE -> sampling utama + multi-seed -> bekukan -> manifest
#                       + checksum. Evaluasi lalu dijalankan dari file beku.
#   'PREPARE_MAPS'    : GEE -> latih RF GEE (300 pohon) pada sampel utama beku ->
#                       GeoTIFF + status ekspor. TIDAK melakukan sampling ulang.
RUN_MODE = 'USE_CACHED_DATA'
RUN_MODE = os.environ.get('FLOOD_DEM_RUN_MODE', RUN_MODE)   # override untuk run tanpa UI

_VALID_MODES = ('USE_CACHED_DATA', 'PREPARE_DATA', 'PREPARE_MAPS')
if RUN_MODE not in _VALID_MODES:
    raise ValueError(f'RUN_MODE={RUN_MODE!r} tidak dikenal. Pilih salah satu dari {_VALID_MODES}.')

GEE_REQUIRED = RUN_MODE in ('PREPARE_DATA', 'PREPARE_MAPS')   # hanya dua mode ini yang menyentuh GEE
RUN_EVALUATION = RUN_MODE != 'PREPARE_MAPS'                   # evaluasi RF selalu dari data beku

# Perlindungan artefak: PREPARE_DATA menolak menimpa dataset beku yang sudah ada,
# PREPARE_MAPS melewati raster yang sudah berstatus COMPLETED (bisa dilanjutkan).
OVERWRITE_FROZEN = False
OVERWRITE_RASTERS = False

# Parameter ekspor peta (PREPARE_MAPS).
EXPORT_NODATA = -9999.0
MAP_TILE_PX = 1024            # ukuran tile unduhan (piksel). Perkecil jika GEE menolak karena kompleksitas.

# Opsi lama (v26) yang terbukti gagal/boros di Kaggle. Default MATI, kode lama dipertahankan.
ENABLE_GEE_INTERACTIVE = False   # geemap.Map (ipyleaflet) tidak tersimpan di output Kaggle
ENABLE_GEE_THUMBNAILS = False    # getThumbURL untuk citra hasil RF gagal HTTP 400 di v26
EXPORT_TO_DRIVE_LEGACY = False   # Export.toDrive oleh service account masuk ke Drive service account

# --- 2. DETEKSI LINGKUNGAN -------------------------------------------
def _detect_env():
    if os.path.isdir('/kaggle/working') or os.environ.get('KAGGLE_KERNEL_RUN_TYPE'):
        return 'kaggle'
    if (os.environ.get('COLAB_RELEASE_TAG') or os.environ.get('COLAB_GPU') is not None
            or 'google.colab' in sys.modules):
        return 'colab'
    return 'local'

ENV = _detect_env()

# --- 3. PATH TERPUSAT --------------------------------------------------
_ROOT_BY_ENV = {
    'colab':  '/content/drive/MyDrive/Analisis Flood DEM Susceptibility',
    'kaggle': '/kaggle/working/Analisis Flood DEM Susceptibility',
    'local':  os.path.abspath('Analisis Flood DEM Susceptibility'),
}
ROOT = os.environ.get('FLOOD_DEM_ROOT', _ROOT_BY_ENV[ENV])

def _build_paths(root, data_dir=None):
    data = data_dir or os.path.join(root, 'data')
    return {
        'root': root,
        'sa_json': os.path.join(root, 'gee-service-account.json'),
        'data': data,
        'frozen_main': os.path.join(data, 'frozen', 'main'),
        'frozen_multiseed': os.path.join(data, 'frozen', 'multiseed'),
        'gee_tables': os.path.join(data, 'gee_tables'),
        'rasters': os.path.join(data, 'rasters'),
        'reference_v26': os.path.join(data, 'reference_v26'),
        'manifest': os.path.join(data, 'manifest.json'),
        'export_status': os.path.join(data, 'export_status.json'),
        'outputs': os.path.join(root, 'outputs'),
        'maps_local': os.path.join(root, 'outputs', 'maps_local'),
    }

PATHS = _build_paths(ROOT)

# Kaggle, mode cached: folder data beku biasanya dipasang sebagai Kaggle Dataset
# (read-only) di /kaggle/input. Cari manifest.json milik proyek ini di sana.
DATA_READ_ONLY = False
if ENV == 'kaggle' and RUN_MODE == 'USE_CACHED_DATA' and not os.path.isfile(PATHS['manifest']):
    for _mp in sorted(glob.glob('/kaggle/input/**/manifest.json', recursive=True)):
        try:
            with open(_mp, 'r', encoding='utf-8') as _fh:
                if json.load(_fh).get('artifact_type') == 'flood_dem_frozen_data':
                    PATHS = _build_paths(ROOT, data_dir=os.path.dirname(_mp))
                    DATA_READ_ONLY = True
                    break
        except Exception:
            continue

def ensure_dirs():
    # Buat struktur folder. Folder data tidak disentuh bila read-only (Kaggle Dataset).
    keys = ['outputs', 'maps_local'] if DATA_READ_ONLY else \
           ['frozen_main', 'frozen_multiseed', 'gee_tables', 'rasters', 'reference_v26',
            'outputs', 'maps_local']
    for k in keys:
        os.makedirs(PATHS[k], exist_ok=True)

if ENV != 'colab':      # di Colab, folder dibuat setelah Drive di-mount (cell berikutnya)
    ensure_dirs()

print(f'Lingkungan : {ENV}')
print(f'Mode       : {RUN_MODE} | GEE diperlukan: {GEE_REQUIRED} | evaluasi: {RUN_EVALUATION}')
print(f'Root       : {PATHS["root"]}')
print(f'Data       : {PATHS["data"]}' + ('  (read-only, Kaggle Dataset)' if DATA_READ_ONLY else ''))
print(f'Outputs    : {PATHS["outputs"]}')
