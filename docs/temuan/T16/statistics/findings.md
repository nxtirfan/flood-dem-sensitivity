# T16 — Audit statistik spasial OOF, raster Moran, dan block bootstrap

## Cakupan dan sumber

Audit ini hanya membaca artefak beku dan menghitung ulang diagnostik; tidak menjalankan GEE, notebook penuh, pelatihan model, atau fold CV. Skrip reproduksi: `docs/temuan/T16/statistics/recompute_statistics.py`; semua CSV hasil audit berada di direktori yang sama.

Sumber utama yang diperiksa:

- Notebook kanonis `Proposal Baru/Flood_DEM_Sensitivity_Notebook_v27_maskAOI.ipynb`: cell 39 (spatial CV dan prediksi OOF), cell 41 (bootstrap blok), cell 42–43 (Moran OOF), cell 64 (Moran peta dan cache keluaran).
- Implementasi offline `Proposal Baru/v27_delivery/uji_offline/cells_baru/moran_oof.py`, `moran_utils.py`, `moran_map.py`, serta helper raster `_raster_array` di `maps_utils.py`.
- Prediksi beku `Proposal Baru/hasil_kaggle/spatial_cv_test_predictions.csv` dan `Proposal Baru/v27_delivery/Analisis Flood DEM Susceptibility/outputs/spatial_cv_test_predictions.csv`; hasil tersimpan `moran_oof_global.csv`, `moran_oof_points.csv`, `moran_prob_map_global.csv`, dan `spatial_cv_delta_auc_bootstrap.csv`.
- GeoTIFF `data/rasters/prob_{srtm,glo30,aw3d30}.tif` (aktif/post-mask), `data/rasters_backup_unmasked/prob_{srtm,glo30,aw3d30}.tif` (pra-mask), serta `data/manifest.json`.

## Temuan dan status

### 1. Moran titik dari OOF — **VERIFIED**

Satu prediksi OOF per masing-masing 5.956 titik dipulihkan dari prediksi tersimpan. Untuk tiap fold dan DEM, urutan label serta blok dari prediksi cocok tepat dengan urutan label/blok di `moran_oof_points.csv`; probabilitas yang dipulihkan cocok dengan probabilitas dalam CSV titik. Tidak ada prediksi yang hilang. Titik memakai koordinat lon/lat dari CSV titik, diproyeksikan ke EPSG:32749; koordinat belum diverifikasi terhadap sumber koordinat independen.

Definisi sesuai cell 43 dan `moran_utils.py`: Global Moran’s I, bobot kNN terarah (bukan disimetriskan) tanpa titik itu sendiri, bobot tiap baris 1/k, jarak UTM 49S; k utama 8 dan sensitivitas 5 serta 12. Permutasi kondisional mengacak nilai antar-lokasi pada graf tetap; `numpy.random.RandomState(42)`, 9.999 permutasi per variabel/k. Nilai harapan nol `−1/(n−1)`; p dua sisi memakai koreksi +1 dan ambang permutasi berpusat pada nilai harapan.

Semua **21/21** kombinasi tersimpan (label, tiga probabilitas, tiga residual × tiga nilai k) direproduksi: selisih I dan p dua sisi nol pada presisi CSV. Untuk k=8, n=5.956:

| Variabel | Moran’s I | z permutasi | p dua sisi |
|---|---:|---:|---:|
| Label referensi | 0,676922 | 109,71 | 0,0001 |
| Probabilitas OOF SRTM | 0,886300 | 143,63 | 0,0001 |
| Probabilitas OOF GLO30 | 0,877050 | 142,86 | 0,0001 |
| Probabilitas OOF AW3D30 | 0,882083 | 142,92 | 0,0001 |
| Residual OOF SRTM | 0,377084 | 61,45 | 0,0001 |
| Residual OOF GLO30 | 0,354520 | 57,90 | 0,0001 |
| Residual OOF AW3D30 | 0,364131 | 59,11 | 0,0001 |

