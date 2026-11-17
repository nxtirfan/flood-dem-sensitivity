# T20 — Koreksi Targeted terhadap Audit T19 (dokumentasi & workbook, tanpa eksperimen baru)

**Tanggal:** 18 November 2026
**Sifat:** Koreksi dokumentasi/audit + pembangunan ulang workbook. **Tidak ada** perubahan pada data beku, sampel, label, model, parameter, raster, atau hasil eksperimen. Tidak ada eksekusi GEE, tidak ada rerun.

## 1. Ringkasan

| Prioritas | Tindakan | Hasil | Status |
|---|---|---|---|
| 1 | Arsipkan workbook T19 rusak; rebuild XLSX + CSV 30 titik dari sumber beku lokal | 30 baris × 39 kolom, tervalidasi | SELESAI |
| 2 | Turunkan klaim penyebab §6.1/§6.2 menjadi indikasi/hipotesis; tandai pekerjaan yang masih diperlukan | Teks T19 diperbarui, angka forensik dipertahankan | SELESAI |
| 2b | Tarik klaim parameter Sentinel-1 (§8.1, ringkasan eksekutif, §2.1) | `RETRACTED`; proposal terbukti konsisten dengan kode | SELESAI |
| 3 | Perbaiki redaksi sampling L1057 proposal setelah verifikasi urutan operasi Cell 31 | Teks diganti; angka 2.978 tidak diubah; PDF 50 hlm, 0 undefined | SELESAI |
| 4 | Rapikan baris Prioritas 5, tabel AOI §4.2, istilah/angka lintas laporan | T19 konsisten | SELESAI |
| 5 | T20, STATUS, CONTEXT, commit | Lihat §6–§7 | SELESAI |

## 2. Prioritas 1 — Workbook 30 titik

**Masalah lama.** XLSX lama menyimpan koordinat/slope sebagai integer skala 10^14–10^16 (contoh `lon_tf = 1,10660809820595e+16` untuk Titik 1), serta mencampur angka dan string (`'1.0'`, `'True'`). Pola ini konsisten dengan penghapusan pemisah desimal koma pada teks angka sebelum serialisasi. File lama **tidak dihapus**, melainkan diarsipkan ke `docs/temuan/T19/arsip/t19_30point_row_by_row_verification_BROKEN-serialisasi.xlsx` (13.950 B).

**Sumber yang dipakai (semua lokal, read-only):**
- `Proposal Baru/v28_delivery/Analisis Flood DEM Susceptibility/outputs/training_sample_features.csv` — koordinat dan `slope_srtm` presisi penuh per `physical_line`.
- `Proposal Baru/olds/hasil_kaggle_v26/training_sample_features.csv` — salinan historis pembanding.
- `Proposal Baru/v28_delivery/Analisis Flood DEM Susceptibility/data/frozen/main/sample_main_raw.parquet` dan `.csv` — nilai slope/koordinat beku.
- `Proposal Baru/v28_delivery/diagnostics_t17/t17_slope_30point_diagnostic.csv` — empat rute diagnostik, nilai, mask, dan pusat piksel.
- `Proposal Baru/v28_delivery/Analisis Flood DEM Susceptibility/data/rasters/proxy_flood_label_sentinel1.tif` — baris/kolom dan nilai label.
- `docs/temuan/T16/slope/slope_points_audit.csv` — pemetaan `physical_line` → baris CSV mentah dan nilai `historic_slope_srtm_training_export_deg`.

**Skrip:** `docs/temuan/T19/build_t19_workbook.py`. **Keluaran:** `t19_30point_row_by_row_verification.xlsx` dan `t19_30point_row_by_row_verification.csv` (CSV kini tersedia seperti yang direferensikan T19 §3.1).

