"""T6: uji logika ekspor raster (tile, mosaik, status, verifikasi grid/NoData) dengan fetch PALSU.
Raster sintetis HANYA untuk menguji kode. Bukan data penelitian. Tidak ada GEE."""
import sys, os, io, json, shutil, tempfile
sys.path.insert(0, '.')
import harness as H, numpy as np, pandas as pd
import rasterio
from rasterio.io import MemoryFile
from rasterio.transform import from_origin

root = tempfile.mkdtemp(prefix='ras_') + '/Analisis Flood DEM Susceptibility'
os.makedirs(root + '/data')
cells = H.load_cells()
ns = H.base_ns(root, 'USE_CACHED_DATA')
H.run_cells(ns, cells, upto_pred=lambda o: o == 6)
H.run_cells(ns, [c for c in cells if c[1] in (8, 10)])   # parameter + cell bantu v26 (PROB_VIS dll)
ns['MAP_TILE_PX'] = 256
NOD = ns['EXPORT_NODATA']

# --- grid dan medan sintetis (elips = AOI; DEM aw3d30 punya lubang void) ---
GRID = ns['make_grid'](500_010.0, 9_200_005.0, 500_010.0 + 29.5 * 900, 9_200_005.0 + 29.5 * 700)
H_, W_ = GRID['height'], GRID['width']
assert GRID['x0'] % 30 == 0 and GRID['y1'] % 30 == 0
yy, xx = np.mgrid[0:H_, 0:W_]
aoi = ((xx - W_ / 2) / (W_ / 2.05)) ** 2 + ((yy - H_ / 2) / (H_ / 2.05)) ** 2 < 1
base = 1 / (1 + np.exp(-(np.sin(xx / 90.0) + np.cos(yy / 120.0))))
prob = {'srtm': np.clip(base, 0, 1), 'glo30': np.clip(base + 0.03 * np.sin(xx / 40.0), 0, 1),
        'aw3d30': np.clip(base - 0.03 * np.cos(yy / 50.0), 0, 1)}
valid = {d: aoi.copy() for d in prob}
valid['aw3d30'][100:140, 200:260] = False          # void ALOS: mask DEM berbeda (harus dilaporkan INFO)
BR = [0.2, 0.4, 0.6, 0.8]
ns['BREAKS'] = BR
ns['RF_GEE'] = {'numberOfTrees': 300}
risk = {d: 1 + (prob[d] > BR[0]).astype(int) + (prob[d] > BR[1]) + (prob[d] > BR[2]) + (prob[d] > BR[3]) for d in prob}
FULL = {}
for d in prob:
    p32 = prob[d].astype('float32')
    FULL[f'prob_{d}'] = (p32, 'prob', valid[d])
    FULL[f'risk_class_{d}'] = (risk[d].astype('float32'), 'risk', valid[d])
for a, b in ns['MAP_PAIRS']:
    m = valid[a] & valid[b]
    FULL[f'delta_abs_{a}_vs_{b}'] = (np.abs(prob[a].astype('float32') - prob[b].astype('float32')), 'delta', m)
    FULL[f'agreement_{a}_vs_{b}'] = ((risk[a] == risk[b]).astype('float32'), 'agreement', m)
FULL['proxy_flood_label_sentinel1'] = ((base > 0.5).astype('float32'), 'label', aoi)

MODE = {'fault': None}


def make_fetch(name):
    arr, kind, m = FULL[name]
    full = np.where(m, arr, NOD).astype('float32')

    def fetch(image, tile):
        r0, c0, th, tw = tile['row_off'], tile['col_off'], tile['height'], tile['width']
        sub = full[r0:r0 + th, c0:c0 + tw]
        tx, ty = tile['x0'], tile['y1']
        if MODE['fault'] == 'shift' and name == 'prob_glo30' and r0 == 0 and c0 == 0:
            tx += 30.0                                   # geser 1 piksel
        if MODE['fault'] == 'short' and name == 'prob_glo30' and r0 == 0 and c0 == 0:
            sub = sub[:-1]; th -= 1                      # tile kurang 1 baris (celah)
        with MemoryFile() as mf:
            with mf.open(driver='GTiff', height=th, width=tw, count=1, dtype='float32', crs=GRID['crs'],
                         transform=from_origin(tx, ty, GRID['res'], GRID['res'])) as ds:
                ds.write(sub, 1)
            return mf.read()
    return fetch


def export_all(names):
    for n in names:
        ns['export_raster'](n, FULL[n][1], n, GRID, make_fetch(n))


def st(n):
    return ns['status_load']()['rasters'][n]


# 1. patahan: geser 1 piksel -> FAILED dengan pesan grid
MODE['fault'] = 'shift'; export_all(['prob_glo30'])
assert st('prob_glo30')['status'] == 'FAILED' and 'Grid tile tidak sesuai' in st('prob_glo30')['error']
print('OK geser 1 piksel terdeteksi ->', st('prob_glo30')['error'][:90])
# 2. patahan: tile kurang 1 baris -> FAILED
MODE['fault'] = 'short'; export_all(['prob_glo30'])
assert st('prob_glo30')['status'] == 'FAILED'
print('OK tile pendek terdeteksi ->', st('prob_glo30')['error'][:90])
# 3. mosaik dengan tile hilang -> celah terdeteksi langsung
tiles = ns['grid_tiles'](GRID, 256)
arrs = [(t, np.zeros((t['height'], t['width']), 'float32')) for t in tiles[:-1]]
try:
    ns['mosaic_tiles'](arrs, GRID); raise SystemExit('GAGAL: celah tidak terdeteksi')
