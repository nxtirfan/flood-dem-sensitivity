# Laporan v27: reproducibility, pembekuan data, dan Global Moran's I

Notebook: `Flood_DEM_Sensitivity_Notebook_v27.ipynb` (SHA-256 `28c8d273bdee11b8c850f6b02e07999c1e371c244ae27bb6ac3416afe5ffc178`).
Notebook v26 tidak diubah dan disalin apa adanya ke `data/reference_v26/` beserta checksum.

## 1. Apa yang sudah terbukti dan apa yang belum

| Komponen | Status | Dasar |
|---|---|---|
| Cell inti eksperimen tidak berubah | Terbukti | Cell 12, 14, 16, 18, 22, 26, 28, 30, 33, 39, 42, 44 v26 identik secara AST, hanya dibungkus guard mode. Cell 20 identik plus satu baris pembekuan. |
| Mode `USE_CACHED_DATA` tanpa GEE | Terbukti (uji) | Seluruh notebook dijalankan dengan koneksi jaringan diblokir. `ee` dan `geemap` tidak pernah diimpor. Tidak ada error. |
| Penolakan artefak rusak | Terbukti (uji) | 8 skenario ditolak dengan pesan jelas: Parquet diubah 1 byte, CSV diubah, manifest hilang, file seed hilang, seed manifest salah, kolom berbeda, seed entri salah, PREPARE_DATA menolak menimpa dataset beku. Sidik jari data terproses mendeteksi perubahan 1e-9. |
| Ekspor raster: tile, mosaik, status | Terbukti pada **data uji palsu** | Tile bergeser 1 piksel, tile pendek, celah, dan tumpang tindih terdeteksi. Mosaik identik piksel demi piksel dengan sumber. Raster yang diubah setelah ekspor terdeteksi lewat SHA-256. |
| Fungsi Moran's I | Terbukti | Nilai $I$ dan $E[I]$ sama dengan pustaka `esda` (selisih di bawah 1e-9 untuk titik dan raster, termasuk raster bermask). |
| `PREPARE_DATA` dan `PREPARE_MAPS` pada GEE | **Belum diuji** | Tidak ada akses GEE di sesi ini. Kode ditulis dan diperiksa sintaksnya, tetapi belum pernah menyentuh GEE. |
| Dataset beku mentah dan manifest asli | **Belum ada** | Memerlukan `PREPARE_DATA` di Colab. Folder `data/frozen/main` dan `multiseed` sengaja kosong. |
| Reproduksi multi-seed | **Belum diuji** | Data per seed belum pernah tersimpan di v26. |
| Reproduksi peta dan statistik spasial | **Belum diuji** | v26 tidak pernah menghasilkan raster. Tidak ada peta lama untuk dibandingkan. |
| Moran's I pada peta probabilitas | **Belum dihitung** | Menunggu raster dari `PREPARE_MAPS`. Kode sudah ada dan hanya menghitung bila raster berstatus COMPLETED. |

**Reproducibility seluruh eksperimen belum bisa diklaim.** Yang sudah diuji hanyalah kode dan jalur data, belum rantai GEE sampai evaluasi.

## 2. Temuan penting: kode sama, data sama, hasil sedikit berbeda antar-lingkungan

Cell evaluasi utama v27 dijalankan di sandbox ini pada `training_sample_features.csv` v26 (dibaca dengan presisi float penuh, arsip fitur yang ditulis ulang cell 28 identik dengan file v26). Hasilnya **tidak identik** dengan CSV Kaggle v26.

| Konfigurasi | AUC holdout (sandbox) | AUC holdout (v26 Kaggle) | Selisih |
|---|---|---|---|
| SRTM | 0,9312 | 0,9318 | -0,0005 |
| GLO-30 | 0,9399 | 0,9404 | -0,0004 |
| AW3D30 | 0,9355 | 0,9360 | -0,0005 |

Rerata AUC spatial CV berselisih paling besar 0,0005. Probabilitas OOF per titik berselisih median 0,015 (maksimum 0,151). Kolom fold, blok, dan label identik. Urutan antar-DEM dan kesimpulan arah tidak berubah (misalnya $\Delta$AUC blok SRTM-GLO30: -0,0173 [-0,0273, -0,0084] di sandbox dan -0,0155 [-0,0250, -0,0072] di v26).

