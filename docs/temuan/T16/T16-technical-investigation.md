# T16 — Investigasi teknis pasca-T15

**Tanggal:** 8 November 2026. **Baseline:** `7ab45a1d1d209f8b0d0570bee87dcf2e02daef28`.

**Kesimpulan:** konflik nilai slope terkonfirmasi, tetapi penyebab per titik masih **BLOCKED** karena slope jalur filter dan raster sumber tidak tersimpan. Validasi geografis AOI juga **BLOCKED** tanpa poligon independen. Statistik lokal dapat direkonstruksi, tetapi ditemukan ketidakselarasan metadata checksum, denominator transisi GEE–lokal, dan penanganan dua piksel terisolasi pada Moran raster AW3D30. Temuan tersebut tidak diperbaiki pada sumber selama T16.

## 1. Ruang lingkup, urutan kerja, dan tingkat bukti

AGENTS.md dan laporan T15 dibaca terlebih dahulu, diikuti CONTEXT.md/STATUS.md. Inventaris dan [rencana investigasi](INVESTIGATION_PLAN.md) dibuat sebelum analisis mendalam. Laporan T15 digunakan sebagai daftar pertanyaan, bukan bukti kebenaran. Semua analisis di bawah dibangun dari notebook, manifest, CSV, GeoTIFF, serta keluaran diagnostik baru.

- **Fakta:** diamati langsung dari berkas/kode atau dihitung ulang dari data tersimpan.
- **Hipotesis:** mekanisme yang masuk akal, tetapi belum dibuktikan pada data/grid yang sama.
- **Belum terbukti/BLOCKED:** memerlukan artefak atau evaluasi GEE yang tidak tersedia dalam audit lokal.
- **VERIFIED** berlaku untuk klaim spesifik yang disebutkan, bukan validasi keseluruhan metodologi.
- **ACCEPTABLE DIFFERENCE** berarti estimand/domain berbeda dapat dilaporkan terpisah; bukan izin menyebut dua angka identik atau menganggap batas geografis sudah benar.
- **FIX REQUIRED** adalah rekomendasi untuk tahap berikutnya; **tidak ada perbaikan pada data/proposal/snapshot T15 diterapkan**.

Tidak ada pelatihan, regenerasi label/sampel, perubahan seed/parameter/model, eksekusi notebook penuh, kompilasi proposal, atau akses aset GEE. Diagnostik OOF/bootstrap hanya menggunakan prediksi yang sudah beku. Semua keluaran baru berada di `docs/temuan/T16/`.

## 2. Inventaris dan pemilihan sumber

[Inventaris awal](source_inventory.csv) mencakup **388 berkas terlacak**: 151 CSV, 36 GeoTIFF, 12 Parquet, dan 8 notebook, beserta ukuran dan SHA-256. Tidak ditemukan berkas penelitian tambahan di luar inventaris; berkas runtime platform bukan artefak penelitian.

| Kelompok | Peran dalam audit |
|---|---|
| Notebook canon `Proposal Baru/Flood_DEM_Sensitivity_Notebook_v27_maskAOI.ipynb` | Definisi kode label, fitur, grid, reduksi, Moran, bootstrap; bukan jaminan setiap output cache berasal dari kode/versi yang sama |
| `Proposal Baru/v27_delivery/Analisis Flood DEM Susceptibility/data/frozen/` | Tabel sampel mentah main dan multiseed, bukan raster slope |
| `data/gee_tables/` pada delivery tersebut | CSV hasil GEE beku; ketujuh hash cocok dengan manifest |
| `data/rasters/` | 13 raster aktif pascamask: probability, risk class, delta, agreement, proxy label |
| `data/rasters_backup_unmasked/` | 10 raster pramask; tidak ada backup risk-class terpisah |
| `old_Analisis Flood DEM Susceptibility/data/rasters/` | 13 raster versi lama, tidak dipakai menggantikan raster aktif |
| `outputs/`, `Proposal Baru/hasil_kaggle/` | Prediksi/statistik tersimpan; kesetaraan diperiksa, bukan diasumsikan dari basename |

