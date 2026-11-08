# T12 — Verifikasi round-2 T11 dan persiapan konsultasi

**Tanggal:** 8 November 2026. **Dasar:** `3b2065d` (versi T11 + AGENTS.md).
**Tugas:** AGENTS.md Bagian 6, tugas A–E pada chatgpt.md.

## Ringkasan keputusan

T11 telah memperbaiki banyak klaim, tetapi beberapa sisipan masih parsial atau memunculkan ambiguitas. T12 memperbaiki teks langsung, tanpa mengubah angka hasil, data, sampel, seed, model, notebook, CSV, raster, gambar, maupun key sitasi. Tidak ada eksperimen atau ekstraksi ulang. Bibliografi T11 dipertahankan; biber tidak diperlukan karena `.bib` tidak berubah. PDF dibangun dengan XeLaTeX tiga lintasan dan paket sumber dibangun ulang dengan direktori `figures/`.

**Makna status:** OK/PARTIAL mengukur pelaksanaan koreksi teks yang diminta, bukan sertifikasi validitas desain/label atau validasi lapangan. “Awal” adalah keadaan T11 yang dibaca; “akhir” adalah hasil T12. Nomor halaman berikut memakai **halaman tercetak**, diikuti **urutan fisik PDF** dalam kurung; empat halaman awal menjelaskan selisih keduanya. Naskah akhir tetap 50 halaman.

## A. Verifikasi 13 koreksi T11

| No. | Koreksi | Awal → akhir | Kutipan naskah akhir dan halaman |
|---|---|---|---|
| 1 | Datum AW3D30 dan offset | PARTIAL → OK | “tinggi ortometrik terhadap model geoid EGM96” — hlm. 8 (PDF 12); daftar acuan pada 3.6 — hlm. 18 (22); “selisih keduanya tidak dapat dijelaskan oleh perbedaan model geoid” — hlm. 28 (32); “EGM96 pada SRTM dan ALOS AW3D30, EGM2008 pada Copernicus DEM GLO-30” — hlm. 41 (45). Generalisasi sebab sensor/datum di pembahasan juga dibatasi. |
| 2 | Pemisahan GEE/sklearn | PARTIAL → OK | “17 masukan pada GEE berbeda representasi dari 24 masukan pada evaluasi utama scikit-learn” dan “Metrik scikit-learn bukan validasi langsung terhadap model pembentuk peta GEE” — hlm. 20 (24), lanjutan metode hlm. 19 (23). Dijelaskan kode landcover mentah dan seluruh sampel beku versus dummy dan pemisahan evaluasi. |
| 3 | Definisi kelas 0 | PARTIAL → OK | “Label kelas 0 bukan bukti bahwa lokasi tersebut tidak berbanjir” — hlm. 7 (11); implikasi kelas positif/negatif yang asimetris pada hlm. 40 (44). Contoh sebab “tidak terakuisisi citra Sentinel-1” dihapus karena bukan fakta yang ditunjukkan audit ini. |
| 4 | Urutan multi-seed | OK → OK | “pada dua dari lima evaluasi holdout (seed 42 dan 100) SRTM mencatatkan AUC sedikit lebih tinggi” dan “tidak lebih dari 0,0006” — hlm. 32 (36). GLO-30 tertinggi pada kelima seed tetap dilaporkan. |
| 5 | Skema fitur per seed | OK → OK | “seed 100, 2024, dan 7 sehingga jumlah input efektif membesar menjadi 25” serta “sampel utama serta seed 42 dan 99 memakai 24 prediktor” — hlm. 32–33 (36–37). Pernyataan 24 input pada ringkasan kini dibatasi ke evaluasi utama sklearn. |
| 6 | Unit bootstrap | OK → OK | “rangkaian 16 blok yang sama dan bukan berarti 1.000 unit data independen” — hlm. 21 (25). Tidak ditafsirkan sebagai tambahan unit spasial independen. |
| 7 | Perbandingan Tique | OK → OK | “mengombinasikan perubahan DEM, metode hidrologi, dan model ML dalam satu rancangan pembandingan” — hlm. 12 (16). Tabel diperjelas menjadi “Fokus variasi sumber DEM pada satu algoritme RF” — hlm. 11 (15); bukan tuduhan desain Tique tidak terkontrol. |
| 8 | Atribusi Meadows | PARTIAL → OK | “FABDEM secara konsisten berada pada peringkat pertama” dan “interpretasi galat tetap perlu mempertimbangkan kondisi lingkungan serta metrik yang dinilai” — hlm. 2 (6). T11 masih menyisakan simpulan universal “tidak satu pun produk … seluruh konteks”; itu dihapus. |
| 9 | Simpulan aspect | OK → OK | “arah lereng masuk sebagai prediktor … tanpa ringkasan numerik lintasproduk yang dilaporkan tersendiri” — hlm. 42 (46). Untuk konsistensi seluruh naskah, RM1/tujuan juga difokuskan pada elevasi dan kemiringan; aspect tetap fitur pada metode. |
| 10 | Abidin | OK → OK | “Geomatics, Natural Hazards and Risk 4.3 (2013). Daring 3 Juli 2012, pp. 226–240” — hlm. 44 (48). BibTeX tetap lima penulis Abidin/Andreas/Gumilar/Sidiq/Fukuda dan key `abidin2015`. |
| 11 | Tadono | OK → OK | Entri Tadono “pp. 157–162” — hlm. 45 (49); key `tadono2016` tetap. |
| 12 | Domain transisi | PARTIAL → OK | “Jumlah piksel pada kedua analisis tidak identik” dan “kontribusinya terhadap selisih tersebut belum dipisahkan” — hlm. 34 (38). Domain tabel dibedakan; registrasi grid tidak lagi dinyatakan sebagai sebab tunggal yang sudah dibuktikan. |
| 13 | Konsistensi istilah label | PARTIAL → OK | “Istilah non-banjir pada pelaporan sampel dan piksel selanjutnya merujuk pada kelas 0 menurut definisi proksi ini” — hlm. 7 (11). Subbab 4.8 merujuk definisi 2.2 dan prosedur 3.5 dengan label LaTeX — hlm. 40 (44). |

