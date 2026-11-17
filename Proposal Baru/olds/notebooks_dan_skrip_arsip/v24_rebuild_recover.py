import ast
import json
import os
import shutil

WS = r"C:\Users\ADMINI~1\AppData\Local\Temp\opencode\v24nb"
SRC_NB = r"D:\Kuliah\1_Metopen\Proposal Baru\Flood_DEM_Sensitivity_Notebook.ipynb"

os.makedirs(WS, exist_ok=True)
shutil.copyfile(SRC_NB, os.path.join(WS, "nb.ipynb"))
raw = open(os.path.join(WS, "nb.ipynb"), "rb").read()
print("0x97 sumber:", raw.count(b"\x97"))
open(os.path.join(WS, "nb_clean.ipynb"), "wb").write(raw.replace(b"\x97", b"-"))

nb = json.loads(open(os.path.join(WS, "nb_clean.ipynb"), encoding="utf-8").read())
assert len(nb["cells"]) == 44, f"sel berubah: {len(nb['cells'])}"
assert "".join(nb["cells"][22]["source"]).startswith("training_image_all"), "sel 22 bukan sampling"

MD21 = """## 10. Sampling identik (seed tetap) - v24 koreksi "sabuk JRC"

Sampler = `stratifiedSample` kuota [3000, 3000] pada **label ter-mask**, `seed=42`,
grid 30 m - identik untuk ketiga DEM.

**Koreksi MET-001 (bias sabuk JRC)**: kode v20-v22 memakai mask
`permanent_water = JRC occ>=80` yang **sparse**; `.Not()` pada piksel no-data
tetap no-data, sehingga kandidat kelas-0 tersaring diam-diam ke sabuk
terpetakan JRC saja (pool 123.616 px = 8,76% dari label=0; elevasi sampel
kelas-0 rata-rata 4,2 m vs 42,7 m se-AOI). **Fix v24**:
`pw_for_sampling = permanent_water.unmask(0)` - no-data diperlakukan bukan
air; pool kembali se-AOI (97,95% dari label=0). Probe piksel di bawah
mencetak ukuran pool kedua mode; audit distribusi sampel tiap band ada di
sel 11b. `SAMPLING_MODE='v22sabuk'` tetap tersedia untuk audit (replika
pola lama).
"""

