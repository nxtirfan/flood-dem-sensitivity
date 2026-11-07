# Isu — Log Detail

> Format per isu: Gejala → Diagnosis → Resolusi → File terkait → Status/Prevalensi.
> Temuan panjang (deep-dive) diarahkan ke `docs/temuan/T0xx-*.md`.

## MET-001 — Mask JRC-GSW sparse menyaring training image ("sabuk air")

- **Gejala**: audit sampel v22 "watery" (kelas-0 elev mean 4,15 m, lc air 30%;
  lat berhenti −7,09) — padahal desain menyebut non-flood acak se-AOI;
  rekonstruksi lokal (Part A) tanpa term mask memberi 42,14 m/perbukitan.
- **Diagnosis**: band `occurrence` JRC GSW = produk **sparse** (hanya valid di
  zona terpetakan — 4,32% ROI); `.Not()` atas piksel tanpa data membuang 95,7%
  AOI dari kandidat kelas-0 (63.499 px ≈ 57,1 km² tersisa). Kelas-1 selamat
  (cabang `eq(1)` meng-unmask). Kode asli dan bukti lengkap:
  `docs/temuan/T01-sampling-bias-jrc-sparse.md`. Sampel artikel SMDS terbit
  mengidap varian lebih parah (mask multiband) → T02.
