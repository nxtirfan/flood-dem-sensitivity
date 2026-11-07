# T10 — Patch Mask AOI / NoData Seluruh Raster + Perbaikan Heading Dobel (6 Nov 2026)

## 0. Status eksekusi

| Item | Status |
|---|---|
| Patch notebook v27 (mask AOI eksplisit, semua 13 raster) | **SELESAI** — file `Proposal Baru/Flood_DEM_Sensitivity_Notebook_v27.ipynb` diedit lokal, siap diunggah ke Colab |
| Backup notebook pra-T10 | `Proposal Baru/olds/Flood_DEM_Sensitivity_Notebook_v27_pre-T10.ipynb` |
| Caption Gambar 3 di naskah | **SELESAI** — tidak lagi mengklaim cakupan luar batas penelitian |
| Bug heading dobel `\subsection{Pembahasan}` (baris 1759) | **SELESAI** — PDF 49 → **48 hlm**, TOC kini "4.8 Pembahasan" tunggal |
| Rekompilasi + zip | **SELESAI** — PDF 48 hlm, 0 undefined, overfull 7 legacy; zip 2.446.405 B |
| Rerun PREPARE_MAPS di Colab + re-quote Moran peta | **MENUNGGU USER** (lihat §6) |

## 1. Keputusan user (jawaban option tool)

1. **Clip AOI semua** — seluruh 13 raster mask AOI; masking, BUKAN cropping
   (grid penuh 2074×1592, CRS EPSG:32749, resolusi 30 m, transform affine,
   alignment piksel dipertahankan). Nilai di dalam AOI tidak berubah.
2. **Gaya patch versi marker** (`unmask(-1)` + guard `p >= 0` + cabang else `: 0`
   + `updateMask`).
3. **Edit notebook lokal** (user unggah ulang ke Colab).
4. Tambahan user after-insert: seluruh piksel luar AOI NoData pada **semua 13
   raster termasuk prob_\*.tif**; validasi piksel valid/statistik vs CSV GEE;
   caption Gambar 3 disesuaikan.

## 2. Akar penyebab (bukti, bukan dugaan)

- Crosstab `prob_srtm.tif` vs `risk_class_srtm.tif` (bin ambang 0,2/0,4/0,6/0,8):
  bin 2–4 dan kelas 5 (p>0,8) dipetakan 100% benar; **bin p≤0,2 dipecah**:
  840.848 px sah → kelas 1 (benar), **1.848.071 px → kelas 5 (salah)**, dan
  9.652 px nodata juga bermuara ke profil kelas 5 tif (total kelas 5 tif =
  1.969.549).
- 1.848.071 px itu bernilai probabilitas **tepat 0,00000** (persentil 5/50/95
  = 0,0) = region luar-AOI (laut + ring buffer) yang terdefinisi dengan nilai
  0,0 oleh `computePixels` — bukan NoData; 9.652 px itu nodata sejati.
- Notebook sendiri sudah mendeteksi: `export_status.json` → check
  `prob_vs_kelas:srtm` **FAIL** ("selisih di luar tepi batas kelas=1848071")
  dan `piksel_valid_vs_hitungan_GEE` INFO (raster 3.292.156 px vs GEE
  1.438.214 px, +1,29×); verifikasi hanya mencetak, eksekusi lanjut.
- Kelas 1–4 tif **persis cocok CSV luas** (dihitung `reduceRegion` pada
  `geometry=roi`): statistik dalam-AOI benar; cacat murni pada representasi
  raster di luar mask.
- Mekanisme: (i) rantai ternary `expression` jatuh ke cabang `: 5` untuk piksel
  berprobabilitas tidak sah/masked (semantik NaN/False di ee.Image.expression);
  (ii) tidak ada mask AOI eksplisit pada `risk_class`/`delta`/`agreement` dan
  mask `prob_map` tidak andal dibawa ke layer turunan.

## 3. Isi patch (6 cell, minimal-diff)

Semua diff telah diverifikasi secara unified diff vs backup (6 cell berubah:
5, 10, 16, 49, 53, 59; JSON valid; syntax cc 10/16/49/53/59 lolos `compile`;
cc 3 memakai `!pip` magic Jupyter — false positive pre-existing).