C22 = """# =====================================================================
# SAMPLING v24 - KOREKSI MET-001 (bias "sabuk JRC") + probe piksel
# ---------------------------------------------------------------------
# Bug v20-v22: sampling_mask memakai permanent_water = JRC occ>=80 yang
# SPARSE. '.Not()' atas piksel no-data tetap no-data sehingga kandidat
# kelas-0 tersaring diam-diam: pool hanya 123.616 px (8,76% dari label=0),
# yaitu sabuk terpetakan JRC di sekitar pantai/sungai.
# Fix v24: pw_for_sampling = permanent_water.unmask(0) - no-data JRC
# diperlakukan BUKAN air; pool kelas-0 kembali se-AOI (1.382.033 px,
# 97,95%). SAMPLING_MODE='v22sabuk' disediakan untuk audit bias.
# =====================================================================
SAMPLING_MODE = 'v24'  # 'v24' = fix (mode utama) | 'v22sabuk' = replika kode lama

training_image_all = (ee.Image.cat([fixed_stack, dem_stack_all])
                      .addBands(flood_label)
                      .clip(roi))

def _masked_count(mask_img, name):
    # Jumlah piksel yang lolos mask (nilai bandnya 1) pada grid SAMPLE_SCALE.
    tot = ee.Image.constant(1).updateMask(mask_img).rename(name).reduceRegion(
        reducer=ee.Reducer.sum(), geometry=roi,
        scale=SAMPLE_SCALE, maxPixels=1e13, tileScale=TILE_SCALE
    ).get(name).getInfo()
    return int(round(float(tot)))

# Histogram label piksel tersedia di ROI (identik notebook sebelumnya).
try:
    n_nonflood, n_flood, label_hist = count_binary_pixels(
        training_image_all.select('flood'), 'flood', roi,
        scale=SAMPLE_SCALE, tileScale=TILE_SCALE
    )
    print('Histogram label piksel tersedia:', label_hist)
    print('Piksel non-flood tersedia:', n_nonflood)
    print('Piksel flood tersedia    :', n_flood)
except Exception as e:
    print('Gagal menghitung histogram label. Fallback ke target sampling manual.', e)
    n_nonflood, n_flood = SAMPLE_PER_CLASS_TARGET, SAMPLE_PER_CLASS_TARGET

# Probe piksel sampling: bukti mekanisme sabuk vs fix (tidak menghentikan run).
try:
    _pw_dense_probe = permanent_water.unmask(0)
    _n_aoi = _masked_count(ee.Image.constant(1), 'px')
    _n_jrc = _masked_count(jrc_water, 'jrc_valid')
    _n_pw = _masked_count(permanent_water, 'pw')
    _n_l0 = _masked_count(flood_label.eq(0), 'label0')
    _p22 = _masked_count(flood_label.eq(0).And(permanent_water.Not()), 'pool_v22')
    _p24 = _masked_count(flood_label.eq(0).And(_pw_dense_probe.Not()), 'pool_v24')
    print(f'[probe] piksel AOI (grid 30 m): {_n_aoi}')
    print(f'[probe] JRC valid: {_n_jrc} ({100.0 * _n_jrc / max(_n_aoi, 1):.2f}% dari AOI)')
    print(f'[probe] permanent_water (occ>=80 & valid): {_n_pw}')
    print(f'[probe] label=0 total: {_n_l0}')
    print(f'[probe] pool kelas-0 sabuk/v22: {_p22} ({100.0 * _p22 / max(_n_l0, 1):.2f}% label=0)')
    print(f'[probe] pool kelas-0 unmask0/v24: {_p24} ({100.0 * _p24 / max(_n_l0, 1):.2f}% label=0)')
except Exception as e:
    print('[probe] dilewati (tidak menghentikan pipeline):', e)

if AUTO_BALANCE_SAMPLE:
    SAMPLE_PER_CLASS = int(min(SAMPLE_PER_CLASS_TARGET, n_nonflood, n_flood))
    if SAMPLE_PER_CLASS <= 0:
        raise ValueError('Tidak ada piksel flood/non-flood yang cukup. '
                         'Periksa ROI, tanggal banjir, atau threshold Sentinel-1.')
else:
    SAMPLE_PER_CLASS = SAMPLE_PER_CLASS_TARGET
print('Sampel per kelas yang diminta:', SAMPLE_PER_CLASS)

if SAMPLING_MODE == 'v24':
    pw_for_sampling = permanent_water.unmask(0)
    print('Mode sampling v24 (FIX): no-data JRC diperlakukan BUKAN air.')
else:
    pw_for_sampling = permanent_water
    print('Mode sampling v22sabuk (AUDIT BIAS): replika persis kode lama.')

sampling_mask = (flood_label.eq(1)
                 .Or(flood_label.eq(0).And(pw_for_sampling.Not())))
label_for_sampling = flood_label.updateMask(sampling_mask)

locs_stage1 = (label_for_sampling.rename('flood')
               .stratifiedSample(
                   numPoints=SAMPLE_PER_CLASS,
                   classBand='flood',
                   classValues=[0, 1],
                   classPoints=[SAMPLE_PER_CLASS, SAMPLE_PER_CLASS],
                   seed=RANDOM_STATE,
                   scale=SAMPLE_SCALE,
                   geometries=True,
                   tileScale=TILE_SCALE)
               .map(add_lon_lat))
print('Titik tahap-1 (stratifiedSample pada label ter-mask):',
      locs_stage1.size().getInfo())

# Tahap 2: ekstraksi SEMUA prediktor pada lokasi tahap-1 (identik v20-v23).
vals_all = predictor_stack_all.sampleRegions(
    collection=locs_stage1,
    scale=SAMPLE_SCALE,
    tileScale=TILE_SCALE
)
print('Titik tahap-2 (pasca-sampleRegions):', vals_all.size().getInfo())
fc_nonflood = vals_all.filter(ee.Filter.eq('flood', 0))
fc_flood = vals_all.filter(ee.Filter.eq('flood', 1))
print('Jumlah sampel mentah non-flood:', fc_nonflood.size().getInfo())
print('Jumlah sampel mentah flood    :', fc_flood.size().getInfo())

# Buang titik yang memiliki null pada band prediktor mana pun (identik).
sample_fc_raw = (fc_nonflood.merge(fc_flood)
                 .filter(ee.Filter.notNull(predictor_bands_all)))
raw_hist = sample_fc_raw.aggregate_histogram('flood').getInfo() or {}
print('Distribusi sampel awal dari GEE:', raw_hist)

def hist_count(hist, target_class):
    total = 0
    for k, v in hist.items():
        try:
            if int(float(k)) == int(target_class):
                total += int(float(v))
        except Exception:
            pass
    return total

raw_n0 = hist_count(raw_hist, 0)
raw_n1 = hist_count(raw_hist, 1)
if raw_n0 <= 0 or raw_n1 <= 0:
    raise ValueError('Sampel hanya berisi satu kelas (n0=%s, n1=%s). '
                     'Periksa kembali mask/stack prediktor dan flood_label.'
                     % (raw_n0, raw_n1))

if AUTO_BALANCE_SAMPLE:
    SAMPLE_PER_CLASS_FINAL = int(min(SAMPLE_PER_CLASS, raw_n0, raw_n1))
    sample_fc_tmp = sample_fc_raw.randomColumn('rand_balance', RANDOM_STATE)
    nonflood_samples = (sample_fc_tmp.filter(ee.Filter.eq('flood', 0))
                        .sort('rand_balance').limit(SAMPLE_PER_CLASS_FINAL))
    flood_samples = (sample_fc_tmp.filter(ee.Filter.eq('flood', 1))
                     .sort('rand_balance').limit(SAMPLE_PER_CLASS_FINAL))
    sample_fc = (nonflood_samples.merge(flood_samples)
                 .randomColumn('random', RANDOM_STATE).sort('random'))
else:
    SAMPLE_PER_CLASS_FINAL = SAMPLE_PER_CLASS
    sample_fc = sample_fc_raw.randomColumn('random', RANDOM_STATE).sort('random')

final_hist = sample_fc.aggregate_histogram('flood').getInfo() or {}
print('SAMPLE_PER_CLASS final:', SAMPLE_PER_CLASS_FINAL)
print('Distribusi sampel final:', final_hist)
print('Jumlah sampel total:', sample_fc.size().getInfo())
"""

