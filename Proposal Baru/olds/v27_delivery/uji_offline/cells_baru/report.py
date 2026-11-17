# =========================================================
# v27 - LAPORAN PEMBANDING v26 vs v27 (semua mode, tanpa GEE)
# Membandingkan CSV hasil run ini (outputs/) dengan hasil v26 (data/reference_v26/).
# Tiap komponen dilaporkan TERPISAH. Komponen yang tidak ada hasilnya dinyatakan BELUM DIUJI.
# Selisih tidak disamarkan: IDENTIK hanya bila semua nilai persis sama.
# =========================================================
COMPARE_COMPONENTS = {
    'evaluasi_utama': ['model_metrics.csv', 'delta_metrics_vs_srtm.csv', 'spatial_cv_metrics.csv',
                       'spatial_cv_test_predictions.csv', 'spatial_cv_delta_auc_bootstrap.csv',
                       'spatial_cv_delta_auc_bootstrap_pixel_legacy.csv', 'sample_audit.csv',
                       'training_sample_features.csv'],
    'multi_seed': ['multiseed_holdout.csv', 'multiseed_spatial_cv.csv', 'multiseed_summary.csv',
                   'multiseed_delta_auc.csv', 'multiseed_test_predictions.csv'],
    'statistik_spasial_peta': ['sensitivity_summary.csv', 'area_per_risk_class_km2.csv',
                               'transition_srtm_vs_glo30.csv', 'transition_srtm_vs_aw3d30.csv',
                               'transition_glo30_vs_aw3d30.csv', 'worldcover_sensitivity.csv'],
    'statistik_dem_gee': ['dem_stats.csv'],
}


def compare_csv(new_path, ref_path):
    if not os.path.isfile(ref_path):
        return 'TIDAK_ADA_REFERENSI', None, None, ''
    if not os.path.isfile(new_path):
        return 'BELUM_DIUJI', None, None, 'hasil v27 belum ada'
    a, b = pd.read_csv(new_path), pd.read_csv(ref_path)
    if list(a.columns) != list(b.columns) or a.shape != b.shape:
        return 'STRUKTUR_BEDA', None, None, f'v27 {a.shape} vs v26 {b.shape}'
    max_abs, max_rel, same = 0.0, 0.0, True
    for c in a.columns:
        if pd.api.types.is_numeric_dtype(a[c]) and pd.api.types.is_numeric_dtype(b[c]):
            x, y = a[c].to_numpy(dtype='float64'), b[c].to_numpy(dtype='float64')
            if not np.array_equal(x, y, equal_nan=True):
                same = False
                d = np.abs(x - y)
                d = d[np.isfinite(d)]
                if d.size:
                    max_abs = max(max_abs, float(d.max()))
                    den = np.maximum(np.abs(y), 1e-12)
                    max_rel = max(max_rel, float((np.abs(x - y) / den)[np.isfinite(x - y)].max()))
        elif not a[c].equals(b[c]):
            same = False
    return ('IDENTIK' if same else 'SELISIH_NUMERIK'), max_abs, max_rel, ''


def run_comparison(new_dir=None, ref_dir=None, save=True):
    new_dir, ref_dir = new_dir or PATHS['outputs'], ref_dir or PATHS['reference_v26']
    sums_p = os.path.join(ref_dir, 'SHA256SUMS.json')
    if os.path.isfile(sums_p):
        with open(sums_p, 'r', encoding='utf-8') as fh:
            sums = json.load(fh)
        bad = [f for f, h in sums.items() if os.path.isfile(os.path.join(ref_dir, f))
               and sha256_file(os.path.join(ref_dir, f)) != h]
        if bad:
            raise FrozenDataError(f'Berkas referensi v26 berubah (SHA-256 berbeda): {bad}')
        print(f'Referensi v26 utuh ({len(sums)} berkas, checksum cocok).')
    else:
        print('PERINGATAN: SHA256SUMS.json referensi v26 tidak ada. Integritas referensi tidak diperiksa.')
    rows = []
    for comp, files in COMPARE_COMPONENTS.items():
        for f in files:
            st, ma, mr, note = compare_csv(os.path.join(new_dir, f), os.path.join(ref_dir, f))
            rows.append({'komponen': comp, 'berkas': f, 'status': st,
                         'maks_selisih_abs': ma, 'maks_selisih_rel': mr, 'catatan': note})
    rep = pd.DataFrame(rows)
    if save:
        rep.to_csv(os.path.join(new_dir, 'validation_v26_vs_v27.csv'), index=False)
    return rep


COMPARISON = run_comparison()
print(COMPARISON.to_string(index=False))
print()
for _comp, _g in COMPARISON.groupby('komponen', sort=False):
    _tested = _g[~_g['status'].isin(['BELUM_DIUJI', 'TIDAK_ADA_REFERENSI'])]
    _same = int((_tested['status'] == 'IDENTIK').sum())
    print(f'{_comp:<24}: diuji {len(_tested)}/{len(_g)} berkas | identik {_same}/{len(_tested)}'
          + ('' if len(_tested) else '  -> BELUM DIUJI'))
print('\nCatatan tafsir: selisih dapat berasal dari (1) data GEE yang ditarik ulang berbeda dari run v26, '
      '(2) versi library berbeda (lihat outputs/run_environment.json), atau (3) kode. '
      'Pisahkan penyebabnya sebelum menyimpulkan. Status IDENTIK pada satu komponen tidak '
      'membuktikan komponen lain.')
