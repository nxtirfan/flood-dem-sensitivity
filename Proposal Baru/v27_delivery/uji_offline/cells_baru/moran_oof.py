# =========================================================
# v27 - GLOBAL MORAN'S I pada (a) probabilitas OOF dan (b) residual OOF spatial CV (evaluasi utama).
# Unit analisis: TITIK sampel (n = jumlah baris dataset utama), BUKAN 16 blok (lihat metodologi).
# Probabilitas = prediksi out-of-fold: tiap titik diprediksi oleh model yang TIDAK melihat blok-nya.
# Residual OOF = label aktual - probabilitas OOF. Prediksi data latih TIDAK dipakai.
# W = kNN (k=8), row-standardized, jarak meter UTM 49S, SATU W yang sama untuk ketiga DEM.
# Ini analisis diagnostik. Hasilnya tidak membuktikan ada/tidaknya spatial leakage.
# =========================================================
_pdf = pd.DataFrame(spatial_pred_rows)
_yv = y.to_numpy()
_blk = np.asarray(_block)
assert len(_yv) == len(data) == len(_blk), 'y dan data tidak sejajar'

# 1. Pulihkan vektor OOF per titik dari spatial_pred_rows (urutan baris = urutan titik uji per fold).
oof_prob = {n: np.full(len(_yv), np.nan) for n in DEM_NAMES}
fold_id = np.full(len(_yv), -1, dtype=int)
for _fi, _fb in enumerate(_folds):
    _te = np.where(np.array([b in _fb for b in _blk]))[0]
    for _n in DEM_NAMES:
        _g = _pdf[(_pdf['fold'] == _fi) & (_pdf['config'] == _n)]
        if not (len(_g) == len(_te)
                and np.array_equal(_g['y_true'].to_numpy(), _yv[_te])
                and np.array_equal(_g['block'].to_numpy(), _blk[_te])):
            raise RuntimeError(f'Pemetaan OOF fold {_fi} {_n} tidak cocok dengan label/blok titik uji. '
                               'Moran\'s I tidak dihitung (tidak akan memaksakan pemetaan).')
        oof_prob[_n][_te] = _g['proba'].to_numpy()
    fold_id[_te] = _fi
assert (fold_id >= 0).all() and not any(np.isnan(v).any() for v in oof_prob.values()), 'ada titik tanpa prediksi OOF'
oof_resid = {n: _yv - oof_prob[n] for n in DEM_NAMES}           # aktual - probabilitas OOF
print('OOF terpulihkan: tiap titik tepat satu prediksi OOF per DEM; y_true dan blok cocok untuk semua fold.')

# 2. Spatial weights (satu definisi untuk semua DEM).
_xy = project_to_utm(data['lon'].to_numpy(), data['lat'].to_numpy())
_rows = []
for _k in [MORAN_K_PRIMARY] + MORAN_K_SENSITIVITY:
    _nbr, _dist = knn_neighbors(_xy, _k)
    _cross = float((fold_id[_nbr] != fold_id[:, None]).mean())
    print(f'W kNN k={_k}: jarak tetangga terjauh median={np.median(_dist[:, -1]):.0f} m, '
          f'p95={np.percentile(_dist[:, -1], 95):.0f} m, maks={_dist[:, -1].max():.0f} m | '
          f'pasangan tetangga lintas fold={100 * _cross:.1f}%')
    _vars = [('label_acuan', 'flood', _yv)]
    for _n in DEM_NAMES:
        _vars.append(('oof_probability', _n, oof_prob[_n]))
        _vars.append(('oof_residual', _n, oof_resid[_n]))
    for _scope, _dem, _x in _vars:
        _r = moran_points(_x, _nbr)
        _r.update({'scope': _scope, 'dem': _dem, 'k': _k, 'weights': f'kNN k={_k}, row-standardized, UTM 49S',
                   'perm_method': 'permutasi kondisional (acak nilai lintas lokasi tetap)',
                   'seed': MORAN_SEED, 'primary': _k == MORAN_K_PRIMARY,
                   'cross_fold_neighbor_share': _cross})
        _rows.append(_r)
moran_oof_df = pd.DataFrame(_rows)[['scope', 'dem', 'k', 'primary', 'n', 'I', 'E_I', 'perm_mean', 'perm_sd',
                                    'z_perm', 'p_two_sided', 'p_upper', 'p_lower', 'n_perm',
                                    'p_min_resolvable', 'seed', 'weights', 'perm_method',
                                    'cross_fold_neighbor_share']]
moran_oof_df.to_csv(os.path.join(OUTPUT_DIR, 'moran_oof_global.csv'), index=False)
pd.DataFrame({'lon': data['lon'].to_numpy(), 'lat': data['lat'].to_numpy(), 'block': _blk,
              'fold': fold_id, 'y': _yv,
              **{f'oof_prob_{n}': oof_prob[n] for n in DEM_NAMES},
              **{f'oof_resid_{n}': oof_resid[n] for n in DEM_NAMES}}
             ).to_csv(os.path.join(OUTPUT_DIR, 'moran_oof_points.csv'), index=False)
print(moran_oof_df[moran_oof_df['primary']][['scope', 'dem', 'n', 'I', 'E_I', 'z_perm', 'p_two_sided', 'n_perm']]
      .round(4).to_string(index=False))
print('\nCatatan: p-value tidak signifikan tidak berarti tidak ada autokorelasi spasial '
      '(daya uji, pilihan W, dan permutasi yang mengasumsikan keterpertukaran). '
      'Moran\'s I adalah diagnostik pendukung dan tidak menghilangkan atau membuktikan ketiadaan spatial leakage.')