C24_OLD = "drop_cols = ['flood', 'split_base']  # v23: split_base hanya untuk split-reuse, bukan fitur"
C24_NEW = ("drop_cols = ['flood']  # v24: sampling tidak lagi membawa split_base (bridging v23)\n"
           "if 'split_base' in data.columns:\n"
           "    drop_cols.append('split_base')")

MD27 = """## 12. Eksperimen Random Forest terkontrol

Ketiga konfigurasi dilatih dengan:

- baris data, urutan data, dan seed yang sama -> train/test split identik,
- parameter RF identik (`RF_SKLEARN`),
- metrik: ROC-AUC, accuracy, precision, recall, F1 (ambang 0.5 dan Youden-optimal).

Tambahan v21 - **validasi spatial 4-fold CV**: 16 blok kuantil lon/lat dibagi
4 fold (seed tetap, fold SAMA untuk ketiga DEM); tiap fold melatih ULANG RF
(parameter identik) pada 12 blok dan menguji pada 4 blok yang ditahan -
tanpa leakage train-test.

Koreksi v22/MET-002: selain pseudo-AUC dari prediksi biner (kolom legacy
`auc_spatial_cv`), AUC spasial dihitung dari **probabilitas**
(`auc_spatial_cv_prob`). Semua prediksi titik uji tersimpan
(`spatial_cv_test_predictions.csv`) sehingga delta-AUC antar-DEM dapat
dibootstrap 1000x: `spatial_cv_delta_auc_bootstrap.csv` - CATATAN:
bootstrap pasangan titik, BELUM blok-spasial (gap ~0,01 antar-DEM belum
layak dijadikan peringkat mutlak).

v24: sampling dikoreksi (sabuk JRC, MET-001) - metrik holdout/CV kini
estimasi se-AOI, bukan hanya dalam domain sabuk.
"""