Catatan pelokasian: handoff lama menyebut beberapa nomor subbab yang tidak persis sama dengan dokumen aktual, misalnya atribusi Meadows yang diperiksa ada pada latar belakang, dan pembandingan Tique pada tabel 2.8. Bukti di atas memakai isi dan pagination PDF aktual, bukan menganggap seluruh nomor dalam handoff benar.

## B dan E. Efek samping, klaim tersisa, dan revisi konkret

| Lokasi / halaman akhir | Kutipan sebelum T12 | Tingkat | Revisi yang diterapkan / batas bukti |
|---|---|---|---|
| RM1/tujuan, hlm. 3–5 (7–9); simpulan hlm. 42 (46) | “elevasi, kemiringan lereng, dan arah lereng” sebagai sasaran perbandingan | SEDANG | Sasaran deskriptif diselaraskan menjadi elevasi dan kemiringan; aspect tetap input dan tidak dipromosikan menjadi temuan yang belum dilaporkan. |
| 3.7, hlm. 19–20 (23–24); pembahasan hlm. 38 (42) | “hanya sumber elevasi dan input yang dibersamaan”; “peta … dengan daya diskriminasi yang tinggi” | TINGGI | Input/jalur latihan dijelaskan berbeda, dan kalimat pembahasan memisahkan peta GEE dari angka diskriminasi sklearn terhadap label proksi. Tidak mengklaim AUC sebagai validasi peta. |
| 4.1, hlm. 28 (32); 4.8 hlm. 38 (42) | Selisih “merupakan gabungan” sebab datum/pengukuran; variasi slope “akibat … sensor dan acuan vertikal” | SEDANG | Nyatakan kontribusi penyebab belum dipisahkan; acuan tinggi yang sama tidak menjelaskan selisih SRTM–AW3D30 melalui beda model geoid. |
| 2.2/4.8, hlm. 7/40 (11/44) | Contoh piksel tanpa akuisisi S1; “hasil ekstrapolasi spasial model” di seluruh area luar JRC | TINGGI | Tidak mengasumsikan data S1 hilang. Nyatakan kandidat kelas 0 dapat berasal dari luar dukungan positif, sehingga area tersebut bukan otomatis area tanpa sampel latihan sama sekali. |
| 4.5, hlm. 33–34 (37–38) | Pola spasial “konsisten pada tiga skema pengambilan sampel”; beda jumlah piksel “akibat perbedaan registrasi grid” | SEDANG | Batasi ringkasan pola pada peta eksperimen utama yang dirangkum Tabel 8; registrasi/grid dan kriteria valid menjadi perhatian, bukan sebab yang telah diisolasi. |
| 4.8, hlm. 39 (43), serta pengantar Bab IV | Perluasan domain “meningkatkan ROC-AUC”; angka 0,17 sebagai efek desain | SEDANG | “bersifat deskriptif dan tidak mengisolasi pengaruh domain atau satu komponen desain tertentu”; semua angka tetap. |
| 4.8, hlm. 40 (44) | Kecocokan label 70% “akibat pembaruan arsip Sentinel-1” | SEDANG | “perbedaan ini belum dapat diatribusikan hanya pada pembaruan arsip Sentinel-1.” Angka 70% tidak diubah atau dianggap validasi lapangan. |
| 4.8, hlm. 41 (45) | “meskipun perbandingan antarproduk tetap valid” | SEDANG | “meskipun perbandingan antarproduk memakai label yang sama.” Label bersama adalah kontrol prosedural, bukan jaminan ranking kebal bias. |
| 1.1, hlm. 2 (6) | “tidak satu pun produk menempati posisi terbaik pada seluruh konteks penilaian” | SEDANG | Ganti dengan temuan FABDEM dan batas interpretasi kondisi/metrik yang didukung abstrak Meadows; tidak melunakkan kalimat itu menjadi klaim universal baru. |
| Tabel 2.8, hlm. 11 (15) | “Variabel lain dikontrol sehingga fokus pada sumber DEM” | KECIL | Perjelas fokus penelitian ini: “Fokus variasi sumber DEM pada satu algoritme RF”; tidak menyiratkan faktor studi lain tidak dikontrol. |

