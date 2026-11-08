# T16 — Audit mask raster dan statistik peta

## Cakupan dan cara reproduksi

Audit ini hanya membaca artefak; tidak ada raster, CSV hasil, notebook, proposal, atau snapshot T15 yang diubah. Moran, OOF, bootstrap, GEE, dan pelatihan model tidak dijalankan. Jalankan dari root repositori:

```sh
/tmp/t16-venv/bin/python docs/temuan/T16/mask/audit_masks.py
```

Skrip memeriksa semua GeoTIFF dalam `Proposal Baru/v27_delivery/`, menghitung ulang kelas/luas/matriks dari raster aktif, membandingkan backup dan CSV beku, dan menulis seluruh audit ke direktori ini. Dependensi yang dipakai: rasterio, numpy, pandas. Perhitungan lokal luas adalah planar (`900 m²/piksel` pada grid UTM); itu bukan perhitungan geodesik maupun validasi batas AOI.

## Ringkasan status

| Pertanyaan | Status | Temuan utama |
|---|---|---|
| Apakah mask raster cocok dengan geometri AOI independen dan tidak mencakup piksel di luar AOI? | **BLOCKED** | Geometri tidak ada di paket lokal. Notebook memilih AOI melalui koleksi eksternal GEE FAO/GAUL; tidak ada batas yang dapat ditumpangtindihkan tanpa akses/ekspor geometri itu. Mask raster tidak dapat dijadikan poligon pembandingnya sendiri. |
| Apakah statistik raster aktif dapat direproduksi pada domain raster tersimpan? | **VERIFIED** | Kelas, luas planar, agreement, dan transisi dihitung ulang dengan domain dan denominator eksplisit. Agreement tersimpan cocok hingga selisih maksimum satu piksel. |
| Selisih luas kelas GEE vs. raster lokal | **ACCEPTABLE DIFFERENCE** | GEE memakai `pixelArea()` dan reduksi dalam ROI; luas lokal menghitung 900 m² bagi setiap piksel pada EPSG:32749. Selisih per kelas maksimum 0,144461 km² (maksimum relatif 0,0963%). Jangan menyamakan dua estimator/domain tanpa keterangan. |
| Selisih transisi GEE vs. raster lokal | **FIX REQUIRED** untuk klaim domain/statistik identik | Total sel matriks GEE lebih banyak 20.178–20.373 (sekitar 1,411%) daripada jumlah piksel pada irisan valid raster. Kode GEE mereduksi pada `scale=30` tanpa CRS eksplisit, sementara raster menggunakan grid ekspor EPSG:32749. Ini menunjukkan prosedur/domain tidak identik; penyebab tepat belum terbukti tanpa geometri/input GEE. Gunakan label/domain terpisah, atau hitung ulang di grid dan mask bersama sebelum menyatakan hasil sebanding langsung. |

## Bukti AOI dan geometri

1. Notebook kanon `Proposal Baru/Flood_DEM_Sensitivity_Notebook_v27_maskAOI.ipynb`, sel 16, membentuk `roi` dari `ee.FeatureCollection('FAO/GAUL/2015/level2')`, memilih ADM2 `Kota Semarang` dan `Demak` (dengan fallback nama `Semarang`, `Demak`), kemudian menggunakan `.geometry()`. Sel yang sama membentuk `_AOI_MASK` dengan `clip(roi).unmask(0)`. Ini mendokumentasikan sumber/prosedur AOI, bukan menyediakan geometri polygon lokal.
2. Penelusuran path vektor, arsip zip, JSON/GeoJSON tertanam, dan metadata skema 12 Parquet tidak menemukan kandidat polygon AOI independen. Parquet sampel memiliki kolom koordinat titik `lat`/`lon`, bukan field geometri batas. Lihat `geometry_candidates.csv`, `embedded_geometry_json_candidates.csv`, `parquet_geometry_metadata.csv`, serta `notebook_aoi_statistics_refs.csv`.
3. Karena polygon sumber berada di koleksi GEE eksternal dan tidak tersedia sebagai artefak lokal, pemeriksaan piksel di luar AOI, geometri administratif persis yang terpilih, luas geodesik AOI, serta validitas geografis mask **BLOCKED**. Tidak ada polygon perkiraan yang dibuat. Diperlukan ekspor geometri yang sama dari koleksi/versi GEE beserta identitas fitur ADM2, lalu rasterisasi/overlay terhadap transformasi aktif.

