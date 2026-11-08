# Handoff T15 — finalisasi terarah, status belum final

Tanggal 8 November 2026. Baca AGENTS.md dan `docs/temuan/T15-finalisasi-terarah.md` untuk ringkasan awal, setiap perubahan sebelum–sesudah, halaman, verifikasi raster, dan investigasi slope.

**Prioritas terbuka:** konflik slope filter <5° vs max11,48° (30/2.978 titik positif ≥5°) belum diketahui penyebabnya; filter dan prediktor memakai jalur grid berbeda tetapi kausalitas belum terbukti. Mask file konsisten dengan NoData/kelas, tetapi belum terverifikasi terhadap geometri AOI independen yang tidak tersedia lokal. Jangan menyatakan dokumen final.

Istilah block bootstrap telah diseragamkan; kesimpulan menyebut agreement79,4–84,3% dan autokorelasi residual yang tetap ada; implikasi mitigasi dibatasi pada potensi. Angka Moran aktif berasal dari CSV pasca-mask lokal T10, bukan cache notebook pra-mask. Luas/agreement dari tabel GEE dan hitungan raster lokal berbeda sedikit dan kini dijelaskan sebagai sumber berbeda. Tidak ada data, notebook, model, label, seed atau angka tabel eksperimen diubah. Tidak ada rerun. PDF51 halaman,0 undefined,5 overfull warisan,1 warning inputenc baseline; ZIP direbuild.

Catatan T12–T14 di bawah bersifat riwayat; angka dan ketentuan lama tidak mengalahkan batas T15.

---

# Handoff pasca-T12 — round-2 selesai, persiapan konsultasi

Tanggal: 8 November 2026. Aturan editor: baca `AGENTS.md` terlebih dahulu.

## Update T14 — tanda baca prosa

Sebanyak 19 titik koma pada prosa diganti dengan pemisahan kalimat; tanda baca pada rincian tetap dipertahankan. PDF tetap 50 halaman; tidak ada perubahan hasil atau pemangkasan isi. Lihat `docs/temuan/T14-tanda-baca.md`. Panjang naskah dan kebutuhan Bab IV–V dikonfirmasi saat konsultasi.

## Update T13 — wording Bab I–V selesai

Pengguna menyetujui perapian bahasa pasca-T12. Rincian dan verifikasi ada di `docs/temuan/T13-revisi-wording.md`. Naskah dan PDF terkini telah diperbarui tanpa rerun atau perubahan angka/data/model; draf pra-audit tidak diterapkan mentah. Kelas WorldCover 20 tidak muncul pada sampel utama, bukan kategori acuan yang sengaja dibuang. Statistik spasial raster berasal dari peta GEE; statistik titik OOF dan metrik berasal dari evaluasi scikit-learn.

PDF akhir T13: 50 halaman, 0 undefined, 5 overfull warisan, 1 warning inputenc yang sudah ada pada baseline. ZIP sumber telah diuji; 300 berkas beku dan bibliografi identik. Beberapa halaman subbab bergeser, jadi gunakan daftar isi PDF terbaru untuk konsultasi. Topik dan batas T12 di bawah tetap relevan; angka historis yang belum terlacak tetap [GATED].

## 1. Status dan keluaran

Tugas A–E round-2 yang diminta pada Bagian 6 AGENTS.md telah dikerjakan langsung di repo. Laporan tunggal sesi: `docs/temuan/T12-round-2.md`.

- A: tabel 13 koreksi T11 dengan status sebelum/sesudah, kutipan dan halaman PDF.
- B: efek samping, rujukan silang, definisi kelas 0 dan klaim historis diperiksa; redaksi yang bermasalah diperbaiki.
- C: offset dijelaskan dengan bahasa acuan tinggi/geoid, dukungan piksel bersama, dan batas atribusi sebab.
- D: tepat lima topik konsultasi Dr. Iqbal, isu, harapan masukan, dan halaman acuan.
- E: revisi tekstual dan ketidakpastian yang masih [GATED - perlu cek artefak] dijelaskan tanpa menciptakan angka atau mengusulkan eksperimen.

Pada akhir T12, PDF memiliki 50 halaman, 0 undefined, dan 7 overfull warisan pada baseline. Naskah serta PDF terkini sudah diperbarui oleh T13; rujuk update di atas. Satu warning inputenc juga muncul pada build T11 asli di sandbox ini: paket diabaikan mesin UTF-8. Karena itu hasil tidak disebut 0 warning. ZIP sumber diperbarui dengan direktori `figures/`.