### Pemeriksaan rujukan dan pengulangan

- Penomoran tetap Bab I–V dan subbab 4.1–4.8. Tidak ditemukan rujukan LaTeX yang undefined pada hasil build akhir.
- Daftar isi/aux ikut diperbarui: awal 3.9.2 berpindah dari hlm. 23 ke 24 dan awal 4.6 dari hlm. 34 ke 35. Rujukan berbasis label tetap terselesaikan; nomor halaman konsultasi memakai PDF akhir, bukan PDF T11.
- Definisi umum kelas 0 berada di 2.2; pengulangan di 4.8 dipertahankan karena membahas implikasi, bukan mendefinisikan kelas dengan makna lain.
- Referensi prosedur pembentukan inventory menggunakan `\ref{ssec:flood-inventory}`, sedangkan pembahasan memakai label `ssec:pembahasan` yang sudah ada.
- Pemakaian aspect sebagai fitur tidak disapu menjadi nol; yang dihapus adalah janji/hasil deskriptif yang tidak didukung. Demikian pula EGM2008 tetap benar untuk GLO-30.
- Key sitasi dan metadata `.bib` tidak berubah pada T12. Pernyataan Meadows mengenai peran penting tutupan lahan tidak dilemahkan tanpa alasan: abstrak sumber memang menyebutnya faktor utama galat vertikal.

### [GATED - perlu cek artefak]

Angka pembanding 1.870 titik, kecocokan 70%, dan CV domain terbatas sekitar 0,70 tetap angka historis yang dilaporkan naskah. Audit round-2 tidak memiliki tabel pasangan label/run/split yang cukup untuk memverifikasi independen seluruh klaim itu. Karena itu tidak dibuat klaim sebab pasti, tidak diciptakan angka pengganti, dan tidak dinyatakan bahwa seluruh hasil historis salah. Kesesuaian terhadap studi acuan bukan validasi ground truth independen. Ini permintaan ketertelusuran arsip, bukan usulan eksperimen baru.

## C. Kejelasan offset 4.1

**Redaksi yang diterapkan:** “SRTM dan ALOS AW3D30 sama-sama memakai model geoid EGM96 sebagai acuan tinggi; karena itu, selisih keduanya tidak dapat dijelaskan oleh perbedaan model geoid.”

Kalimat berikutnya menempatkan GLO-30 pada EGM2008 dan menyatakan kontribusi penyebab belum dipisahkan. Untuk pembaca non-geodesi, frasa “sebagai acuan tinggi” menerangkan fungsi model geoid, tanpa menyamakan dua produk atau menyimpulkan semua perbedaannya berasal dari sensor. Offset −1,56/+0,39 m dipertahankan. Dijelaskan pula bahwa yang dihitung adalah rerata selisih pada dukungan valid bersama, bukan pengurangan dua rerata dengan domain berbeda. Bukti kode/output tersimpan: notebook sel 27, `subtract` sebelum `reduceRegion(mean)`, AW3D30 +0,39494527631611825; notebook tidak dijalankan atau diubah.