Penyebab yang paling mungkin adalah perbedaan versi library (sandbox memakai scikit-learn 1.9.1, sedangkan versi di run Kaggle v26 tidak tercatat). Ini dugaan, belum terbukti. Konsekuensinya, hasil di Colab juga dapat sedikit berbeda dari v26 walaupun data identik. v27 sekarang mencatat versi dependensi di `outputs/run_environment.json` dan di manifest. Konfigurasi dan parameter tidak diubah untuk memaksakan kesamaan.

## 3. Ringkasan perubahan dari v26

| Cell v26 | Perubahan | Alasan |
|---|---|---|
| Baru | Konfigurasi terpusat (`RUN_MODE`, `PATHS`, deteksi lingkungan), preamble Colab/Drive | Satu sumber path, tiga mode |
| 3 | Tambah `rasterio`, `pyarrow` | Kebutuhan GeoTIFF dan Parquet |
| 4 | OUTPUT_DIR dari `PATHS`, `ee/geemap` hanya diimpor bila GEE dipakai | Mode cached tanpa GEE. Preamble Kaggle dipertahankan |
| 6 | Dibungkus guard, tambah path service account Colab, cek akses project dan metadata aset | Mode cached tanpa autentikasi |
| 8 | Dipecah: parameter (semua mode) dan ROI (GEE). `SEEDS_MULTI` dipindah ke parameter | Parameter harus tersedia tanpa GEE |
| 12 sampai 22 | Hanya dibungkus guard | Dilewati di mode cached |
| 24 | Dipecah: unduh dan bekukan (PREPARE_DATA), pembersihan dari tabel beku (semua mode) | Inti pembekuan |
| 28, 30, 33, 26 | Hanya dibungkus guard | Identik |
| 31 | Dipecah: ekstraksi GEE dan pembekuan per seed, lalu evaluasi dari tabel beku | Seed 42 multi-seed dibekukan terpisah dari dataset utama |
| 35 | `sample_fc` dibentuk ulang dari tabel beku utama dan diverifikasi identik | Tanpa sampling ulang |
| 37, 40 | Peta geemap dan thumbnail dinonaktifkan secara default | Terbukti gagal atau tidak tersimpan di Kaggle |
| 39, 42 | Hanya dibungkus guard | Identik |
| 44 | `Export.toDrive` dinonaktifkan, diganti unduhan per tile dengan status dan verifikasi | Ekspor v26 tidak terverifikasi |
| Baru | Helper pembekuan/manifest/validasi, utilitas raster, visualisasi lokal, laporan pembanding v26 vs v27 | Sesuai rancangan yang disetujui |
| Baru | Fungsi Moran, Moran OOF, Moran peta, bagian metodologi | Permintaan tambahan |

Semua cell ber-`id` agar tidak memicu peringatan nbformat. Kode lama tidak dihapus.

## 4. Audit kelayakan Global Moran's I

1. **Probabilitas.** Dua sumber ada, dan masing-masing menjawab pertanyaan berbeda. Probabilitas OOF pada titik sampel dipakai sebagai analisis utama yang sebanding dengan residual, karena tiap titik diprediksi model yang tidak melihat blok titik itu. Probabilitas peta GEE berasal dari model yang dilatih pada seluruh sampel, sehingga mengukur struktur permukaan prediksi, bukan kinerja. Peta dihitung terpisah dan baru tersedia setelah `PREPARE_MAPS`.
2. **Residual OOF.** Dihitung $r_i=y_i-\hat{p}_i^{OOF}$. Prediksi data latih tidak dipakai. Artefak v26 tidak menyimpan koordinat pada prediksi OOF, tetapi dapat dipulihkan dari urutan fold. Pemulihan diverifikasi: label dan blok seluruh titik uji cocok untuk semua fold dan DEM, dan tiap titik tepat satu kali menjadi titik uji. Bila ada ketidakcocokan, kode berhenti dan tidak menghitung.
3. **16 blok tidak layak** sebagai unit analisis: satu blok hanya berisi 1 titik, median 305, maksimum 967, dan ada blok tanpa salah satu kelas. Agregasi ke 16 unit tidak dilakukan.
4. **Spatial weights.** Titik tidak beraturan dengan kepadatan sangat bervariasi (jarak tetangga terdekat median 149 m, maksimum 1,5 km), sehingga dipilih kNN ($k=8$, uji kepekaan 5 dan 12), jarak meter UTM 49S, row-standardized. Satu W dan satu deret permutasi dipakai untuk ketiga DEM. Tidak ada koordinat ganda. Untuk raster dipakai queen 8 tetangga pada grid yang sama.
5. **Inferensi.** Permutasi kondisional, $B=9.999$ (titik) dan $B=999$ (raster), seed 42. $p$ terkecil yang dapat dilaporkan adalah 0,0001.
6. **Kendala.** Prediksi OOF tiap fold berasal dari model berbeda. Hanya 4,4 persen pasangan tetangga ($k=8$) lintas fold. Analisis dilakukan pada evaluasi utama, belum pada multi-seed.