T10 (`docs/temuan/T10-patch-mask-aoi-nodata.md`) melaporkan patch NoData dan menyebut 13 raster termask; sepuluh raster probabilitas/delta/agreement/label disunting lokal dengan menjaga nilai valid dan menulis NoData di luar mask valid raster, sementara tiga `risk_class` tidak disunting lokal. Karena audit mask turunan memakai domain raster valid yang telah disimpan—dan kelas risiko menjadi acuan domain pada surgery—kesesuaian antar-mask membuktikan konsistensi artefak, bukan verifikasi geometri independen. Ini batas sumber-mask yang penting, bukan bukti bahwa mask salah.

## Inventaris grid, validitas, dan efek backup

Semua 36 GeoTIFF diperiksa: 13 `data/rasters/` aktif, 10 `data/rasters_backup_unmasked/`, dan 13 `old_Analisis Flood DEM Susceptibility/data/rasters/`. Tidak ditemukan pasangan GeoTIFF yang identik byte demi byte; file dengan nama sama pada grup berbeda adalah versi/peran historis, bukan otomatis duplikat identik. Metadata semua file ada di `raster_inventory.csv`; hash dan pengelompokan per file tercatat di sana.

Ketiga belas raster aktif berbagi grid yang sama: 2.074 × 1.592; EPSG:32749; ukuran piksel 30 × 30 m; transformasi affine `[30, 0, 419280, 0, -30, 9258540]`; extent `[419280, 9210780, 481500, 9258540]`; NoData `-9999`. Grid ini hanya membuktikan keselarasan, bukan kebenaran batas AOI.

| Raster kelas | Valid pixels, nilai kelas 1–5 | Luas domain planar |
|---|---:|---:|
| SRTM | 1.444.085 | 1.299,6765 km² |
| GLO-30 | 1.444.085 | 1.299,6765 km² |
| AW3D30 | 1.429.582 | 1.286,6238 km² |

Backup tersedia untuk 10 raster, bukan tiga `risk_class`. Pada grid yang sama, nilai seluruh piksel valid bersama identik antara raster aktif dan backup. Sembilan raster non-label memiliki 1.848.071 sel tambahan valid pada backup; label banjir memiliki 1.857.723. Perubahan yang terukur adalah pemangkasan domain valid/penetapan NoData, bukan perubahan nilai pada area overlap. AW3D30 memiliki 14.503 sel valid lebih sedikit daripada SRTM/GLO-30 pada raster aktif. Detail: `mask_effect_backup.csv`.

## Hitung ulang kelas, agreement, dan transisi lokal

Kelas yang diaudit adalah nilai integer 1–5. Luas = jumlah piksel valid bernilai kelas × 900 m². Setiap DEM menggunakan domain validnya sendiri untuk luas; matriks pasangan memakai irisan piksel valid dan berkategori 1–5 dari kedua raster. Agreement = diagonal matriks ÷ jumlah sel pada irisan yang sama. Dengan demikian denominator SRTM–GLO-30 adalah 1.444.085; untuk pasangan yang melibatkan AW3D30, 1.429.582.

| DEM | Kelas 1 (km²) | Kelas 2 | Kelas 3 | Kelas 4 | Kelas 5 |
|---|---:|---:|---:|---:|---:|
| SRTM | 756,7632 | 232,9821 | 113,9751 | 95,3127 | 100,6434 |
| GLO-30 | 822,5379 | 189,8685 | 98,4150 | 79,2810 | 109,5741 |
| AW3D30 | 772,3755 | 222,0534 | 108,1035 | 88,1253 | 95,9661 |

| Pasangan (baris → kolom) | Sel domain bersama | Sel diagonal | Agreement |
|---|---:|---:|---:|
| SRTM → GLO-30 | 1.444.085 | 1.146.218 | 79,3733% |
| SRTM → AW3D30 | 1.429.582 | 1.204.815 | 84,2774% |
| GLO-30 → AW3D30 | 1.429.582 | 1.165.421 | 81,5218% |

Matriks 5×5 lengkap, count, persentase baris, dan denominator tersedia di `agreement_transition_local.csv`; luas per kelas di `class_area_local.csv`. Raster agreement tersimpan memiliki domain valid yang sama dengan matriks. Jumlah sel agreement berbeda dari hitungan diagonal paling banyak satu sel untuk dua pasangan (nol untuk pasangan ketiga), sehingga persentase cocok dalam ±0,0001 poin persentase (`agreement_raster_check.csv`). Ini memverifikasi replikasi raster internal saja.