**Temuan provenance:** dari 45 referensi hash yang diuji, 35 cocok dengan file aktif; 10 pada `manifest.maps.rasters` cocok dengan **backup pramask**, bukan raster aktif. Semua 13 hash pada `export_status.json` cocok dengan raster aktif. Ini **FIX REQUIRED pada metadata**, bukan bukti kerusakan nilai raster. Rincian: [manifest_hash_audit.csv](manifest_hash_audit.csv), [PROVENANCE_FINDINGS.md](PROVENANCE_FINDINGS.md).

Dari 20 pasangan CSV hasil_kaggle–delivery, tujuh nama memiliki perbedaan numerik substantif: luas, statistik DEM, sensitivitas, tiga transisi, dan WorldCover. Maksimum perbedaan luas antarversi mencapai **17,564393 km²**; jangan mencampurkannya dengan selisih GEE–lokal pada versi yang sama. Prediksi OOF, fitur, prediksi multiseed, dan metrik model cocok pada toleransi absolut 1e-10 meski sebagian byte/hash berbeda. Lihat [result_copy_numeric_audit.csv](result_copy_numeric_audit.csv).

Nomor cell dalam laporan ini adalah **indeks JSON 0-based**, kecuali laporan slope yang secara eksplisit menggunakan nomor tampilan 1-based.

## 3. Tahap 1 — Forensik slope

### 3.1 Fakta yang direproduksi — VERIFIED

- Tabel fitur berisi 5.956 titik, dengan 2.978 positif.
- **30/2.978 = sekitar 1,0074%** titik positif memiliki `slope_srtm >=5°`; maksimum **11,4838371276855°**.
- Ketigapuluh koordinat cocok unik terhadap raw frozen dan salinan delivery. Nilai lon, lat, label, serta slope cocok tepat setelah pemetaan kandidat; ini bukan kesalahan penyambungan baris antartabel.
- Tidak ada ID sampel permanen pada CSV. Audit menggunakan **locator nomor baris fisik**, bukan mengarang ID asli. Pencarian kandidat koordinat dibulatkan 12 desimal, kemudian kesamaan angka koordinat dan label diperiksa secara eksplisit.
- Kode label memakai `ee.Terrain.slope(ee.Image('USGS/SRTMGL1_003').select('elevation').clip(roi))`, lalu `.lt(SLOPE_MAX_FOR_FLOOD)` dengan ambang 5 (cell 15 dan 21).
- Kode fitur mereproyeksi DEM ke **EPSG:32749, skala nominal 30 m sebelum menghitung slope** (cell 27). Ini jalur berbeda dari slope filter label.

[Tabel 30 titik](slope/slope_points_audit.csv) memuat locator, koordinat, nilai fitur/raw, pemeriksaan kecocokan, slope saat filter/raster sumber, CRS, resolusi, affine, resampling, mask, dan status ketersediaannya. **Kolom yang tidak dapat direkonstruksi diberi NA_BLOCKED**, bukan diisi slope fitur sebagai pengganti. Lihat [laporan slope](slope/findings.md) dan [visualisasi](slope_audit_overview.png).

### 3.2 Akar sebab — BLOCKED

Tidak tersedia GeoTIFF DEM/slope asli atau intermediate `slope_for_label`; 13 raster aktif adalah produk turunan peta/label. Karena itu, nilai slope pada saat filter, transformasi aktual source/intermediate, dan mask efektif pada 30 titik belum bisa diperiksa lokal.

**Hipotesis yang didukung struktur kode:** reproyeksi sebelum/ sesudah diferensiasi elevasi serta evaluasi pada grid/pusat piksel berbeda dapat menghasilkan slope berbeda. Dokumentasi API menyatakan nearest-neighbor sebagai default reproyeksi dan keluaran sampleRegions mengikuti pusat piksel. Namun kontrak API serta perbedaan kode **tidak membuktikan** sebab numerik pada 30 titik ini. Jangan menyatakan “filter gagal” ataupun “pasti akibat resampling”.

**Dampak:** klaim bahwa seluruh nilai fitur slope positif harus `<5°` tidak benar; klaim bahwa label pasti melanggar filter juga belum terbukti. Belum ada dasar untuk menghapus 30 titik, menaikkan ambang, atau menghitung ulang model.