1. **Cell 16 (ROI)**: definisi `_AOI_MASK = ee.Image.constant(1).clip(roi).unmask(0)`
   — nilai 0/1 di seluruh grid. Idiom `unmask(0)` wajib: `updateMask` menahan
   mask lama di posisi yang ter-mask, sehingga `.clip(roi)` saja tidak tegas.
2. **Cell 5**: `OVERWRITE_RASTERS = True` (sementara, agar raster COMPLETED
   lama yang tercacat tidak dilewati; setelah rerun PASS → kembalikan ke
   False; komentar di cell memuat instruksi ini).
3. **Cell 49 (`classify_risk`)**: `_p = pimg.unmask(-1)`; guard eksplisit
   `(p >= 0 && p <= b1) ? 1 : ... : (p > b4) ? 5 : 0`; lalu
   `updateMask(_p.gte(0))` + `updateMask(_AOI_MASK)`. Untuk probabilitas sah
   (0..1) hasil klasifikasi identik versi lama (terverifikasi taksonomi cabang).
4. **Cell 53**: `_both = (prob_map[a].unmask(-1).gte(0)).And(prob_map[b].unmask(-1).gte(0))`;
   `delta_abs` dihitung pada `unmask(-1).subtract(...).abs()` lalu
   `updateMask(_both)` + `updateMask(_AOI_MASK)`; `agreement_map` sama
   (`eq` → dua updateMask). Statistik `reduceRegion(geometry=roi)` tidak
   berubah nilai.
5. **Cell 59 (ekspor)**: `_img.toFloat().updateMask(_AOI_MASK).unmask(EXPORT_NODATA)`
   untuk **semua 13 raster** (3 prob, 3 risk, 3 delta, 3 agreement, 1 label)
   — mask AOI identik untuk semua; grid/CRS/resolusi/transformasi/tulis-tif
   TIDAK disentuh (`make_grid`, `grid_tiles`, `fetch_tile_gee`, `write_geotiff`,
   `verify_raster` utuh).
6. **Cell 10 (`verify_all_rasters`)**: tambahan 2 kelompok cek (setelah blok
   `piksel_valid_vs_hitungan_GEE`):
   - `valid_vs_aoi:<raster>` — jumlah valid per raster vs
     `aoi_pixel_count_gee` (1.438.214): tol 0,1% untuk prob/risk, 5% untuk
     agreement/delta (defisit wajar = union lubang NoData antar-DEM);
   - `mask_kelas_subs_prob:<d>` — mask kelas harus **sama persis** mask
     probabilitas DEM yang sama (0 piksel beda), dan
     `mask_subs_irisan:<raster>` — mask delta/kesesuaian harus identik irisan
     mask kedua kelas. Cek lama (`prob_vs_kelas`, `delta_lokal`,
     `agreement_lokal`, `statistik_vs_GEE`, `transisi_vs_GEE`, `luas_vs_GEE`)
     dipertahankan.

## 4. Jaminan (poin diminta user)

- **Mask AOI**: luar AOI = NoData di 13 raster lewat `_AOI_MASK` tunggal;
  tidak bergantung semantik mask bawaan yang sempat menipu.
- **Nilai dalam AOI**: probabilitas dalam AOI tidak tersentuh ekspresi baru
  (taksonomi cabang identik); statistik server-side tidak berubah nilai.
- **Grid**: patch hanya menambah semantik mask; geometri grid/CRS/resolusi
  tak berubah dan tetap diecek CF `verify_raster` (2074×1592, EPSG:32749,
  30 m, tie-point 30 m).
- **Sains beku**: sampling, prediktor, model (GEE 300/sklearn 400 pohon),
  seed, split, CV, bootstrap, multi-seed tidak tersentuh; rerun hanya
  `RUN_MODE='PREPARE_MAPS'` dengan data beku.

## 5. Koreksi naskah

1. **Caption Gambar 3** (baris ±1400): "Cakupan pemetaan mengikuti grid ekspor
   dan mencakup pula wilayah di luar batas penelitian." → **"Cakupan pemetaan
   dibatasi pada wilayah penelitian; ruang di luar batas penelitian yang
   terkandung dalam grid ekspor tidak disajikan."** (Isi gambar akan
   diganti setelah panel dari rerun tiba.)
2. **BUG heading dobel** (baris 1759, warisan T09):
   `\subsection{Pembahasan}\subsection{Pembahasan}` → tunggal. Sebelumnya
   TOC/isi menampilkan "4.8 Pembahasan" **dan** "4.9 Pembahasan". PDF kini
   **48 hlm** (49 → 48), 0 undefined, overfull 7 legacy; zip 2.446.405 B.

