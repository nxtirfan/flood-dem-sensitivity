import numpy as np, pandas as pd, time, sys
sys.path.insert(0, '/tmp/claude-0/-home-claude/b722b6b3-0211-5390-b052-8e74f84418ea/scratchpad/eelib')
ns = {'np': np, 'pd': pd, 'time': time}
exec(open('build/cells/moran_utils.py').read(), ns)
import esda, libpysal
from libpysal.weights import KNN, lat2W

rng = np.random.RandomState(1)
# 1. titik: I dan E[I] vs esda (kNN row-standardized)
xy = rng.rand(400, 2) * 10000
x = np.sin(xy[:, 0] / 1500) + rng.randn(400) * 0.3
nbr, _ = ns['knn_neighbors'](xy, 8)
r = ns['moran_points'](x, nbr, B=999, seed=1)
w = KNN.from_array(xy, k=8); w.transform = 'r'
m = esda.Moran(x, w, permutations=999)
print('titik  I mine=%.10f esda=%.10f | E mine=%.6f esda=%.6f' % (r['I'], m.I, r['E_I'], m.EI))
assert abs(r['I'] - m.I) < 1e-10 and abs(r['E_I'] - m.EI) < 1e-12
print('       perm_mean=%.5f (harus mendekati E[I]=%.5f) | p_dua_sisi=%.4f' % (r['perm_mean'], r['E_I'], r['p_two_sided']))

# 2. raster penuh vs esda lattice queen
H, W = 30, 40
g = np.add.outer(np.arange(H), np.arange(W)).astype(float) + rng.randn(H, W) * 3
valid = np.ones((H, W), bool)
rr = ns['moran_raster'](g, valid, B=199, seed=1)
w2 = lat2W(H, W, rook=False); w2.transform = 'r'
m2 = esda.Moran(g.ravel(), w2, permutations=0)
print('raster I mine=%.10f esda=%.10f' % (rr['I'], m2.I)); assert abs(rr['I'] - m2.I) < 1e-5

# 3. raster dengan mask
valid2 = valid.copy(); valid2[5:12, 10:20] = False; valid2[0, 0] = False
rr2 = ns['moran_raster'](g, valid2, B=99, seed=1)
ids = -np.ones((H, W), int); ids[valid2] = np.arange(valid2.sum())
neigh = {}
for i in range(H):
    for j in range(W):
        if not valid2[i, j]:
            continue
        neigh[ids[i, j]] = [ids[i + a, j + b] for a in (-1, 0, 1) for b in (-1, 0, 1)
                            if (a or b) and 0 <= i + a < H and 0 <= j + b < W and valid2[i + a, j + b]]
w3 = libpysal.weights.W(neigh); w3.transform = 'r'
m3 = esda.Moran(g[valid2], w3, permutations=0)
print('raster+mask I mine=%.10f esda=%.10f' % (rr2['I'], m3.I)); assert abs(rr2['I'] - m3.I) < 1e-5

# 4. sifat dasar
sm = ns['moran_raster'](np.add.outer(np.arange(H), np.arange(W)).astype(float), valid, B=49)['I']
cb = ns['moran_raster'](np.tile((np.arange(W) % 2).astype(float), (H, 1)), valid, B=49)['I']   # garis kolom bergantian: 6 dari 8 tetangga queen berlawanan, 2 sama -> I ~ -0.5
rn = ns['moran_raster'](rng.randn(H, W), valid, B=49)['I']
print('gradien I=%.3f garis-bergantian I=%.3f acak I=%.3f' % (sm, cb, rn)); assert sm > 0.9 and -0.6 < cb < -0.4 and abs(rn) < 0.15

# 5. determinisme
a = ns['moran_points'](x, nbr, B=199, seed=7); b = ns['moran_points'](x, nbr, B=199, seed=7); assert a == b
print('SEMUA UJI MORAN LULUS')
