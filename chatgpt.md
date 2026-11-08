# Handoff lanjutan ke ChatGPT-6 (pasca-T11: verifikasi koreksi + persiapan konsultasi dosen)

> Cara pakai: salin seluruh berkas ini sebagai satu pesan ke ChatGPT-6,
> lalu tempel/dokumen-kan PDF proposal versi terbaru (50 halaman, 8 Nov 2026).
> ChatGPT tidak punya akses berkas/ artefak data proyek; semua fakta penting
> sudah disarikan di dalam teks. Peran yang diminta: pembaca kritis
> (proofreader + konsultan strategi konsultasi), BUKAN penyanjung.
> Jangan mengusulkan rerun/eksperimen baru — itu diagnosis untuk agen lain.

## 1. Status dokumen

- Naskah: `proposal_revisi-final.tex`, PDF 50 halaman, 0 warning undefined,
  7 overfull legacy (<15pt). Semua revisi paket sebelumnya (T05–T10 +
  instruksimu A–K) sudah digabung. Versi ini adalah versi pasca-T11.
- T11 = eksekusi koreksi berdasarkan auditmu (6 TINGGI + 8 SEDANG + LOW).
  Semua koreksi bersifat **teks/klaim/bibliografi SAJA**: tidak ada angka
  hasil, sampel, seed, model, CSV, raster yang diubah.

## 2. Daftar koreksi T11 yang seharusnya sudah ada di naskah

1. **Datum AW3D30 = EGM96** (bukan EGM2008). Seharusnya terkoreksi di:
   - 2.3.3: ada satu kalimat propositi bahwa tinggi dilaporkan ortometrik
     terhadap model geoid EGM96.
   - 3.6 (tabel produk): kolom datum/dasar vertikal mendaftar
     "EGM96 (SRTM), EGM2008 (Copernicus DEM GLO-30), EGM96 (ALOS AW3D30)".
   - 4.1 (paragraf offset): kalimat reinterpretasi seharusnya menyatakan
     gabungan perbedaan acuan vertikal antarproduk **plus** perbedaan
     karakteristik pengukuran; **karena SRTM dan ALOS AW3D30 memakai model
     geoid yang sama (EGM96), selisih kedua produk tidak boleh disandarkan
     ke perbedaan datum geoid**; offset +0,39 m dipertahankan.
   - 4.8 (keterbatasan): poin datum kini berbunyi
     "(EGM96 pada SRTM dan ALOS AW3D30 dibandingkan EGM2008 pada GLO-30)".
2. **Pemisahan pipeline GEE vs sklearn (3.7)**: ada satu kalimat baru yang
   menyatakan dua implementasi tidak dipandang sebagai satu model yang sama;
   kesetaraan antar jalur tidak dituntut. Tidak menggantikan penjelasan
   300 vs 400 pohon.
3. **Definisi label kelas-0 (2.2)**: kelas 1 = terdeteksi banjir oleh
   pipeline proksi; kelas 0 = TIDAK diidentifikasi oleh pipeline yang
   sama — dan bukan bukti lokasi tidak berbanjir (termasuk piksel tanpa acuan S1 /
   tak terakuisisi / di luar dukungan JRC). Selain itu: keterbatasan
   4.8 mengulang konsekuensi makna label ini secara eksplisit.
4. **Klaim urutan multiseed (4.4)**: sebelumnya "urutan SRTM>AW3D30
   konsisten 5/5 seed" — DISELESAIKAN jadi: GLO-30 tertinggi konsisten
   5/5 seed; pasangan SRTM–AW3D30 BERBALIK TIPIS pada holdout seed 42 & 100,
   selisih ≤ 0,0006; bukan klaim monotonik.
5. **Catatan skema fitur antar-seed (4.4)**: satu kalimat yang states
   bahwa `lc_20` hadir sebagai kolom dummy pada sampel seed 100/2024/7
   (25 input) tetapi tidak pada seed utama & 42/99 (24 input), sehingga
   perbandingan antar-seed valid di dalam pasangan seed masing-masing.
6. **Caveat bootstrap (3.8)**: satu kalimat bahwa 1.000 resample adalah
   jumlah sampel ulang pada 16 blok, bukan 1.000 unit data spasial
   independen.
7. **Kritik Tique (2.8 & 2.10)** ditulis ulang faktual: Tique = rancangan
   banyak faktor (penelitian berbeda); penelitian ini = perlakuan tunggal
   satu-faktor variasi sumber elevasi. Tidak lagi menyebut Tique "tidak
   terkontrol".
8. **Meadows (2.1)** dilunakkan: keunggulan produk mengikuti kondisi
   lingkungan dan metrik, bukan klaim "tidak ada satu produk terbaik yang
   otomatis menang".
