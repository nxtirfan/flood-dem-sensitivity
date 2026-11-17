# T18 — Konsolidasi Eksperimen v28 & Penutupan Penuh Audit Teknis T16–T17

**Tanggal**: 13 November 2026  
**Cakupan**: Penyelesaian seluruh *open problems* dari `T15-finalisasi-terarah.md`, `T16-technical-investigation.md`, dan `T17-gee-slope-investigation.md` ke dalam notebook kanonik `Flood_DEM_Sensitivity_Notebook_v28.ipynb` (`72` sel) dan folder `Proposal Baru/v28_delivery/`, tanpa mengubah naskah proposal LaTeX (`proposal_revisi-final.tex` tetap pada baseline T15, 51 halaman).

---

## 1. Bukti Eksak Diagnostik GEE 30 Titik Sampel Banjir (`srtm_slope >= 5°`)

Berdasarkan eksekusi `T17_Diagnostik_Slope_dan_AOI_v28.ipynb` di Google Earth Engine pada ke-30 koordinat sampel positif (`flood = 1`) yang memiliki `srtm_slope >= 5°` di dalam `training_sample_features.csv` (`t17_slope_route_summary.csv` & `t17_slope_30point_diagnostic.csv`):

| Rute Evaluasi GEE | CRS & Skala | `n_valid` | `n_slope_lt_5` | `n_slope_gte_5` | Min (`°`) | Mean (`°`) | Max (`°`) | Max `|Δ|` vs CSV Historis |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `label_native_projection_control` | `EPSG:4326` (`30,922 m`) | 30 | **30** | **0** | 1,316168 | 3,797728 | 4,987200 | 10,167669 |
| `feature_srtm_slope_analysis_grid` | `EPSG:32749` (`30 m`, reproyeksi sebelum `slope`) | 30 | **0** | **30** | 5,103612 | 6,245420 | 11,483837 | **0,000000** |
| `feature_slope_final_sampling_grid_control` | `EPSG:32749` (`30 m`, grid sampling akhir) | 30 | **0** | **30** | 5,103612 | 6,245420 | 11,483837 | **0,000000** |
| `label_slope_forced_analysis_grid_control` | `EPSG:32749` (`30 m`, reproyeksi sesudah `slope`) | 30 | 8 | 22 | 4,986845 | 6,070221 | 11,230177 | 0,253660 |

**Kesimpulan**:
1. Saat pembentukan label inventori banjir (`slope = ee.Terrain.slope(srtm)` pada proyeksi asli `EPSG:4326`), ke-30 titik tersebut seluruhnya memiliki kemiringan lereng `< 5°` (`1,316°–4,987°`), sehingga lolos filter `slope.lt(5)` secara sah.
2. Saat pembentukan fitur prediktor (`dem_30m = raw.resample('bilinear').reproject('EPSG:32749', None, 30)` diikuti `ee.Terrain.slope(dem_30m)`), ke-30 titik yang berada di tepi transisi piksel mengalami perubahan gradien lokal menjadi `5,104°–11,484°` (cocok 100% hingga `0,000000°` dengan nilai historis di `training_sample_features.csv`).
3. Tidak terdapat *bug* pada kode *filtering* maupun kebocoran sampel, sehingga **model Random Forest tidak perlu dilatih ulang (*no retraining required*)**.

---

## 2. Verifikasi Poligon Batas AOI Independen (`aoi_semarang_demak.geojson`)

Poligon batas administratif resmi diekspor dari `FAO/GAUL/2015/level2` (`ADM2_NAME` = `Demak` dan `Kota Semarang`, `feature_count = 2`, luas geodesik `1.310,0915 km²`, luas planar `EPSG:32749` `1.303,5283 km²`) ke dalam `aoi_semarang_demak.geojson` dan `aoi_metadata.json`. Hasil verifikasi independen terhadap ke-13 GeoTIFF aktif (`aoi_independent_mask_verification.csv`):

- **Kelompok SRTM & GLO-30 (`10` raster)**: `1.444.085` piksel valid (`1.444.077` pusat piksel berada di dalam poligon; `8` piksel berpotongan langsung dengan garis batas AOI dengan jarak pusat maksimum `5,563 m`).
- **Kelompok AW3D30 (`3` raster)**: `1.429.582` piksel valid (`1.429.575` pusat piksel berada di dalam poligon; `7` piksel berpotongan langsung dengan garis batas AOI dengan jarak pusat maksimum `5,563 m`).
- **Piksel di luar batas AOI melebihi 1 piksel (`> 30 m`)**: **`0` piksel** di seluruh 13 raster.

---

## 3. Rekomputasi Moran's I Global Peta Probabilitas (`moran_prob_map_global.csv`)

Fungsi `compute_raster_moran` di dalam `Flood_DEM_Sensitivity_Notebook_v28.ipynb` diperbarui agar mendeteksi dan mengecualikan piksel terisolasi (*degree* 0 pada matriks *Rook contiguity*) sebelum standardisasi baris (*row-standardization*) dan uji permutasi kondisional (`B = 999`, `seed = 42`):

| Konfigurasi DEM | `n_valid_total` | `n_isolated_excluded` | `n_used` | Moran's `I` | `E[I]` | `perm_mean` | `perm_sd` | `z_perm` | `p_two_sided` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `srtm` | 1.444.085 | 0 | 1.444.085 | `0,9577138908` | `-6,924805e-07` | `7,544885e-06` | `0,000405` | `2362,881173` | `0,001` |
| `glo30` | 1.444.085 | 0 | 1.444.085 | `0,9530758017` | `-6,924805e-07` | `-1,329648e-05` | `0,000405` | `2351,676997` | `0,001` |
| `aw3d30` | 1.429.582 | 2 | 1.429.580 | `0,9544217226` | `-6,995066e-07` | `-8,797807e-06` | `0,000424` | `2251,992351` | `0,001` |

---

## 4. Sinkronisasi Checksum SHA-256 & Penataan Arsip

1. **Sinkronisasi `manifest.json` & `export_status.json`**: Seluruh **45 checksum SHA-256** (`13` di `export_status.json`, `13` di `manifest.maps.rasters`, dan `19` file dataset/tabel di `manifest.json`) telah disinkronkan 100% (`0` mismatch) terhadap file aktif di `v28_delivery`, sementara hash pra-masking v26 disimpan pada field `pre_aoi_mask_v26_sha256`.
2. **Sinkronisasi `Proposal Baru/hasil_kaggle/`**: Ketujuh CSV spasial pasca-masking (`area_by_class.csv`, `sensitivity_summary.csv`, `worldcover_stratification.csv`, `dem_stats.csv`, `transition_matrix_*.csv`) dan `moran_prob_map_global.csv` di `Proposal Baru/hasil_kaggle/` telah disinkronkan dengan `v28_delivery` (versi lama pra-masking diarsipkan ke `Proposal Baru/olds/hasil_kaggle_v26_legacy/`).
3. **Arsip `v27`**: Folder `v27_delivery/` dan `Flood_DEM_Sensitivity_Notebook_v27_maskAOI.ipynb` telah dipindahkan ke `Proposal Baru/olds/`.
