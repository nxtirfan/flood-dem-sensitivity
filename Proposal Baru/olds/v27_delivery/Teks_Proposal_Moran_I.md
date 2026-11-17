# Teks proposal: Autokorelasi Spasial, Spatial Leakage, dan Global Moran's I

Status teks: bagian A, C, dan D adalah teks metodologi dan batasan yang siap tempel. Bagian B (Hasil dan Pembahasan) hanya memuat angka yang benar-benar sudah dihitung di sesi ini dari artefak v26. Angka yang belum ada ditandai **[BELUM DIVERIFIKASI]**. Penyempurnaan bahasa lanjutan sebaiknya tidak mengubah angka maupun tafsir di bagian B.

---

## A. Tambahan untuk bab Metodologi (siap tempel)

### Autokorelasi spasial dan spatial leakage

Data kejadian banjir bersifat spasial, sehingga nilai pada lokasi yang berdekatan cenderung lebih mirip daripada nilai pada lokasi yang berjauhan. Gejala ini disebut autokorelasi spasial. Pada penelitian ini sumbernya jelas, sebab elevasi, kemiringan lereng, jarak ke sungai, dan genangan berubah secara kontinu di ruang. Akibatnya amatan tidak saling bebas, dan pembagian data latih dan uji secara acak membuat titik uji hampir selalu memiliki tetangga dekat di data latih.

Kondisi tersebut melahirkan spatial leakage, yaitu bocornya informasi lingkungan lokasi uji ke dalam proses pelatihan. Model dapat tampak akurat karena mengenali lingkungan sekitar titik uji, bukan karena mempelajari hubungan antara prediktor dan banjir yang dapat digeneralisasi ke wilayah baru. Karena itu penelitian ini memakai spatial cross-validation dengan 16 blok kuantil koordinat yang dibagi ke dalam empat fold. Pada setiap fold, model dilatih ulang tanpa blok uji, sehingga probabilitas out-of-fold (OOF) pada tiap titik berasal dari model yang tidak pernah melihat blok titik tersebut. Fungsi spatial cross-validation adalah mengurangi leakage melalui rancangan pembagian data. Rancangan ini belum sempurna karena blok yang bersebelahan tidak dipisahkan zona penyangga, sehingga titik di tepi blok tetap dapat berdekatan dengan data latih.

### Global Moran's I sebagai analisis diagnostik pendukung

Global Moran's I dipakai untuk menggambarkan seberapa kuat suatu variabel mengelompok secara spasial. Untuk nilai $x_i$ pada $n$ lokasi, bobot spasial $w_{ij}$ yang distandardisasi per baris sehingga $S_0=\sum_{i}\sum_{j}w_{ij}=n$, dan $z_i=x_i-\bar{x}$, statistiknya adalah

$$I=\frac{n}{S_0}\,\frac{\sum_{i}\sum_{j}w_{ij}\,z_i\,z_j}{\sum_{i}z_i^{2}},\qquad E[I]=-\frac{1}{n-1}.$$

Nilai $I$ di atas $E[I]$ menunjukkan pengelompokan nilai yang mirip, nilai di bawah $E[I]$ menunjukkan pola berselang-seling.

Pengujian dirumuskan sebagai berikut.