Seluruh p mencapai resolusi minimum 1/(9.999+1), bukan estimasi peluang yang lebih kecil. Pada k=8 terdapat 4,4178% sisi tetangga yang melintasi fold; jarak ke tetangga ke-8 median 612 m, persentil ke-95 1.245 m, maksimum 3.903 m. Angka Moran menggambarkan label/probabilitas/residual OOF pada **titik**, bukan peta penuh dan bukan ukuran independen atas kebocoran spasial. Statistik tetap mengandung autokorelasi residual yang nyata.

### 2. Block bootstrap ΔAUC — **VERIFIED**

Cell 41 memakai 16 blok kuantil lon/lat yang sama dengan rancangan spatial CV. Unit resampling adalah blok: 16 ID blok diambil dengan pengembalian; semua baris dari setiap blok terpilih digabungkan, termasuk duplikasi blok, untuk menghitung ROC-AUC tiap DEM. Draw yang sama dipakai berpasangan pada ketiga DEM. Ada 1.000 iterasi, `np.random.RandomState(RANDOM_STATE)` dengan `RANDOM_STATE=42` (MT19937), dan CI persentil 2,5–97,5; SD memakai `ddof=1`.

Rekonstruksi dari kedua CSV prediksi menghasilkan statistik yang sama persis dengan `spatial_cv_delta_auc_bootstrap.csv` di `hasil_kaggle` dan delivery:

| ΔAUC | Rerata | SD | CI persentil 95% |
|---|---:|---:|---:|
| SRTM − GLO30 | −0,015460 | 0,004740 | [−0,024968; −0,007199] |
| SRTM − AW3D30 | −0,004670 | 0,002763 | [−0,009559; 0,001279] |
| GLO30 − AW3D30 | 0,010790 | 0,004212 | [0,004140; 0,019760] |

Ini adalah ketidakpastian **bersyarat pada prediksi OOF, pembagian fold, dan 16 blok yang sudah ada**. Bootstrap tidak melatih ulang model, mengulang CV, mengulang pengambilan sampel, atau mengukur variasi antar-run/model. Karena itu, istilah yang tepat adalah block bootstrap atas prediksi OOF tersimpan, bukan validasi independen baru. CI SRTM−AW3D30 memuat nol; dua CI lain tidak.

Salinan prediksi Kaggle dan delivery memiliki hash berkas berbeda, tetapi kunci baris/fold/konfigurasi/blok/label sama. Dari 17.868 probabilitas, 2.323 berbeda secara bit/nilai float setelah parsing; maksimum selisih absolut hanya 3,33×10⁻¹⁶. Kedua CSV bootstrap memiliki SHA-256 identik dan keduanya direproduksi; perbedaan numerik prediksi tidak mengubah hasil bootstrap pada presisi keluaran. Perbedaan hash prediksi adalah ketidakidentikan serialisasi/nilai floating-point sangat kecil, bukan perbedaan substantif yang terukur di sini.

### 3. Moran raster — **FIX REQUIRED untuk konsistensi AW3D30; SRTM/GLO30 VERIFIED**

Implementasi sumber (`moran_utils.py`, sama dengan fungsi di notebook cell 11) memakai bobot queen 8-arah, row-standardized terhadap tetangga valid, dan mengeluarkan piksel valid terisolasi (`use = valid & (cnt > 0)`). Validitas dibentuk dari nilai finite dan bukan NoData −9999. Statistik dihitung pada raster probabilitas penuh (bukan titik OOF); tidak ada transformasi grid yang diterapkan ulang.

| Raster aktif | Piksel valid | n menurut sumber (island dikeluarkan) | I hitung ulang | I CSV tersimpan | Selisih |
|---|---:|---:|---:|---:|---:|
| SRTM | 1.444.085 | 1.444.085 | 0,957714 | 0,957714 | < 3×10⁻¹⁰ |
| GLO30 | 1.444.085 | 1.444.085 | 0,953076 | 0,953076 | < 3×10⁻¹⁰ |
| AW3D30 | 1.429.582 | **1.429.580** | **0,954421723** | **0,954415** | **+0,000006333** |