**Usulan wording:** “Kode label menerapkan ambang slope SRTM `<5°`, sedangkan fitur slope dihitung melalui jalur grid prediktor. Terdapat 30 dari 2.978 titik positif dengan fitur slope ≥5°; nilai pada jalur filter belum tersedia sehingga penyebabnya belum ditetapkan.”

## 4. Tahap 2 — AOI dan mask raster

### 4.1 Asal AOI teridentifikasi; geometri independen BLOCKED

Cell 16 memilih `FAO/GAUL/2015/level2`, ADM0 Indonesia, ADM2 `Kota Semarang` dan `Demak`, dengan fallback `Semarang` dan `Demak`, lalu `.geometry()`. Cache cell 16 mencetak `['Demak', 'Kota Semarang']` tanpa pesan fallback: ini membuktikan cabang utama pada eksekusi cache, bukan geometri setiap ekspor. Konfigurasi aktif `ROI_MODE='SEMDEMAK_ONLY'`; rectangle konfigurasi alternatif **bukan** poligon AOI aktual dan tidak digunakan sebagai pengganti.

Pencarian mencakup jalur vektor, isi ZIP, kandidat geometri tertanam dalam JSON/notebook, dan metadata skema 12 Parquet. Tidak ditemukan poligon AOI independen yang dapat dipakai overlay. Nama sumber dan kode seleksi tidak menggantikan geometri/identitas fitur aktual pada run beku. Bukti pencarian tersedia dalam CSV `mask/*geometry*`, [roi_branch_provenance.csv](mask/roi_branch_provenance.csv), dan [laporan mask](mask/findings.md).

Dengan demikian: **jumlah piksel di luar AOI = tidak diketahui, bukan nol**. Validitas geografis batas, luas geodesik AOI, serta efek batas terhadap luas/agreement belum dapat dihitung. Tidak dibuat geometri perkiraan atau poligon dari mask raster.

### 4.2 Grid dan domain tersimpan — VERIFIED

Semua 13 raster aktif memiliki:

- CRS **EPSG:32749**, ukuran **2.074 × 1.592**, piksel **30 × 30 m**;
- affine enam komponen **[30, 0, 419280, 0, -30, 9258540]**;
- batas **[419280, 9210780, 481500, 9258540]**, NoData **−9999**.

| Domain kelas/probabilitas | Piksel valid | Luas planar |
|---|---:|---:|
| SRTM | 1.444.085 | 1.299,6765 km² |
| GLO-30 | 1.444.085 | 1.299,6765 km² |
| AW3D30 | 1.429.582 | 1.286,6238 km² |

AW3D30 memiliki **14.503 piksel / 13,0527 km²** lebih sedikit. Kesamaan CRS/grid **tidak berarti** kesamaan mask atau denominator. Kekurangan cakupan ini tidak boleh ditafsirkan sebagai perubahan kelas oleh model pada seluruh wilayah.

Mask pascaproses dibangun dari domain valid risk-class yang telah tersedia. Kecocokan mask antarraster merupakan pemeriksaan internal yang melingkar bila dipakai untuk membuktikan batas AOI; ia bukan pembandingan geografis independen.

Pada overlap aktif–backup, semua nilai piksel valid sama. Sembilan raster non-label kehilangan 1.848.071 piksel valid backup; proxy label kehilangan 1.857.723. Ini mengukur **dampak pemangkasan domain tersimpan**, bukan luas yang terbukti berada di luar AOI. Inventaris 36 GeoTIFF dan efek backup: [raster_inventory.csv](mask/raster_inventory.csv), [mask_effect_backup.csv](mask/mask_effect_backup.csv).

## 5. Tahap 3A — Luas, agreement, transisi

### 5.1 Rekonstruksi lokal — VERIFIED pada domain yang dinyatakan

Kelas: 1–5, ambang probability beku **0,2; 0,4; 0,6; 0,8**, dengan batas atas inklusif menurut cell 49. Luas memakai raster kelas tersimpan dan `jumlah piksel × 900 m²`, bukan re-klasifikasi probability float yang dapat berbeda pada ambang.

