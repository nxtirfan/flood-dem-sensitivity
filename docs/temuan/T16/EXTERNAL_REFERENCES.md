# Rujukan API untuk interpretasi, bukan bukti hasil GEE baru

Diakses 8 November 2026 melalui dokumentasi resmi Google Earth Engine. Tidak ada akses aset, autentikasi, ekstraksi atau evaluasi GEE dilakukan pada T16. Dokumentasi menjelaskan kontrak operator; ia tidak merekonstruksi nilai piksel yang tidak tersimpan.

1. https://developers.google.com/earth-engine/apidocs/ee-image-reduceregion — tanpa `crs`, reduksi memakai proyeksi band pertama; `scale` adalah skala nominal meter; `crsTransform` eksplisit menentukan grid dan tidak boleh digabung dengan `scale`.
2. https://developers.google.com/earth-engine/guides/reducers_reduce_region — reducer berbobot memakai bobot minimum mask dan fraksi cakupan region; reducer tidak berbobot memakai pusat piksel. Karena itu mean berbobot GEE bukan otomatis mean semua piksel valid GeoTIFF.
3. https://developers.google.com/earth-engine/apidocs/ee-image-pixelarea — proyeksi default WGS84 dengan skala 1 derajat. Dalam cell 54, pixelArea merupakan band pertama dan reduceRegion hanya memberi scale=30, bukan crs/transform: ini tidak mendefinisikan grid UTM ekspor.
4. https://developers.google.com/earth-engine/apidocs/ee-reducer-frequencyhistogram — histogram frekuensi **berbobot**. Konversi `int(v)` pada cell 53 dapat membuang bagian pecahan; CSV integer tidak mempertahankan histogram berbobot asli. Besaran kehilangan aktual tidak dapat dipulihkan tanpa nilai mentah.
5. https://developers.google.com/earth-engine/guides/resample — nearest-neighbor merupakan default reproyeksi; resample('bilinear') berlaku pada reproyeksi berikutnya. Rantai operasi dan grid keluaran harus dilacak; beda jalur saja tidak membuktikan sebab nilai 30 titik.
6. https://developers.google.com/earth-engine/apidocs/ee-image-sampleregions — default proyeksi band pertama, scale menyesuaikan proyeksi; geometri keluaran pada pusat piksel, piksel dengan band masked dikeluarkan.

Untuk klaim batas bobot, grid dan resampling, rujuk kontrak ini bersama bukti kode lokal. Penyebab numerik selisih GEE–lokal tetap memerlukan grid/geometri dan evaluasi GEE identik; jangan mengatribusikan seluruh selisih ke satu mekanisme tanpa pengujian tersebut.