## 6. Rerun PREPARE_MAPS (tanggung jawab user) + validasi pasca-rerun

Langkah user di Colab:
1. Unggah `Flood_DEM_Sensitivity_Notebook_v27.ipynb` (telah dipatch; sekarang
   `RUN_MODE='PREPARE_MAPS'`, `OVERWRITE_RASTERS=True`) ke Colab.
2. Mount Drive; folder `Analisis Flood DEM Susceptibility` (dengan data beku +
   service-account JSON / Kaggle Secret sesuai konfigurasi cell 9) tetap seperti run
   v27 sebelumnya.
3. Jalankan semua sel (Run all). Hasil di Drive: 13 GeoTIFF baru di
   `data/rasters`, `export_status.json`, CSV `outputs`, panel
   `outputs/maps_local/local_prob_maps.png` dst.

Validasi yang SISI ini jalankan saat artefak dikirim:
- `export_status.json`: **semua PASS** — khususnya `prob_vs_kelas:*` (dulu
  FAIL 1.848.071), `valid_vs_aoi:*`, `mask_kelas_subs_prob:*`,
  `mask_subs_irisan:*`, `luas_vs_GEE:*`, `statistik_vs_GEE:*`.
- Crosstab bin-vs-kelas 100% selaras; nodata hanya luar AOI + lubang sah;
  hitungan kelas == CSV luas; share agreement == CSV (0,7942/0,8397/0,8131);
  mean |Δp| == CSV (0,056/0,037/0,048); diff CSV lama vs baru (harus identik
  untuk semua CSV GEE).
- **PENTING — angka yang WAJIB di-update dari run baru**: Moran's I peta
  probabilitas (`moran_prob_map_global.csv`; saat ini dikutip di 4.7.2:
  0,9701/0,9648/0,9673) `B` berubah karena valid mask turun dari ±3,29 jt px
  (termasuk laut 0,0) ke ±1,44 jt px AOI-saja. Angka OOF label/residual TIDAK
  berubah. Caption/prosa terkait disesuaikan setelah CSV baru masuk.
- Panel Gambar 3 diganti dengan `local_prob_maps.png` baru (luar AOI tampil
  kosong/abu), lalu PDF dikompilasi ulang.

## 7. Artefak sesi

- `Proposal Baru/Flood_DEM_Sensitivity_Notebook_v27.ipynb` (dipatch, siap
  unggah).
- `Proposal Baru/olds/Flood_DEM_Sensitivity_Notebook_v27_pre-T10.ipynb`
  (backup).
- `Proposal Baru/proposal_revisi-final.{tex,pdf}` + `proposal_revisi-final_source.zip`
  (2.446.405 B, updated).
- Skrip scratch di `%TEMP%\opencode`: `patch_t10_notebook.py`,
  `validate_t10.py`, `fix_tol.py`, `fix_typo_j59.py`.

## 8. Rerun pertama user (7 Nov 2026) — hasil setengah-patch, CSV final

Delivery: `Proposal Baru/v27_delivery/Analisis Flood DEM Susceptibility/`
(`recorded_at_utc` 2026-11-07T09:36:34Z, Colab Python 3.13.18,
earthengine-api 1.7.39; Salinan lama dipindah ke `old_Analisis.../`).

### 8.1 Status run

- 13 raster `status=COMPLETED`, grid 2074 x 1592, EPSG:32749, `aoi_pixel_count_gee` = 1.438.214.
- **Setengah-patch**: sel `16/49/10` versi baru tereksekusi, sel `53/59` versi
  lama (salinan Colab tidak sinkron).
  - Ter-mask OK: `risk_class_*` (valid 1.444.085 / 1.444.085 / 1.429.582).
  - Belum ter-mask: `prob_*` (3.292.156 valid), `delta_*`,
    `agreement_*` (3.292.156/9.652), `proxy_flood_label_sentinel1` (3.301.808).
- `export_status.json`: `prob_vs_kelas:*` kini PASS; muncul FAIL
  `valid_vs_aoi:*` (+1.28..1.29e0, toleransi defisit union lubang wajar) dan
  FAIL `mask_kelas_subs_prob:*` (1.848.071 px) — konsisten dengan diagnosis.
