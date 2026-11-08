# T16 — Forensik provenance slope

**Lingkup:** hanya pembacaan notebook, manifest, CSV beku, dan daftar raster v27. Tidak ada notebook/eksperimen/GEE yang dijalankan. Data sumber dan proposal tidak diubah.

## Kesimpulan dan status

| Temuan | Status | Kesimpulan |
|---|---|---|
| Ada 30 sampel banjir positif dengan `slope_srtm >= 5°` | **VERIFIED** | Direproduksi dari `Proposal Baru/hasil_kaggle/training_sample_features.csv`: 30 dari 2.978 baris flood=1; maksimum 11,4838371276855°. |
| Koordinat dan nilai 30 sampel cocok dengan frozen raw | **VERIFIED** | Kandidat dipadankan dengan lon/lat dibulatkan 12 desimal untuk pencarian; setiap pasangan lalu diuji dengan kesamaan numerik lon dan lat secara exact, serta kesamaan flood dan `slope_srtm`. Semua pemeriksaan cocok 30/30. Tidak ada ID sampel stabil; CSV audit memakai nomor baris fisik sebagai locator saja. |
| Kode label membatasi slope SRTM `<5°` | **VERIFIED sebagai perilaku kode** | Notebook kanon menghitung slope label dari `USGS/SRTMGL1_003` lalu menerapkan `.lt(5)` pada pembentukan `flood_raw`. Ini membuktikan aturan tertulis, bukan nilai slope filter yang benar-benar diterima tiap titik saat ekspor. |
| Jalur slope label sama persis dengan jalur slope prediktor | **VERIFIED: berbeda** | Label menghitung `ee.Terrain.slope` atas SRTM yang di-clip tanpa reproyeksi eksplisit; jalur prediktor mereproyeksi DEM ke EPSG:32749/30 m dahulu, baru menghitung slope. Tidak ada override resampling eksplisit pada kode terkait. Default Earth Engine adalah nearest-neighbor ketika reproyeksi dijalankan, tetapi lintasan reproyeksi/evaluasi implisit aktual per titik tidak tersedia untuk diverifikasi. |
| Penyebab 30 nilai prediktor ≥5° | **BLOCKED** | Tidak ada raster DEM/slope sumber atau raster slope perantara label di delivery. Nilai slope saat filtering, affine transform sumber, mask piksel efektif, dan hasil sampling yang dipakai untuk 30 titik tidak dapat direkonstruksi lokal. Perbedaan grid adalah mekanisme yang masuk akal, tetapi belum terbukti menyebabkan kasus-kasus ini. |
| Perlu mengubah kode atau mengulang hasil sekarang | **BLOCKED** | Bukti saat ini tidak cukup untuk memilih koreksi implementasi atau menyatakan perbedaan dapat diterima. Jangan mengubah filter/label atau angka beku sebelum perbandingan dua slope di koordinat dan grid aktual tersedia. |

## Bukti yang direproduksi

1. Notebook kanon `Proposal Baru/Flood_DEM_Sensitivity_Notebook_v27_maskAOI.ipynb` (nomor sel tampilan 1-based):
   - Sel 16, baris 22–23: `SLOPE_MAX_FOR_FLOOD = 5`.
   - Sel 22, baris 21–22: `dem_for_label = ee.Image('USGS/SRTMGL1_003').select('elevation').clip(roi)` dan `ee.Terrain.slope(dem_for_label)`.
   - Sel 22, baris 29–32: mask label menggabungkan ambang Sentinel-1, permanent-water mask, dan `slope_for_label.lt(SLOPE_MAX_FOR_FLOOD)`.
   - Sel 28, baris 2–9: konfigurasi DEM di-load; koleksi DEM memakai `.mosaic()`.
   - Sel 28, baris 29–37: DEM prediktor direproyeksi ke `EPSG:32749`, skala 30 m sebelum `ee.Terrain.slope` (sel 28, baris 64–73).
   - Sel 28, baris 80–84: stack prediktor juga direproyeksi ke grid analisis bersama.