| DEM | Kelas 1 | Kelas 2 | Kelas 3 | Kelas 4 | Kelas 5 |
|---|---:|---:|---:|---:|---:|
| SRTM, km² | 756,7632 | 232,9821 | 113,9751 | 95,3127 | 100,6434 |
| GLO-30, km² | 822,5379 | 189,8685 | 98,4150 | 79,2810 | 109,5741 |
| AW3D30, km² | 772,3755 | 222,0534 | 108,1035 | 88,1253 | 95,9661 |

Luas menggunakan domain tiap DEM; transisi menggunakan **irisan valid pasangan**. Agreement = diagonal matriks / seluruh piksel pada irisan tersebut. Transisi berarti perpindahan kelas **antarproduk DEM**, bukan perubahan temporal banjir.

| Pasangan | Denominator lokal | Diagonal lokal | Agreement lokal | Total matriks GEE beku |
|---|---:|---:|---:|---:|
| SRTM → GLO-30 | 1.444.085 | 1.146.218 | 79,3733% | 1.464.458 |
| SRTM → AW3D30 | 1.429.582 | 1.204.815 | 84,2774% | 1.449.760 |
| GLO-30 → AW3D30 | 1.429.582 | 1.165.421 | 81,5218% | 1.449.763 |

Matriks lengkap 5×5, proporsi seluruh domain, dan persentase **bersyarat baris asal**: [agreement_transition_local.csv](mask/agreement_transition_local.csv). Jangan menyamakan persentase baris dengan persentase AOI.

Raster agreement tersimpan berbeda maksimum **satu piksel pada dua pasangan** dari kesamaan kelas yang dihitung langsung; dampak <0,0001 poin persentase. Jadi konsistensi mendekati identik, bukan identik sempurna. Kedua mismatch terjadi pada baris/kolom 0-based (525,1332), pusat UTM (459255,9242775): kelas SRTM/GLO-30 sama-sama 4 tetapi agreement tersimpan 0; kelas SRTM/AW3D30 adalah 4/3 tetapi agreement tersimpan 1. Penyebabnya belum terbukti; lihat [agreement_pixel_mismatches.csv](mask/agreement_pixel_mismatches.csv). Ketidaksamaan diskret ini perlu dicatat/ditelusuri bila konsistensi bit-exact dijadikan kriteria penerimaan; tidak memerlukan pelatihan ulang untuk diagnosis.

### 5.2 GEE versus lokal — beda estimand terkonfirmasi, sebab selisih lengkap BLOCKED

Fakta kode dan kontrak API:

1. **Luas GEE** (cell 54) memakai `pixelArea().addBands(risk_class)` dan reducer sum/group dalam ROI, hanya `scale=30`, tanpa `crs/crsTransform`. Band pertama pixelArea secara default berproyeksi WGS84; ini tidak menetapkan grid UTM ekspor. Luas lokal adalah luas planar piksel valid utuh.
2. **Agreement GEE** (cell 53) memakai mean berbobot dalam ROI. Bobot reduksi melibatkan mask serta fraksi piksel yang tertutup ROI; berbeda dari mean semua sel valid utuh di GeoTIFF.
3. **Transisi GEE** memakai `frequencyHistogram`, yang menurut API merupakan histogram **berbobot**, lalu `int(v)`. Konversi ini dapat membuang pecahan. CSV integer tidak menyimpan bobot asli. Potensi kehilangan karena truncation <25 unit per matriks 5×5, sehingga konversi ini sendiri **tidak menjelaskan** kelebihan sekitar 20 ribu pada total GEE.
4. Tanpa CRS eksplisit, reduceRegion memakai proyeksi band pertama. Stack prediktor dideklarasikan UTM, tetapi proyeksi aktual citra hasil klasifikasi/expression untuk setiap reduksi tidak tersimpan. Jangan menyatakan semua reduksi GEE pasti ber-CRS berbeda ataupun pasti ber-CRS sama dengan GeoTIFF.

Rujukan kontrak resmi dan batas penggunaannya: [EXTERNAL_REFERENCES.md](EXTERNAL_REFERENCES.md).

**Luas:** selisih per kelas GEE–lokal maksimum **0,144461 km²**; maksimum relatif **0,0963%**. **ACCEPTABLE DIFFERENCE untuk pelaporan estimator terpisah**, bukan pembuktian bahwa semua selisih berasal dari satu faktor atau mask AOI benar. Tidak ada toleransi ilmiah universal yang ditetapkan hanya karena selisih kecil.

