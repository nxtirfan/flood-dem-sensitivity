# T13 — Revisi wording Bab I–V pasca-T12

**Tanggal:** 8 November 2026. **Dasar:** commit T12 `9f62066`. Pengguna menyetujui perapian bahasa naskah tanpa perubahan data, angka, model, metode, atau hasil eksperimen.

## Cakupan dan keputusan

- Bab I: merapikan latar belakang, transisi penelitian terdahulu, serta rumusan masalah dan tujuan. Pertanyaan membedakan performa model dari pola spasial peta; aspek tetap prediktor, bukan hasil deskriptif yang tidak dilaporkan.
- Bab II: memadatkan definisi, uraian Random Forest, dan kerangka teori. Interpretasi Meadows/Tique, datum, label, sitasi, dan batas klaim T12 dipertahankan.
- Bab III: memadatkan uraian eksperimen, faktor perlakuan, dan keterangan prediktor MERIT Hydro. Penjelasan input, pelatihan, dan evaluasi GEE/scikit-learn tetap dibedakan.
- Bab IV–V: merapikan uraian Moran's I OOF/raster dan keterbatasan kejadian/lokasi; statistik raster dan statistik titik OOF diperjelas berasal dari jalur yang berbeda.
- Draf wording pra-audit tidak diterapkan secara massal. Lima belas usulan Bab II–V dipilih setelah dicocokkan dengan naskah pasca-T12 dan ditinjau kembali; usulan yang tidak cocok, mengubah struktur/angka, atau berisiko mengaburkan batas klaim dilewati. Perapian Bab I disusun ulang terhadap versi T12, bukan menjalankan skrip penggantian lama.

## Klarifikasi faktual saat proofreading

Bagian 3.6 menyebut kelas semak belukar WorldCover kode 20 sebagai “kategori acuan yang tidak dimodelkan”. Pernyataan itu diperbaiki menjadi: kelas tersebut **tidak muncul pada sampel utama**, sehingga tidak menghasilkan dummy pada evaluasi tersebut. Ini bukan perubahan pengodean atau model: CSV beku `data/frozen/main/sample_main_raw.csv` memuat kode 10, 30, 40, 50, 60, 80, 90, 95 dan tidak memuat 20; notebook sel 35 memakai `get_dummies(..., drop_first=False)`; manifest mencatat kedelapan dummy pada sampel utama. Kehadiran kode 20 pada beberapa multi-seed tetap dijelaskan terpisah di 4.4. Tidak ada angka hasil yang diubah.

Kalimat keterbatasan 4.8 juga diperjelas: statistik **raster** berasal dari peta GEE, sedangkan statistik **titik OOF** dan metrik performa berasal dari evaluasi scikit-learn. Pemisahan ini selaras dengan bagian diagnostik dan tidak menyatakan kesetaraan kedua estimator.

## Verifikasi

- XeLaTeX tiga lintasan: PDF **50 halaman**, **0 undefined**, **5 overfull** yang tersisa dari 7 warisan pada baseline T12; tidak ditemukan overfull baru. Ada **1 warning inputenc** yang juga muncul pada baseline sandbox; bukan 0 warning. Bibliografi tidak diubah, sehingga biber tidak dijalankan.
- Pemeriksaan terhadap T12 menunjukkan urutan seluruh token angka, rentang rumus, kunci sitasi, referensi, struktur section/subsection, dan lingkungan LaTeX identik. Ini bukan bukti otomatis bahwa semua makna kalimat sama; perubahan dibaca dan ditinjau terhadap batas penelitian.
- **301 hash** (300 berkas data/notebook/gambar/logo zona beku dan `references.bib`) identik dengan baseline. Tidak ada notebook, model, training, eksperimen, atau ekstraksi dijalankan ulang.
- Sweep isi PDF untuk 23 fakta dan batas T12, termasuk datum, label proksi, GEE/sklearn, seed, bootstrap, angka raster/transisi, referensi, dan klarifikasi dummy; klaim lama dicek tidak muncul. Halaman revisi utama diinspeksi visual.
- ZIP sumber berisi 9 anggota, CRC lolos, isi sama dengan sumber/PDF akhir, dan semua jalur `includegraphics` tersedia. Ukuran **2.342.616 byte**.
- Daftar isi dan rujukan silang dibangun ulang. Beberapa halaman tercetak bergeser (misalnya 1.3 dari 4 ke 3, 3.2 dari 16 ke 15, 3.9.2 dari 24 ke 23); lima topik konsultasi di T12 tetap relevan, tetapi gunakan PDF dan daftar isi terbaru untuk lokasi persis.

## Batas dan tindak lanjut

Kecocokan label 70% serta angka pembanding historis tetap memerlukan ketertelusuran artefak, seperti T12. Perapian redaksi bukan validasi ground truth, pembuktian mask per piksel, penghapusan leakage, atau validasi langsung model peta GEE. Langkah berikut adalah konsultasi Dr. Iqbal menggunakan `docs/temuan/T12-round-2.md` dan PDF terbaru, diikuti keputusan artikel SMDS.