- **Resolusi**: `permanent_water.unmask(0)` sebelum `.Not()` pada mask sampling
  (mode `v24`); mode `v22` dipertahankan untuk audit bias. Diimplementasi di
  reanalisis lokal (v24, 17 Okt) + kernel v24 (18 Okt, seluruh tahap jalan;
  sampel 2.978/kelas; artefak `Proposal Baru\hasil_kaggle_v24\`).
- **File**: `docs/temuan/T01-*`, `docs/temuan/T02-*`, notebook/kernel v20–v24,
  `D:\Kuliah\1_Metopen\ARTIKEL REFERENCE - SMT 4\Flood Susceptibility Mapping\main.tex` (375–390, 881–889).
- **Status**: RESOLVED (kernel v24 18 Okt — sampel 2.978/kelas; audit
  kelas-0 se-AOI elev 42,67 m; angka hasil di T01 §9, temuan_empiris §9).
  **Prevalensi**: tiap kode yang menyentuh `permanent_water.Not()` atau mask
  multiband di GEE.

## MET-002 — Metrik/angka naskah tidak selaras artefak (audit T03)

- **Gejala**: kolom `auc_spatial_cv` v22 = pseudo-AUC dari prediksi biner
  (bukan ROC-AUC probabilitas); Tabel `tab:spatial-cv` proposal memuat F1 yang
  tidak cocok CSV sumber; klaim "(median ±5–9 m)" berasal dari p50 grid
  (8,50/4,94/8,53 m) tapi ditulis rancu; offset AW3D30 "+0,40" vs terverifikasi
  "+0,39"; "(12 non-DEM + 5 topografi)" = 17 ≠ 25 prediktor; ambang Youden
  dihitung pada data uji (optimistis) tanpa penanda.
- **Diagnosis/daftar koreksi**: lengkap + bukti per butir di
  `docs/temuan/T03-audit-metrik-qc.md`.
- **Resolusi**: edit `proposal.tex` + kernel v24 sudah semuanya menerapkan:
  AUC probabilitas (bukan pseudo), Tabel spatial-CV v24 (0,870/0,890/0,875),
  median grid + offset +0,39 eksplisit, count prediktor 24 (11+8+5), Youden
  ditandai optimistis, agreement v24 lengkap, BAB IV = angka kernel final.
- **Status**: RESOLVED (18 Okt 2026; PDF 22 hlm., 0 undefined/overfull).
  **Prevalensi**: tiap kutip angka ke naskah.

## MET-003 — Implikasi ke artikel SMDS yang sudah terbit

- **Gejala/user**: "berarti artikel SMDS saya yang sudah terbit jadi masalah?"
- **Diagnosis**: sampel terbit mengidap MET-001 varian multiband — KEDUA kelas
  terkurung sabuk (935 px banjir ≈ 0,84 km² vs luas banjir 44–56 km² yang
  dilaporkan naskah itu sendiri); naskah sudah ber-hedge kuat dan bahkan
  menyebut "sampling grid starts at the edge of the permanent-water mask"
  (main.tex:881–882) → bukan kategori retraksi; kategori = keterbatasan
  yang perlu klarifikasi. Detail + opsi A/B/C: `docs/temuan/T02-*`.
- **Resolusi**: (A, disarankan) tangani di artikel baru sebagai kontribusi
  metodologis; (B) corrigendum singkat bila co-author setuju; (C) diamkan —
  tidak direkomendasikan (dataset publik memungkinkan audit).
- **Status** menunggu keputusan bersama 6 co-author.

## MET-004 — Arsip S1 GEE bergeser (label-match 69,9%)

- **Gejala**: v23 bridging menyusun ulang label dengan kode/parameter/tanggal
  identik → hanya 69,9% titik CSV baseline memuat label yang cocok.
- **Diagnosis**: hipotesis terkuat = reprocessing arsip ESA/GEE + ambang
  tajam (rasio 1,25 / −18 dB) sensitif; uji peta lokasi yang tidak cocok
  diusulkan (murah), belum dijalankan.
- **Resolusi**: klaim dilunakkan ("kode/parameter identik; realisasi cocok
  70%"); v23 tetap dipakai sebagai bridging ±0,05.
- **Status**: ACCEPTED. **Prevalensi**: reproduksi lintas-waktu arsip berumur.

## MET-005 — Spatial holdout v20 terkontaminasi

- **Gejala**: AUC spatial-holdout 0,92 padahal training ≈ 0,80.
- **Diagnosis**: model dievaluasi pada blok yang ikut dilatih (tanpa retrain).
- **Resolusi**: 4-fold spatial CV dengan retrain per fold (v22); spatial
  `v20` invalid → jangan dikutip.
- **Status**: FIXED. **Prevalensi**: tiap desain validasi spasial.

## MET-006 — `Image.sample` numPixels bukan kuota

- **Gejala**: minta 3000/kelas, kembali 244/135 (v18) meski pool 1,4 jt/58 rb px.
- **Diagnosis**: `numPixels` = perkiraan; `stratifiedSample` + `classPoints`
  yang memenuhi kuota eksak.
- **Status**: FIXED (sejak v20). **Prevalensi**: tiap sampling besar GEE.

## MET-007 — Tile viz timeout menghancurkan run (v21)

- **Gejala**: `Map3.addLayer` → getMapId timeout SETELAH RF/CV selesai;
  CSV akhir tidak tersimpan; workspace ikut ter-wipe.
- **Resolusi**: seluruh cell visualisasi dibungkus try/except (v22).
- **Status**: FIXED. **Prevalensi**: tiap notebook dengan tile render.

## MET-008 — Byte `0x97` di notebook JSON

- **Gejala**: kernel push/parse gagal pada notebook hasil edit encoding.
- **Resolusi**: `raw.replace(b"\x97", b"-")` sebelum write.
- **Status**: FIXED. **Prevalensi**: tiap patch byte notebook lama.

## MET-009 — Konstruksi label memakai pita JRC terkurung ("flood=1 mustahil di luar pita JRC")

- **Gejala**: audit v26 dugaan N-1 dari pembacaan kode sel 12; angka probe log kernel "JRC valid 12,78%" menimbulkan pertanyaan cakupan label.
- **Diagnosis** (T04, probe GEE fresh 19–20 Okt, di `probe_v26/`): gate `permanent_water.Not()` pada **sel 12 (label, bukan sampling)** tanpa `unmask(0)` menyebabkan `flood_raw` ter-mask pada piksel JRC no-data → `selfMask()` + `connectedPixelCount` + `unmask(0)` membuat flood=1 HANYA mungkin di dalam pita occ JRC. Bukti: flood=1 & JRC no-data = 0 pada 4 jalur eksekusi (probe 1/2/5; sum & histogram) × 2 grid (WGS-default & EPSG:32749, 30 m). Pita: footprint mask>0 = 189.345 px (12,88% AOI; angka kernel 187.777 = Σ berbobot, BUKAN jumlah piksel); occ-bernilai = 63.499 px (4,32%). flood_raw masked = 1.259.427 px (85,70% AOI; 99,92% karena JRC, sisanya slope no-data; S1 no-data = 0). Mask band `occurrence` terbukti FRAKSIONAL 0..1 (bukan binari) — kunci interpretasi angka.
- **Resolusi**: TIDAK diubah (sesuai batasan user); menunggu keputusan (a) tampilkan keterbatasan di proposal Bab IV, (b) opsi belakang rerun dengan `unmask(0)` pada sel 12. Fairness antar-DEM terjaga (label identik lintas eksperimen).
- **File**: `docs/temuan/T04-audit-v26-label-jrc-probe.md`, `docs/temuan/probe_v26/*`.
- **Status**: DIAGNOSED — keputusan user. **Prevalensi**: tiap run yang membentuk label dari mask sparse JRC yang sama (v20–v26); sampling v24 sudah diperbaiki (terpisah, MET-001), label belum.