## D. Lima topik konsultasi Dr. Iqbal — urut prioritas

| Prioritas / topik | Isu singkat | Maksud / masukan yang diharapkan | Halaman acuan akhir |
|---|---|---|---|
| 1. Makna label dan asimetri dukungan | Kelas 0 bukan bukti kering, sementara contoh positif hanya dibentuk dalam dukungan JRC. | Meminta penilaian apakah batas klaim reproduksi label proksi dan penjelasan asimetri sudah cukup tegas untuk proposal ini. | 7 dan 40 (PDF 11 dan 44), 3.5 pada 16–17 (20–21). |
| 2. Hubungan peta dan metrik | GEE membentuk peta dengan input/jalur latihan berbeda dari evaluasi sklearn. | Menyepakati cara memisahkan kesimpulan sensitivitas peta dari kesimpulan diskriminasi model agar pembaca tidak menganggap satu validasi yang sama. | 19–20 (23–24), 38 dan 41 (42 dan 45). |
| 3. Perbandingan desain sampel dan ketidakpastian | Kontras domain sempit versus penuh bersifat deskriptif dan tidak mengisolasi satu efek kausal, sementara inferensi blok memakai 16 unit. | Meminta prioritas penekanan saat menjelaskan kontras historis, CI, dan batas independensi spasial tanpa mengklaim leakage hilang. | 21 (25), 27 (31), 31–33 (35–37), 39 (43). |
| 4. Lingkup topografi dan interpretasi datum | Hasil deskriptif meliputi elevasi/slope, aspect merupakan input, dan sebab offset belum dipisahkan. | Meminta persetujuan keselarasan RM1–hasil–simpulan serta kejelasan penjelasan geoid bagi pembaca non-geodesi. | 3–5 (7–9), 18 (22), 28 (32), 42 (46). |
| 5. Pesan praktis hasil perbandingan DEM | GLO-30 unggul pada ukuran evaluasi yang dilaporkan, tetapi selisih kecil, urutan SRTM/AW3D30 tidak selalu sama, dan sensitivitas berbeda menurut tutupan lahan. | Menentukan rekomendasi bersyarat paling relevan untuk pesisir serupa tanpa menyatakan DEM terbaik universal atau luas kelas risiko sebagai luas genangan aktual. | 31–35 (35–39), 38–39 (42–43), 42–43 (46–47). |

## Verifikasi teknis dan batasnya

- XeLaTeX tiga lintasan: berhasil, **50 halaman**, **0 undefined**.
- **7 overfull** tetap pada paragraf/tabel warisan yang sama seperti baseline pada toolchain ini; tidak ada overfull baru. Underfull tetap tercatat dan tidak dianggap nol warning.
- Terdapat **1 warning `inputenc`**: paket diabaikan oleh mesin UTF-8 XeLaTeX. Warning yang sama muncul ketika T11 asli dibangun pada sandbox ini; tidak dinyatakan sebagai 0 warning. Preamble tidak diubah untuk mengejar perubahan di luar lingkup.
- Dependensi XeLaTeX/biber dipasang dan setup proyek dipersistensikan agar build berikutnya dapat diulang; tidak ada dependensi/model ilmiah yang diubah.
- Seluruh **300 berkas zona beku** yang tercakup baseline SHA256 tetap identik. Semua rentang matematika inline lama pada TEX identik; penambahan 17 input adalah dokumentasi skema GEE yang sudah ada, bukan perubahan hasil.
- PDF: sweep 13 butir koreksi, klaim lama, angka acuan, bibliografi, dan rujukan; inspeksi visual halaman perubahan. Paket ZIP diverifikasi 9 anggota dan path gambar terhadap sumber saat ini, ukuran 2.343.873 byte.
- Tidak mengklaim pemeriksaan mask AOI per piksel, validasi ground truth, atau kesetaraan estimator telah diselesaikan oleh revisi teks ini.

## Sumber verifikasi sumber luar

Penjelasan datum dan atribusi Meadows mengikuti pemeriksaan sumber resmi pada audit sebelumnya; tidak menggunakan handoff sebagai bukti ilmiah:
- AW3D30 v4.1: https://developers.google.com/earth-engine/datasets/catalog/JAXA_ALOS_AW3D30_V4_1
- Meadows: https://doi.org/10.1080/17538947.2024.2308734
- Abidin: https://doi.org/10.1080/19475705.2012.692336
- Tadono: https://doi.org/10.5194/isprs-archives-XLI-B4-157-2016