**Agreement:** GEE summary sekitar 79,3582%; 84,2697%; 81,5161%, dekat dengan lokal tetapi bukan angka pada domain/prosedur identik. Agreement dari diagonal histogram GEE sedikit berbeda lagi akibat definisi/representasi histogram; jangan mengganti summary dengan diagonal tanpa penjelasan.

**Transisi:** total GEE lebih besar **20.178–20.373 unit, sekitar 1,411%**. **FIX REQUIRED** bila disebut jumlah piksel dari raster final atau dipakai dengan denominator lokal. Penyebab numerik lengkap **BLOCKED** sampai geometri, proyeksi/transformasi reduksi, mask, dan hasil berbobot mentah tersedia. Selisih grid/domain masuk akal, tetapi belum diisolasi melalui evaluasi identik. Angka yang dekat pada rasio tidak membuktikan domain identik.

**Dampak kesimpulan:** pola agreement sekitar 79–84% tetap didukung raster lokal. Luas kelas ekstrem serta perbedaan cakupan perlu dibaca pada domain yang dinyatakan; audit belum mengesahkan seluruh wilayah administratif.

## 6. Tahap 3B — Moran dan block bootstrap

### 6.1 Moran OOF — VERIFIED

Rekonstruksi memakai satu prediksi OOF per **5.956 titik**, bukan probabilitas peta GEE. Alignment label/blok/fold terhadap CSV titik diperiksa. Koordinat diproyeksikan ke UTM 49S; graf kNN **terarah, tidak disimetriskan**, tanpa self-neighbor, bobot row-standardized 1/k. K utama 8; sensitivitas 5 dan 12.

Seluruh **21/21 kombinasi** (label, tiga probability OOF, tiga residual, masing-masing pada tiga k) mereproduksi I dan p tersimpan pada presisi CSV. Permutasi mengacak nilai dengan graf tetap, RandomState(42), **9.999** ulangan.

| k=8 | SRTM | GLO-30 | AW3D30 |
|---|---:|---:|---:|
| I probabilitas OOF | 0,886300 | 0,877050 | 0,882083 |
| I residual OOF | 0,377084 | 0,354520 | 0,364131 |

I label = 0,676922. P dua sisi = **0,0001**, batas resolusi permutasi, bukan nol. Sebanyak 4,4178% sisi kNN melintasi fold; angka ini bukan estimator kebocoran atau bukti independensi spasial. Autokorelasi residual tetap ada. Lihat [moran_oof_recomputed.csv](statistics/moran_oof_recomputed.csv).

### 6.2 Moran raster — FIX REQUIRED untuk konsistensi AW3D30

Domain: raster probability aktif, bobot queen 8 tetangga valid, row-standardized. Implementasi canon mengeluarkan piksel valid tanpa tetangga. **Bukan** graf titik OOF, bukan variabel residual, dan bukan domain cache pramask.

| DEM | n sesuai kode | I hasil ulang | I tersimpan |
|---|---:|---:|---:|
| SRTM | 1.444.085 | 0,9577138906 | 0,9577138908 |
| GLO-30 | 1.444.085 | 0,9530758014 | 0,9530758017 |
| AW3D30 | **1.429.580** | **0,9544217226** | **0,9544153895**; n=1.429.582 |

SRTM/GLO-30 cocok dalam <3×10⁻¹⁰. AW3D30 memiliki **dua piksel terisolasi**: baris/kolom 0-based (473,994) dan (710,829), pusat UTM (449115,9244335) dan (444165,9237225). Kedua piksel masuk denominator hasil tersimpan, sementara kode sekarang mengeluarkannya. Versi perhitungan yang mempertahankan semua piksel valid mereproduksi I tersimpan pada enam desimal; ini mengidentifikasi **ketidakselarasan definisi island/denominator**, bukan bukti tanggal/versi historis pembuat CSV.

Pemeriksaan independen float64 dengan konvolusi SciPy juga memberi I AW3D30 **0,9544217225**, n=1.429.580: [independent_raster_moran_check.csv](independent_raster_moran_check.csv), [isolated_raster_pixels.csv](isolated_raster_pixels.csv).