C28 = """def get_positive_class_proba(model, X_test):
    proba = model.predict_proba(X_test)
    classes = np.array(model.classes_)
    pos_idx = int(np.where(classes == 1)[0][0])
    return proba[:, pos_idx]


# Split v22/v24: train_test_split acak (test 25%, stratify y, seed 42) -
# identik untuk ketiga konfigurasi. (v23 bridging sempat memakai kolom
# 'split_base' baseline; pada v24 sampling dikoreksi sehingga undian acak
# penuh dipakai sebagai skema resmi. Bila kolom split_base ada, split lama
# otomatis dipakai untuk kompatibilitas.)
if 'split_base' in data.columns:
    _tr_b = (data['split_base'].to_numpy() == 'train')
    print('Split dipakai ulang dari baseline: train=%d test=%d' % (
        int(_tr_b.sum()), int((~_tr_b).sum())))
else:
    _tr_b = None
    print('Split v24: train_test_split acak (test 25%, stratify=y, seed=%d)'
          % RANDOM_STATE)

results = []
for name in DEM_NAMES:
    cols = fixed_feature_cols + dem_cols(name)
    X_cfg = X_all[cols]

    if _tr_b is None:
        X_train, X_test, y_train, y_test = train_test_split(
            X_cfg, y, test_size=0.25, stratify=y, random_state=RANDOM_STATE)
    else:
        X_train, X_test = X_cfg.iloc[_tr_b], X_cfg.iloc[~_tr_b]
        y_train, y_test = y.iloc[_tr_b], y.iloc[~_tr_b]

    rf = RandomForestClassifier(**RF_SKLEARN)
    rf.fit(X_train, y_train)

    y_proba = get_positive_class_proba(rf, X_test)
    y_pred_05 = (y_proba >= 0.5).astype(int)

    fpr, tpr, thresholds = roc_curve(y_test, y_proba)
    best_idx = np.argmax(tpr - fpr)
    best_threshold = thresholds[best_idx]
    y_pred_opt = (y_proba >= best_threshold).astype(int)

    results.append({
        'config': name,
        'label': DEM_CONFIGS[name]['label'],
        'roc_auc': roc_auc_score(y_test, y_proba),
        'accuracy_05': accuracy_score(y_test, y_pred_05),
        'precision_05': precision_score(y_test, y_pred_05, zero_division=0),
        'recall_05': recall_score(y_test, y_pred_05, zero_division=0),
        'f1_05': f1_score(y_test, y_pred_05, zero_division=0),
        'best_threshold_youden': best_threshold,
        'accuracy_opt': accuracy_score(y_test, y_pred_opt),
        'precision_opt': precision_score(y_test, y_pred_opt, zero_division=0),
        'recall_opt': recall_score(y_test, y_pred_opt, zero_division=0),
        'f1_opt': f1_score(y_test, y_pred_opt, zero_division=0),
        'fpr': fpr, 'tpr': tpr, 'y_test': y_test, 'y_pred_opt': y_pred_opt,
        'model': rf,
    })
    print(f'RF {name}: selesai dilatih ({len(cols)} prediktor).')

# ------------------------------------------------------------------
# VALIDASI SPASIAL v21 (16 blok kuantil lon/lat -> 4 fold, retrain per
# fold TANPA leakage) + KOREKSI MET-002: AUC spasial dari PROBABILITAS
# (kolom baru auc_spatial_cv_prob); kolom legacy auc_spatial_cv tetap
# pseudo-AUC dari prediksi biner untuk kontinuitas v20-v23.
# Prediksi semua titik uji disimpan ke spatial_cv_test_predictions.csv.
# ------------------------------------------------------------------
_lon = data['lon'].to_numpy()
_lat = data['lat'].to_numpy()
_lon_q = np.quantile(_lon, [0.25, 0.5, 0.75])
_lat_q = np.quantile(_lat, [0.25, 0.5, 0.75])
_block = np.digitize(_lon, _lon_q) + 4 * np.digitize(_lat, _lat_q)
_rng = np.random.RandomState(RANDOM_STATE)
_shuffled = _rng.permutation(np.unique(_block))
_folds = [set(f.tolist()) for f in np.array_split(_shuffled, 4)]
print('Fold spasial (blok uji per fold):', [sorted(f) for f in _folds])

def _safe_metrics(yt, yp):
    m = {'accuracy': accuracy_score(yt, yp),
         'precision': precision_score(yt, yp, zero_division=0),
         'recall': recall_score(yt, yp, zero_division=0),
         'f1': f1_score(yt, yp, zero_division=0)}
    try:
        m['roc_auc'] = roc_auc_score(yt, yp) if len(np.unique(yt)) > 1 else float('nan')
    except Exception:
        m['roc_auc'] = float('nan')
    return m

cv_rows = []
spatial_pred_rows = []
for fi, fold_blocks in enumerate(_folds):
    _te = np.array([b in fold_blocks for b in _block])
    _tr = ~_te
    for name in DEM_NAMES:
        _cols = fixed_feature_cols + dem_cols(name)
        _rf = RandomForestClassifier(**RF_SKLEARN)
        _rf.fit(X_all.iloc[_tr][_cols], y.iloc[_tr])
        _proba = get_positive_class_proba(_rf, X_all.iloc[_te][_cols])
        _pred = (_proba >= 0.5).astype(int)
        _m = _safe_metrics(y.iloc[_te], _pred)
        try:
            _auc_prob = roc_auc_score(y.iloc[_te], _proba)
        except Exception:
            _auc_prob = float('nan')
        cv_rows.append({'fold': fi, 'config': name,
                        'n_train': int(_tr.sum()), 'n_test': int(_te.sum()),
                        'test_pos_rate': round(float(y.iloc[_te].mean()), 4),
                        'auc_spatial_cv': _m['roc_auc'],
                        'auc_spatial_cv_prob': _auc_prob,
                        'accuracy_spatial_cv': _m['accuracy'],
                        'precision_spatial_cv': _m['precision'],
                        'recall_spatial_cv': _m['recall'],
                        'f1_spatial_cv': _m['f1']})
        for _y_v, _p_v in zip(y.iloc[_te], _proba):
            spatial_pred_rows.append({'fold': fi, 'config': name,
                                      'y_true': float(_y_v),
                                      'proba': float(_p_v)})
        _aucleg = _m['roc_auc']
        _f1leg = _m['f1']
        print(f'Fold {fi} {name}: train={int(_tr.sum())} test={int(_te.sum())} '
              f'AUCprob={_auc_prob:.3f} AUClegacy={_aucleg:.3f} F1={_f1leg:.3f}')

spatial_cv_df = pd.DataFrame(cv_rows)
spatial_cv_df.to_csv(os.path.join(OUTPUT_DIR, 'spatial_cv_metrics.csv'), index=False)
pd.DataFrame(spatial_pred_rows).to_csv(
    os.path.join(OUTPUT_DIR, 'spatial_cv_test_predictions.csv'), index=False)
print('Ringkasan spatial CV (mean lintas fold; *_prob = koreksi MET-002):')
print(spatial_cv_df.groupby('config')[
    ['auc_spatial_cv_prob', 'auc_spatial_cv', 'f1_spatial_cv',
     'accuracy_spatial_cv']].mean().round(4).to_string())

# Bootstrap delta-AUC antar-DEM dari pasangan prediksi titik yang sama
# (CATATAN: belum blok-spasial - gap ~0,01 antar-DEM belum layak jadi
# peringkat mutlak; bootstrap blok/kelompok spasial menyusul).
try:
    _pool = {cfg: (g['y_true'].to_numpy(), g['proba'].to_numpy())
             for cfg, g in pd.DataFrame(spatial_pred_rows).groupby('config')}
    _pairs_boot = [('srtm', 'glo30'), ('srtm', 'aw3d30'), ('glo30', 'aw3d30')]
    _rng_b = np.random.RandomState(RANDOM_STATE)
    _NBOOT = 1000
    _boot_rows = []
    for _a, _b in _pairs_boot:
        if _a not in _pool or _b not in _pool:
            continue
        _ya, _pa = _pool[_a]
        _yb, _pb = _pool[_b]
        _n = min(len(_ya), len(_yb))
        _deltas = np.empty(_NBOOT)
        for _i in range(_NBOOT):
            _idx = _rng_b.randint(0, _n, size=_n)
            _deltas[_i] = (roc_auc_score(_ya[_idx], _pa[_idx])
                           - roc_auc_score(_yb[_idx], _pb[_idx]))
        _row = {'pair': f'{_a}-minus-{_b}',
                'auc_a': float(roc_auc_score(_ya, _pa)),
                'auc_b': float(roc_auc_score(_yb, _pb)),
                'delta_auc_mean': float(np.mean(_deltas)),
                'ci_low': float(np.percentile(_deltas, 2.5)),
                'ci_high': float(np.percentile(_deltas, 97.5)),
                'n_iter': _NBOOT}
        _boot_rows.append(_row)
        print(f"dAUC {_a} - {_b}: {_row['delta_auc_mean']:+.4f} "
              f"[{_row['ci_low']:+.4f}, {_row['ci_high']:+.4f}]")
    pd.DataFrame(_boot_rows).to_csv(
        os.path.join(OUTPUT_DIR, 'spatial_cv_delta_auc_bootstrap.csv'), index=False)
except Exception as _e:
    print('Bootstrap dAUC dilewati:', _e)

metrics_df = pd.DataFrame([
    {k: v for k, v in r.items() if k not in ['fpr', 'tpr', 'y_test', 'y_pred_opt', 'model']}
    for r in results
])
metrics_df.to_csv(os.path.join(OUTPUT_DIR, 'model_metrics.csv'), index=False)

# Sensitivitas performa: delta metrik terhadap konfigurasi SRTM.
base = metrics_df.set_index('config').loc['srtm']
delta_df = pd.DataFrame([
    {
        'config': r['config'],
        'delta_roc_auc': r['roc_auc'] - base['roc_auc'],
        'delta_accuracy_opt': r['accuracy_opt'] - base['accuracy_opt'],
        'delta_precision_opt': r['precision_opt'] - base['precision_opt'],
        'delta_recall_opt': r['recall_opt'] - base['recall_opt'],
        'delta_f1_opt': r['f1_opt'] - base['f1_opt'],
    }
    for r in results
])
delta_df.to_csv(os.path.join(OUTPUT_DIR, 'delta_metrics_vs_srtm.csv'), index=False)

# Arsip fitur sampel (flood/lon/lat + seluruh fitur) untuk audit offline.
try:
    _feat = pd.concat([data[['flood', 'lon', 'lat']].reset_index(drop=True),
                       X_all.reset_index(drop=True)], axis=1)
    _feat.to_csv(os.path.join(OUTPUT_DIR, 'training_sample_features.csv'), index=False)
    print('training_sample_features.csv tersimpan.')
except Exception as e:
    print('training_sample_features.csv gagal:', e)

display(metrics_df)
display(delta_df)
"""