## 5. Hasil numerik Moran's I

Dihitung dari artefak v26 (`n=5.956`, $B=9.999$). **Belum diulang pada dataset beku v27.** Tabel lengkap ada di `Teks_Proposal_Moran_I.md` dan CSV di `outputs/moran_dari_artefak_v26/`.

| Variabel | DEM | $I$ | $p$ dua sisi |
|---|---|---|---|
| Label banjir (acuan) | | 0,677 | 0,0001 |
| Probabilitas OOF | SRTM / GLO-30 / AW3D30 | 0,886 / 0,877 / 0,882 | 0,0001 |
| Residual OOF | SRTM / GLO-30 / AW3D30 | 0,377 / 0,355 / 0,364 | 0,0001 |

Residual OOF masih terkelompok secara spasial pada ketiga DEM. Urutan antar-DEM konsisten pada $k=5, 8, 12$ tetapi selisihnya kecil dan tidak diuji. Moran's I peta probabilitas: **belum tersedia**.

## 6. Kendala yang belum terselesaikan

1. `PREPARE_DATA` dan `PREPARE_MAPS` belum pernah dijalankan pada GEE. Risiko yang belum teruji: parameter `computePixels` untuk grid, batas ukuran dan waktu komputasi per tile (jika gagal, kecilkan `MAP_TILE_PX`), format `ee.data.getAsset` untuk metadata aset, dan pembentukan `sample_fc` dari daftar angka.
2. Tarikan GEE baru belum tentu identik dengan run v26 (aset GEE dapat diperbarui). Selisih harus dilaporkan, bukan disamarkan. Manifest mencatat jumlah dan hash ID scene sebagai bukti.
3. Rekonstruksi `sample_fc` dari artefak v26 tidak mungkin identik: urutan baris asli dan kolom mentah tidak tersimpan. Karena itu `PREPARE_MAPS` hanya memakai tabel mentah hasil `PREPARE_DATA`, dan tidak menyediakan jalur dari CSV v26.
4. Versi library Kaggle pada run v26 tidak tercatat, sehingga penyebab selisih pada bagian 2 tidak dapat dipastikan.
5. GEE melatih RF peta pada `landcover` mentah, sedangkan sklearn memakai one-hot. Ini warisan v26 dan tidak diubah.
6. Moran's I belum dihitung pada multi-seed dan peta.

## 7. Yang sengaja tidak dilakukan

* Tidak mengubah label, AOI, prediktor, preprocessing, sampling, parameter RF (GEE 300 pohon dan sklearn 400 pohon), holdout 75:25, spatial 4-fold CV, block bootstrap 1.000 iterasi, multi-seed lima seed, dan metrik.
* Tidak menyeragamkan seed 42 multi-seed dengan dataset utama.
* Tidak menambah LOCV/LOOCV, LISA, atau Local Moran's I.
* Tidak membuat data sintetis sebagai pengganti data GEE. Raster dan tabel sintetis hanya dipakai di uji kode (`uji_offline/`) dan tidak masuk hasil.
* Tidak mengubah konfigurasi library agar hasil menyerupai v26.
* Tidak mengagregasi data menjadi 16 blok untuk Moran's I.
* Tidak menghapus kode lama (`Export.toDrive`, geemap, thumbnail masih ada, nonaktif).