**Validasi (dijalankan setelah simpan, dengan memuat ulang XLSX):** `max_row=31`, `max_column=39`, header 39 kolom sesuai skema lama, seluruh 30 × 39 sel cocok dengan nilai yang dihitung (float dengan `rel_tol=1e-14` sesuai batas 15 digit Excel; bool/int/string eksak). Perbandingan terhadap T19 §3.1:

| Besaran | Selisih maksimum | Perlakuan |
|---|---|---|
| Bujur/lintang | `1,42 × 10⁻¹⁴°` | Serialisasi CSV; diterima |
| Slope rute native/forced | `4,89 × 10⁻⁹°` | T17 CSV membulatkan ke 6 desimal; diterima |
| Slope rute feature/final | `1,78 × 10⁻¹⁵` (1 ULP, **Titik 17** saja) | Lihat kontradiksi di §5 |
| `\|Δ\|` vs v28 / T16 | `1,81 × 10⁻¹⁵` | Klas presisi yang sudah dijelaskan T19 §3.2 |
| Jarak ke pusat piksel | `0,0113 m` | Pusat piksel T17 dibulatkan 6 desimal; diterima |
| Baris/kolom raster proxy | 0 | 30/30 eksak |

Excel menyimpan maksimum 15 digit signifikan (Titik 1 terbaca `110.6608098205957`); presisi penuh `.17g` tersimpan di CSV. Tidak ada lagi nilai berskala 10^14–10^16.

## 3. Prioritas 2 — Koreksi klaim T19

- **§6.1:** judul "bukti teknis mengapa" → "indikasi teknis … (HIPOTESIS)"; pernyataan "membuktikan secara matematis" → "indikasi kuat (bukan pembuktian)". Ditambahkan **Batas klaim (koreksi T20)**: fakta terverifikasi = angka denominator, selisih `~1,41%`, dan tidak adanya `crs` pada `reduceRegion`. Yang masih diperlukan: inspeksi proyeksi/transformasi aktual `code_img`, reproduksi histogram dengan `crs='EPSG:32749'` + `crsTransform` terkunci, dan perbandingan dengan tabulasi GeoTIFF lokal.
- **§6.2:** "mekanisme penyebab" → hipotesis; rekonstruksi `prob_srtm ≈ 0,59915–0,59993` dipertahankan sebagai fakta turunan, tetapi eksperimen reproduksi ekspor/computePixels pada kondisi identik dinyatakan masih diperlukan.
- **Ringkasan eksekutif Prioritas 5, §6.3, dan §9 klaim 6:** status tetap **PARTIALLY VERIFIED**; hasil T18 tidak dinyatakan selesai.
- **§8.1 baris 1, ringkasan Prioritas 7, §9, §2.1 baris 5:** klaim parameter `VV / -16 dB / 4 piksel` **DITARIK**; lihat §4.

## 4. Prioritas 2b — Penarikan temuan parameter Sentinel-1

Bukti lokal yang diperiksa:

| Sumber | Lokasi | Isi |
|---|---|---|
| `Proposal Baru/Flood_DEM_Sensitivity_Notebook_v28.ipynb` | Cell 15 (indeks 0-based) | `S1_POLARIZATION = 'VH'`, `AFTER_DB_THRESHOLD = -18`, `MIN_CONNECTED_PIXELS = 8`, `SAMPLE_PER_CLASS_TARGET = 3000` |
| `Proposal Baru/v28_delivery/Flood_DEM_Sensitivity_Notebook_v28.ipynb` | Cell 15; SHA-256 kedua salinan `CAAF908094918A03BB8E48F80DE1209850CA2DCB2855B3690E1C9A4E62406DF9` | Sama |
| `Proposal Baru/v28_delivery/Analisis Flood DEM Susceptibility/data/manifest.json` | blok `config` | `"S1_POLARIZATION": "VH"`, `"AFTER_DB_THRESHOLD": -18`, `"MIN_CONNECTED_PIXELS": 8`, `"SAMPLE_PER_CLASS_TARGET": 3000`, `"SAMPLE_PER_CLASS_FINAL": 2978` |
| `Proposal Baru/olds/notebooks_dan_skrip_arsip/Flood_DEM_Sensitivity_Notebook_v23arsip.ipynb`, `v25arsip`, `v26`, `v27_maskAOI`, `v27_pre-T10` | definisi konstanta | Kelima notebook memakai `VH`, `-18`, `8` |
| Notebook v28 Cell 21 L29–37 | ekspresi `flood_raw` | Memakai `lt(AFTER_DB_THRESHOLD)` dan `.gte(MIN_CONNECTED_PIXELS)`, bukan literal `-16`/`4` |