C41 = """# Guard EXPORT_TO_DRIVE v24 (pelajaran v21: satu task gagal TIDAK boleh
# menghentikan kernel; kegagalan di-log, ekspor lainnya lanjut).
EXPORT_TO_DRIVE = True
DRIVE_FOLDER = 'GEE_DEM_Sensitivity_Semarang_Demak'

def export_image(img, name):
    if not EXPORT_TO_DRIVE:
        print('EXPORT_TO_DRIVE = False - lewati', name)
        return
    try:
        task = ee.batch.Export.image.toDrive(
            image=img.toFloat(),
            description=name,
            folder=DRIVE_FOLDER,
            fileNamePrefix=name,
            region=roi,
            scale=30,
            maxPixels=1e13
        )
        task.start()
        print('Export started:', name)
    except Exception as e:
        print(f'Export GAGAL ({name}): {e}')

if EXPORT_TO_DRIVE:
    # Peta probabilitas, kelas kerawanan, delta, dan kesesuaian.
    for name in DEM_NAMES:
        export_image(prob_map[name], f'prob_{name}')
        export_image(risk_class[name], f'risk_class_{name}')
    for p in pairs:
        export_image(delta_abs[p], f'delta_abs_{p[0]}_vs_{p[1]}')
        export_image(agreement_map[p], f'agreement_{p[0]}_vs_{p[1]}')

    # Label banjir dan sampel training.
    export_image(flood_label.toByte(), 'proxy_flood_label_sentinel1')
    try:
        task_table = ee.batch.Export.table.toDrive(
            collection=sample_fc,
            description='training_sample_dem_sensitivity',
            folder=DRIVE_FOLDER,
            fileNamePrefix='training_sample_dem_sensitivity',
            fileFormat='CSV'
        )
        task_table.start()
        print('Export started: training_sample_dem_sensitivity (CSV)')
    except Exception as e:
        print(f'Export tabel sampel GAGAL: {e}')
else:
    print('EXPORT_TO_DRIVE = False. Ubah menjadi True jika ingin export ke Google Drive.')
print('Catatan: CSV metrik/sensitivitas sudah tersimpan di OUTPUT_DIR:', OUTPUT_DIR)
"""