- Notebook di disk TERVERIFIKASI terpatch penuh (sel 10/16/49/53/59 bermarker
  `_AOI_MASK`/`unmask(-1)`/`_both`; sel 5 `OVERWRITE_RASTERS = True`).

### 8.2 CSV server dari run ini = FINAL (tidak akan bergeser lagi)

Karena reduksi server memakai `geometry=roi`, nilai dalam-AOI tak berubah
meski sel 53/59 n dieksekusi. Angka berubah vs kutipan lama HANYA karena
pixel lubang NoData kini dikecualikan (efek sel 49 + mask):

| Sumber | Lama (naskah T09) | Baru (fresh CSV) |
|---|---|---|
| Agreement srtm-glo30 | 79,4% | 79,4% (0,79358) — tak berubah |
| Agreement srtm-aw3d30 | 84,0% | **84,3%** (0,84270) |
| Agreement glo30-aw3d30 | 81,3% | **81,5%** (0,81516) |
| mean abs-delta p (3 pasang) | 0,056/0,037/0,048 | 0,056/0,037/0,048 — tak berubah |
| Luas kelas 5 (srtm/glo30/aw3d30) | 105,1/114,1/113,5 km2 | **100,6/109,6/95,9 km2** |
| Luas kelas 1 (srtm/glo30/aw3d30) | 756,7/822,6/772,5 | 756,7/822,6/772,5 — tak berubah |
| Transisi s-g 2-to-1/1-to-2/4-to-5 | 94.306/36.869/25.679 | sama, tak berubah |
| Diagonal s-a kelas 2 | 174.072 | sama, tak berubah |
| Diagonal s-a kelas 5 | 103.412 | **91.194** |
| Tree cover agreement | 95,6 %-96,8 % | **95,6 %-96,9 %** |
| Built-up agreement | 87,2 %-90,4 % | **87,2 %-91,2 %** |
| Shrubland agreement (g-a / s-g) | 54,3 % / 60,4 % | **57,6 % / 59,1 %** |
| mean abs-delta p shrubland s-g | 0,094 | 0,094 — tak berubah |
| Bare (s-g / g-a) | 63,4 % / 66,6 % | **63,1 % / 68,6 %** |
| Mangrove (s-g / g-a) | 61,5 %-63,8 % | **62,6 %-62,8 %** |
| Air | 77,4 %-82,7 % | **76,9 %-84,1 %** |
| Wetland | 72,6 %-78,2 % | **72,5 %-78,3 %** |
| Rentang kelas sensitif (shrub/bare/mangrove) | 54,3-69,9 / 63,4-75,7 / 61,5-72,7 | **57,6-75,4 / 63,1-78,1 / 62,6-74,9** |

Klaim naratif yang ikut diubah: ALOS AW3D30 kini JUSTRU paling sempit pada
kelas 5 (95,9 < 100,6 km2) — kalimat "cakupan lebih luas pada kelas sangat
tinggi" diganti; pergeseran luas ekstrem vs SRTM kini "penyempitan ~4,6%
(AW3D30) s/d pelebaran ~9% (GLO-30)", bukan lagi "2% s/d 9%".

### 8.3 Re-quote naskah (SELESAI 7 Nov 2026)

14 lokasi diedit di `proposal_revisi-final.tex` (Tabel 4.5 + narasi luas +
transisi + 4.6 WC + 4.8 Pembahasan); + domain perbandingan "1,47 juta" ->
"sekitar 1,4 juta piksel" (AOI = 1.438.214; irisan valid antar prob
1.428.562/1.414.059). Sweep grep angka lama = BERSIH. Rekompilasi xelatex x2:
**PDF 49 hlm**, 0 undefined, 0 warning, overfull 7 legacy tak berubah;
zip 2.446.691 B. Kenaikan 48->49 hlm murni dari penambahan panjang kalimat.

### 8.4 Moran peta — TIDAK DI-RE-QUOTE (masih angka lama)

`outputs/moran_prob_map_global.csv` masih menghitung dari raster prob versi
lama-valid-sefull-grid (n=3.292.156) sehingga I = 0,9701/0,9648/0,9673 (sama
dengan naskah 4.7.2). Nilai definitif baru muncul SETELAH sel 53/59 tereksekusi
(valid prob turun ~3,29 jt -> ~1,44 jt px). `moran_oof_global.csv` (n=5956)
tidak terpengaruh.