Dampak selisih sekitar **0,000006333** kecil; pembulatan tiga desimal dan kesimpulan autokorelasi peta sangat kuat tidak berubah. Namun prosedur yang diklaim dan output harus diselaraskan. Usulan setelah persetujuan: hitung ulang diagnostik Moran AW3D30 beserta inferensi yang bergantung pada domain, atau dokumentasikan secara tepat kebijakan island dan normalisasinya. Tidak perlu melatih model ulang.

**Batas verifikasi:** p peta tersimpan 0,001 berasal dari 999 permutasi. T16 menghitung ulang I deterministik, **tidak** mengulang 999 permutasi pada >1,4 juta piksel. P peta belum diverifikasi ulang; jangan menyebutnya hasil uji baru T16. Ini pembatasan komputasi audit, bukan klaim bahwa data raster tidak tersedia.

Cache cell 64 memakai domain pramask: n≈3,29 juta dan I≈0,9701 / 0,9648 / 0,9673. Rekonstruksi dari backup mereproduksi angka tercetak itu. Perbedaannya terhadap pascamask **ACCEPTABLE DIFFERENCE sebagai statistik domain berbeda**, bukan satu hasil yang dapat dipertukarkan. Pemangkasan domain mengubah I sekitar 0,012–0,013 tanpa mengubah nilai pada overlap.

### 6.3 Block bootstrap — VERIFIED, dengan batas inferensi

Unit resampling adalah **16 blok kuantil lon/lat** dari rancangan tersimpan; 16 ID blok diambil dengan pengembalian per draw, seluruh baris blok ikut termasuk duplikasi. Prediksi OOF tetap; draw berpasangan antar-DEM; **1.000 iterasi**, RandomState(42), CI persentil 2,5–97,5%, SD ddof=1.

| ΔAUC | Rerata | CI 95% |
|---|---:|---:|
| SRTM − GLO-30 | −0,015460307 | [−0,024967700; −0,007199263] |
| SRTM − AW3D30 | −0,004669962 | [−0,009558602; 0,001279257] |
| GLO-30 − AW3D30 | 0,010790344 | [0,004139837; 0,019759753] |

Kedua salinan prediksi menghasilkan statistik tersimpan yang sama. CI SRTM–AW3D30 meliputi nol. Ini ketidakpastian **bersyarat pada prediksi, label, fold, dan 16 blok beku**; bukan bootstrap dengan refit model, bukan pengulangan CV, dan bukan validasi terhadap label banjir independen. Lihat [block_bootstrap_recomputed.csv](statistics/block_bootstrap_recomputed.csv) dan [laporan statistik](statistics/findings.md).

## 7. Tahap 4 — Keputusan dan rekomendasi per masalah

