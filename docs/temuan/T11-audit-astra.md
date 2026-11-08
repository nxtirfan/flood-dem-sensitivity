# T11 — Audit GPT-Astra (8 Nov 2026) & Eksekusi Koreksi Teks

## 0. Ringkasan
Audit eksternal (laporan GPT "astra max", tersimpan `.hoplite/artifacts/audit-final.md` di sisi pengguna) menemukan 6 temuan TINGGI + 8 SEDANG + beberapa RENDAH. Semua temuan TINGGI diverifikasi agen ke artefak asli **sebelum** diedit; semuanya terkonfirmasi. Eksekusi = **koreksi klaim/metode tertulis/bibliografi SAJA** — tanpa menyentuh data beku, sampling, seed, model, CSV, raster, atau rerun. Naskah tetap dianggap konsisten dengan keluaran tersimpan; pesan audit bahwa kecocokan angka adalah konsistensi-naskah-vs-artefak, BUKAN validasi model terhadap banjir lapangan, dipatuhi (tidak ditambahkan claim validasi baru).

## 1. Verifikasi temuan (agen, ke artefak)

| # | Temuan TINGGI | Verifikasi agen | Hasil |
|---|---|---|---|
| 1 | Datum AW3D30 keliru (naskah: EGM2008) | Web: JAXA Product Description AW3D30 v4.1 + katalog GEE `JAXA/ALOS/AW3D30/V4_1` → **EGM96** | SALAH di naskah, 4 titik + 1 klausul; koreksi diterapkan |
| 2 | Metrik sklearn ≠ validasi peta GEE (GEE: raw landcover, 17 input, 300 pohon; sklearn: one-hot, 24 input, 400 pohon) | Notebook canon: cell 15 (GEE features), cell 35 (get_dummies, 400 pohon) | TERKONFIRMASI; kalimat pemisahan ditambah di 3.7 (jalur tetap terkendali dalam masing-masing pipeline) |
| 3 | Kelas-0 terkurung dukungan JRC | Sel 21/31 (propagasi mask JRC) + T04 | TERKONFIRMASI; definisi label ditambah di 2.2 (label referensi) & 4.8 (keterbatasan) |
| 4 | Klaim urutan lengkap 5/5 seed salah | `hasil_kaggle/multiseed_holdout.csv`: seed 42 SRTM 0.949691 > AW3D30 0.949468; seed 100 SRTM 0.953995 > AW3D30 0.953426; GLO-30 tertinggi 5/5 | TERKONFIRMASI; 4.4 ditulis ulang (GLO-30 5/5; AW3D30–SRTM berbalik tipis pada 2 holdout, selisih ≤ 0,0006) |
| 5 | Kritik Tique "lebih terkontrol" tidak tertopang | Naskah 2.8 & tabel 2.10 | DITAHAN; difase fakta (Tique = rancangan banyak-faktor, ini = perlakuan satu faktor) |
| 6 | Simpulan aspect tanpa bukti | `dem_stats.csv` hanya elevasi+slope; tidak ada ringkasan aspect | KESIMPULAN (5.1 item 1) diubah: perbedaan dilaporkan pada elevasi & slope; aspect masuk sebagai input dekomposisi |

Temuan SEDANG:
1. **Skema fitur berubah antar-seed** — diverifikasi langsung ke data beku `data/frozen/multiseed/sample_seed_*_raw.csv`: kelas lc عام `20` hadir pada seed 100/2024/7 (9 kelas → 25 input), tidak ada pada main & seed 42/99 (24 input). Ditambah catatan skema fitur di 4.4 (pasangan intra-seed tetap valid).
2. Label slope<5° SRTM — sudah diakui naskah; tidak diubah.
3. Bootstrap 16 blok — kalimat "1.000 resample ≠ 1.000 unit spasial independen" ditambah di 3.8.
4. Moran raster vs OOF — naskah 4.7.2/4.8 sudah memisahkan; tidak diubah.
5. Domain transisi vs Moran — catatan domain (registrasi grid reduksi GEE vs grid ekspor) ditambah di 4.5.
6. Angka historis (70%, 1.870 titik, ~0,70) — artefak run pembanding tersimpan (v23/olds); status dianggap tercatat; naskah tidak diubah.
7. Meadows "tidak terdapat satu produk terbaik otomatis" — dilunakkan 2.1 (keunggulan bergantung kondisi & metrik).
8. Abidin — Crossref `10.1080/19475705.2012.692336` = GNHR **4(3): 226–240, 2013** (daring 3 Jul 2012), 5 penulis (+ T.P. Sidiq, TANPA Pohan/Deguchi). `references.bib` diselaraskan.

Temuan RENDAH yang dieksekusi:
- `tadono2016` pages 157–161 → **157–162** (cocok katalog GEE/ISPRS).
- ZIP sumber dibangun ulang dengan struktur `figures/fig_*.png` (tepat dengan jalur `\includegraphics`).
- Tidak diubah: panel pagetitle peta kecil (visual, halaman tetap), checkpoint T10 `6c656fce…` (md5 canon kini memang berubah; catatan STATUS kini mencantumkan nilai final), Moran output lama di notebook (historis; CSV aktif adalah sumber naskah).

## 2. Kalimat kunci yang mengganti interpretasi AW3D30
4.1 (offset): "…gabungan perbedaan acuan vertikal bawaan antarproduk (EGM96 untuk SRTM dan ALOS AW3D30, EGM2008 untuk Copernicus DEM GLO-30) serta perbedaan karakteristik pengukuran; karena SRTM dan ALOS AW3D30 memakai model geoid yang sama, selisih kedua produk tidak dapat disandarkan pada perbedaan datum geoid." Offset AW3D30 +0,395 m & APPLY vertical offset=FALSE TIDAK diubah.

## 3. Build final
- `xelatex` ×2 + `biber`: **PDF 50 hlm** (49→50 karena kalimat tambah), 0 undefined/0 warning; overfull 7 (warisan).
- ZIP `proposal_revisi-final_source.zip` 2.344.058 B (9 entri, figures/ terstruktur).
- Sweep PDF warisan angka lamabersihkalima: "EGM2008 pada Copernicus DEM GLO-30 serta ALOS" 0; "terisolasi" 0; pages 401 0; "bertahan secara" 0; "lebih terkontrol" 0; "226-240" 1; "157-162" 1.

## 4. Sisa (dari laporan audit, memerlukan alasan)
- Semua saran "wajib kuasai lisan" (aspek kualitas label, jalur GEE/sklearn, makna CV blok/bootstrap/Moran) = bahan konsultasi dosen, bukan ubah naskah.
- Item "bisa ditunda dengan batasan dinyatakan" (label independen, buffer CV, penyamaan pipeline, fitur tetap lintas seed, koreksi geoid, generalisasi) semua memerlukan eksperimen baru → tidak dieksekusi sesuai batasan audit.
