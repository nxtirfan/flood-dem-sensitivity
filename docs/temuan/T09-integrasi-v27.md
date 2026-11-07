# T09 — Integrasi v27 ke naskah (5–6 Nov 2026)

## 1. Ruang lingkup
Paket integrasi hasil run Colab v27 ke `Proposal Baru/proposal_revisi-final.tex` sesuai instruksi user (paket A–H). Menutup: sisip Moran's I (metodologi 3.8.1, hasil 4.7), gambar peta probabilitas, re-quote angka v26 → v27, sitasi Moran 1950, notebook, zip sumber, dan pemindahan kredensial.

## 2. Yang diubah di naskah
1. `references.bib` + entri `moran1950` (Biometrika 37(1/2):17–23, DOI 10.1093/biomet/37.1-2.17, terverifikasi via situs penerbit); biber ulang; sitasi `[28]` muncul di 3.8.1 pada kalimat definisi.
2. **Bab III — subsubbab baru 3.8.1 Diagnostik Autokorelasi Spasial** (verbatim `Teks_Proposal_Moran_I.md` §A), disisip sebelum `\subsection{Analisis Sensitivitas}`: 5.956 titik; kNN k=8 UTM 49S row-standardized; kepekaan k=5/12; formulasi I dan p (B=9.999 titik / B=999 raster, seed 42); dua kelompok data (OOF-prob & OOF-residual vs raster GEE 300 pohon); justifikasi unit titik bukan 16 blok (median 305 titik, maks 967, ada blok tanpa salah satu kelas, masalah modifiable areal unit); median jarak tetangga 149 m hingga 1,5 km; batas tafsir diagnostik.
3. **Bab IV — subbab baru 4.7 Analisis Autokorelasi Spasial** (+ 4.7.1 titik sampel OOF, 4.7.2 raster) SEBELUM Pembahasan yang kini menjadi 4.8 otomatis:
   - **Tabel 9** — Moran's I titik sampel (n=5.956, KNN k=8, B=9.999, E[I]=−0,000168): label 0,677 (z 109,7); OOF SRTM 0,886 (143,6), GLO-30 0,877 (142,9), AW3D30 0,882 (142,9); residual 0,377 (61,4), 0,355 (57,9), 0,364 (59,1); p dua sisi 0,0001 semua.
   - **Tabel 10** — kepekaan residual OOF k=5/8/12: 0,418/0,377/0,345; 0,393/0,355/0,326; 0,405/0,364/0,334 (semua turun ketika k naik; pola searah).
   - **Tabel 11** — raster probabilitas: I = 0,970064/0,964818/0,967303; piksel valid 3.292.156/3.292.156/3.277.652; E[I] = −3,0375×10⁻⁷ (SRTM & GLO-30), −3,0510×10⁻⁷ (AW3D30); p=0,001 (B=999, seed 42).
   - Paragraf pembahasan verbatim (§B) mencakup justifikasi block bootstrap, rasio autokorelasi residual terhadap label 52–56 persen, share pasangan tetangga lintas fold 4,4 persen (k=8), dan pembatasan tafsir: OOF-prob / OOF-residual / raster TIDAK disatukan.
   - **Gambar baru fig:prob-maps** (`figures/fig_prob_maps.png`, disalink dari `maps_local/local_prob_maps.png`) di 4.3; caption menyebut batas kelas 0,2/0,4/0,6/0,8 dan cakupan grid ekspor yang mencakup wilayah di luar batas penelitian.
4. **Keterbatasan 4.8** — dua paragraf baru (verbatim §C) setelah paragraf granularitas spatial CV, sebelum Subbab 5.2.
5. **Kesimpulan Bab V item 3** — dua kalimat Moran ditambah setelah kalimat spatial CV/block bootstrap (tanpa membuat kesimpulan ke-5), dengan rujukan Subbab 4.7.
6. Rujukan literal `Subbab~4.7` → `Subbab~4.8` pada 3 titik.
7. **Re-quote angka v26 → v27** (sumber: CSV v27):
   - Luas kelas 5: 105,2/114,2/113,4 → **105,1/114,1/113,5 km²** (kelas 1 tetap 756,7/822,6/772,5 km²).
   - Transisi SRTM→GLO-30: 94.318 → 94.306; 36.935 → 36.869; 25.687 → 25.679 piksel.
   - Diagonal SRTM–AW3D30: 173.994 → 174.072; 103.420 → 103.412 piksel.
   - WorldCover: semak g-a 55,0→54,3; semak s-g 60,7→60,4; terbuka 63,6→63,4 dan 67,0→66,6; mangrove 62,0→61,5 dan 64,1→63,8; air 77,5→77,4 dan 82,8→82,7; lahan basah 72,5→72,6 (78,2 tetap). Rentang Pembahasan: 54,3–69,9; 63,4–75,7; 61,5–72,7 persen.
   - **Tetap** (sudah cocok v27): |Δp| 0,056/0,037/0,048; sensitivitas antarpeta 79,42/83,95/81,31 persen; |Δp| semak s-g 0,094; pohon 95,6–96,8; terbangun 87,2–90,4; lahan basah 78,2; rentang luas ekstrem 2–9 persen.

