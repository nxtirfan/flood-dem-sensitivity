# =========================================================
# v27 - GLOBAL MORAN'S I (diagnostik pendukung). Hanya Global, TIDAK ada LISA.
# Mandiri (numpy + scipy), tanpa libpysal/esda, kompatibel Kaggle dan Colab.
#
# Definisi (W distandardisasi baris, sehingga S0 = n):
#   I = (n / S0) * sum_ij w_ij z_i z_j / sum_i z_i^2,   z_i = x_i - mean(x)
#   E[I] = -1 / (n - 1) di bawah H0 (tidak ada autokorelasi spasial)
# Inferensi: PERMUTASI KONDISIONAL. Nilai x diacak lintas lokasi tetap, I dihitung ulang
# B kali. p dua sisi = (1 + #{|I_perm - E[I]| >= |I_obs - E[I]|}) / (B + 1).
# Deret permutasi ditentukan seed (RandomState(seed)), sehingga IDENTIK untuk ketiga DEM
# dan untuk setiap variabel yang dibandingkan (perbandingan berpasangan yang adil).
# =========================================================
from scipy.spatial import cKDTree

MORAN_K_PRIMARY = 8            # tetangga terdekat (kNN) untuk W utama
MORAN_K_SENSITIVITY = [5, 12]  # uji kepekaan terhadap definisi W
MORAN_B_POINTS = 9999          # jumlah permutasi (titik)
MORAN_B_MAP = 999              # jumlah permutasi (raster peta; mahal secara komputasi)
MORAN_SEED = 42


def project_to_utm(lon, lat, crs='EPSG:32749'):
    # lon/lat (derajat) -> meter pada CRS analisis proyek (UTM 49S), agar jarak kNN dalam meter.
    from rasterio.warp import transform
    xs, ys = transform('EPSG:4326', crs, list(map(float, lon)), list(map(float, lat)))
    return np.column_stack([xs, ys])


def knn_neighbors(xy, k):
    # k tetangga terdekat (tanpa diri sendiri). W row-standardized: tiap tetangga berbobot 1/k.
    tree = cKDTree(xy)
    d, idx = tree.query(xy, k=k + 1)
    if np.any(d[:, 1] == 0):
        raise ValueError('Ada titik dengan koordinat identik. Pada data titik duplikat, kNN tidak terdefinisi tegas.')
    return idx[:, 1:], d[:, 1:]


def moran_points(x, nbr, B=None, seed=None):
    # Global Moran's I untuk data titik, W = kNN row-standardized.
    B = MORAN_B_POINTS if B is None else B
    seed = MORAN_SEED if seed is None else seed
    x = np.asarray(x, dtype='float64')
    n = len(x)
    z = x - x.mean()
    ss = float((z * z).sum())
    if ss == 0:
        raise ValueError('Varians nol: Moran\'s I tidak terdefinisi.')
    I_obs = float((z * z[nbr].mean(axis=1)).sum() / ss)
    EI = -1.0 / (n - 1)
    rng = np.random.RandomState(seed)
    Ip = np.empty(B)
    for b in range(B):
        zp = z[rng.permutation(n)]
        Ip[b] = (zp * zp[nbr].mean(axis=1)).sum() / ss
    return _moran_summary(I_obs, EI, Ip, n)


def _moran_summary(I_obs, EI, Ip, n):
    B = len(Ip)
    return {'n': int(n), 'I': float(I_obs), 'E_I': float(EI),
            'perm_mean': float(Ip.mean()), 'perm_sd': float(Ip.std(ddof=1)),
            'z_perm': float((I_obs - Ip.mean()) / Ip.std(ddof=1)),
            'p_two_sided': float((1 + np.sum(np.abs(Ip - EI) >= abs(I_obs - EI))) / (B + 1)),
            'p_upper': float((1 + np.sum(Ip >= I_obs)) / (B + 1)),
            'p_lower': float((1 + np.sum(Ip <= I_obs)) / (B + 1)),
            'n_perm': int(B), 'p_min_resolvable': 1.0 / (B + 1)}


def _shift_sum(a):
    # Jumlah 8 tetangga queen untuk setiap piksel (tepi diperlakukan tanpa tetangga di luar grid).
    H, W = a.shape
    out = np.zeros_like(a)
    out[1:, :] += a[:-1, :]
    out[:-1, :] += a[1:, :]
    out[:, 1:] += a[:, :-1]
    out[:, :-1] += a[:, 1:]
    out[1:, 1:] += a[:-1, :-1]
    out[1:, :-1] += a[:-1, 1:]
    out[:-1, 1:] += a[1:, :-1]
    out[:-1, :-1] += a[1:, 1:]
    return out


def moran_raster(arr, valid, B=None, seed=None):
    # Global Moran's I untuk raster (W queen, row-standardized). Hanya piksel valid yang punya
    # minimal satu tetangga valid ikut dihitung (piksel terisolasi dikeluarkan).
    B = MORAN_B_MAP if B is None else B
    seed = MORAN_SEED if seed is None else seed
    v = np.where(valid, arr, 0).astype('float32')
    m = valid.astype('float32')
    cnt = _shift_sum(m)
    use = valid & (cnt > 0)
    n = int(use.sum())
    vals = v[use].astype('float64')
    mean = vals.mean()
    zfull = np.zeros_like(v)
    zfull[use] = (vals - mean).astype('float32')
    # relasi tetangga simetris: piksel terisolasi tidak pernah menjadi tetangga piksel lain, jadi cnt konsisten
    ss = float((zfull[use].astype('float64') ** 2).sum())
    if ss == 0:
        raise ValueError('Varians nol: Moran\'s I tidak terdefinisi.')
    cnt_safe = np.where(cnt > 0, cnt, 1).astype('float32')

    def _I(zf):
        lag = _shift_sum(zf) / cnt_safe
        return float((zf[use].astype('float64') * lag[use].astype('float64')).sum() / ss)

    I_obs = _I(zfull)
    EI = -1.0 / (n - 1)
    rng = np.random.RandomState(seed)
    zvals = zfull[use].copy()
    Ip = np.empty(B)
    for b in range(B):
        zp = np.zeros_like(zfull)
        zp[use] = zvals[rng.permutation(n)]
        Ip[b] = _I(zp)
    return _moran_summary(I_obs, EI, Ip, n)


print('Fungsi Global Moran\'s I siap (kNN titik, queen raster, permutasi kondisional).')
