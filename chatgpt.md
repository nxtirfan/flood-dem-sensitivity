# Handoff debat ke ChatGPT (isu label JRC)

> Cara pakai: salin seluruh isi berkas ini sebagai satu pesan ke ChatGPT.
> ChatGPT tidak punya akses berkas proyek; semua fakta penting sudah dikutip
> di dalam teks. Peran yang diminta: pengkritik metodologi yang kasar dan
> jujur (adversarial), bukan penyanjung posisi penulis.
> Tanggal: 2 Nov 2026. Penulis: M Irfan Al Hakim, proposal metopen UNNES.
> Naskah acuan: proposal Bab I sampai V, PDF 42 halaman; dokumen audit T04.

## 1. Desain ringkas

- Topik: sensitivitas DEM (SRTM, Copernicus GLO-30, ALOS AW3D30, kisaran
  30 m) untuk peta kerawanan banjir Random Forest di Google Earth Engine;
  pesisir Semarang Demak; satu kejadian Sentinel-1 Maret 2024.
- Prediktor 24 kolom: 5 per-DEM (elevasi, slope, aspect sin, aspect cos,
  validitas) + 11 non-DEM (HAND, area hulu, lebar sungai, jarak sungai,
  jarak air permanen JRC, CHIRPS 7 hari, CHIRPS 30 hari, indeks Sentinel-2)
  + 8 dummy WorldCover. Prediktor non-DEM identik untuk ketiga DEM.
- Sampling: stratifiedSample 2978 piksel per kelas, seed 42, split 75:25.
  Sampel identik untuk ketiga DEM.
- Dua model: sklearn RF 400 pohon untuk evaluasi; smileRandomForest 300
  pohon untuk peta di GEE.
- Kriteria label: rasio VH lebih dari 1,25; VH pasca di bawah -18 dB; bukan
  air permanen JRC; slope di bawah 5 derajat; konektivitas minimal 8 piksel.
- Evaluasi: spatial CV 4-fold pada 16 blok; bootstrap blok 16 blok 1.000
  kali; multi-seed 5 seed.
- Dua run: v24 run utama (statistik deskriptif dan peta); v26 replikasi kode
  identik (bootstrap dan multiseed). Kedua run diberi label terpisah di
  naskah.

## 2. Angka utama

- Holdout AUC: SRTM 0,9318; GLO-30 0,9404; AW3D30 0,9360.
- Spatial CV pooled OOF: SRTM 0,9032; GLO-30 0,9174; AW3D30 0,9080.
- Rerata ROC-AUC sampel ulang blok (v26): SRTM 0,894; GLO-30 0,910; AW3D30
  0,899.
- Multi-seed holdout: 0,939 (SD 0,014); 0,947 (SD 0,010); 0,940 (SD 0,012).
- Multi-seed spatial CV: 0,869 (SD 0,017); 0,889 (SD 0,013); 0,877
  (SD 0,017).
- Bootstrap blok: GLO-30 minus AW3D30 = +0,0108 dengan selang +0,0041
  hingga +0,0198. SRTM minus GLO-30 = -0,0155 dengan selang -0,0250 hingga
  -0,0072. Keduanya tidak memuat nol. SRTM minus AW3D30 = -0,0047 dengan
  selang -0,0096 hingga +0,0013; memuat nol; dilaporkan marginal.
- Bootstrap piksel: GLO-30 minus SRTM = 0,0141 dengan selang 0,0109 hingga
  0,0173; selang lebih sempit.
- Peta: persetujuan kelas SRTM-AW3D30 = 83,95 persen; SRTM-GLO-30 = 79,42
  persen; AW3D30-GLO-30 = 81,30 persen. Luas kelas sangat tinggi = 105,2;
  114,2; 113,4 km persegi.
- Run bridging v23: AUC SRTM = 0,802 dibanding baseline = 0,852; label
  cocok sekitar 70 persen.

## 3. Fakta label pita JRC (hasil audit T04)

- Kode sel 12: permanent_water = band JRC occurrence lebih dari atau sama
  dengan 80. flood_raw = s1_ratio.gt(1.25).And(after_pol_db.lt(-18))
  .And(permanent_water.Not()).And(slope_for_label.lt(5)). flood_label =
  flood_raw.selfMask().connectedPixelCount(100, True).gte(8).unmask(0).
- Mask band occurrence JRC bersifat fraksional dari 0 sampai 1, bukan biner.
- Ukuran pita: footprint 189.345 piksel = 12,88 persen AOI; nilai occ yang
  benar-benar terbaca = 63.499 piksel = 4,32 persen. Angka 12,78 persen pada
  log kernel = jumlah berbobot, bukan hitungan piksel.
- flood=1 = 58.574 piksel; semuanya berada di dalam pita. flood=1 di area
  JRC no-data = 0, teruji pada 4 jalur hitungan dan 2 grid.
- flood=0 = 1.410.981 piksel; tersebar di seluruh AOI; di dalam pita
  152.564 piksel; di luar pita 1.258.417 piksel.
- flood_raw dimask = 1.259.427 piksel = 85,70 persen AOI; 99,92 persen karena
  JRC no-data; sisanya slope no-data di tepi ROI; kontribusi Sentinel-1 nol.