## 3. Temuan audit (perlu keputusan user)
1. **Raster `risk_class_*.tif` / `agreement_*.tif` TIDAK selaras CSV:**
   - `risk_class_*.tif` memuat ±1.969.549 piksel kelas 5 (±60 persen grid) sedangkan CSV luas kelas 5 hanya ±105–114 km² (±116–127 ribu piksel).
   - Kelas 1–4 dari `risk_class_*.tif` **persis cocok** dengan CSV luas (840.848 px = 756,7 km² dst.) → indikasi kuat defek cabang klasifikasi risiko: piksel p<0,2 dan no-data ikut terlempar ke kelas 5.
   - Kesesuaian antar-KELAS dari risk tif = 0,9098/0,9297/0,9180; share tif `agreement_*` langsung = 0,3482/0,3682/0,3590 — keduanya tidak cocok dengan CSV `sensitivity_summary` (79,42/83,95/81,31 persen) maupun satu sama lain.
   - Kesesuaian antar-DEM yang dihitung sendiri dari bin `prob_*.tif` = 90,95/93,14/91,94 persen — menegaskan bahwa angka CSV sumber GEE kemungkinan besar memakai geometri AOI (tidak tersedia lokal), sehingga tidak bisa direplikasi dari raster bbox.
2. **Hanya `prob_*.tif` yang selaras dan dipakai** (fig:prob-maps); panel risk/agreement/delta DITAHAN dari naskah sampai sel `PREPARE_MAPS` diperbaiki (patch cabang klasifikasi risiko + kombiner kesesuaian) dan di-run ulang.
3. PNG `local_agreement_maps.png`/`local_risk_class_maps.png`/`local_delta_maps.png` tidak diintegrasikan karena berakar pada raster yang sama yang bermasalah.

## 4. Validation_v26_vs_v27.csv & Laporan_v27.md
- Kolom `catatan` pada CSV diisi hasil audit manual (bukan klaim verifikasi otomatis); kolom `status` TIDAK_ADA_REFERENSI dipertahankan; notebook v27 tetap sumber kebenaran utama.
- `Laporan_v27.md` ditambah bagian 9: catatan pasca-run Colab, daftar re-quote, temuan raster, pindahnya kredensial.

## 5. Kompilasi & pengemasan
- **PDF 49 halaman** (naik dari 43), 0 undefined, 0 warning; 7 overfull kecil (maks 8,67pt) semuanya legacy.
- Total tabel 11 (+3 Moran), gambar 4 (+fig:prob-maps).
- ZIP sumber baru 2.446.733 B: tex + bbl + pdf + bcf + bib + logo + figures/fig_roc.png + figures/fig_agreement.png + figures/fig_prob_maps.png — **tanpa kredensial, tanpa raster**.
- Kredensial: `gee-service-account.json` dipindahkan dari delivery ke `Proposal Baru/.credentials/`.

## 6. Sisa risiko / lanjutan
1. Peta kesesuaian menunggu rerun `PREPARE_MAPS` dengan patch; setelah jadi, dikirim sebagai kandidat gambar kesesuaian 4.3 atau lampiran.
2. Geometri AOI tidak tersedia sebagai file lokal (grid ekspor = 109,95–111,05 / −7,45…−6,65), sehingga silang luas CSV vs raster di dalam AOI tidak bisa dibuktikan lokal — butuh definisi polygon AOI dari user bila ingin audit lebih dalam.
3. Angka keesuaian PNG v27 (91–93 persen) TIDAK dipakai sebagai angka naskah; naskah tetap memakai CSV `sensitivity_summary` (dihitung GEE di dalam AOI).
