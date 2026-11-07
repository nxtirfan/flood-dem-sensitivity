# DRAFT PROPOSAL METOPEN — DESAIN BARU (ML/RF)

> **Status:** DRAFT aktif menggantikan seluruh isi `Arsip Proposal Usang\`.
> Desain: **3 DEM → Random Forest terkontrol → peta kerawanan → sensitivitas spasial → stratifikasi WorldCover.**
> Tanpa multi-event, tanpa DEMNAS, tanpa NASADEM, tanpa SHAP.
> Naskah formal (LaTeX → PDF): `proposal.tex` / `proposal.pdf` di folder ini.

---

## 1. Identitas

| Item | Isi |
|---|---|
| Nama | M Irfan Al Hakim |
| NIM | 2404220023 |
| Email | mirfanhakim25@students.unnes.ac.id |
| Dosen | Dr. Iqbal Kharisudin, M.Sc. |
| **Judul** | **Analisis Sensitivitas Produk Elevasi Global terhadap Pemetaan Kerawanan Banjir Berbasis Machine Learning Menggunakan Google Earth Engine: Studi Komparatif SRTM, Copernicus DEM GLO-30, dan ALOS AW3D30 di Wilayah Pesisir Semarang-Demak** |

## 2. Inti penelitian (5 kata)

**DEM → RF → MAP → COMPARE → STRATIFY**

Perlakuan = **sumber produk elevasi** (SRTM / Copernicus GLO-30 / ALOS AW3D30).
Dikunci identik: AOI, flood inventory Sentinel-1, prediktor non-topografi, sampling + seed, split data, parameter RF.

## 3. Rumusan Masalah

1. Seberapa berbeda parameter topografi (elevasi, slope, aspect) dari SRTM, Copernicus GLO-30, dan ALOS AW3D30 di pesisir Semarang–Demak?
2. Bagaimana Random Forest memetakan kerawanan banjir dengan flood inventory Sentinel-1?
3. Seberapa besar perbedaan hasil pemetaan ketika sumber produk elevasi diganti dalam eksperimen terkontrol?
4. Bagaimana pola sensitivitas spasial (perubahan probabilitas, kesesuaian, perubahan kelas) dan apakah berbeda antar kelas tutupan lahan?

## 4. Data

| Data | Asset GEE | Peran |
|---|---|---|
| SRTM | `USGS/SRTMGL1_003` | Konfigurasi 1 (elevasi/slope/aspect) |
| Copernicus GLO-30 | `COPERNICUS/DEM/GLO30` | Konfigurasi 2 |
| ALOS AW3D30 | `JAXA/ALOS/AW3D30/V4_1` | Konfigurasi 3 |
| Sentinel-1 GRD | `COPERNICUS/S1_GRD` | Flood inventory pra/pasca kejadian |
| JRC GSW | `JRC/GSW1_4/GlobalSurfaceWater` | Mask air permanen + jarak air permanen |
| MERIT Hydro | `MERIT/Hydro/v1_0_1` | HAND, daerah aliran, lebar/jarak sungai (**dikunci**) |
| CHIRPS | `UCSB-CHG/CHIRPS/DAILY` | Curah hujan 7 & 30 hari (**dikunci**) |
| Sentinel-2 SR | `COPERNICUS/S2_SR` | Indeks spektral (**dikunci**) |
| ESA WorldCover | `ESA/WorldCover/v200` | Prediktor + **stratifikasi sensitivitas** |

Prediktor **bervariasi**: elevasi, slope, aspect (dari DEM yang diuji).
Prediktor **dikunci**: variabel MERIT Hydro, jarak air permanen, CHIRPS, indeks spektral, kelas tutupan lahan.

## 5. Langkah Analisis

1. Flood inventory: rasio perubahan backscatter VV/VH pra/pasca + masking JRC; laporkan threshold & luas.
2. Sampling stratified (jumlah, lokasi, seed identik antar konfigurasi); seimbangkan kelas; split latih/uji perhatikan struktur spasial.
3. Hitung elevasi/slope/aspect per DEM + layer prediktor dikunci.
4. Latih `ee.Classifier.smileRandomForest`, parameter identik; ambang via indeks Youden.
5. Tiga peta probabilitas kerawanan.
6. Perbandingan performa: accuracy, precision, recall, F1, ROC-AUC (split uji sama).
7. Sensitivitas spasial: (a) peta Δprobabilitas, (b) peta kesesuaian kelas, (c) matriks perpindahan kelas + luas zona berubah.
8. Stratifikasi WorldCover: metrik sensitivitas per kelas tutupan lahan.
9. Rekomendasi: DEM paling stabil, zona paling sensitif, tutupan lahan paling rentan.

## 6. Referensi utama (5 — sudah diverifikasi)

1. Tique dkk. (2026) — `10.1007/s11069-025-07868-y` — komparasi data-driven flood susceptibility Nigeria.
2. Meadows dkk. (2024) — `10.1080/17538947.2024.2308734` — akurasi vertikal 5 DEM global di lingkungan rawan banjir.
3. Fatdillah dkk. (2022) — `10.3390/w14142208` — DEM resolution → estimasi kerusakan/risiko banjir (Kuala Lumpur).
4. Fikri dkk. (2026) — `10.3390/w18101203` — resolusi DEM → akurasi/efisiensi HEC-RAS (Cimanceuri, Indonesia).
5. Al Hakim dkk. (2026) — **`10.15294/smds.v1i1.62500`** — baseline SMDS (Sentinel-1 + ensemble ML, Semarang–Demak; RF terbaik).
   - ⚠️ **Koreksi dari teks form asli:** DOI `10.1016/j.jenvman.2025.127128` itu milik Zerouali dkk. (Jeddah), **bukan** artikel SMDS. Sudah diperbaiki di `form_isian_google.md`.

## 7. Catatan desain (keputusan yang mengikat)

- Framing: **sensitivitas SUMBER produk elevasi** (ketiganya ~30 m, bukan perbandingan resolusi).
- Pelabelan jujur: SRTM ≈ DEM C-band; Copernicus & ALOS = **DSM**; tidak ada bare-earth DTM murni.
- Sentinel-1 = flood inventory (bukan ground truth); satu kejadian (bukan multi-event).
- Tanpa SHAP — fokus pada sensitivitas DEM, bukan interpretasi model (hindari pengulangan baseline).
- Tanpa statistik inferensial Friedman/Wilcoxon (tidak ada blok event) — sensitivitas bersifat deskriptif-inferensial terbatas.
- Datum EGM96 (SRTM) vs EGM2008 (Copernicus) harus diharmonisasi — kritis di dataran 0–3 m.

## 8. Checklist

- [x] Arsip desain lama → `Arsip Proposal Usang\` (+ README)
- [x] Isian Google Form tersimpan (`form_isian_google.md`, DOI terkoreksi)
- [x] Draft markdown Bab I–III (file ini)
- [x] `proposal.tex` + `references.bib` (31 entri) + `proposal.pdf` (0 sitasi hilang) — ditulis ulang ke **desain kunci final**: cover + lembar persetujuan + BAB I 1.1–1.6 + BAB II 2.1–2.10 (+Gambar 2.1 kerangka berpikir TikZ) + BAB III 3.1–3.11 + BAB IV 4.1–4.7 rancangan hasil (tanpa fabrikasi angka)
- [x] Notebook GEE `Flood_DEM_Sensitivity_Notebook.ipynb` (41 sel 0–20, 0 syntax error) — sambung tangan dari notebook SMDS; perlakuan = 3 DEM; output = 3 peta + metrik + Δprobabilitas/agreement/transisi + stratifikasi WorldCover
- [ ] Jalankan notebook di Colab (verifikasi asset ID 3 DEM → sampel → 3× RF → hasil)
- [ ] Konsultasi ke Dr. Iqbal dengan `draft_proposal.md` / `proposal.pdf`
- [ ] Audit literatur → kunci predictor final + parameter RF (`git init` + push repo privat berjalan paralel)