- flood_label akhir mengisi 0/1 penuh di seluruh AOI karena unmask(0)
  dipanggil setelah filter konektivitas. Hanya kelas-1 yang terkunci dalam
  pita; kelas-0 berdomain penuh dengan negatif in-pita 152.564 piksel.
- Menambah permanent_water.unmask(0) sebelum Not() membuat piksel luar pita
  diperlakukan bukan-air-permanen; kandidat banjir bisa lahir di luar pita;
  inventory berubah; rerun penuh wajib dan seluruh angka Bab IV dihitung
  ulang (catatan T04 E-2).

## 4. Isu reviewer dan keputusan yang menunggu

- Reviewer menilai pembentukan label memakai mask JRC sehingga kelas=1
  hanya lahir di dalam pita sekitar 13 persen AOI, sedangkan kelas=0
  tersebar di seluruh AOI.
- Reviewer menuduh permanent_water.Not() memerlukan unmask(0) sebelum
  diterapkan pada pembentukan label.
- Dua opsi reviewer: (1) perbaiki label lalu jalankan ulang seluruh
  eksperimen utama; (2) pertahankan hasil dan batasi klaim. Reviewer tidak
  menganjurkan opsi 2 hanya demi cepat selesai. Saat ini keputusan
  menunggu; naskah sudah memuat kalimat keterbatasan.

## 5. Yang sudah ada di naskah saat ini

- Subbab 4.7 memuat kalimat keterbatasan: label hanya terbentuk di dalam
  pita, dan prediksi di luar pita dibaca sebagai ekstrapolasi spasial.
- Daftar klaim yang tidak boleh dinyatakan: tidak ada kalibrasi banjir di
  luar pita; luas absolut kelas sangat tinggi bukan luas genangan fisik
  penuh; inventory tidak mewakili seluruh genangan kejadian; tidak
  menyatakan produk terbaik universal.
- Label sumber run: bootstrap dan multiseed berasal dari v26; statistik
  deskriptif dan spasial berasal dari v24; klausa kecuali analisis
  pembanding memisahkan bridging v23.
- Bootstrap blok dan bootstrap piksel diterangkan terpisah di subbab 4.4.
- Bab V Kesimpulan merangkum jawaban berbasis hasil atas keempat rumusan
  masalah (rujukan Subbab 4.2 hingga 4.6).

## 6. Dua probe murah sebelum komit rerun (posisi penulis)

- Probe-1: hitung flood_raw bernilai TRUE di luar pita bila
  permanent_water.unmask(0) ditambahkan sebelum Not(). Bila hasil mendekati
  nol, rerun tidak akan mengubah apapun. Bila hasil banyak dan berpola,
  rerun mengubah inventory secara substansial.
- Probe-2: latih ulang dengan kelas-0 dibatasi di dalam pita (pool
  152.564) lalu bandingkan ranking DEM. Bila ranking bertahan, asimetri
  domain tidak mengubah ranking. Bila ranking berubah, rerun menjadi
  mendesak.

## 7. Pertanyaan untuk ChatGPT (jawab tegas dengan alasan)

1. Apakah kombinasi kelas=1 terkunci dalam pita sekitar 13 persen plus
   kelas=0 seluruh AOI 100 persen merupakan konfound berarti, dengan
   mempertimbangkan 152.564 piksel kelas=0 juga berada di dalam pita? Atau
   negatif in-pita justru hard negatives yang memperkuat validitas
   internal?
2. Bila label diperluas dengan unmask(0): di luar pita, keputusan bukan air
   permanen menjadi asumsi, bukan observasi. Apakah trade-off cakupan
   versus kualitas label lebih baik dibanding mempertahankan domain label?
3. Apakah kesimpulan komparatif DEM (peringkat GLO-30 di atas AW3D30 di
   atas SRTM; perbedaan kecil tetapi konsisten pada 5 dari 5 seed) tahan
   terhadap asimetri domain label, mengingat label sama bagi ketiga
   konfigurasi (konfound common-mode)? Kapan konfound common-mode tetap
   bisa merusak ranking relatif DEM?
4. Apakah kalimat keterbatasan subbab 4.7 sudah cukup, atau perlu klausul
   tambahan di Bab 3 atau 4.7 untuk menutup risiko validitas model
   keseluruhan?
5. Bila rerun dilakukan: apakah arah perubahan metrik dapat diprediksi?
   Bagaimana implikasinya bagi ranking DEM dan luas kelas risiko?
6. Dengan premis (a) ini proposal metopen, bukan skripsi final; (b) rerun
   mengubah seluruh angka Bab IV; (c) hasil rerun tidak pasti menaikkan
   kualitas: mana yang Anda pilih, opsi 1 atau opsi 2? Sebutkan alasan.

## 8. Catatan pelengkap

- Probe-1 hanya memerlukan reduceRegion kecil di GEE; kuota proyek
  nonkomersial masih memungkinkan.
- Probe-2 memerlukan satu ekspor data pelatihan kecil dari GEE.
- Bila Anda membutuhkan informasi tambahan untuk berdebat, minta penulis
  melengkapi bagian tertentu.