## Perbandingan CSV GEE dengan raster aktif

Notebook sel 53 baris 41–56 membentuk kode transisi dari `risk_class` dan menjalankan `frequencyHistogram().reduceRegion(geometry=roi, scale=30, ...)`; tidak menetapkan CRS eksplisit di pemanggilan itu. Sel 54 baris 1–17 menjumlahkan `ee.Image.pixelArea()` per kelas melalui `reduceRegion(geometry=roi, scale=30, ...)`. Sel 16 mendefinisikan `roi`; sel 59 mengekspor mask/grid. Baris-baris bukti diekstrak di `notebook_aoi_statistics_refs.csv`.

CSV `data/gee_tables/{area_per_risk_class_km2,transition_*.csv}` identik secara nilai dengan CSV yang sama nama di `outputs/`; dua folder itu bukan dua pengukuran independen. Hitungan ulang independen dari GeoTIFF aktif menunjukkan:

| Tabel transisi | GEE CSV total | Raster shared-valid total | Selisih | Selisih relatif |
|---|---:|---:|---:|---:|
| SRTM → GLO-30 | 1.464.458 | 1.444.085 | 20.373 | 1,4108% |
| SRTM → AW3D30 | 1.449.760 | 1.429.582 | 20.178 | 1,4115% |
| GLO-30 → AW3D30 | 1.449.763 | 1.429.582 | 20.181 | 1,4117% |

Meski total denominator berbeda, persentase diagonal GEE tetap dekat dengan lokal: 79,3586% vs 79,3733%; 84,2702% vs 84,2774%; 81,5164% vs 81,5218%. Kemiripan rasio tidak menyamakan jumlah sampel/domain. Perbedaan 1,41% tidak dapat dijelaskan oleh perbedaan estimasi luas `pixelArea` saja karena transisi adalah hitungan kategori, bukan luas. Akar perbedaan pastinya belum dapat dipisahkan antara proyeksi default/reduksi skala, batas geometri yang dirasterisasi, dan mask sumber tanpa GEE serta geometri/input yang sama.

Luas raster lokal dibanding angka GEE berbeda paling besar 0,144461 km² per pasangan kelas; nilai maksimum relatif 0,0963%. Arah selisih berbeda antar kelas, dan GEE memakai luas piksel (`pixelArea`) sementara audit raster menghitung luas planar 900 m² per sel. Selisih kecil ini wajar sebagai estimator/domain berbeda, tetapi tidak memberi validasi geografis AOI.

**Rekomendasi pelaporan:** tulis bahwa area GEE adalah pengukuran berbasis `pixelArea` dalam reduksi ROI dan luas lokal adalah hitungan sel pada grid raster final. Untuk transisi, laporkan domain/denominator eksplisit dan jangan mengutip tabel GEE sebagai matriks dari raster final sampai keduanya direproduksi pada CRS, transformasi, mask, dan aturan inklusi batas yang sama. Bila kesetaraan langsung merupakan klaim yang diperlukan, perlu hitung ulang terarah GEE atau ekspor ulang statistik pada grid raster tetap; ini tidak dilakukan dalam audit read-only.

## Berkas audit

- `audit_masks.py` — reproduksi inventaris, kelas, transisi, backup, dan pembandingan GEE.
- `raster_inventory.csv`, `raster_exact_duplicates.csv`, `active_grid_signatures.csv` — 36 metadata raster, duplikat hash, grid aktif.
- `class_area_local.csv`, `agreement_transition_local.csv`, `agreement_raster_check.csv` — hitung ulang statistik lokal.
- `mask_effect_backup.csv` — perubahan mask dan pemeriksaan nilai pada backup.
- `gee_vs_local.csv` — nilai tabel beku vs hitungan lokal.
- `geometry_candidates.csv`, `embedded_geometry_json_candidates.csv`, `parquet_geometry_metadata.csv`, `notebook_aoi_statistics_refs.csv` — pencarian geometri dan bukti kode ROI/reduksi.

## Batas kesimpulan

Tidak dilakukan akses GEE, pengunduhan boundary FAO/GAUL, overlay polygon independen, atau penghitungan ulang server-side. Karena itu tidak ada klaim bahwa piksel luar AOI telah ditemukan atau bahwa polygon GEE sudah cocok dengan mask. Audit Moran/OOF/bootstrap ditangani di ruang lingkup lain dan tidak termasuk hasil ini.