| Masalah | Status | Klasifikasi / akar sebab terbukti | Tindakan setelah izin dan dampak |
|---|---|---|---|
| 30 slope positif ≥5° | VERIFIED untuk fakta; BLOCKED untuk sebab | Keterbatasan data; jalur grid filter/prediktor berbeda, sebab per titik belum terbukti | Ekspor diagnostik terbatas dua slope dan mask pada koordinat sama. Jangan relabel, ubah ambang, atau rerun model dahulu |
| Mask terhadap AOI independen | BLOCKED | Poligon asli tidak tersedia; kesamaan mask turunan bersifat internal | Dapatkan geometri/identitas fitur run asli; overlay memakai affine aktif. Dampak geografis belum diketahui |
| Luas GEE–lokal | ACCEPTABLE DIFFERENCE dalam batas pelaporan terpisah | Estimator/grid yang didefinisikan kode berbeda; kontribusi setiap penyebab belum diisolasi | Nyatakan sumber dan definisi luas. Jika perlu angka identik, hitung ulang pada geometri/grid/mask/aturan bobot sama; bukan langsung mengganti angka |
| Transisi GEE disebut pixel count raster final | FIX REQUIRED; atribusi sebab BLOCKED | Domain/proyeksi reduksi belum ditetapkan identik; histogram berbobot di-cast integer | Pisahkan denominator dan versi; ekspor frekuensi mentah serta reduksi grid eksplisit. Tidak ada bukti perlu retraining |
| Agreement satu piksel tidak identik | FIX REQUIRED bila konsistensi bit-exact diklaim | Ketidaksetaraan artefak diskret terbukti; penyebab rinci belum terbukti | Lacak piksel terkait ke evaluasi GEE asli. Dampak <0,0001 pp; jangan mengklaim exact match |
| Moran OOF dan block bootstrap | VERIFIED | Implementasi tersimpan dapat direproduksi pada prediksi/domain beku | Pertahankan angka; batasi wording sesuai domain dan conditional uncertainty |
| Moran raster AW3D30 | FIX REQUIRED | Dua island masuk hasil tersimpan, tetapi dikeluarkan kode canon | Selaraskan kebijakan island dan diagnostik/p inferensinya; dampak I sangat kecil, bukan alasan retraining |
| Cache Moran pramask vs pascamask | ACCEPTABLE DIFFERENCE bila dipisahkan | Domain nyata berbeda, backup mereproduksi cache | Labeli cache historis, jangan menggunakannya sebagai hasil raster aktif |
| 10 hash manifest stale | FIX REQUIRED | Manifest menunjuk backup, export_status menunjuk aktif | Perbaiki metadata terversi/lineage pada tahap berizin; angka raster tidak perlu diubah |
| Salinan CSV hasil berbeda | FIX REQUIRED untuk provenance yang ambigu | Basename sama bukan versi sama | Cantumkan path/hash/versi sumber per tabel; audit ini tidak menimpa sumber mana pun |

**Wording lintas statistik yang direkomendasikan:** “Statistik GEE dan raster lokal disajikan menurut domain, grid, mask, dan definisi masing-masing. Kesamaan numerik yang dekat tidak dianggap identitas prosedur. Validasi geografis AOI dan penyebab perbedaan slope masih memerlukan artefak sumber tambahan.”

## 8. Bukti minimum untuk membuka BLOCKED

1. **Slope:** ekspor 30 lokasi beku, nilai slope label tepat sebelum filter, nilai slope fitur, label sebelum/sesudah connected-component filter, mask tiap tahap, proyeksi lengkap (CRS + affine), scale, aturan sampling/reproyeksi, versi/waktu aset. Gunakan locator T16 dan koordinat sumber; jangan mengambil ulang sampel acak.
2. **AOI:** geometri asli hasil seleksi GAUL pada run yang menghasilkan artefak, identitas fitur ADM2, cabang seleksi yang benar-benar dipakai, CRS dan hash file. Jangan mengganti dengan rectangle, convex hull titik, atau polygonisasi mask.
3. **GEE–lokal:** proyeksi/transformasi aktual citra probability, risk-class, pixelArea dan mask sebelum setiap reduceRegion; histogram berbobot **tanpa int()**, kebijakan bobot/batas ROI, dan diagnostik pada grid/mask ekspor yang sama. Pisahkan reproduksi prosedur lama dari usulan prosedur baru.
4. **Moran:** putuskan kebijakan island, lalu bila diperlukan reproduksi 999 permutasi peta dengan domain, seed, RNG, dtype, serta versi implementasi terdokumentasi. Tidak perlu pelatihan ulang.

Ini adalah permintaan artefak/diagnostik terbatas untuk tahap berikutnya, **bukan** eksekusi eksperimen tambahan yang sudah dilakukan atau persetujuan untuk mengubah hasil beku.

## 9. Reproduksi dan integritas

Petunjuk perintah, dependensi, dan cakupan komputasi ada pada [README.md](README.md). Hasil OOF dan bootstrap cocok meskipun lingkungan audit berbeda dari lingkungan historis; versi lengkap dicatat pada `diagnostic-requirements.txt` dan `statistics/runtime_versions.csv`.

Verifikasi akhir: **388/388 SHA-256 sumber tidak berubah**, termasuk proposal, PDF, notebook, data, raster, dan snapshot T15; lihat [source_integrity_check.csv](source_integrity_check.csv). Perubahan repositori dibatasi ke direktori T16. Tidak ada klaim verifikasi AOI independen atau nilai slope filter yang tidak didukung data.
