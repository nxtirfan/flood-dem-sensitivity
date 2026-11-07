# Temuan Empiris: Eksperimen Sensitivitas DEM (Run Kaggle v17–v22)

> Dokumen ini merangkum SELURUH angka dan temuan empiris pipeline GEE + scikit-learn.
> Ditulis untuk direview pihak ketiga (mis. GPT) dan sebagai jejak audit metodologis.
>
> | Run | Status | n | Peran bukti |
> |---|---|---|---|
> | v17 | COMPLETE | 270 | Diagnostik pipeline (pilot kecil) |
> | v18 | COMPLETE | 270 | Uji stabilitas + diagnostik sampling |
> | v20 | COMPLETE (GPU T4) | 5872 | Pilot sampel besar (spatial holdout INVALID — leakage) |
> | v21 | ERROR (viz timeout) | 5872 | Hanya log spatial-CV awal yang selamat (≈0,64–0,66) |
> | v22 | COMPLETE (GPU T4) | 5872 | **Kandidat hasil utama** |
> | v23 | COMPLETE (GPU T4) | 1720 | **Bridging ke baseline**: titik+split baseline, prediktor diekstrak ulang |
>
> Lokasi file sumber: `Proposal Baru\hasil_kaggle_v17\` (v17),
> `Proposal Baru\hasil_kaggle_v20\` (v20), `Proposal Baru\hasil_kaggle_v22\` (v22),
> `Proposal Baru\hasil_kaggle_v23\` (v23, bridging).
> Kernel: `nxtirfan/flood-dem-sensitivity-srtm-vs-glo-30-vs-aw3d30` (Kaggle, privat).
> Notebook lokal: `Proposal Baru\Flood_DEM_Sensitivity_Notebook.ipynb` (44 sel).
> Mulai v20, push kernel memakai GPU T4.

---

## 1. Desain eksperimen

- **Pertanyaan**: apakah SUMBER produk elevasi global mengubah peta kerawanan banjir ML?
- **Perlakuan (satu-satunya yang diubah)**: produk DEM — SRTM v3 (C-band DEM),
  Copernicus GLO-30 (DSM), ALOS AW3D30 v4.1 (DSM). Ketiganya ~30 m → framing = sensitivitas
  SUMBER, bukan resolusi.
- **Dikunci identik**: AOI (pesisir Semarang–Demak, 1310,09 km², grid analisis EPSG:32749 30 m),
  inventory banjir Sentinel-1 (1 kejadian), 12 prediktor non-DEM (HAND, upa_log, river_width,
  dist_river, dist_perm_water, rain_7d, rain_30d, NDVI, NDWI, MNDWI, NDBI, WorldCover),
  sampling + seed (42) + split + parameter RF.
- **Model**: Random Forest sklearn (400 trees, identik) untuk metrik holdout; RF GEE
  (`smileRandomForest`, 300 trees) untuk peta probabilitas penuh + perbandingan spasial piksel-per-piksel.
- **Klarifikasi penting (jangan salah tulis di proposal)**: yang identik dengan
  penelitian terdahulu (baseline SMDS) adalah POPULASI inventori (peta `flood_label`,
  deterministik) — BUKAN titik-titik sampelnya. Titik sampel kita (stratifiedSample
  pada single-band label + ekstraksi two-stage) adalah undian BERBEDA dari populasi
  yang sama; mekanisme sampling baseline (langsung pada stack multi-band ber-mask)
  justru terbukti gagal direplikasi (v15–v16). Satu master sample (5872 lokasi)
  dipakai IDENTIK untuk ketiga konfigurasi DEM — tidak ada "sampel Copernicus/ALOS
  dari penelitian terdahulu" karena memang tidak diperlukan: nilai ketiga DEM
  diekstrak pada lokasi yang sama lalu dibandingkan.
- **Split**: train/test 75/25, stratified, seed 42 (test ≈ 67–68 sampel pada n=270).
- **Kelas kerawanan**: 5 kelas dari probabilitas dengan batas [0.2, 0.4, 0.6, 0.8], sama untuk ketiga peta.
- **Penanganan mask final / v22** (berlaku identik ke-3 DEM):
  `river_width` (MERIT `wth`, hanya valid di sungai) → `unmask(0)` — 0 = tidak ada
  sungai yang dipetakan (makna substantif);
  `aspect` (variabel sirkular, ter-mask alami di terrain datar) → `aspect_sin` /
  `aspect_cos` (0 netral di dataran) + `aspect_valid` (flag slope > 0).
  Riwayat: v17/v18 memakai `aspect → -1` (kode datar, workaround yang dapat dibela
  untuk pilot, digantikan sin/cos pada v22 atas masukan reviewer).
  Void ALOS dipertahankan sebagai mask (missingness jujur).

---

## 2. Hasil run v17 (pilot, sampel seimbang 135/kelas, n = 270)

Alur sampel v17: diminta 3000/kelas → mentah {0: 239, 1: 135} → diseimbangkan ke minoritas → 135/kelas.

### 2.1 Metrik holdout (sklearn RF, test ≈ 68 sampel)

| Konfigurasi | ROC-AUC | Akurasi | Presisi | Recall | F1 | Thr. Youden |
|---|---|---|---|---|---|---|
| SRTM | 0.748 | 0.691 | 0.710 | 0.647 | 0.677 | 0.424 |
| Copernicus GLO-30 | 0.736 | 0.662 | 0.649 | 0.706 | 0.676 | 0.519 |
| ALOS AW3D30 | 0.761 | 0.691 | 0.686 | 0.706 | 0.696 | 0.540 |

### 2.2 Sensitivitas spasial (perbandingan piksel PENUH se-ROI di GEE, bukan dari n=270)

| Pasangan | mean\|Δprobabilitas\| | Agreement kelas |
|---|---|---|
| SRTM vs GLO-30 | 0.046 | 76.4% |
| SRTM vs AW3D30 | 0.036 | 81.6% |
| GLO-30 vs AW3D30 | 0.045 | 76.5% |

### 2.3 Luas per kelas kerawanan (km²)

| Kelas | SRTM | GLO-30 | AW3D30 |
|---|---|---|---|
| 1 (sangat rendah) | 14.5 | 20.6 | 14.1 |
| 2 (rendah) | 394.5 | 512.7 | 417.9 |
| 3 (sedang) | 588.1 | 503.8 | 578.0 |
| 4 (tinggi) | 279.5 | 248.3 | 261.2 |
| 5 (sangat tinggi) | 27.7 | 19.0 | 33.2 |

Pola: GLO-30 menggelembungkan kelas 2 (+~30% vs SRTM) dan mengecilkan kelas 4–5;
kelas 3 dominan di semua konfigurasi (~500–588 km²).

### 2.4 Matriks transisi kelas (baris = asal, kolom = tujuan; satuan piksel 30 m)

**SRTM → GLO-30** (total pindah terbesar di kelas 3→2: 169.065 px; 3→4: 34.532 px):

|  | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| 1 | 13692 | 2602 | 0 | 0 | 0 |
| 2 | 9461 | 405958 | 29069 | 24 | 0 |
| 3 | 0 | 169065 | 459026 | 34532 | 1 |
| 4 | 0 | 43 | 79260 | 229199 | 6427 |
| 5 | 0 | 0 | 261 | 15985 | 14942 |

**SRTM → AW3D30** (diagonal dominan; pindah terbesar 3→2: 82.634 px):

|  | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| 1 | 11288 | 4699 | 0 | 0 | 306 |
| 2 | 4543 | 383523 | 50771 | 0 | 5674 |
| 3 | 0 | 82634 | 541109 | 30566 | 8314 |
| 4 | 0 | 0 | 59285 | 247505 | 8139 |
| 5 | 0 | 0 | 0 | 16195 | 14993 |

**GLO-30 → AW3D30** (pindah terbesar 2→3: 153.655 px — cerminan kelas-2 GLO-30 yang menggembung):

|  | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| 1 | 12897 | 9497 | 1 | 0 | 757 |
| 2 | 2934 | 415981 | 153655 | 44 | 5052 |
| 3 | 0 | 45354 | 456003 | 59748 | 6512 |
| 4 | 0 | 24 | 41505 | 226122 | 12087 |
| 5 | 0 | 0 | 0 | 8352 | 13018 |

### 2.5 Stratifikasi WorldCover (sorotan; file lengkap `worldcover_sensitivity.csv`)

- **SRTM vs GLO-30**: Tree cover paling sensitif (agreement 69,1%, pindah kelas 30,9%);
  Shrubland paling stabil (agreement 86,0%).
- **SRTM vs AW3D30**: semua kelas agreement 73–85%; kelas Air 26,8% pindah kelas.
- **GLO-30 vs AW3D30**: kelas Air paling sensitif (agreement 65,3%, pindah 34,7%);
  Tree cover agreement 72,8%. mean|Δp| tertinggi pada Air (0,055) dan Tree cover (0,052).

### 2.6 Statistik deskriptif DEM (validasi kewarasan input)

Elevasi mean: SRTM 40,62 m / GLO-30 39,06 m / AW3D30 41,36 m
(median ~5–9 m — konsisten dataran pesisir + perbukitan selatan;
offset vertikal GLO-30 −1,56 m dan AW3D30 +0,40 m vs SRTM, dilaporkan tanpa koreksi).
Slope mean: SRTM 3,03° / GLO-30 2,46° / AW3D30 3,13°.

---

## 3. Hasil run v18 (uji stabilitas + diagnostik sampling; n = 270 juga)

Perubahan v18 vs v17: (a) aspect 0 → −1; (b) diagnostik tahap sampling
(cacah lokasi tahap-1 vs titik tahap-2 + fraksi null per band). Selebihnya identik.

### 3.1 Metrik holdout v18 (test ≈ 68 sampel)

| Konfigurasi | ROC-AUC | Akurasi | Presisi | Recall | F1 |
|---|---|---|---|---|---|
| SRTM | 0.669 | 0.662 | 0.720 | 0.529 | 0.610 |
| Copernicus GLO-30 | 0.634 | 0.632 | 0.655 | 0.559 | 0.603 |
| ALOS AW3D30 | 0.650 | 0.632 | 0.680 | 0.500 | 0.576 |

### 3.2 Sensitivitas spasial v18

| Pasangan | mean\|Δp\| | Agreement |
|---|---|---|
| SRTM vs GLO-30 | 0.050 | 74.7% |
| SRTM vs AW3D30 | 0.036 | 81.5% |
| GLO-30 vs AW3D30 | 0.052 | 71.9% |

### 3.3 Perbandingan v17 vs v18 (TEMUAN KUNCI #1 — stabilitas)

- Metrik holdout BERAYUN BESAR antar-run (AUC SRTM 0.748 → 0.669; AW3D30 0.761 → 0.650).
  Penyebab: test hanya ±68 sampel → varians estimasi besar (CI akurasi ≈ ±0.11–0.12).
- Sensitivitas spasial STABIL antar-run (agreement SRTM–AW3D30: 81.6% → 81.5%;
  GLO-30 selalu paling divergen). Penyebab: dihitung dari JUTAAN piksel se-ROI di GEE,
  bukan dari n=270.
- Kesimpulan sementara: **pola sensitivitas spasial dapat dipercaya meski model lemah**;
  **peringkat model antar-DEM (AW3D30 "terbaik") BELUM dapat diklaim** — selisih AUC
  (0.012–0.025) tenggelam dalam noise sampling.

---

## 4. Diagnostik sampling v18 (TEMUAN KUNCI #2 — akar masalah n kecil)

Angka eksak dari log kernel v18 (status COMPLETE):

| Tahap | Kelas 0 (non-flood) | Kelas 1 (flood) |
|---|---|---|
| Piksel tersedia di ROI (30 m) | 1.410.980 | 58.573 |
| Diminta (`SAMPLE_PER_CLASS`) | 3000 | 3000 |
| Lokasi tahap-1 (`Image.sample` single-band) | **244** | **135** |
| Titik tahap-2 (`sampleRegions` 21 band) | 239 | 135 |
| Setelah filter notNull | 239 | 135 |
| Final (balance ke minoritas) | 135 | 135 |

- **Kehilangan 92–95% terjadi di TAHAP-1** (`ee.Image.sample` pada single-band
  `flood_label` mengembalikan 244/135 dari 3000 yang diminta, padahal 1,4 jt / 58 rb
  piksel tersedia). Tahap-2 hampir tanpa kehilangan (244→239, 135→135).
- **Fraksi null per band pada data terekstrak = 0,0 untuk SEMUA 21 band**
  (aspect_*, elevation_*, slope_* ketiga DEM, HAND, dsb.) → hipotesis "mask multi-band
  menggugurkan titik" GUGUR untuk kondisi pasca-perbaikan.
- Riwayat perbaikan: v15/v16 (river_width masih ber-mask, sampling langsung pada stack
  21-band) → hanya 10–12 titik. v17 (`river_width.unmask(0)` + sampling dua tahap) → 270.
  Kernel diagnostik terpisah membuktikan `river_width` (MERIT `wth`) hanya valid di
  17.031 dari ~1.467.000 piksel (1,2%) — bottleneck saat itu.
- Status: penyebab `sample()` mengembalikan sedikit titik BELUM diketahui mekanismenya
  (dugaan: perilaku internal `Image.sample` pada region besar; BUKAN kekurangan piksel).
  **Status: TERATASI di v20** — ganti tahap-1 dengan `stratifiedSample` pada
  single-band label (lihat §5.1).

---

## 5. Run v20 — sampling BESAR via stratifiedSample (n = 5872)

Perubahan vs v18: tahap-1 memakai `stratifiedSample` pada single-band `flood_label`
(`classPoints=[3000, 3000]`, seed 42) + audit distribusi sampel + spatial holdout
(16 blok kuantil lon/lat, 4 blok ditahan: [0, 9, 11, 14]).

### 5.1 Sampling v20 — masalah tahap-1 TERKONFIRMASI & TERATASI

| Tahap | Kelas 0 | Kelas 1 |
|---|---|---|
| Piksel tersedia (30 m) | 1.410.980 | 58.573 |
| Diminta | 3000 | 3000 |
| Lokasi tahap-1 (stratifiedSample) | **3000** | **3000** (kuota tepat terpenuhi) |
| Titik tahap-2 (sampleRegions) | — (total 5921, hilang 1,3%) | — |
| Mentah pasca-filter notNull | 2936 | 2985 |
| Final (balance) | 2936 | 2936 (n total 5872) |

Fraksi null per band tetap 0,0. Retensi tahap-2 = 98,7%. **Fix metodologis valid.**

### 5.2 Metrik holdout v20 (sklearn RF, test 25% ≈ 1468 sampel)

| Konfigurasi | ROC-AUC | Akurasi | Presisi | Recall | F1 |
|---|---|---|---|---|---|
| SRTM | 0.811 | 0.723 | 0.717 | 0.736 | 0.726 |
| Copernicus GLO-30 | 0.810 | 0.736 | 0.729 | 0.749 | 0.739 |
| ALOS AW3D30 | 0.807 | 0.730 | 0.726 | 0.738 | 0.732 |

**Ketiga DEM kini praktis IDENTIK (rentang AUC 0,004)** — perbedaan performa model
antar-DEM yang tampak pada n=270 hilang pada n besar. Mendekati baseline SMDS
(AUC 0,852) tetapi belum menyamai (satu kejadian, fitur lebih sedikit).

### 5.3 Sensitivitas spasial v20 (piksel penuh se-ROI)

| Pasangan | mean\|Δp\| | Agreement |
|---|---|---|
| SRTM vs GLO-30 | 0.061 | 68.3% |
| SRTM vs AW3D30 | 0.035 | 81.1% |
| GLO-30 vs AW3D30 | 0.057 | 69.6% |

Pola TIGA KALI konsisten (v17/v18/v20): **SRTM–AW3D30 ≈ 81–82%, pasangan
dengan GLO-30 selalu lebih divergen (kini 68–70%)**. Divergensi justru menguat
pada model yang lebih baik.

### 5.4 Luas per kelas v20 (km²)

| Kelas | SRTM | GLO-30 | AW3D30 |
|---|---|---|---|
| 1 | 121.3 | 221.1 | 130.7 |
| 2 | 479.6 | 506.3 | 478.9 |
| 3 | 412.1 | 334.0 | 402.0 |
| 4 | 244.1 | 203.6 | 239.2 |
| 5 | 47.2 | 39.3 | 53.6 |

GLO-30 konsisten menggelembungkan kelas 1–2 dan mengecilkan kelas 3–5.

### 5.5 Matriks transisi v20 (sorotan)

- **SRTM→GLO-30**: 3→2 sebesar 156.652 px; 2→1 sebesar 125.117 px (perpindahan
  besar ke kelas lebih rendah — konsisten inflasi kelas rendah GLO-30).
- **SRTM→AW3D30**: diagonal dominan (2→2: 463.077; 3→3: 362.792).
- **GLO-30→AW3D30**: 2→3 sebesar 144.869 px (cerminan kelas-2 GLO-30 yang menggembung).

### 5.6 Stratifikasi WorldCover v20 (sorotan)

- **Built-up PALING sensitif** pada pasangan GLO-30: agreement 62,5% (srtm–glo30)
  dan 65,4% (glo30–aw3d30); mean|Δp| tertinggi 0,081; 37,5% piksel built-up pindah kelas.
- Tree cover: agreement 60,6% (srtm–glo30), pindah 39,4%.
- Mangroves paling stabil (agreement ~81–85%). Kelas Air: agreement 65–75%.

### 5.7 Audit sampel v20 (`sample_audit.csv`)

- Rentang lon/lat kedua kelas mencakup seluruh ROI (lon 110,29–110,83;
  lat −7,09–−6,71) → **tidak ada konsentrasi spasial kasar**.
- Sampel flood lebih rendah & datar sesuai fisika: mean elevasi SRTM 3,24 m (vs 4,15
  non-flood); mean slope SRTM 1,73° (vs 1,93°); slope GLO-30 flood 0,39° (vs 0,70°).
- Komposisi flood: Cropland 52,3%, Air 31,0%, Wetland 15,5%.
  Komposisi non-flood: Cropland 43,6%, Air 30,0% (WorldCover, bukan JRC),
  Wetland 16,9%.
- **Caveat fusi data**: 30% sampel non-flood jatuh pada piksel "Air" WorldCover
  meski perairan permanen JRC sudah dikecualikan → kedua produk air tidak identik;
  perlu catatan metodologis, bukan cacat fatal (label ikut JRC+S1, konsisten antar-DEM).

### 5.8 Spatial holdout v20 — ADA CACAT, jangan dikutip sebagai hasil

| Konfigurasi | n | AUC-spatial | F1-spatial |
|---|---|---|---|
| SRTM | 2377 | 0.917 | 0.910 |
| GLO-30 | 2377 | 0.920 | 0.913 |
| AW3D30 | 2377 | 0.921 | 0.914 |

**Angka ini TERINFLASI dan TIDAK VALID sebagai uji generalisasi spasial**:
model dilatih pada random-train 75% dari SEMUA baris, sehingga ±75% titik
spatial-test sudah dilihat saat training (kontaminasi train-test).
Skor 0,92 ≈ akurasi training, bukan generalisasi. **Status: SUDAH DIGANTIKAN** —
v22 memakai 4-fold spatial CV dengan retrain per fold (lihat §6.3).

### 5.9 Keterbatasan yang diakui (revisi pasca-v20)

1. Satu kejadian banjir, satu AOI, satu seed (42) — generalisasi belum diuji.
2. Inventory Sentinel-1 = proksi (bukan ground truth lapangan).
3. Threshold S1 + tanggal kejadian belum diuji sensitivitasnya (di luar lingkup).
4. SRTM = DEM C-band; Copernicus/ALOS = DSM (bukan DTM bare-earth).
5. Offset datum EGM96 vs EGM2008 dilaporkan tanpa koreksi.
6. Spatial holdout v20 terkontaminasi (lihat 5.8) — menunggu desain ulang v21.
7. Perbedaan produk air JRC vs WorldCover (lihat 5.7) — perlu catatan metodologis.

---

## 6. Run v22 — spatial CV valid + aspect sin/cos (n = 5872, HASIL UTAMA)

Perubahan vs v20 (v21 ERROR sebelum CSV tersimpan — hanya log yang selamat):
(a) aspect `-1` → `aspect_sin`/`aspect_cos` (0 netral di dataran) + `aspect_valid`
(flag slope>0), identik ketiga DEM — 25 prediktor;
(b) spatial holdout bocor DIGANTI 4-fold spatial CV: 16 blok → 4 fold
(seed tetap, fold SAMA untuk 3 DEM), tiap fold latih ULANG RF (parameter identik)
hanya pada 12 blok, uji pada 4 blok;
(c) SEMUA visualisasi tile (Map/Map2/Map3) dibuat fault-tolerant (pelajaran v21:
`Map3.addLayer` → getMapId timeout SETELAH semua sains selesai).
Hasil di `Proposal Baru\hasil_kaggle_v22\` (15 file + `spatial_cv_metrics.csv`).

### 6.1 Sampling v22 — reproduksibel

Identik dengan v20 (seed sama): tahap-1 3000/3000 → tahap-2 5921 →
final 2936/kelas (n=5872). Audit `sample_audit.csv` identik v20.

### 6.2 Metrik holdout v22 (random-split, test ±1468)

| Konfigurasi | ROC-AUC | Akurasi | F1 |
|---|---|---|---|
| SRTM | 0.830 | 0.750 | 0.756 |
| Copernicus GLO-30 | 0.828 | 0.736 | 0.740 |
| ALOS AW3D30 | 0.829 | 0.746 | 0.752 |

Ketiga DEM tetap IDENTIK (rentang AUC 0,002). Encoding sin/cos menaikkan AUC
±0,02 vs v20 untuk SEMUA konfigurasi secara merata (0,807–0,811 → 0,828–0,830).

### 6.3 Spatial CV v22 — estimasi generalisasi yang JUJUR (`spatial_cv_metrics.csv`)

| Fold | n train | n test | pos_rate test | AUC srtm | AUC glo30 | AUC aw3d30 |
|---|---|---|---|---|---|---|
| 0 | 3501 | 2371 | 0.457 | 0.651 | 0.657 | 0.641 |
| 1 | 4698 | 1174 | 0.756 | 0.627 | 0.624 | 0.616 |
| 2 | 3982 | 1890 | 0.395 | 0.643 | 0.631 | 0.646 |
| 3 | 5435 | 437 | 0.501 | 0.686 | 0.693 | 0.689 |
| **mean** | — | — | — | **0.652** | **0.651** | **0.648** |

- Generalisasi spasial ≈ **0,65** vs random-split 0,83 → optimism gap ±0,18,
  sesuai prediksi literatur (random-split optimistis pada data spasial).
- F1 spatial: SRTM 0,575–0,731; pola sama untuk ketiga DEM.
- **Ketiga DEM identik pula di bawah spatial CV** (mean 0,648–0,652).
- Fold 1 (test 75,6% flood) dan fold 2 (test 39,5% flood) menunjukkan
  komposisi blok bervariasi — sumber varians antar-fold yang wajar dilaporkan.

### 6.4 Sensitivitas spasial v22 (piksel penuh)

| Pasangan | mean\|Δp\| | Agreement |
|---|---|---|
| SRTM vs GLO-30 | 0.069 | 64.3% |
| SRTM vs AW3D30 | 0.040 | 77.1% |
| GLO-30 vs AW3D30 | 0.061 | 67.7% |

Pola KEEMPAT KALI konsisten: SRTM–AW3D30 paling mirip (77–82%),
pasangan GLO-30 divergen (64–70%). Divergensi GLO-30 sedikit menguat
pada encoding baru — arah temuan tidak berubah.

### 6.5 Sorotan lain v22

- Luas kelas: GLO-30 tetap menggelembungkan kelas 1 (253,7 vs 127,8–178,6 km²)
  dan mengecilkan kelas 3 (308,4 vs 371,1–387,6 km²).
- WorldCover: **built-up makin sensitif** — agreement srtm–glo30 56,7%
  (was 62,5%), mean|Δp| 0,094; tree cover 55,1%; mangroves tetap stabil (~80–84%).
- Transisi SRTM→GLO-30: 2→1 sebesar 158.578 px; 3→2 sebesar 157.057 px.

### 6.6 Status bukti (untuk reviewer)

- v17/v18 → diagnostik pipeline (n=270, metrik tidak stabil).
- v20 → pilot sampel besar (n=5872); spatial holdout-nya INVALID (leakage).
- v21 → ERROR (viz timeout); hanya log spatial-CV awal yang selamat
  (≈0,64–0,66 — konsisten dengan v22).
- **v22 → kandidat hasil utama**: n besar + spatial CV valid + encoding final.
  Major revision reviewer (1) dan (3) TERJAWAB; (2) terjawab via audit +
  blocking (ketergantungan spasial diakui lewat gap 0,83→0,65, bukan dihapus).

## 7. Run v23 — bridging ke sampel baseline (n = 1720, titik+split identik)

Motivasi: memanfaatkan `train_test_split_assignment.csv` dari kernel revision
baseline (1870 titik, 935/kelas, split train 1402/test 468 + 5 spatial fold —
diunduh dari output kernel, tersedia publik di akun yang sama). Nilai prediktor
baseline DIBUANG; yang dipakai hanya lon/lat + label + split. Semua 27 band
diekstrak ulang; ketiga DEM berbagi 1870 lokasi yang sama (master sample).

### 7.1 Retensi & konsistensi label

- Impor 1870 → tahap-2 1778 (95,1%) → pasca-notNull {0:860, 1:918} →
  balance 860/kelas (n=1720). Split terpakai: train 1295 / test 425.
- **Konsistensi label CSV vs `flood_label` kita pada titik yang sama: 0,699.**
  Padahal kode S1, parameter (threshold 1,25/−18 dB/slope<5°/connected≥8),
  tanggal, ROI, bahkan SAMPLE_SCALE/TILE_SCALE (30/8) semuanya identik.
### 7.1b Mengapa arsip historis bisa bergeser (penjelasan)

Periode akuisisi yang sama TIDAK menjamin piksel yang sama, karena:

1. **Reprocessing arsip.** ESA secara berkala mengolah ulang arsip Sentinel-1
   (versi prosesor/IPF baru, koreksi orbit, kalibrasi radiometrik, pembersihan
   noise tepi), dan GEE ikut menelan versi barunya. Tanggal tetap "Maret 2024",
   tetapi angka desibel tiap piksel dapat bergeser sepersekian dB.
2. **Amplifikasi ambang.** Label kita memakai threshold tajam (rasio > 1,25 dan
   < −18 dB), dan di dataran banjir area LUAS duduk persis di sekitar ambang
   itu. Analogi: batas lulus 60 — geseran 1 poin memindahkan puluhan persen
   peserta antar-kategori meski soalnya sama.
3. **Kandidat slope-mask GUGUR** (terverifikasi langsung dari kedua notebook:
   keduanya memakai slope SRTM < 5°), sehingga drift arsip menjadi hipotesis
   terkuat — tetapi tetap hipotesis, bukan fakta terbukti.
4. **Uji penentu (diusulkan, belum dijalankan)**: petakan DI MANA 30% yang tidak
   cocok berada. Jika menumpuk di tepi patch banjir → teori ambang+geseran
   terbukti. Jika tersebar sampai tengah patch → ada perbedaan struktural yang
   belum ditemukan; klaim bridging ditunda sampai ketemu. Uji ini murah
   (kernel diagnostik kecil, bukan full pipeline).
- Klaim "inventory identik" DILUNAKKAN menjadi "kode dan parameter identik;
  realisasi label cocok 70%".

### 7.2 Metrik bridging (split baseline, test 425) — vs baseline RF 0,852

| Konfigurasi | ROC-AUC | Akurasi | F1 |
|---|---|---|---|
| SRTM (kita, titik+split baseline) | 0.802 | 0.732 | 0.740 |
| Copernicus GLO-30 | 0.795 | 0.706 | 0.713 |
| ALOS AW3D30 | 0.792 | 0.734 | 0.744 |
| Baseline RF (publikasi, titik+split sama) | 0.852 | 0.782 | 0.795 |

- Pipeline kita di titik/split baseline mencapai 0,80 — sebola (±0,05) dengan
  0,852, validasi kewarasan lolos; selisih dijelaskan oleh set fitur berbeda
  (25 vs set baseline), encoding baru, dan hyperparameter RF berbeda.
- Ketiga DEM lagi-lagi IDENTIK (rentang AUC 0,01) — pola kelima kali.

### 7.3 Sensitivitas spasial v23

| Pasangan | mean\|Δp\| | Agreement |
|---|---|---|
| SRTM vs GLO-30 | 0.055 | 73.5% |
| SRTM vs AW3D30 | 0.035 | 81.9% |
| GLO-30 vs AW3D30 | 0.054 | 73.6% |

Pola KELIMA KALI konsisten (SRTM–AW3D30 ≈ 82%, pasangan GLO-30 ≈ 73–74%).

### 7.4 Spatial CV bridging — LEMAH, laporkan apa adanya

Mean AUC ≈ 0,57/0,59/0,56 (fold 2 bahkan <0,50); n per fold kecil + label
CSV-vs-inventory 30% berbeda menambah noise. v22 (mean 0,65, n=5872) tetap
estimasi spasial yang kredibel; v23 bukan penggantinya untuk generalisasi.

### 7.5 Status bukti (revisi)

- **v22 → hasil utama** (tidak berubah).
- **v23 → jembatan komparabilitas**: (a) pipeline kita ±0,05 dari baseline di
  titik/split identik; (b) pola sensitivitas spasial independen-terhadap-sampel
  (5 run, 3 skema sampling berbeda, hasil sama); (c) temuan 70% label-match
  sebagai catatan audit inventori.

## 8. Status pertanyaan reviewer (diperbarui pasca-v23)

1. ~~Laporkan v17/v18 sebagai hasil pilot?~~ → **Terjawab**: v17/v18 = diagnostik
   pipeline saja; tidak masuk hasil utama. Pola spasialnya yang stabil dipakai
   sebagai indikasi awal.
2. ~~"GLO-30 paling divergen, AW3D30 paling mirip SRTM" sah?~~ → **Terjawab, YA
   dengan batasan**: sah sebagai *map sensitivity/disagreement* (konsisten 4 run),
   BUKAN sebagai akurasi/superioritas DEM.
3. ~~aspect = −1 + river_width = 0 dapat dibela?~~ → **Terjawab + digantikan**:
   `river_width = 0` defensible (makna substantif); `−1` acceptable untuk pilot,
   digantikan encoding sin/cos + flag pada v22.
4. ~~stratifiedSample perbaikan yang tepat?~~ → **Terjawab + terimplementasi**:
   kuota 3000/3000 tepat terpenuhi (v20/v22); satu master sample untuk ketiga DEM.
5. Risiko bias seleksi spasial (balancing 1:1 tidak menghapusnya) → **Dijawab
   sebagian**: audit (§5.7) + blocking mengakui ketergantungan spasial lewat
   gap random-split vs spatial-CV (0,83 → 0,65). Sisa: multi-season/multi-AOI
   di luar lingkup proposal.
6. Bridging baseline (baru, §7) → pipeline kita 0,80 vs 0,852 di titik/split
   identik (validasi kewarasan lolos); pola spasial 5× konsisten; temuan
   label-match 70% dicatat sebagai audit inventori, bukan kegagalan.

## 9. Koreksi sampling v24 (17 Okt 2026) - fix sabuk JRC, hasil LOKAL

Temuan T01 (bias "sabuk JRC", MET-001): kode v20-v22 memakai
`permanent_water` = JRC `occurrence>=80` yang SPARSE; `.Not()` atas no-data
membuang 91,2% label=0 dari kandidat kelas-0 -> sampel non-flood v20-v22
terkurung sabuk terpetakan JRC (elev 4,15 m vs 42 m se-AOI). Diverifikasi:
replika lokal seed-42 pada `reanalisis_v24.py` mode `v22` menghasilkan sampel
kelas-0 IDENTIK PENUH dengan Kaggle v22 (elev 4,1546+-15,6915, lat
-7,092424..-6,710280, lc identik 4 dp). Detail bukti: `temuan/T01` d4-d8.

Fix: `pw_for_sampling = permanent_water.unmask(0)` (no-data JRC = bukan air)
sebelum `.Not()` pada sampling_mask; pool kelas-0 = 1.382.033 px (97,95% dari
label=0). Analisis RF identik (seed 42, AUC proba-corrected - MET-002).

### Hasil dua mode (lokal sklearn, n = 5872 sabuk / 5956 fix)

| Metrik | SRTM | GLO-30 | AW3D30 |
|---|---|---|---|
| v22 sabuk: AUC holdout | 0,8267 | 0,8205 | 0,8187 |
| v22 sabuk: AUC spatial-CV (proba) | 0,6979 | 0,6999 | 0,6954 |
| v24 fix: AUC holdout | 0,9312 | 0,9399 | 0,9355 |
| v24 fix: AUC spatial-CV (proba) | 0,8694 | 0,8895 | 0,8747 |
| v24 fix: dAUC bootstrap vs SRTM (95%) | - | +0,0161 [+0,0128..+0,0194] | +0,0054 [+0,0027..+0,0080] |

Pembacaan: (a) order GLO-30 > AW3D30 > SRTM konsisten 2 skema pada sampel
terkoreksi, gap ~0,01; (b) dalam domain sabuk ketiga DEM TIDAK terbedakan
(0,695-0,700, CI meliputi 0); (c) dua skala ini estimasi domain berbeda dan
harus dilaporkan berdampingan.

CAVEAT: bootstrap belum blok-spasial (CI optimistis utk gap 0,01); angka
lokal sklearn = 24 prediktor (1 kolom drop otomatis). Angka final = rerun
kernel GPU T4 di bawah (25 prediktor). Artefak lokal: `Temp\opencode\reanalisis_v24\run_{v22sabuk,v24fix}\` — temp workspace kemudian ter-wipe;
semua angka kunci telah dipindahkan ke dokumen ini dan `temuan/T01` §8.

### Hasil akhir kernel v24 (18 Okt 2026, GPU T4; angka FINAL)

Kernel id `nxtirfan/flood-dem-sensitivity-notebook-v24-fix-sabuk-jrc`
(v25; runtime ~50 menit; 19 artefak tersimpan di
`Proposal Baru\hasil_kaggle_v24\`; ekspor peta 12 item ke Drive).

Replikasi lokal FULL: probe identik (AOI 1.469.555; JRC valid 187.777;
pw 28.948; label0 1.410.981; pool sabuk 123.616/8,76%; pool v24
1.382.033/97,95%); n final 2.978/kelas; audit kelas-0 identik 6 dp
(elev_srtm 42,6682; lat -7,136890..-6,709741); fold spasial sama
([[0,1,5,14],[8,9,11,13],[2,4,7,15],[3,6,10,12]]).

| Metrik | SRTM | GLO-30 | AW3D30 |
|---|---|---|---|
| AUC holdout (n test = 1.489)            | 0,9318 | 0,9404 | 0,9360 |
| Accuracy @0,5 / F1 @0,5                 | 0,8744 / 0,8791 | 0,8899 / 0,8945 | 0,8784 / 0,8833 |
| AUC spatial-CV (proba; 4 fold blok)     | 0,8699 | 0,8899 | 0,8747 |
| AUC spatial-CV (legacy pseudo)          | 0,7883 | 0,8170 | 0,7936 |
| F1 spatial-CV / Accuracy spatial-CV      | 0,7964 / 0,8020 | 0,8263 / 0,8240 | 0,8016 / 0,8044 |
| Bootstrap dAUC vs SRTM (1.000x, 95%)    | - | +0,0141 [+0,0109..+0,0173] | +0,0048 [+0,0023..+0,0074] |
| Bootstrap dAUC glo30 - aw3d30           | - | - | - (glo30 > aw3d30: +0,0094 [+0,0063..+0,0124]) |
| AUC pooled 4 fold (dari bootstrap)      | 0,9032 | 0,9174 | 0,9080 |

Sensitivitas spasial penuh peta (4.249.500 px AOI):

| Pasangan | mean abs delta prob | agreement rate |
|---|---|---|
| SRTM vs GLO-30  | 0,0555 | 79,42% |
| SRTM vs AW3D30  | 0,0371 | 83,95% |
| GLO-30 vs AW3D30 | 0,0483 | 81,30% |

Luas 5 kelas risiko (km2, SRTM/GLO-30/AW3D30):
- Kelas 1 (sangat rendah): 756,7 / 822,6 / 772,5
- Kelas 2: 233,2 / 190,0 / 222,0
- Kelas 3: 114,0 / 98,4 / 108,1
- Kelas 4: 95,3 / 79,2 / 88,2
- Kelas 5 (sangat tinggi): 105,2 / 114,2 / 113,4

Matriks transisi (px) + sensitivitas per kelas WorldCover tersimpan
lengkap di `Proposal Baru\hasil_kaggle_v24\`
(transition_*.csv, worldcover_sensitivity.csv).

Pembacaan final:
1. Urutan GLO-30 > AW3D30 > SRTM KONSISTEN pada 3 skema (holdout,
   spatial-CV 4 fold blok, pooled CV), tetapi gap jujur kecil
   (0,005-0,014; bukan beda besar).
2. POLA SPASIAL 6x KONSISTEN (v17-v24): SRTM dan AW3D30 paling sejalan
   (agreement 83,95%; mean abs delta 0,0371); GLO-30 tetap paling
   divergen terhadap keduanya — GLO-30 juga paling agresif menandai risiko
   tinggi (kelas 5: 114,2 km2 vs 105,2 SRTM), konsisten dengan karakternya
   sebagai DSM paling mulus (vegetasi/gedung ikut naik).
3. Lompatan besar performa v22 -> v24 menunjukkan estimasi SANGAT
   sensitif terhadap DOMAIN SAMPLING kelas-0 (bagian mask JRC) — pesannya
   ke skripsi: domain sampling label jauh lebih menentukan presisi daripada
   perbedaan DEM itu sendiri; pilihan DEM memengaruhi orde 0,01 AUC.
4. Luas kelas 5 bergeser 5-9 km2 antar DEM (SRTM 105,2 / GLO-30 114,2 /
   AW3D30 113,4) — perbedaan region-level signifikan (delta ~4-12%) dan
   layak dikritisi spasial per-blok; peta per-blok tersimpan di Drive.

Caveat tersisa (utk proposal/diskusi):
- bootstrap ΔAUC piksel-level (1.000x, resample baris sampel) BELUM
  blok-spasial — CI pada gap 0,01 masih optimistis; saran: cluster
  bootstrap per blok 16 untuk versi artikel.
- gap 0,01 pada 5.956 sampel acak: perbandingan antar-DEM lebih tepat
  dibaca sebagai "komparasi nilai tak berbeda secara praktis" — klaim
  praktis = ketiga DEM memadai untuk pemetaan risiko banjir pesisir
  Semarang-Demak, dengan GLO-30 sedikit lebih baik jika diukur se-AOI.
- kolom fitur lokal (24) vs kernel (25): metrik beda ~0,001-0,005 —
  hasil KERNEL dijadikan rujukan (angka di atas).


## 10. Kernel v26 - respons reviewer (18 Okt 2026, COMPLETE; artefak Proposal Baru\hasil_kaggle_v26\, 25 file)

Pipeline utama tereplikasi PERSIS di v26 (model_metrics=sama dengan v24 sampai
desimal ketiga), lalu menambah dua analisis baru (patch notebook, 47 sel).

### 10.1 Block bootstrap 16 blok (utama; spatial_cv_delta_auc_bootstrap.csv)
- Resampling blok kuantil lon/lat (16 blok yang sama dengan CV spasial),
  dengan penggantian, 1.000 iterasi, seed 42; AUC kedua DEM dihitung pada
  resample yang sama (paired).
- Pooled CV AUC: SRTM 0,894 / GLO-30 0,910 / AW3D30 0,899.
- Delta AUC (95% CI percentile): GLO-30-SRTM -0,0155 [-0,0250, -0,0072]
  (tidak memuat 0); GLO-30-AW3D30 +0,0108 [+0,0041, +0,0198] (tidak memuat 0);
  SRTM-AW3D30 -0,0047 [-0,0096, +0,0013] (CI MEMUAT 0 - keunggulan AW3D30
  atas SRTM marginal).
- Bootstrap piksel-level lama disimpan sebagai pembanding
  (spatial_cv_delta_auc_bootstrap_pixel_legacy.csv; |Delta| GLO-30-SRTM
  0,0141 [0,0109, 0,0173]).

### 10.2 Multi-seed 5 seed (42/100/2024/7/99; multiseed_*.csv)
- Tiap seed = pipeline ulang dari nol (sampling GEE, ekstraksi, split acak,
  spatial CV). RF sklearn 400 pohon, min_leaf 2, class_weight balanced,
  random_state=seed.
- Holdout AUC mean/std: SRTM 0,939/0,014, GLO-30 0,947/0,010, AW3D30
  0,940/0,012. Spatial-CV proba: SRTM 0,869/0,017, GLO-30 0,889/0,013,
  AW3D30 0,877/0,017.
- Delta AUC lintas seed (mean +/- std, semua tanda per-seed konsisten kecuali
  disebut): holdout GLO-30-AW3D30 +0,0070+/-0,0027 (5/5 positif); holdout
  GLO-30-SRTM -0,0082+/-0,0048 (5/5); holdout SRTM-AW3D30 -0,0012+/-0,0021
  (2 positif / 3 negatif - DEM mendekati); spatial CV GLO-30-AW3D30
  +0,0121+/-0,0055 (5/5); spatial CV GLO-30-SRTM -0,0200+/-0,0039 (5/5);
  spatial CV SRTM-AW3D30 -0,0079+/-0,0034 (5/5 - AW3D30 di atas SRTM).
- Peringkat GLO-30 > AW3D30 > SRTM konsisten 5/5 seed, kedua skema.
- **Koreksi label (T05, 22 Okt)**: baris di atas menulis pasangan sesuai
  sebutan lama "GLO-30-SRTM"; CSV sesungguhnya memakai pair
  `srtm-minus-glo30` dst. → makna benar: **holdout SRTM−GLO-30 =
  −0,0082; spatial CV SRTM−GLO-30 = −0,0200** (GLO-30 di atas SRTM);
  pasangan lain sesuai sebutan. Naskah final memakai subscript explicit
  ΔAUC_SRTM−GLO-30 dsb. (lihat `temuan/T05-adopsi-revisi-gemini.md`).

### 10.3 Catatan seed-42 multiseed vs primary
- Batch multiseed seed-42 (holdout 0,9497/0,9551/0,9495) TIDAK identik
  primary (0,9318/0,9404/0,9360): jalur ekstraksi multiseed = realisasi
  terpisah (urutan baris ee_to_df berbeda menggeser pemilihan balancing
  pandas walau RF deterministik). CV multiseed nyaris cocok dengan primary
  (0,869/0,889/0,877 vs 0,870/0,890/0,875) dan holdout primary berada dalam
  1 std rerata multiseed. Narasi dokumen: "lima realisasi independen",
  BUKAN klaim identik seed-42 = primary.

### 10.4 Status bukti pasca-v26
- Klaim yang KINI didukung: (a) keunggulan GLO-30 atas SRTM dan atas AW3D30
  bertahan pada block bootstrap (CI tidak memuat 0); (b) peringkat identik di
  5/5 seed; (c) SRTM vs AW3D30 tidak dapat ditegakkan (CI memuat 0; holdout
  multiseed tanda campuran), AW3D30 konsisten di atas SRTM pada spatial CV.
- Caveat tersisa: granularitas blok kasar (16); satu kejadian; satu AOI.
### 10.5 Probe label-domain pita JRC (N-1 -> MET-009, 20 Okt, T04)
- Audit v26 = dugaan N-1: sel 12 (label) memakai `permanent_water.Not()`
  tanpa `unmask(0)` → flood=1 hanya mungkin di dalam pita occ JRC.
  Probe fresh GEE (5 skrip; bukti `temuan/probe_v26/`): terkonfirmasi
  (c)=0 pada 4 jalur × 2 grid.
- Angka kunci: footprint mask>0 = 189.345 px (12,88% AOI); angka kernel
  "12,78%" (187.777) = Σ luas efektif berbobot mask band (fraksional
  0..1), bukan jumlah piksel; occ-bernilai = 63.499 px (4,32%) — definisi
  lama T01 KEMBALI SAHIH. flood_raw masked 85,70% AOI (99,92% karena JRC);
  flood=1 penuh 58.573 px (3,99% AOI) semuanya di dalam pita.
- Fairness antar-DEM terjaga (label identik lintas eksperimen); yang tak
  dapat diklaim: inventory mewakili seluruh genangan; perilaku banjir di
  luar pita. Kalimat keterbatasan draf ada di T04 (bag. E-1) — MENUNGGU
  keputusan pengguna sebelum tersentuh proposal.