## 8. Langkah berikutnya di Colab

1. Unggah notebook v27 dan folder `Analisis Flood DEM Susceptibility` ke Drive, letakkan `gee-service-account.json` di root folder.
2. Set `RUN_MODE = 'PREPARE_DATA'`, jalankan semua cell. Hasil: `data/manifest.json`, Parquet dan CSV beku, evaluasi dari file beku, Moran's I titik.
3. Set `RUN_MODE = 'PREPARE_MAPS'`, jalankan. Hasil: GeoTIFF, `export_status.json`, Moran's I peta.
4. Kembalikan ke `USE_CACHED_DATA` untuk semua run berikutnya. Cell terakhir menampilkan laporan pembanding terhadap v26 per komponen.
5. Kirim `manifest.json`, `export_status.json`, dan folder `outputs` agar validasi multi-seed dan peta dapat dilaporkan terpisah.

## 9. Catatan pasca-run Colab (5 Nov 2026, integrasi naskah)

Run Colab v27 sudah selesai dan artefaknya (outputs, data, GeoTIFF, maps_local) telah
diintegrasikan ke naskah (proposal_revisi-final.tex). Catatan untuk laporan ini:

1. **validation_v26_vs_v27.csv**: kolom catatan pada CSV kini terisi hasil audit manual
   pada sesi integrasi; bukan hasil kalkulasi otomatis. Kolom status dengan nilai
   TIDAK_ADA_REFERENSI dipertahankan apa adanya (akurat: tidak ada kalimat di naskah yang
   menautkan masing-masing komponen ke angka run lain). Notebook v27 tetap menjadi sumber
   kebenaran utama angka semua CSV tersebut.
2. **Reproduksibilitas model-level terbukti**: spatial_cv_metrics.csv, multiseed_summary.csv,
   multiseed_delta_auc.csv, spatial_cv_delta_auc_bootstrap.csv, dan sample_audit.csv identik
   tingkat byte dengan run v26; model_metrics.csv hanya berbeda 1 ulp (ambang Youden GLO-30);
   training_sample_features.csv nilai fiturnya identik pada 10 digit desimal (hash md5
   berbeda karena perbedaan format penulisan, bukan isi).
3. **Angka peta yang dirujuk pada naskah diperbarui ke v27**: luas kelas 5 (105,1 / 114,1 /
   113,5 km2), transisi SRTM-GLO-30 (94.306 / 36.869 / 25.679 piksel), diagonal SRTM-AW3D30
   (174.072 / 103.412 piksel), dan 9 nilai kesesuaian WorldCover (54,3; 60,4; 63,4; 66,6;
   61,5; 63,8; 77,4; 82,7; 72,6 persen). Angka sensitivitas antarpeta (79,42 / 83,95 / 81,31
   persen) dan share |dp| (0,056 / 0,037 / 0,048) dari run v26 sudah cocok dengan CSV v27.
4. **Peta risiko dan kesesuaian (risk_class, agreement, delta_abs) TIDAK diintegrasikan**:
   tiga produk raster ini tidak selaras dengan CSV kelas-5 (risk_class_*.tif memuat ~1,97 juta
   piksel kelas 5, sedangkan luas CSV hanya sekitar 105-114 km2) dan share kesesuaiannya
   (34,8-36,8 persen) tidak cocok dengan CSV (79,4-84,0 persen). Kelas 1-4 pada
   risk_class_*.tif persis cocok dengan CSV luas kelas, sehingga indikasi kuat terdapat
   defek pada cabang klasifikasi risiko untuk piksel p<0,2 dan piksel no-data. Hanya
   prob_*.tif yang selaras dan dibawa ke naskah sebagai figures/fig_prob_maps.png. Peta
   kesesuaian/risiko perlu dihasilkan ulang (re-run PREPARE_MAPS setelah patch klasifikasi
   risiko) sebelum digunakan.
5. **Kredensial**: gee-service-account.json pada folder delivery dipindahkan ke
   Proposal Baru/.credentials/ agar tidak terbawa repositori / arsip publikasi.