## 2. Perubahan tekstual penting

1. GEE memakai kode tutupan lahan mentah sebagai satu band, 17 input, RF 300 pohon, dan seluruh sampel beku utama; evaluasi utama sklearn memakai dummy tutupan lahan, 24 input, RF 400 pohon, serta pemisahan sampel. Metrik sklearn bukan validasi langsung model pembentuk peta GEE.
2. Kelas 0 berarti tidak diidentifikasi oleh pipeline proksi, bukan bukti lokasi kering. Kandidat negatif dapat berasal dari luar dukungan label positif JRC; area itu bukan otomatis area tanpa sampel latihan sama sekali.
3. RM1/tujuan dan simpulan diselaraskan ke hasil elevasi/slope. Aspect tetap prediktor sinus/kosinus/validitas, tanpa klaim ringkasan perbandingan tersendiri.
4. AW3D30 dan SRTM sama-sama EGM96, GLO-30 EGM2008. Offset tidak mengisolasi kontribusi sensor maupun acuan tinggi. Selisih berpasangan pada piksel valid bersama tidak wajib sama dengan pengurangan rerata marginal.
5. Klaim universal yang masih teratribusi ke Meadows dihapus; temuan FABDEM dan ketergantungan galat terhadap kondisi/metrik dilaporkan sesuai sumber.
6. Domain matriks/server GEE dan Moran/raster ekspor dibedakan tanpa mengklaim penyebab tunggal selisihnya sudah terbukti. Kontras CV domain sempit/penuh tetap deskriptif, bukan efek kausal terisolasi.
7. Ringkasan pola spasial dibatasi ke peta eksperimen utama yang dirangkum tabel, bukan otomatis seluruh skema historis. Pemakaian label yang sama tidak dinyatakan menjamin semua perbandingan bebas bias.

## 3. Angka acuan yang tidak diubah

Urutan angka: SRTM / GLO-30 / AW3D30.

- Holdout **utama**: AUC 0,931780 / 0,940375 / 0,935989.
- Multi-seed **seed 42**: AUC 0,949691 / 0,955071 / 0,949468; bukan sampel utama yang sama. Jangan menyebut 0,9497 sebagai AUC holdout utama.
- Rerata per-fold spatial CV probabilitas: 0,869914 / 0,889937 / 0,874749. Jangan tertukar dengan pooled OOF atau rerata AUC bootstrap.
- Multi-seed: GLO-30 tertinggi 5/5; urutan SRTM/AW3D30 berbalik tipis pada holdout seed 42 dan 100, bukan selalu AW3D30 > SRTM.
- Skema dummy: 25 input untuk seed 100/2024/7, 24 untuk main/42/99.
- Moran raster pasca-mask: 0,957714 / 0,953076 / 0,954415; n 1.444.085 / 1.444.085 / 1.429.582; p 0,001.
- Agreement: 79,4% SRTM–GLO-30; 84,3% SRTM–AW3D30; 81,5% GLO-30–AW3D30.
- Luas kelas 5: 100,6 / 109,6 / 95,9 km²; bukan luas genangan aktual.
- Offset GLO-30/AW3D30 terhadap SRTM: −1,56/+0,39 m; APPLY_VERTICAL_OFFSET tetap False.
- Bootstrap blok dan metadata Abidin/Tadono tetap seperti hasil koreksi T11.

## 4. Batas verifikasi

Tidak menjalankan notebook, model, bootstrap, ekstraksi, atau eksperimen. SHA256 300 berkas zona beku identik dan rentang matematika inline lama dalam TEX tidak berubah. Key sitasi dan `.bib` tidak diubah pada T12.

Angka pembanding historis 1.870 titik, kecocokan 70%, dan CV domain terbatas sekitar 0,70 tetap memerlukan ketertelusuran artefak run/split/label; belum terverifikasi independen bukan berarti terbukti salah. Jangan menyatakan pembaruan arsip Sentinel-1 sebagai sebab tunggal yang sudah diketahui. Jangan mengklaim ground truth, ketiadaan leakage, mask eksak per piksel, atau kesetaraan estimator hanya dari revisi teks.

## 5. Langkah berikut

Bawa PDF terbaru dan lima topik prioritas pada Bagian D laporan T12 ke konsultasi Dr. Iqbal. Setelah arahan dosen, putuskan tindak lanjut naskah dan artikel SMDS. Tidak ada eksperimen baru yang diperintahkan oleh handoff ini; perubahan data/label/model tetap memerlukan persetujuan eksplisit pengguna.