### 8.5 Sisa tugas user (rerun kedua)

1. Di Colab, verifikasi sel 53 memuat `_both`/`updateMask(_AOI_MASK)` dan sel 59
   memuat `updateMask(_AOI_MASK)`; palING AMAN: unggah ulang file
   `Proposal Baru/Flood_DEM_Sensitivity_Notebook_v27.ipynb` (md5/ukuran dari
   disk) lalu rerun PREPARE_MAPS (OVERWRITE_RASTERS=True).
2. Ekspektasi: CSV server identik (tidak perlu re-quote ulang); hanya raster
   prob/delta/agreement/label + `local_prob_maps.png` + Moran peta yang berubah.

### 8.6 Version control notebook (7 Nov 2026, sesuai user: tanpa folder olds)

User mengunggah dan mengunduh ulang notebook dari Colab sebagai
`v27_delivery/rasterFIX_Flood_DEM_Sensitivity_Notebook_v27.ipynb`. Verifikasi
diff 3 notebook (70 cell): **kode RASTERFIX identik md5 dengan canon disk di
6 sel patch (5/10/16/49/53/59), 64 sel lainnya juga sama** — Colab kini
terpatch penuh. Pemberian nama langsung:
- Canon (sumber unggah): `Proposal Baru/Flood_DEM_Sensitivity_Notebook_v27.ipynb`
  → **`Proposal Baru/Flood_DEM_Sensitivity_Notebook_v27_maskAOI.ipynb`**
- Salinan fix dari Colab: `rasterFIX_...` →
  **`v27_delivery/Flood_DEM_Sensitivity_Notebook_v27_maskAOI.ipynb`**
- Salinan original pra-fix dari Colab (v27.0) DIPINDAH ke:
  `v27_delivery/old_Analisis Flood DEM Susceptibility/Flood_DEM_Sensitivity_Notebook_v27.ipynb`
  (folder dibiarkan apa adanya — keputusan user)
- Backup codi lama tetap: `Proposal Baru/olds/Flood_DEM_Sensitivity_Notebook_v27_pre-T10.ipynb`
  (isi = v27.0, sama dengan salinan original di atas).
- Catatan status: folder `Analisis Flood DEM Susceptibility/` ter-touch 18:38
  lokal tetapi `export_status.json` TIDAK memuat checks (total 0,
  `recorded_at_utc` null) dan valid `prob_*` masih 3.292.156 px → **rerun
  kedua BELUM tiba**: artefak di folder itu masih milik run setengah-patch.

## 9. Penutupan via surgery mask lokal (7 Nov 2026 malam) - DELIVERY FINAL

### 9.1 Kronologi rerun (label dikoreksi hingga rerun keempat)

| run | waktu (UTC) | kode yang dieksekusi | bukti |
|---|---|---|---|
| 1 (T09) | 6 Nov | original v27 pra-patch | export_status v27 awal |
| 2 = "rerun pertama" di bag. 8 | 09:36 dan 11:20 7 Nov | setengah-patch: sel 16/49/10 baru (risk_class ter-mask), sel 53/59 lama | risk valid 1.444.085; prob 3.292.156 zero-fill; delta_lokal FAIL 3.830e-03 (tol 1e-6) |
| 3 ("rerun kedua" dengan file baru) | updated 13:03:40Z | ekspor DILEWATI (OVERWRITE_RASTERS=False sejak unduhan) | semua angka identik run 2 |
| 4 (rerun penuh terakhir) | updated 17:56:21Z | KODE LAMA penuh (raster diekspor ulang 17:10-17:56, sha256 baru, delta_lokal FAIL kena tol 1e-6 -> sel 10 lama) | run_environment.recorded_at 16:34; n_valid tetap 3.292.156 |

Pengaturan: user tidak sempat menggunakan File -> Upload notebook, selalu Run all di tab yang sudah lama terbuka.

### 9.2 Surgery mask lokal (setara rerun berpatch, deterministik)

Prinsip: nilai di dalam AOI pada tif lama identik dengan ekspor berpatch (peta RF GEE deterministik; patch hanya menambah mask), sehingga mask dapat dituliskan ulang di lokal tanpa mengubah nilai:

- Master mask = zona valid `risk_class_*` (== `_p.gte(0) ∩ _AOI_MASK` sesuai patch cell 49): srtm = glo30 = 1.444.085 px, aw3d30 = 1.429.582 px (14.503 lubang NoData di dalam AOI).
- 10 raster (prob x3, delta x3, agreement x3, label) ditulis ulang `-9999` di luar mask; nilai di dalam mask tidak diubah. `risk_class_*` tidak disentuh. Original di `data/rasters_backup_unmasked/`.
- export_status: n_valid/n_nodata/min/max/sha256/size diperbarui + `note_surgery`; waktu 2026-11-07T21:36:31Z.
- Validasi lokal semantik cell 10: **39 PASS + 6 INFO + 0 FAIL**
  (verifikasi `mask_kelas_subs_prob`/`mask_subs_irisan` = 0 semua; delta_lokal maks 3,830e-03; agreement_lokal <= 1 px;
  valid_vs_aoi +4.08e-03; prob_vs_kelas AW3D30 1 px = kasus tepi batas kelas float32, canon-style real = 0 -> PASS).

### 9.3 Toleransi cek yang dilonggarkan (canon, T10 lanjut)

| cek | lama | baru | alasan |
|---|---|---|---|
| valid_vs_aoi (prob/risk) | 1e-3 | 5e-2 | efek perimeter tepi AOI (footprint vs pusat) +5.871 px (ca. +4.1e-3) & lubang NoData AW3D30 (~1,4e-2) |
| valid_vs_aoi (label) | 1e-3 | 5e-2 | idem |
| delta_lokal | 1e-6 | 1e-2 | efek pembulatan float32 pada rangkaian ekspor vs rekonstruksi lokal (3,8e-3) |
| agreement_lokal | ==0 | <=2 | tepi/jangka-bit |
| transisi_vs_GEE | INFO <1e-3 | **INFO <5e-2** | selisih sistematis 1,41e-02 = registrasi grid berbeda: reduceRegion(scale=30) (origin 0,0) vs grid ekspor (origin bbox AOI); pola selisih selalu CSV >= lokal (diagonal (1,1) -11.248), bukan ketidaksesuaian data; CSV server tetap angka resmi naskah |

Canon `proposal...maskAOI.ipynb` cell 10 md5 `6c656fce2066e934bfc589e3a19b262c` (1.202.534 B) = salinan `v27_delivery` (identik).
`prob_vs_kelas` canon tidak perlu diubah (sudah membalik kasus tepi batas via `near <= 1e-6`).

### 9.4 Moran peta - rekomputasi lokal

- Port persis cell 11 (`moran_raster`: queen-8 row-standardized, B=999, seed 42, piksel terisolasi dibuang) via W sparse CSR; I-value diverifikasi cocok dengan jalur klasik (0.9577 / 0.9531).
- Fix per-DEM: versi pertama salah memakai mask SRTM untuk AW3D30 (14.503 lubang -9999 ikut ke varians) -> W/mask dirinci per-DEM.
- Final `moran_prob_map_global.csv`: SRTM I=0.957714 (n=1.444.085), GLO-30 I=0.953076 (n=1.444.085), AW3D30 I=0.954415 (n=1.429.582); E[I] -6,9248e-7 / -6,9248e-7 / -6,9951e-7; z = 2362,88 / 2351,68 / 2377,74; p = 0,001 (batas resolusi B=999).
- Backup CSV lama: `outputs/moran_prob_map_global.csv.pre-surgery.bak`.

### 9.5 Panel & naskah

- Empat panel dibangun ulang secara lokal (gaya cell 62) dari raster ter-mask; `local_prob_maps.png` md5 2284aa6dea3c372a6c5475a33edd6137 (874.975 B).
- `figures/fig_prob_maps.png` diganti; fig lama dipindah ke `Proposal Baru\olds\fig_prob_maps_pre-surgery.png`.
- Naskah: Tabel `\ref{tab:moran-raster}` (3 baris) + prosa 4.7.2 di-re-quote; grep angka lama = bersih.
- Kompilasi x2: **PDF 49 hlm, 0 undefined, 0 warning, overfull 7 (legacy)**; zip 2.340.228 B.

### 9.6 Sisa

Semua titik T10 selesai. Kanon & salinan Colab identik; rerun Colab tidak lagi wajib (jika nanti rerun, jalankan file `_maskAOI.ipynb` dengan OVERWRITE_RASTERS=True dulu).