9. **Simpulan aspect (5.1 item 1)**: disesuaikan dengan statistik DEM
   yang tersedia (elevasi & slope); tidak lagi menyebut perbedaan
   "arah lereng" sebagai hasil yang didokumentasikan — aspect masuk
   hanya sebagai input dekomposisi.
10. **Abidin (bib)**: metadata diperbarui ke Crossref — GNHR **4(3):
    226–240, 2013**, daring 3 Jul 2012; 5 penulis (Abidin, Andreas,
    Gumilar, Sidiq, Fukuda); tidak lagi memakai volume 6(5–7) 401–427
    atau daftar penulis 6 orang; key sitasi tetap `abidin2015`.
11. **tadono2016 (bib)**: pages 157–161 → **157–162**.
12. **Catatan domain transisi (4.5)**: satu kalimat bahwa nilai matriks
    transisi dihitung pada reduksi server GEE dengan registrasi grid yang
    sedikit berbeda dari grid raster ter-ekspor; persentase dan luas
    dilaporkan pada domain masing-masing tabel.
13. Sisipan penyesuaian kalimat lain yang perlu mengikuti definisi label baru (2.2).

## 3. Angka final yang menjadi acuan (CSV v27-T10, tidak berubah)

- Holdout AUC: SRTM 0,9497 (seed 42); spatial-CV pooled proba ~0,90xx
  (0,9032/0,9174/0,9080), rerata per-fold ~0,70→0,87-0,89 pasca fix-sabuk.
- Moran peta raster (re-quote terbaru): **0,957714 / 0,953076 / 0,954415**
  (n = 1.444.085 / 1.444.085 / 1.429.582 piksel; p = 0,001).
- Matriks transisi: 94.306 / 36.869 / 25.679 piksel (srtm→glo30) dan
  174.072 / 91.194 piksel (srtm→aw3d30, diagonal kelas 2 & 5).
- WorldCover per kelas & rentang, sensitivitas spasial 79–84%, luas
  kelas 5: 100,6 / 109,6 / 95,9 km² (kini ALOS paling sempit).
- Bootstrap blok v26: GLO-30 minus AW3D30 = +0,0108 [+0,0041, +0,0198];
  GLO-30 minus SRTM = +0,0155 [+0,0072, +0,0250]; SRTM–AW3D30 selang
  masih memuat 0 (marginal).
- Multi-seed holdout: 0,939 / 0,947 / 0,940 (SD 0,014 / 0,010 / 0,012).

## 4. Tugas kamu (round 2)

Kamu menerima PDF terbaru. Baca ulang dokumen dengan peran:
(A) proofreader mutakhir, (B) audit konsistensi narasi, (C) persiapan
konsultasi.

A. **Verifikasi Tuntas T11**: pastikan 13 item pada daftar pada Bagian 2 benar-benar
   telah dieksekusi di PDF terbaru. Untuk tiap item, kutip baris/frasa
   asli dan beri OK / PARTIAL / MISS.
B. **Cari efek samping koreksi**: nomor Subbab/cross-reference salah
   (nomor bisa bergeser), kalimat sisipan yang memicu paragraf patah
   atau double-spacing, duplikasi definisi label antara 2.2 dan 4.8,
   sitasi yang kini tidak konsisten (abidin2015 → GNHR 4(3); tadono →
   157–162), dan klaim historis yang tersisa menggunakan interpretasi
   lama (EGM2008 untuk ALOS, "urutan konsisten 5/5 seed", "arah lereng").
C. **Verifikasi redaksi** offset 4.1: evaluasi seberapa jelas alasan
   "selisih SRTM - ALOS AW3D30 tidak bisa disandarkan ke beda datum"
   bagi pembaca non-geodesi; bila masih kabur, usulkan 1 revisi kalimat.
D. **Persiapan konsultasi Dr. Iqbal**: dari seluruh naskah, usulkan
   **5 topik pembicaraan-kunci teratas** untuk mengumpulkan input dosen,
   urut dari yang paling strategis. Tiap topik beri: isu singkat (1 kalimat),
   maksud/ekspektasi (1 kalimat), dan halaman acuan.
E. **Ketiada-kepastian yang masih boleh dipertanyakan**: daftar asersi
   dalam naskah yang secara logikanya TIDAK memaksa eksperimen baru,
   tapi masih berupa kelemahan redaksi bisa usulkan satu kalimat
   penggantinya lebih jujur tanpa memungut eksperimen baru.

Format keluaran: Tabel per temuan (lokasi/halaman, kutipan, tipu: TINGGI /
SEDANG / KECIL, usulan revisi konkretnya). Bila kamu tidak yakin dari pro
asonya (misal jika detail persis data buat sesuatu), tandai
**[GATED - perlu cek artefak]** dan jangan mengarang angka atau angka.
Jangan mengusulkan rerun.