def set_src(idx, text, kind):
    nb["cells"][idx]["source"] = text.splitlines(keepends=True)
    if kind is not None:
        nb["cells"][idx]["cell_type"] = kind


set_src(21, MD21, "markdown")
set_src(22, C22, None)

src24 = "".join(nb["cells"][24]["source"])
assert C24_OLD in src24, "marker sel 24 tidak ditemukan"
nb["cells"][24]["source"] = src24.replace(C24_OLD, C24_NEW).splitlines(keepends=True)

set_src(27, MD27, "markdown")
set_src(28, C28, None)
set_src(41, C41, None)

out = os.path.join(WS, "nb_v24.ipynb")
with open(out, "w", encoding="utf-8") as fh:
    json.dump(nb, fh, ensure_ascii=False, indent=1)

chk = json.loads(open(out, encoding="utf-8").read())
assert len(chk["cells"]) == 44
ncode = 0
for i, c in enumerate(chk["cells"]):
    if c["cell_type"] == "code":
        ncode += 1
        # Hanya baris magic TANPA indentasi yang dibuang (baris lanjutan
        # ber-operator % di dalam kurung tetap diparsing sebagai Python).
        src = "\n".join(l for l in "".join(c["source"]).splitlines()
                        if not l.startswith(("!", "%")))
        try:
            ast.parse(src)
        except SyntaxError as e:
            lines = "".join(c["source"]).splitlines()
            ctx = "\n".join(lines[max(0, e.lineno - 3):e.lineno + 2]) if e.lineno else ""
            raise SystemExit(f"SYNTAX ERROR cell {i}: {e}\n---\n{ctx}")
print(f"VALID: {len(chk['cells'])} sel | {ncode} code cell compile OK")
print("0x97 sisa:", open(out, "rb").read().count(b"\x97"))