**Kesimpulan:** proposal (VH, < -18 dB, 8 piksel) konsisten dengan kode; parameter eksperimen tidak diubah. Atribusi lama bahwa `VV/-16/4` menghasilkan `58.573` piksel banjir juga ditarik karena tidak ada bukti lokalnya; T19 tidak menjalankan eksperimen untuk menentukan hubungan tersebut.

## 5. Prioritas 3 — Perubahan proposal (satu paragraf, L1057)

**Verifikasi urutan operasi sebelum edit** — `Flood_DEM_Sensitivity_Notebook_v28.ipynb` Cell 31: L58–65 kuota `3.000` per kelas → L78–88 `stratifiedSample` → L93–97 `sampleRegions` (ekstraksi prediktor) → L104–108 `filter(ee.Filter.notNull(predictor_bands_all))` → L120–135 penyeimbangan `min(SAMPLE_PER_CLASS, raw_n0, raw_n1)` + `randomColumn('rand_balance', 42).sort().limit()`, menghasilkan `2.978` per kelas sesuai `manifest.json.config`.

Teks lama (L1057–1059): "Pengambilan sampel dilakukan terstratifikasi sebanyak 2.978 titik per kelas (*seed* 42) mengikuti jumlah populasi berlabel pada kedua kelas, kemudian data dibagi …"

Teks baru: "Pengambilan sampel dilakukan secara seimbang dengan menargetkan 3.000 sampel untuk masing-masing kelas (*seed* 42). Setelah proses ekstraksi prediktor, sampel yang memiliki nilai prediktor tidak lengkap dieliminasi melalui penyaringan `notNull`. Selanjutnya, dilakukan penyeimbangan jumlah sampel antarkelas sehingga diperoleh 2.978 sampel banjir dan 2.978 sampel nonbanjir untuk pemodelan. Data kemudian dibagi 75% latih dan 25% uji …"

Catatan: kata `seed~42` dipertahankan dari teks lama agar informasi sampling tidak hilang. Tidak ada angka, sampel, label, model, atau parameter yang diubah.

**Kompilasi:** tiga kali `xelatex -interaction=nonstopmode proposal_revisi-final.tex` → `Output written on proposal_revisi-final.pdf (50 pages)`, **0 undefined**. Sweep PDF: frasa baru muncul 1×; `2.978 sampel banjir` 1×. `bbl`/`bcf` yang sempat terhapus di worktree dipulihkan dari HEAD agar sitasi tidak undefined. Zip sumber direbuild karena tex berubah (entri sama: tex, bib, logo, 11 figures; tidak ada perubahan isi figures).

## 6. Kontradiksi material yang ditemukan dan dicatat (tanpa keputusan diam-diam)

1. **Titik 17, 1 ULP:** `t17_slope_30point_diagnostic.csv` memberi `11,483837127685549`, sedangkan string `slope_srtm` di `training_sample_features.csv` v28 lokal memberi `11,483837127685547`. T19 §3.1 menampilkan `|Δ| vs v28 = 0,0e+00`, tetapi secara lokal selisihnya `1,78 × 10⁻¹⁵`. Tidak ada angka beku yang diubah; selisih didokumentasikan di catatan §3.1 T19 dan di workbook (`feat_diff_vs_tf` Titik 17 = `1,776357e-15`). Ini termasuk kelas selisih serialisasi yang sudah dijelaskan T19 §3.2.
2. **§2.1 T19 memuat literal salah** (`after_pol_db.lt(-16)`, `.gte(4)`); dikoreksi menjadi nama konstanta sesuai Cell 21 dan nilai dari Cell 15.
3. **T19 tidak menyebut sumber jarak snap** angka `15,11 / 8,24`; rebuild menghitung ulang dari pusat piksel (T17, 6 desimal) dengan `pyproj.Geod`, selisih maks `0,0113 m` terhadap tabel lama.