2. Manifest `Proposal Baru/v27_delivery/Analisis Flood DEM Susceptibility/data/manifest.json` menyimpan konfigurasi `SLOPE_MAX_FOR_FLOOD: 5`, aset SRTM `USGS/SRTMGL1_003`, target 3.000 per kelas, serta 5.956 sampel main/2.978 positif per kelas. Manifest tidak menyertakan slope per titik pada saat filter atau raster sumber slope.
3. Frozen raw dan training export tidak memiliki kolom ID permanen. Kandidat dipilih dari tabel `hasil_kaggle/training_sample_features.csv`; 30 koordinat cocok unik terhadap frozen raw, termasuk nilai `flood` dan `slope_srtm`. Urutan baris raw berbeda, sehingga pencocokan menggunakan koordinat, bukan menganggap indeks baris setara.
4. Raster di `data/rasters/` berjumlah 13, yaitu probability, risk-class, agreement, delta, dan proxy flood-label; tidak ada GeoTIFF DEM atau slope. Raster proxy label bukan DEM atau raster slope dan tidak dipakai sebagai substitusi.
5. Notebook historis v25, v26, dan v27 pre-T10 juga memuat jalur kode ambang slope SRTM. Kesamaan kode historis tidak menyediakan keluaran slope filter yang hilang atau bukti kausal untuk sampel v27.

Rincian semua 30 locator, koordinat, nilai pada kedua CSV, exact-equality flags, spesifikasi grid yang diketahui, serta kolom metadata sumber yang BLOCKED ada di `slope_points_audit.csv`. Locator adalah nomor baris fisik CSV, bukan ID permanen. Kolom slope sumber/filter berisi `NA_BLOCKED`, bukan nilai perkiraan. CRS dan skala prediktor EPSG:32749/30 m diidentifikasi dari kode, tetapi affine prediktor serta CRS/resolusi/affine/mask slope filter diekspor sebagai BLOCKED.

## Interpretasi teknis

Yang dapat dibuktikan adalah **ketidaksetaraan jalur pemrosesan**: slope untuk filter label dibentuk dari asset SRTM yang langsung di-clip; slope prediktor dibentuk sesudah DEM melalui reproyeksi eksplisit ke grid analisis 30 m. Slope merupakan turunan elevasi, sehingga grid/proyeksi dan pengambilan sampel dapat mengubah nilai lokal. Akan tetapi, tanpa slope pada jalur label, slope prediktor sebelum/ketika sampling, transformasi raster, dan mask pada koordinat yang sama, belum dapat dikatakan bahwa reproyeksi itulah penyebab 30 kasus.

Ini bukan bukti bahwa filter `<5°` tidak ada atau bahwa data label sengaja menerima titik >5°. Sebaliknya, angka pada training table adalah nilai fitur prediktor dan tidak boleh disebut sebagai rekonstruksi slope yang digunakan filter. Penyaringan komponen-terhubung setelah mask juga tidak dapat menjelaskan titik melebihi ambang jika slope, proyeksi, dan piksel yang dievaluasi identik; perbedaan jalur perlu diuji.

## Kebutuhan untuk membuka status BLOCKED

Perlu satu ekspor diagnostik terbatas (tanpa melatih model) pada 30 koordinat frozen yang sama: (a) nilai `slope_for_label` tepat sebelum mask flood, (b) slope band `slope_srtm` prediktor sebelum sampling, (c) mask/validitas tiap band, dan (d) CRS, affine transform, ukuran/resolusi, serta aturan resampling/reprojection aktual tiap citra. Alternatifnya, DEM/SRTM source assets dan seluruh intermediate yang identik dengan run beku harus tersedia bersama bukti waktu/versi. Tanpa itu, penyebab tidak boleh dipilih dari hipotesis.

**Rekomendasi redaksi sementara:** “Kode pembentukan label menerapkan ambang slope SRTM `<5°`, sedangkan tabel sampel merekam slope SRTM dari jalur prediktor yang direproyeksi ke grid analisis. Sebanyak 30 dari 2.978 titik positif memiliki nilai fitur tersebut ≥5° (maksimum 11,483837°); nilai slope pada jalur filter belum tersedia untuk verifikasi sehingga sebab perbedaan belum ditetapkan.” Hindari menyebut 30 sampel itu sebagai bukti filter gagal sebelum audit dua jalur selesai.