except RuntimeError as e:
    assert 'celah' in str(e); print('OK celah mosaik terdeteksi ->', str(e)[:80])
arrs2 = arrs + [(tiles[0], np.zeros((tiles[0]['height'], tiles[0]['width']), 'float32'))] + [(tiles[-1], np.zeros((tiles[-1]['height'], tiles[-1]['width']), 'float32'))]
try:
    ns['mosaic_tiles'](arrs2, GRID); raise SystemExit('GAGAL: tumpang tindih tidak terdeteksi')
except RuntimeError as e:
    assert 'tumpang tindih' in str(e); print('OK tumpang tindih terdeteksi')
# 4. jalur normal untuk semua raster (statusnya harus COMPLETED)
MODE['fault'] = None
print('jumlah tile per raster:', len(tiles), '| grid', GRID['width'], 'x', GRID['height'])
export_all(list(FULL))
stt = ns['status_load']()['rasters']
assert all(stt[n]['status'] == 'COMPLETED' for n in FULL), {n: stt[n]['status'] for n in FULL}
print('OK 13 raster COMPLETED (FAILED sebelumnya ditimpa setelah perbaikan)')
# 5. mosaik == sumber persis (tidak ada pergeseran)
for n in ['prob_srtm', 'prob_glo30', 'delta_abs_srtm_vs_glo30']:
    with rasterio.open(root + f'/data/rasters/{n}.tif') as ds:
        got = ds.read(1)
    arr, kind, m = FULL[n]
    exp = np.where(m, arr, NOD).astype('float32')
    assert np.array_equal(got, exp), n
print('OK isi GeoTIFF hasil mosaik IDENTIK piksel-demi-piksel dengan sumber (tidak ada pergeseran/celah)')
# 6. lanjut/skip bila sudah COMPLETED
before = st('prob_srtm')['finished_at_utc']
export_all(['prob_srtm']); assert st('prob_srtm')['finished_at_utc'] == before; print('OK raster COMPLETED dilewati saat dijalankan ulang')
# 7. verifikasi menyeluruh
checks = ns['verify_all_rasters'](GRID, int(valid['srtm'].sum()))
nf = ns['print_checks'](checks)
assert nf == 0, 'ada FAIL pada jalur normal'
assert any(c['check'].startswith('nodata_antar_DEM') and c['status'] == 'INFO' for c in checks)
print('OK verifikasi menyeluruh: 0 FAIL; beda mask NoData antar DEM dilaporkan sebagai INFO')
# 8. korupsi terdeteksi: agreement dirusak
p = root + '/data/rasters/agreement_srtm_vs_glo30.tif'
with rasterio.open(p, 'r+') as ds:
    a = ds.read(1); a[300:310, 300:310] = 1 - a[300:310, 300:310]; ds.write(a, 1)
checks = ns['verify_all_rasters'](GRID, None)
assert any(c['status'] == 'FAIL' and 'sha' in c['detail'].lower() or c['status'] == 'FAIL' for c in checks)
print('OK raster yang diubah setelah ekspor terdeteksi (SHA-256 berbeda)')
# 9. raster dengan transform berbeda terdeteksi oleh verify_raster
alt = dict(GRID); alt['x0'] += 30
try:
    ns['verify_raster'](root + '/data/rasters/prob_srtm.tif', alt, 'prob'); raise SystemExit('GAGAL')
except RuntimeError as e:
    assert 'transform' in str(e); print('OK transform/extent berbeda terdeteksi')
# 10. visualisasi lokal + Moran peta (B kecil)
# pulihkan raster rusak lalu jalankan
shutil.copy(root + '/data/rasters/agreement_srtm_vs_glo30.tif', root + '/data/rasters/_rusak.tif'); os.remove(root + '/data/rasters/_rusak.tif')
ns['OVERWRITE_RASTERS'] = True; export_all(['agreement_srtm_vs_glo30']); ns['OVERWRITE_RASTERS'] = False
ns['MORAN_B_MAP'] = 19
viz_src = [c for c in cells if c[0] == 'code' and 'def show_local_maps' in c[2]][0][2]
mm_src = [c for c in cells if c[0] == 'code' and 'def run_moran_map' in c[2]][0][2]
exec(compile(viz_src, 'viz', 'exec'), ns)
assert ns['LOCAL_MAPS_SHOWN'] is True and os.path.isfile(root + '/outputs/maps_local/local_prob_maps.png')
print('OK visualisasi lokal membaca GeoTIFF dan menyimpan PNG')
exec(compile(mm_src, 'mm', 'exec'), ns)
print(ns['moran_map_df'][['dem', 'n', 'I', 'E_I', 'n_perm', 'p_two_sided']].round(4).to_string(index=False))
print('SEMUA UJI RASTER LULUS')