## 7. Isu yang masih terbuka (tidak dinyatakan selesai)

| Isu | Status |
|---|---|
| Reproduksi penuh graph historis `flood_label` (T19 Prioritas 1) | **BLOCKED** (citra perantara tidak tersimpan; `label_native_projection_control` bukan reproduksi) |
| `max_abs_diff = 0,0` terhadap kolom historis T17 (Prioritas 2) | **PARTIALLY VERIFIED** (pembulatan `.round(6)`, 1 ULP Titik 17) |
| Provenance & NoData dalam AOI (Prioritas 3) | **PARTIALLY VERIFIED** (GeoJSON ekspor ulang 12 Nov; `4.261`/`18.763` piksel NoData di dalam poligon) |
| Moran's I (Prioritas 4) | **PARTIALLY VERIFIED** (narasi "Rook" di T18/Laporan_v28 salah; permutasi AW3D30 saja yang dihitung ulang di v28) |
| Denominator transisi `~1,41%` (Prioritas 5A) | **PARTIALLY VERIFIED** — penyebab **hipotesis**; inspeksi proyeksi `code_img` + reproduksi dengan CRS terkunci belum dilakukan |
| 2-pixel agreement mismatch (Prioritas 5B) | **PARTIALLY VERIFIED** — mekanisme **hipotesis**; reproduksi ekspor identik belum dilakukan |
| Proposal revisi 15 Nov: klaim "reproyeksi bilinear" dan `N = 1.469.555` Tabel 4 | Masih terbuka; **tidak disentuh** dalam koreksi targeted ini |
| Status klaim T18 di §9 | Tetap **PARTIALLY VERIFIED** untuk 5 dari 7 klaim; tidak ada pernyataan bahwa audit T16–T18 selesai |

## 8. Daftar file yang diubah

| File | Alasan |
|---|---|
| `docs/temuan/T19/T19_VERIFICATION.md` | Koreksi klaim, retraksi parameter, tabel AOI, catatan toleransi |
| `docs/temuan/T19/t19_30point_row_by_row_verification.xlsx` | Rebuild dengan float benar |
| `docs/temuan/T19/t19_30point_row_by_row_verification.csv` | Baru — salinan presisi penuh `.17g` |
| `docs/temuan/T19/build_t19_workbook.py` | Baru — skrip rebuild + validasi |
| `docs/temuan/T19/arsip/t19_30point_row_by_row_verification_BROKEN-serialisasi.xlsx` | Arsip workbook rusak |
| `docs/temuan/T20-koreksi-targeted-t19.md` | Laporan sesi ini |
| `docs/STATUS.md`, `CONTEXT.md` | Log keputusan dan next action |
| `Proposal Baru/proposal_revisi-final.tex` | Redaksi sampling L1057 saja |
| `Proposal Baru/proposal_revisi-final.pdf` | Hasil kompilasi (3× xelatex) |
| `Proposal Baru/proposal_revisi-final_source.zip` | Rebuild karena tex berubah |
| `Proposal Baru/proposal_revisi-final.bbl`, `.bcf` | Dipulihkan dari HEAD (identik, agar kompilasi valid) |

Tidak diubah: notebook mana pun, `v28_delivery/`, `hasil_kaggle/`, raster, CSV hasil, sampel, model, konfigurasi, dan angka eksperimen.