AW3D30 aktif memiliki dua piksel valid tanpa tetangga queen valid. Keduanya masuk sebagai observasi pada `moran_prob_map_global.csv` (n=1.429.582), walau source code saat ini menyatakan island dikeluarkan. Penghitungan alternatif yang memasukkan seluruh piksel valid menghasilkan I=0,954415389, yang cocok dengan CSV tersimpan pada enam desimal. Dengan demikian, penyebab numerik teridentifikasi: definisi denominator/island pada hasil tersimpan berbeda dari kode sumber yang sekarang tersedia. Sejarah persis kapan/versi kode yang menghasilkan CSV tidak dapat dipastikan dari artefak yang ada. Dampak numeriknya kecil dan tidak mengubah pembulatan tiga desimal (0,954), tetapi keluaran perlu diselaraskan dengan definisi kode yang diklaim. Tidak ada model atau raster yang perlu dihitung ulang; cukup hitung ulang diagnostik AW3D30/CSV terkait atau nyatakan eksplisit bahwa island ikut dihitung.

P-value peta yang tersimpan adalah 0,001 (999 permutasi; batas resolusi minimum). Karena 999 permutasi pada lebih dari 1,4 juta piksel mahal, audit ini menghitung ulang I deterministik saja dan tidak menjalankan ulang permutasi raster; p-value map tetap hasil tersimpan, belum diverifikasi ulang secara independen.

### 4. Cached notebook vs domain raster aktif — **ACCEPTABLE DIFFERENCE**

Output tersimpan cell 64 notebook memuat n pra-mask 3.292.156 (SRTM/GLO30) dan 3.277.652 (AW3D30), dengan I tercetak 0,9701, 0,9648, dan 0,9673. Moran dihitung ulang pada `rasters_backup_unmasked` menghasilkan n yang sama setelah island dikeluarkan; I=0,970064, 0,964818, dan 0,967303 (membulat ke cache). Ini mendukung bahwa cache cell 64 adalah pra-mask. Nilainya tidak boleh dibandingkan sebagai hasil domain yang sama dengan raster aktif pasca-mask.

SHA-256 GeoTIFF backup pra-mask cocok dengan `maps.rasters` di manifest untuk ketiga DEM; SHA-256 file aktif pasca-mask tidak cocok dengan hash ekspor manifest tersebut. Hal ini konsisten dengan backup sebagai ekspor asli dan file aktif sebagai produk pasca-mask, tetapi checksum manifest bukan bukti geometri AOI independen. Hasil aktif dari CSV Moran pasca-mask karena itu dibedakan dari cache lama, bukan digabungkan sebagai satu rangkaian.

## Keterbatasan dan lingkungan

Manifest mencatat lingkungan keluaran asli Python 3.13.16, NumPy 2.4.6, pandas 2.2.3, scikit-learn 1.6.1, SciPy 1.16.3, dan rasterio 1.5.2. Rekonstruksi berjalan di Python 3.12.3, NumPy 2.5.4, pandas 3.1.1, scikit-learn 1.9.1, SciPy 1.18.1, rasterio 1.5.2. Angka OOF dan bootstrap tetap cocok dengan CSV pada presisi yang ditulis meskipun versinya berbeda. Metode kNN/Moran memakai SciPy; `libpysal`/`esda` tidak dipakai dalam hitung ulang ini.

CSV pendamping: `moran_oof_recomputed.csv`, `moran_oof_neighbors.csv`, `moran_raster_recomputed.csv`, `block_bootstrap_recomputed.csv`, `source_provenance.csv`, dan `runtime_versions.csv`. Semua berada di `docs/temuan/T16/statistics/` dan dibangkitkan skrip yang sama. Data sumber, notebook, model, prediksi, raster, proposal, serta file di luar direktori T16 tidak diubah.