* $H_0$: nilai tersebar acak secara spasial (tidak ada autokorelasi spasial).
* $H_1$: terdapat autokorelasi spasial (uji dua sisi).
* Taraf signifikansi $\alpha=0{,}05$.
* Kriteria penolakan: tolak $H_0$ jika $p$-value lebih kecil dari $\alpha$.
* $p$-value dihitung dengan permutasi kondisional. Nilai $x_i$ diacak lintas lokasi yang tetap sebanyak $B=9.999$ kali (seed 42), lalu
$$p=\frac{1+\#\{|I_{perm}-E[I]|\ge |I_{obs}-E[I]|\}}{B+1}.$$
Dengan $B=9.999$, $p$ terkecil yang dapat dilaporkan adalah $1/(B+1)=0{,}0001$. Untuk peta raster dipakai $B=999$ karena jumlah pikselnya sangat besar.

Dua kelompok data dianalisis.

1. **Probabilitas OOF dan residual OOF pada titik sampel.** Probabilitas $\hat{p}_i^{OOF}$ berasal dari spatial cross-validation evaluasi utama, dan residual dihitung sebagai $r_i=y_i-\hat{p}_i^{OOF}$ dengan $y_i$ label aktual. Prediksi data latih tidak dipakai karena sudah dilihat model dan akan membuat residual tampak lebih kecil dan lebih acak dari yang sebenarnya.
2. **Peta probabilitas kerawanan per DEM** (raster hasil Random Forest GEE 300 pohon). Peta dilatih pada seluruh sampel, sehingga analisis ini menggambarkan struktur spasial permukaan prediksi dan bukan kinerja out-of-fold.

Unit analisis adalah titik sampel, bukan 16 blok. Agregasi ke 16 unit tidak layak karena blok kuantil sangat tidak seimbang (satu blok hanya memuat 1 titik, median 305 titik, maksimum 967 titik, dan ada blok tanpa salah satu kelas). Selain itu, 16 unit memberi daya uji yang sangat rendah, menimbulkan masalah modifiable areal unit (hasil bergantung pada cara batas blok ditarik), dan menghapus struktur di dalam blok, padahal blok adalah satuan pembagian fold.

Bobot spasial untuk titik adalah $k$ tetangga terdekat ($k=8$) dengan jarak dihitung dalam meter pada UTM zona 49S dan distandardisasi per baris. Pilihan ini sesuai karena titik sampel tersebar tidak beraturan dengan kepadatan yang sangat bervariasi (jarak tetangga terdekat bermedian sekitar 149 m dan mencapai 1,5 km), sehingga ambang jarak tetap akan menyisakan titik tanpa tetangga di area jarang dan terlalu banyak tetangga di area padat. Metode kNN menjamin setiap titik memiliki jumlah tetangga yang sama. Uji kepekaan memakai $k=5$ dan $k=12$. Definisi bobot dibangun sekali dari koordinat dan dipakai identik untuk ketiga DEM, dengan deret permutasi yang sama, sehingga perbandingan antar-DEM adil. Untuk raster dipakai kontigu queen (8 tetangga) yang distandardisasi per baris pada grid yang sama untuk ketiga DEM.

### Batas interpretasi

Moran's I adalah analisis diagnostik pendukung. Statistik ini menggambarkan struktur spasial probabilitas dan galat, tetapi tidak menghilangkan spatial leakage dan tidak membuktikan ketiadaannya. Pencegahan leakage tetap bergantung pada rancangan evaluasi spasial. Hasil yang tidak signifikan tidak dibaca sebagai bukti tidak adanya autokorelasi, karena dapat disebabkan oleh daya uji, pilihan bobot spasial, atau asumsi keterpertukaran pada uji permutasi. Perbedaan nilai $I$ antar-DEM tidak diuji secara inferensial pada tahap ini.

---

## B. Draft Hasil dan Pembahasan (angka sudah dihitung, sumber dan status dicantumkan)

**Sumber angka:** dihitung dengan kode notebook v27 dari artefak run v26 (`training_sample_features.csv` dan `spatial_cv_test_predictions.csv`, run Kaggle). Pemetaan OOF ke koordinat diverifikasi: label dan blok seluruh titik uji cocok dan setiap titik tepat satu kali berada di fold uji. **Status: belum diulang pada dataset beku v27 dari GEE.** Nilai pada dataset beku baru dapat sedikit berbeda.

Tabel. Global Moran's I pada titik sampel ($n=5.956$, kNN $k=8$, $B=9.999$, $E[I]=-0{,}0002$).

| Variabel | DEM | $I$ | $z$ permutasi | $p$ dua sisi |
|---|---|---|---|---|
| Label banjir (acuan) | | 0,677 | 109,7 | 0,0001 |
| Probabilitas OOF | SRTM | 0,886 | 143,6 | 0,0001 |
| Probabilitas OOF | GLO-30 | 0,877 | 142,9 | 0,0001 |
| Probabilitas OOF | AW3D30 | 0,882 | 142,9 | 0,0001 |
| Residual OOF | SRTM | 0,377 | 61,4 | 0,0001 |
| Residual OOF | GLO-30 | 0,355 | 57,9 | 0,0001 |
| Residual OOF | AW3D30 | 0,364 | 59,1 | 0,0001 |

Nilai $p=0{,}0001$ adalah batas resolusi uji permutasi (tidak ada permutasi yang lebih ekstrem dari nilai amatan), bukan nilai $p$ yang tepat.

Peta probabilitas per DEM: **[BELUM DIVERIFIKASI]**. Raster belum dihasilkan karena mode PREPARE_MAPS belum dijalankan. Tidak ada angka yang dilaporkan untuk bagian ini.

**Teks pembahasan (siap tempel, mengikuti angka di atas):**

Probabilitas OOF pada ketiga DEM memiliki Moran's I yang tinggi (0,877 sampai 0,886) dan signifikan pada $\alpha=0{,}05$ ($p<\alpha$, tolak $H_0$). Hasil ini wajar karena probabilitas dihasilkan dari prediktor yang berubah halus di ruang, dan menunjukkan bahwa peta kerawanan yang dihasilkan membentuk kelompok spasial yang koheren, bukan pola acak.

Informasi yang lebih relevan bagi evaluasi model ada pada residual OOF. Moran's I residual bernilai positif dan signifikan pada ketiga DEM (0,355 sampai 0,377), sehingga $H_0$ ditolak. Artinya galat prediksi pada lokasi yang berdekatan cenderung searah, dan masih ada struktur spasial yang tidak ditangkap model, misalnya akibat proses hidrologi lokal yang tidak diwakili prediktor. Sebagai pembanding, label banjir sendiri memiliki Moran's I 0,677, sehingga autokorelasi residual kira-kira separuh dari autokorelasi label (sekitar 52 persen sampai 56 persen), yang berarti model menyerap sebagian, tetapi tidak seluruh, struktur spasial tersebut. Implikasi praktisnya adalah bahwa amatan galat tidak independen, sehingga selang kepercayaan yang mengandalkan resampling titik secara bebas cenderung terlalu sempit. Temuan ini mendukung pemakaian block bootstrap pada perbandingan AUC antar-DEM.

Di antara ketiga DEM, residual GLO-30 memiliki Moran's I terendah (0,355), disusul AW3D30 (0,364) dan SRTM (0,377). Urutan ini sama pada $k=5$ dan $k=12$, dan sejalan dengan urutan AUC. Namun selisihnya kecil, tidak diuji secara inferensial, dan nilai $I$ turun bersama kenaikan $k$ pada ketiganya, sehingga urutan ini hanya dibaca sebagai konsistensi arah, bukan bukti keunggulan satu DEM.

Hasil ini tidak boleh dibaca sebagai bukti bahwa spatial cross-validation bebas dari leakage atau sebaliknya. Sekitar 4,4 persen pasangan tetangga ($k=8$) berada pada fold yang berbeda. Angka ini deskriptif dan tidak menyatakan besar leakage. Probabilitas OOF tiap fold juga berasal dari model yang berbeda, sehingga diskontinuitas di batas fold dapat ikut memengaruhi nilai $I$.

Kepekaan terhadap bobot spasial (Moran's I pada $k=5$ dan $k=12$):

| Variabel | DEM | $k=5$ | $k=8$ | $k=12$ |
|---|---|---|---|---|
| Residual OOF | SRTM | 0,418 | 0,377 | 0,345 |
| Residual OOF | GLO-30 | 0,393 | 0,355 | 0,326 |
| Residual OOF | AW3D30 | 0,405 | 0,364 | 0,334 |

---

## C. Tambahan untuk bagian Batasan Penelitian (siap tempel)

* Spatial cross-validation memakai 16 blok bersebelahan tanpa zona penyangga, sehingga titik di tepi blok dapat berdekatan dengan data latih. Leakage berkurang tetapi tidak dapat dinyatakan hilang.
* Global Moran's I adalah analisis diagnostik. Hasilnya tidak membuktikan ada atau tidaknya spatial leakage, dan hasil yang tidak signifikan tidak menunjukkan ketiadaan autokorelasi.
* Nilai Moran's I bergantung pada definisi bobot spasial. Uji kepekaan dilakukan untuk $k=5$, 8, dan 12, tetapi definisi lain (misalnya pita jarak) tidak diuji.
* Probabilitas OOF tiap fold berasal dari model berbeda, dan analisis dilakukan pada evaluasi utama saja. Moran's I belum dihitung pada dataset multi-seed.
* Uji permutasi mengasumsikan keterpertukaran nilai di bawah $H_0$, yang dapat dilanggar oleh residual yang heteroskedastis.
* Perbedaan Moran's I antar-DEM tidak diuji secara inferensial.

## D. Revisi kalimat pada bagian lain

| Jika naskah menyatakan | Revisi yang disarankan |
|---|---|
| Spatial CV mengatasi atau menghilangkan leakage | Spatial CV mengurangi risiko leakage melalui pemisahan blok uji dari blok latih. |
| Moran's I membuktikan model bebas autokorelasi atau bebas leakage | Moran's I dipakai sebagai diagnostik struktur spasial probabilitas dan residual, bukan sebagai bukti ketiadaan leakage. |
| Residual tidak signifikan berarti tidak ada autokorelasi | Hasil tidak signifikan tidak cukup untuk menyimpulkan tidak ada autokorelasi. |
| Hasil bootstrap titik biasa | Gunakan block bootstrap sebagai analisis utama, dengan autokorelasi residual (Moran's I positif) sebagai salah satu justifikasi. |
