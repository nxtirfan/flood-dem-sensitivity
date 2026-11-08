# T15 — Finalisasi terarah A–E: revisi terbatas, status belum final

**Tanggal:** 8 November 2026. **Dasar:** `305128e` (merge PR #1; T12–T14).
**Ruang lingkup:** hanya permintaan pengguna A–G. Tidak ada rewrite menyeluruh, perubahan bab, referensi baru, perubahan data/model, atau eksperimen ulang.

## Putusan

**Dokumen belum dapat dinyatakan final secara metodologis.** Revisi yang didukung bukti telah diterapkan, tetapi penyebab konflik slope <5° versus 11,48° belum terbukti dan mask geografis AOI belum dapat diverifikasi independen. Angka luas/agreement reduksi GEE dan raster lokal tidak identik; sumbernya kini dinyatakan terpisah, tidak dicampurkan.

## Ringkasan sebelum edit (disampaikan di chat sebelum perubahan)

| Poin | Status awal | Temuan |
|---|---|---|
| A | Perlu revisi | Ada “bootstrap blok”, “bootstrap pada tingkat blok”, dan bentuk terformat terpisah. Istilah metode diseragamkan menjadi block bootstrap. |
| B | Perlu revisi | Simpulan membatasi perubahan peta pada kelas sangat tinggi, padahal kelas sangat rendah juga berubah. Residual OOF positif sudah diakui, tetapi keterbatasan evaluasi perlu ditegaskan. |
| C | Terverifikasi sebagian / belum dapat dipastikan | CSV Moran pasca-mask dan raster cocok n/hash/grid; tabel area/agreement GEE berbeda sedikit dari hitungan raster lokal. Output notebook tersimpan masih pra-mask. Tidak ada geometri AOI lokal yang dapat dipakai sebagai acuan independen. |
| D | Belum dapat dipastikan penyebabnya | Maksimum 11,483837° dan 30 titik ≥5° terkonfirmasi pada data beku; beda jalur grid filter/prediktor terkonfirmasi, tetapi hubungan sebabnya belum terbukti. |
| E | Perlu revisi terbatas | Implikasi mitigasi perlu dibatasi pada potensi identifikasi/prioritas wilayah. Framing sensitivitas, proxy, dan bukan DEM terbaik universal sudah sesuai. |

## 1. Perubahan dan lokasi

Halaman berikut adalah **halaman tercetak**, dengan urutan fisik PDF dalam kurung. Naskah hasil revisi 51 halaman; nomor halaman telah dicek pada PDF hasil build, bukan disalin dari PDF lama.

| Poin | Lokasi | Tindakan |
|---|---|---|
| A | 3.7 hlm. 19–20 (23–24), 3.8 hlm. 20–21 (24–25), 3.9.1 hlm. 23 (27), 5.1 hlm. 43–44 (47–48) | block bootstrap dipakai konsisten, termasuk penyebutan pertama. Bootstrap untuk bagging RF dan bootstrap tingkat piksel tidak diganti karena berbeda konsep. Tidak ditemukan variasi tersisa pada metode yang sama di tabel/caption. |
| B | 5.1 hlm. 43–44 (47–48) | Sebut agreement 79,4–84,3%, perubahan kelas ekstrem, dan autokorelasi residual yang masih tersisa. |
| C | 4.5 hlm. 34 (38); 4.7.2 hlm. 37–38 (41–42) | Pisahkan domain statistik GEE dan raster lokal; jelaskan asal CSV Moran pasca-mask, cache notebook pra-mask, grid, NoData, serta batas verifikasi AOI. Angka tabel hasil tidak diganti. |
| D | 4.2 hlm. 29 (33) | Ganti kesan bahwa statistik slope sepenuhnya sejalan dengan filter menjadi catatan konflik, jalur pemrosesan berbeda, dan kebutuhan konfirmasi. |
| E | 1.4 hlm. 4 (8) | Batasi implikasi pada potensi pengaruh peta terhadap identifikasi/prioritas untuk kajian mitigasi, bukan perubahan keputusan yang telah dibuktikan. |

## 2. Sebelum–sesudah tiap perubahan penting

Kutipan mempertahankan notasi LaTeX sumber. Penambahan angka 79,4–84,3% pada simpulan mengulang tabel aktif; angka 30 titik berasal dari pemeriksaan statis CSV beku, bukan eksperimen baru.

### A-first — 3.7, hlm. 19–20 (PDF 23–24)

**Sebelum:**

> validasi silang spasial dan bootstrap blok pada Subbab~3.8.

**Sesudah:**

> validasi silang spasial dan \textit{block bootstrap} pada Subbab~3.8.

### A-method — 3.8, hlm. 20–21 (PDF 24–25)

**Sebelum:**

> \item \textbf{bootstrap blok}:

**Sesudah:**

> \item \textbf{block bootstrap}:

### A-sensitivity — 3.9.1, hlm. 23 (PDF 27)

**Sebelum:**

> \textit{bootstrap} blok pada Subbab~3.8

**Sesudah:**

> \textit{block bootstrap} pada Subbab~3.8

### B-map-conclusion — 5.1 butir 2, hlm. 43 (PDF 47)

**Sebelum:**

> pergantian sumber elevasi dalam kerangka eksperimen terkontrol. Pola spasial
> ketiganya serupa dengan variasi terbatas pada kelas risiko sangat tinggi
> (Subbab~4.3 dan Subbab~4.5).

**Sesudah:**

> pergantian sumber elevasi dalam kerangka eksperimen terkontrol. Ketiga peta
> menunjukkan tingkat kesesuaian kelas sebesar 79,4\% hingga 84,3\%.
> Meskipun sebagian besar piksel memiliki kelas kerawanan yang sama,
> pergantian sumber elevasi tetap menghasilkan perubahan distribusi spasial,
> terutama pada kelas kerawanan ekstrem, yaitu sangat rendah dan sangat tinggi
> (Subbab~4.3 dan Subbab~4.5).

### B-spatial-conclusion — 5.1 butir 3, hlm. 43–44 (PDF 47–48)

**Sebelum:**

> sehingga peringkat keduanya belum dapat dipisahkan. Autokorelasi spasial
> diperhitungkan melalui validasi silang spasial dan \textit{bootstrap} pada
> tingkat blok (Subbab~3.8). Diagnostik autokorelasi spasial menguatkan rancangan
> tersebut: Moran's I residual OOF bernilai positif dan signifikan pada ketiga
> DEM (0,355 sampai 0,377), sehingga amatan galat tidak bebas antarlokasi dan
> \textit{block bootstrap} tetap menjadi analisis utama perbandingan antarproduk.

**Sesudah:**

> sehingga peringkat keduanya belum dapat dipisahkan. Risiko ketergantungan
> spasial diperhatikan melalui validasi silang spasial dan \textit{block bootstrap}
> (Subbab~3.8). Namun, Moran's I residual OOF masih bernilai positif dan
> signifikan pada ketiga DEM (0,355 sampai 0,377). Dengan demikian, rancangan
> evaluasi ini belum dapat dianggap sepenuhnya menghilangkan ketergantungan
> spasial. Prosedur \textit{block bootstrap} tetap menjadi analisis utama perbandingan
> antarproduk.

### E-implications — 1.4, hlm. 4 (PDF 8)

**Sebelum:**

> Hal tersebut memiliki implikasi praktis yang langsung menyangkut pengambilan
> keputusan: peta \textit{flood susceptibility} merupakan dasar penentuan
> area prioritas mitigasi, sehingga pergantian sumber elevasi berpotensi
> mengubah daftar area yang ditandai berisiko tinggi. Hasil penelitian ini
> memberikan ukuran seberapa besar perubahan tersebut, serta menjadi
> pertimbangan pemilihan produk elevasi bagi praktisi yang bekerja dengan
> data terbuka \cite{fereshtehpour2024}.

**Sesudah:**

> Perbedaan peta \textit{flood susceptibility} berpotensi memengaruhi
> identifikasi wilayah kerawanan dan penentuan prioritas wilayah untuk kajian
> mitigasi lebih lanjut. Penelitian ini mengukur sensitivitas hasil pemetaan
> terhadap sumber elevasi, bukan membuktikan perubahan keputusan mitigasi.
> Hasilnya dapat menjadi bahan pertimbangan bagi praktisi yang bekerja dengan
> data terbuka \cite{fereshtehpour2024}.

### D-slope-confirmation — 4.2, hlm. 29 (PDF 33)

**Sebelum:**

> ketiga produk (98,99\%, 99,97\%, dan 98,76\%). Kondisi tersebut sejalan dengan
> kriteria penyaringan lereng di bawah $5^{\circ}$ yang digunakan untuk
> mengurangi kemungkinan masuknya piksel dengan karakteristik lereng yang
> berpotensi menghasilkan artefak pada inventori banjir, seperti artefak
> geometris radar pita-C (\textit{layover} dan \textit{foreshortening}) pada
> area berlereng curam di bagian selatan wilayah kajian, tanpa memangkas
> domain genangan di kawasan pesisir. Karena acuan penyaringan menggunakan
> lereng dari SRTM, label tidak sepenuhnya independen terhadap karakteristik
> salah satu produk perlakuan. Desain ini tetap diterapkan identik pada ketiga
> eksperimen, dan implikasinya dibahas pada Subbab~4.8.

**Sesudah:**

> ketiga produk (98,99\%, 99,97\%, dan 98,76\%). Namun, filter label SRTM
> $<5^{\circ}$ belum sepenuhnya konsisten dengan slope hasil ekstraksi.
> Pada sampel beku, 30 dari 2.978 titik berlabel banjir memiliki prediktor
> slope SRTM sedikitnya $5^{\circ}$, dengan maksimum $11{,}48^{\circ}$ tersebut.
> Filter label dihitung dari SRTM sebelum reproyeksi eksplisit, sedangkan slope
> prediktor dihitung setelah DEM direproyeksi ke EPSG:32749 pada resolusi 30~m.
> Kedua jalur memakai aset SRTM yang sama, tetapi nilai slope filter pada
> koordinat sampel dan mask perantara tidak tersedia untuk pemeriksaan
> berpasangan. Penyebab ketidaksesuaian ini belum dapat dipastikan dari
> artefak yang tersedia; perbedaan grid belum dapat dinyatakan sebagai
> penyebab yang terbukti. Konsistensi filter dan hasil ekstraksi masih
> memerlukan konfirmasi sebelum dokumen dinyatakan final. Karena acuan
> penyaringan memakai SRTM, label juga tidak sepenuhnya independen terhadap
> salah satu produk perlakuan, meskipun label diterapkan identik pada ketiga
> eksperimen (Subbab~4.8).

### C-server-domain — 4.5, hlm. 34 (PDF 38)

**Sebelum:**

> dipisahkan. Persentase dan luas dibaca menurut domain masing-masing tabel,
> bukan dengan mengasumsikan penyebut yang identik antaranalisis.

**Sesudah:**

> dipisahkan. Luas kelas dan persentase kesesuaian pada tabel Subbab~4.5
> merujuk pada reduksi GEE, bukan hitungan ulang raster lokal pasca-mask.
> Nilainya sedikit berbeda pada kedua sumber tersebut. Karena itu, domain
> masing-masing sumber harus dibedakan dan penyebut antaranalisis tidak
> diasumsikan identik.

### C-moran-provenance — 4.7.2, hlm. 37–38 (PDF 41–42)

**Sebelum:**

> Piksel valid tanpa tetangga valid tidak disertakan. Hasil disajikan pada
> Tabel~\ref{tab:moran-raster}.

**Sesudah:**

> Piksel valid tanpa tetangga valid tidak disertakan. Hasil disajikan pada
> Tabel~\ref{tab:moran-raster}. Angka ini merujuk pada CSV aktif pasca-perbaikan
> mask lokal T10, bukan output tersimpan notebook yang masih memuat hasil
> pra-mask. Ketiga raster memakai EPSG:32749, resolusi 30~m, dimensi
> $2074\times1592$, dan transformasi affine yang sama. Pemeriksaan raster
> menunjukkan kesamaan mask probabilitas dan kelas pada setiap DEM serta
> nilai NoData $-9999$ pada sel termask. Namun, mask tersebut belum dapat
> dicocokkan secara independen dengan batas geografis AOI karena geometri
> AOI tidak tersimpan dalam paket lokal. Ketepatan batas mask terhadap AOI
> masih memerlukan konfirmasi.

## 3. Verifikasi raster dan NoData

### Asal sumber, bukan hanya kecocokan angka

- Dataset aktif: `Proposal Baru/v27_delivery/Analisis Flood DEM Susceptibility/`.
- `data/export_status.json`: waktu pembaruan/masking lokal **2026-11-07T21:36:31Z**; `note_surgery` menyatakan mask diambil dari zona valid risk-class terkait dan diterapkan pada 13 raster. Ini **perbaikan lokal T10**, bukan bukti notebook dijalankan penuh ulang dengan hasil tersebut.
- Ketiga angka Moran di naskah cocok dengan `outputs/moran_prob_map_global.csv` pasca-mask. Cache notebook sel 64 (`5ce950024c7c`) masih mencatat pra-mask: 0,9701 / 0,9648 / 0,9673 dan n 3.292.156 / 3.292.156 / 3.277.652. Cache itu tidak dipakai sebagai hasil mutakhir.
- Area/agreement berasal dari `outputs/area_per_risk_class_km2.csv` dan `outputs/sensitivity_summary.csv`, masing-masing identik dengan salinan `data/gee_tables/`. Keduanya tabel reduksi GEE, bukan jumlah sel pada raster lokal pasca-mask. Tidak ada data lama v26 yang disubstitusikan ke hasil aktif.
- Seluruh **13 raster cocok SHA256** dengan manifest ekspor. Ke-13 file dibaca piksel/metadata secara read-only dengan rasterio; bukan hanya tag TIFF/hash. Moran tidak dihitung ulang, tidak ada permutasi/eksperimen ulang. Nilai I diverifikasi terhadap CSV dan provenance yang tersedia, bukan divalidasi ulang secara independen sebagai estimasi statistik.

### Grid dan alignment

Seluruh 13 raster memiliki satu kombinasi grid:
- CRS **EPSG:32749**.
- Resolusi **30 × 30 m**, dimensi **2074 × 1592**.
- Affine `(a,b,c,d,e,f) = (30, 0, 419280, 0, -30, 9258540)`.
- NoData **−9999**. Rotasi/skew nol; origin, dimensi, resolusi, transform, dan CRS identik. Ini membuktikan registrasi grid lokal sama, **bukan mask/cakupan valid antar-DEM identik**.

### Angka aktif dan pemeriksaan langsung

| DEM | n CSV Moran | Piksel valid raster aktual | Moran I CSV pasca-mask | Area kelas 5 CSV GEE (km²) | Naskah (km²) | Area kelas 5 raster lokal (km²) |
|---|---:|---:|---:|---:|---:|---:|
| SRTM | 1.444.085 | 1.444.085 | 0,9577138908 → 0,957714 | 100,5781191 | 100,6 | 100,6434 |
| GLO-30 | 1.444.085 | 1.444.085 | 0,9530758017 → 0,953076 | 109,6330731 | 109,6 | 109,5741 |
| AW3D30 | 1.429.582 | 1.429.582 | 0,9544153895 → 0,954415 | 95,9286285 | 95,9 | 95,9661 |

Area lokal adalah jumlah sel × 900 m²; CRS metrik/grid 30 m mendukung perhitungan ini. Ini pemeriksaan deterministik artefak, bukan pengubahan hasil eksperimen. Perbedaannya nyata, bukan dianggap nol: khusus AW3D30, 95,9661 membulat ke **96,0**, bukan 95,9. Karena itu 95,9 **hanya** dipertahankan sebagai ringkasan tabel GEE, dan tidak dilaporkan sebagai hasil hitung ulang raster lokal.

| Pasangan | Agreement CSV GEE | Agreement raster lokal (irisan valid) | Rerata \|Δp\| CSV GEE | Rerata \|Δp\| raster lokal |
|---|---:|---:|---:|---:|
| SRTM–GLO-30 | 79,3581763% → 79,4% | 79,3733056% | 0,0555755847 | 0,0555743244 |
| SRTM–AW3D30 | 84,2697059% → 84,3% | 84,2774321% | 0,0371256609 | 0,0371237970 |
| GLO-30–AW3D30 | 81,5160525% → 81,5% | 81,5218015% | 0,0483255699 | 0,0483248940 |

Agreement pada presisi naskah sama; nilai mentah/domain tidak identik. Jumlah piksel irisan lokal masing-masing 1.444.085, 1.429.582, 1.429.582. Perbedaan metode reduksi/registrasi/domain belum diisolasi sebagai sebab pasti seluruh selisih. Jangan membuat klaim bahwa semua tabel telah diverifikasi pada satu denominator yang sama.

### NoData: apa yang terbukti dan belum

**Terbukti pada file:**
- Mask probabilitas dan kelas risiko identik untuk tiap DEM; **0 sel kelas valid** pada lokasi probabilitas NoData.
- Sel termask semuanya bernilai −9999. Sel risiko valid hanya kelas 1–5.
- Nilai kelas dicek terhadap probabilitas tersimpan dan batas interval 0,2/0,4/0,6/0,8: **0 ketidakcocokan pada ketiga DEM**. Perbandingan memakai float64 agar pembulatan batas float32 tidak menimbulkan mismatch semu; ini pemeriksaan konsistensi file, bukan pelatihan/pembuatan peta baru.
- Seluruh sel tepi grid tidak valid. SRTM dan GLO-30 memakai mask valid yang sama; AW3D30 memiliki 14.503 piksel valid lebih sedikit.
- Karena itu bug kelas risiko pada sel tanpa probabilitas tidak ditemukan pada raster aktif menurut pemeriksaan ini.

**Belum terbukti secara geografis:**
- Tidak tersedia AOI polygon/geometry lokal atau mask AOI independen. Notebook sel 16 membentuk ROI dari koleksi GEE `FAO/GAUL/2015/level2`; keberadaan kode itu bukan bukti bahwa mask lokal tepat mengikuti geometri.
- Mask lokal T10 memakai zona valid risk-class terkait sebagai master. Memakainya lagi sebagai satu-satunya “acuan AOI” akan melingkar. Hitungan AOI GEE di manifest 1.438.214 juga tidak sama dengan jumlah valid raster, sehingga tidak dipakai untuk mengklaim mask eksak.
- Maka, pernyataan “semua piksel geografis di luar AOI pasti NoData” **belum dapat dipastikan independen**. Yang diverifikasi adalah NoData terhadap mask file yang tersedia. Kode sekarang menyertakan `_AOI_MASK`/guard NoData, tetapi notebook tidak dijalankan ulang dan kode bukan pengganti pemeriksaan geometri.

## 4. Investigasi slope <5° versus 11,48°

| Jalur | Bukti kode / artefak | Hasil |
|---|---|---|
| Pembentukan label | Sel 21 `a09065b4d47f`, baris 21–22: asset `USGS/SRTMGL1_003`, `ee.Terrain.slope(dem_for_label)`; baris 32 `slope_for_label.lt(SLOPE_MAX_FOR_FLOOD)`, parameter 5 | Filter `<5°` memang ada; bukan filter `≤5°` atau ambang 11,48°. Tidak ada alasan untuk diam-diam mengubah metodologi. |
| Prediktor | Sel 27 `2998e19532be`, baris 36: DEM direproject ke `ANALYSIS_CRS/ANALYSIS_SCALE` (EPSG:32749, 30 m), kemudian baris 66 `ee.Terrain.slope(dem_raw[name])` | Sumber SRTM sama, tetapi slope dihitung setelah jalur reproyeksi berbeda dari pembentukan label. Tidak terbukti ada dataset SRTM lain. |
| Ekstraksi | Sel 31 `3d8ca7c28c4d`, `stratifiedSample` baris 79–85 dan `sampleRegions` baris 93–95 memakai `SAMPLE_SCALE=30` | Skala ekstraksi terkonfirmasi; nilai raster filter di tiap koordinat tidak disimpan sehingga efek evaluasi lazy GEE/grid/sampling tidak dapat dipisahkan. Tidak mengasumsikan bilinear/nearest tertentu tanpa bukti. |
| Sampel beku | `data/frozen/main/sample_main_raw.csv`, label flood=1 | n=2.978, max slope_srtm=**11,483837127685547°**, n≥5°=**30**, persentase <5°=**98,99261249%**. Ini mendukung angka naskah 11,48° dan 98,99%, bukan membuktikan konsistensi filter. |

**Putusan:** bukan kesalahan ketik maksimum yang terbukti. Ada ketidaksesuaian nilai prediktor dengan ambang label. Perbedaan urutan perhitungan/grid adalah kemungkinan yang didukung keberadaan dua jalur kode, tetapi **belum terbukti menyebabkan 30 titik tersebut**. Nilai slope filter, mask perantara, dan pasangan ekstraksi pada grid yang sama tidak tersedia. Ketidaksesuaian ditandai untuk konfirmasi; angka tidak diganti, filter tidak diubah, dan tidak dilakukan rerun. Kalimat lama yang menganggap statistik itu sepenuhnya sejalan dengan filter telah diganti dengan catatan jujur.

## 5. Masalah belum terselesaikan dan langkah konfirmasi

1. **Sebab konflik slope:** memerlukan ketertelusuran nilai filter versus prediktor/mask perantara pada titik yang sama; tidak dapat diselesaikan hanya melalui revisi bahasa. Jika konfirmasi memerlukan ekstraksi/eksekusi baru, itu perlu persetujuan terpisah.
2. **Geometri mask AOI:** memerlukan polygon/mask independen untuk memeriksa sel terhadap batas geografis, bukan menguji mask dengan dirinya sendiri.
3. **Domain statistik GEE versus raster lokal:** nilai telah dibedakan; penyebab persis seluruh selisih belum dibuktikan. Jika dikehendaki satu domain tunggal untuk semua statistik, itu keputusan analisis baru, bukan alasan mengganti angka parsial secara diam-diam.
4. Batas ketertelusuran angka historis yang dicatat T12 tetap ada; tidak menjadi objek koreksi numerik baru pada pekerjaan ini.

## 6. Verifikasi dokumen dan perlindungan data

- XeLaTeX tiga lintasan berhasil: **51 halaman**, **0 undefined**, **5 overfull warisan**, **1 warning inputenc** yang sama dengan baseline. Penambahan catatan C–D membuat dokumen bertambah satu halaman; tidak dilakukan pemadatan/redesain untuk mengejar jumlah halaman.
- Tidak ada perubahan struktur Bab I–V, heading, key sitasi/ref, tabel hasil, persamaan, bibliografi, atau gambar. Semua 301 hash berkas beku dan bibliografi identik dengan baseline.
- Angka hasil lama tidak diganti. Nilai kesimpulan mengulang tabel GEE yang tersedia; jumlah 30 titik adalah pemeriksaan sampel statis. Pemeriksaan luas/agreement lokal dilaporkan terpisah sebagai audit, bukan menggantikan tabel eksperimen.
- Tidak menjalankan notebook, GEE, model, training, bootstrap, permutasi Moran, sampling, atau eksperimen. Pemeriksaan CSV dan raster adalah inspeksi read-only dengan aritmetika deterministik.
- PDF hasil edit disweep untuk terminologi dan klaim, serta halaman 4.2, 4.7.2, dan 5.1 diinspeksi visual. ZIP sumber dibangun ulang dengan path `figures/`, 9 anggota dan CRC/isi diperiksa.
- Paket analisis baca raster ditempatkan dalam virtualenv `.hoplite/venv-raster` (tidak dikomit); tidak mengubah dependency ilmiah notebook atau data proyek.

**Status akhir: revisi terarah selesai, bukan deklarasi dokumen final.** Konflik slope dan verifikasi geografis AOI tetap terbuka dan harus dibawa ke konsultasi/pembelaan secara eksplisit.
