"""Jalankan cell Moran (moran_utils + moran_oof, kode persis dari notebook) pada artefak v26:
training_sample_features.csv + spatial_cv_test_predictions.csv. Hasil = angka dari data v26, BUKAN dari tarikan GEE baru."""
import numpy as np, pandas as pd, time, os, sys
Z = '/tmp/claude-0/-home-claude/b722b6b3-0211-5390-b052-8e74f84418ea/scratchpad/zipx/'
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
t = pd.read_csv(Z + 'training_sample_features.csv', float_precision='round_trip')
p = pd.read_csv(Z + 'spatial_cv_test_predictions.csv', float_precision='round_trip')
ns = {'np': np, 'pd': pd, 'time': time, 'os': os,
      'data': t[['flood', 'lon', 'lat']].copy(), 'y': t['flood'].astype(int),
      'DEM_NAMES': ['srtm', 'glo30', 'aw3d30'], 'OUTPUT_DIR': OUT,
      'spatial_pred_rows': p.to_dict('records')}
# _block dan _folds: persis seperti cell 28 v26
lon, lat = t.lon.to_numpy(), t.lat.to_numpy()
lq = np.quantile(lon, [0.25, 0.5, 0.75]); tq = np.quantile(lat, [0.25, 0.5, 0.75])
ns['_block'] = np.digitize(lon, lq) + 4 * np.digitize(lat, tq)
sh = np.random.RandomState(42).permutation(np.unique(ns['_block']))
ns['_folds'] = [set(f.tolist()) for f in np.array_split(sh, 4)]
t0 = time.time()
exec(open('/tmp/claude-0/-home-claude/b722b6b3-0211-5390-b052-8e74f84418ea/scratchpad/build/cells/moran_utils.py').read(), ns)
exec(open('/tmp/claude-0/-home-claude/b722b6b3-0211-5390-b052-8e74f84418ea/scratchpad/build/cells/moran_oof.py').read(), ns)
print('waktu: %.0f s' % (time.time() - t0))
