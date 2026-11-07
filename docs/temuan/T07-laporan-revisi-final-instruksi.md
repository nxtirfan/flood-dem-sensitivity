# T07 — Laporan Revisi Final per Instruksi A–K (4 Nov 2026)

Dokumen sumber: `Proposal Baru\proposal_revisi-final.tex` (satu-satunya file .tex yang diutak-atik).
Hasil kompilasi: **PDF 43 hlm, 747.731 byte, 0 undefined, 0 warning, overfull 7 (3 legacy 6,45–8,67 pt + 4 mikro 1,60–2,95 pt — semua warisan), biber ulang (bbl baru)**.

---

## A. PERUBAHAN TEKS (8 titik, semua terverifikasi ada di PDF)

| # | Kaplok (jembatan) | Frasa | Sebelum → Sesudah | Alasan |
|---|---|---|---|---|
| A1 | Naskah 3.7 `proposal_revisi-final.tex` (L~1035) | "Konfigurasi Random Forest ... 300 pohon ... implementasi scikit-learn dengan 400 pohon" | dipertahankan, parafrase dihapus (Benarkan 300/400 via kode kernel: GEE `RF_GEE = dict(numberOfTrees=300...)`, sklearn `RF_SKLEARN = dict(n_estimators=400, min_samples_leaf=2,...)` menemukan di `Flood_DEM_Sensitivity_Notebook_v26.ipynb`) | B1 |
| A2 | **(SISIPAN BARU 3.7)** setelah paragraf config (L~1048) | — | `Implementasi pemodelan dilakukan pada dua lingkungan. Peta probabilitas spasial dihasilkan melalui implementasi Random Forest pada Google Earth Engine dengan sampel dan parameter yang sama, sementara evaluasi kinerja model dilakukan pada implementasi Random Forest scikit-learn dengan sampel dan parameter yang setara. Statistik spasial pada peta berasal dari implementasi pertama, sedangkan metrik evaluasi berasal dari implementasi kedua.` | B1 (paragraf diberikan di instruksi; dimasukkan verbatim) |
| A3 | 3.5 (L~933) | Slope filter = "efektif berfungsi untuk menyingkirkan artefak... tidak menggeser populasi label" | `bertujuan menyingkirkan artefak geometris radar pita-C pada area berlereng curam, seperti layover dan foreshortening, bukan membatasi domain pesisir` → `digunakan untuk mengurangi kemungkinan masuknya piksel dengan karakteristik lereng yang berpotensi menghasilkan artefak pada inventori banjir, misalnya artefak geometris radar pita-C (layover dan foreshortening) pada area berlereng curam, bukan membatasi domain pesisir` | C1 (frasa literal TIDAK ada di naskah — lihat D1; terapkan padanan ke dekrastasi) |
| A4 | 4.2 blok deskripsi slope (L~1272) | sama idiom | `tujuan kriteria penyaringan lereng di bawah 5°, yaitu menyingkirkan artefak geometris radar pita-C (layover dan foreshortening)... tanpa memangkas domain genangan` → `kriteria penyaringan lereng di bawah 5° yang digunakan untuk mengurangi kemungkinan masuknya piksel dengan karakteristik lereng yang berpotensi menghasilkan artefak pada inventori banjir, seperti artefak geometris radar pita-C (layover dan foreshortening)...` | C1 |
| A5 | Blok akhir 4.2 (L~1198) | "jauh melampaui selisih antarproduk elevasi dan menunjukkan bahwa estimasi performa sangat dipengaruhi desain sampel kelas non-banjir" | `Selisih sekitar 0,17 ini menunjukkan bahwa hasil evaluasi perlu ditafsirkan dengan mempertimbangkan desain pengambilan sampel kelas non-banjir.` | C3 (pengganti #2 dipakai; #1 kehilangan makna duplikat — lihat catatan rule 3) |
| A6 | Pembahasan (L~1576) | idiom perbandingan | `(ΔAUC ≈ 0,17), jauh lebih besar daripada selisih antarproduk elevasi (ΔAUC ≈ 0,01)` → `... dibandingkan selisih antarproduk elevasi (ΔAUC ≈ 0,01)` | C3 (varian kalimat di 4.7; angka 0,17 & 0,01 tetap; morph ke deskriptif) |
| A7 | Pembahasan (L~1558) | "perbedaan delineasi spasial yang bermakna bagi perencanaan wilayah" | `... perbedaan delineasi spasial yang dapat menjadi pertimbangan dalam interpretasi hasil pemetaan kerawanan banjir` | C2 |
| A8 | Kesimpulan item 1 (L~1672) | "berbeda secara statistik dan spasial" | `menunjukkan perbedaan secara deskriptif dan spasial, termasuk nilai median elevasi dan offset vertikal antarproduk` | D1 |
| A9 | Kesimpulan item 2 (L~1674) | "sehingga satu-satunya komponen yang berbeda antarpeta adalah sumber elevasi" | `Ketiga peta probabilitas kerawanan banjir dihasilkan menggunakan sampel, label, dan konfigurasi pemodelan yang dipertahankan sama, dengan lima prediktor turunan DEM yang disesuaikan menurut produk elevasi yang digunakan. Perbedaan hasil antarpeta kemudian dianalisis sebagai sensitivitas terhadap pergantian sumber elevasi dalam kerangka eksperimen terkontrol. Pola spasial ketiganya serupa dengan variasi terbatas pada kelas risiko sangat tinggi (Subbab 4.3 dan Subbab 4.5).` | D2 (lima prediktor = elevasi, slope, aspect_sin/cos/valid — telah diverifikasi vs `training_sample_features.csv`: 5+11+8 = 24) |
| A10 | 3.7 (L~1037) | "tebal minimum daun" | `jumlah minimum sampel pada simpul daun (minimum samples leaf)` | G |
| A11 | Bab V item saran ke-2 (L~1678) | "kesensitifan" | `sensitivitas` | G |
| A12 | Keterbatasan P2 4.7 (L~1600) | H.5 kosong | tambahan 1 kalimat: `Dengan demikian, hasil evaluasi perlu ditafsirkan sebagai kemampuan model mereproduksi label proksi tersebut, bukan sebagai ukuran akurasi terhadap seluruh kejadian banjir aktual di lapangan.` | H.5 (poin 5 belum tertulis; disisipkan minimal sesuai wacking instruksi) |

---

## B. VERIFIKASI NUMERIK (dilakukan ulang seluruhnya; sumber = artefak v24/v26)

| Klaim naskah | Sumber artefak | Status |
|---|---|---|
| Holdout: 0,932 / 0,940 / 0,936 (Tabel+pembahasan) | `v26 model_metrics` roc_auc 0.9318/0.9404/0.9360 | ✔ |
| Akurasi 0,874/0,890/0,878; presisi 0,847/0,858/0,849; recall 0,914/0,934/0,921; F1 0,879/0,895/0,883 | `v26 model_metrics` idem | ✔ |
| CV: 0,870/0,890/0,875 (mean-fold); akurasi 0,802/0,824/0,804; F1 0,796/0,826/0,802 | `v26 spatial_cv_metrics` auc_spatial_cv_prob (kolom per fold, rata-rata = 0.8699/0.8899/0.8747); akurasi & F1 juga 100% cocok | ✔ |
| Pooled OOF 0,903/0,917/0,908 — TIDAK dikutip di naskah (F.11 lolos) | hanya di `v26 spatial_cv_delta_auc_bootstrap_pixel_legacy.csv` (auc_a/auc_b) | ✔ (diam) |
| ModelYouden (3.8): 0,52/0,495/0,521; 4.3 menyatakan 0,5 utama | `v26 model_metrics` best_threshold_youden 0.5205/0.4953/0.5209 | ✔ **B2 = konsisten, tanpa revisi** |
| Block bootstrap: rerata AUC 0,894/0,910/0,899; DM SRTM−GLO30 −0,0155 [−0,0250;−0,0072]; DM GLO30−AW3D30 +0,0108 [+0,0041;+0,0198]; DM SRTM−AW3D30 −0,0047 [−0,0096;+0,0013] (muat nol); "maksimal ~0,016" | `v26 spatial_cv_delta_auc_bootstrap` persis; "maks 0,016" = |−0,0155| | ✔ |
| Pixel-bootstrap legacy: 0,0141 [0,0109; 0,0173] | `v26 spatial_cv_delta_auc_bootstrap_pixel_legacy` | ✓ |
| Multi-seed: tab. 0,939±0,014 / 0,947±0,010 / 0,940±0,012 (holdout) dan 0,869±0,017 / 0,889±0,013 / 0,877±0,017 (CV) | `multiseed_summary` | ✔ |
| "GLO-30 > AW3D30 > SRTM bertahan 5/5 seed di kedua skema" | `multiseed_delta_auc` per-seed tanda konsisten semua pasangan, 5/5, kedua skema | ✔ |
| Δ CV SRTM−AW3D30 −0,0079±0,0034; Δ holdout −0,0012±0,0021; Δ holdout GLO30−AW3D30 +0,0070±0,0027; Δ holdout SRTM−GLO30 −0,0082±0,0048 | `multiseed_delta_auc` | ✔ |
| 4.1: mean elevasi 40,62/39,06/41,36; median 8,50/4,94/8,53; offset GLO30 −1,56, AW3D30 +0,39; mean slope 3,03/2,46/3,13 | `v24 dem_stats` untuk semua kecuali offset; offset dari log kernel v26 "Offset vertikal rata-rata: glo30 -1.5601, aw3d30 0.3949" — **offset adalah selisih rata-rata per piksel (metode kernel), bukan selisih mean dem_stats** (dem_stats diff-of-means = +0.74) | ✔ dengan catatan estimasi berbeda (D2, catatan) |
| 4.2: median slope banjir 1,35/0,28/0,96°; p99 SRTM 4,92°; maks 11,48°; share <5° 98,99/99,97/98,76; median |Δslope| 0,85–1,24° | hitung ulang di `training_sample_features.csv` (2978 titik banjir, persentil-linear): 1,3469→1,35; 0,2808→0,28; 0,9556→0,96; p99 4,9162→4,92; maks 11,4838→11,48; share 98,99/99,97/98,76; median |Δslope| 0,845/0,956/1,235 → "0,85 hingga 1,24" | ✔ |
| Spearman "tidak melebihi |0,06|" | hitung ulang = \-0.024 / +0.0124 / +0.0604 (titik banjir) → maks 0,0604 | ✘ DIPERBAIKI: "tidak melebihi |0,07|" (dengan keterangan di kalimat) |
| Luas kelas 5 = 105,2/114,2/113,4 km²; kelas 1 = 756,7/822,6/772,5 km² | `v24 area_per_risk_class_km2` 105.158/114.173/113.430 & 756.66/822.59/772.54 | ✔ |
| AAU total 1,469.555 piksel; 94.348 & 36.959 (SRTM→GLO30); 25.655 (SRTM→GLO30); diag kelas-2 174.013, kelas-5 103.374 (SRTM→AW3D30) | `v24 transition_*` | ✔ |
| Sensitivitas peta: mean |Δp| 0,056/0,037/0,048; kesepakatan 79,4/83,9/81,3 | `v24 sensitivity_summary` | ✔ |
| WorldCover (4.6 + pembahasan): pohon 95,6–96,8 (Δp 0,011–0,021); terbangun 87,2–90,4; semak 54,0 (GLO30-AW3D30) & 60,2 (SRTM-GLO30); |Δp| max 0,095 (SRTM-GLO30); bare 63,6 & 66,9; mangrove 61,8–64,3 (pasangan GLO30) dan 61,8–73,2 (pembahasan); air 77,4–82,7; wetland 72,6–78,3; shrubland / bare / mangrove rentang 54,0–70,1 / 63,6–75,4 / 61,8–73,2 | `v24 worldcover_sensitivity` semuanya cocok (detail min-max dihitung dari 9 pasangan×metrik) | ✔ |
| Label: 1.410.981 non-banjir & 58.573 banjir; sampel 2.978/kelas (seed 42); n_uji = 1.489 (75:25) | log kernel v26 `Piksel flood tersedia: 58573` + `[probe] label=0 total: 1410981`; `sample_audit` n=2978/jawaban; 5956×0,25=1489 | ✔ |

---

## C. VERIFIKASI DATASET DAN REFERENSI

| Komponen | Kondisi | Status |
|---|---|---|
| Naskah Bab II tabel `tab:data` row WorldCover | "(v200)" | ✔ (sudah sama) |
| Kode GEE | `ESA/WorldCover/v2021 ESA WorldCover 2021: 'ESA/WorldCover/v200'` di `Flood_DEM_Sensitivity_Notebook_v26.ipynb` | ✔ (asset v200) |
| Referensi [21] (key `zanaga2021`) | dari "ESA WorldCover 10 m 2020 v100, Zanaga et al. 2021, DOI 10.5281/zenodo.5571936, 19 penulis" | **DIPERBAKI** ke "ESA WorldCover 10 m **2021 v200**, Zanaga et al. **2022**, DOI **10.5281/zenodo.7254221**, 16 penulis" (dari Zenodo 7254221 & katalog GEE) |
| Key bib | `zanaga2021` dipertahankan (tidak di rename; proposal.tex baseline tidak diutak-atik) | ✔ |
| bbl | `proposal_revisi-final.bbl` diregenerasi via biber; bbl verifikasi "v200 / 7254221 / Daems hadir; v100 / 5571936 / Souverijns hilang" | ✔ |
| Kuinging | `proposal.tex` baseline TIDAK diutak-atik (mtime 11-02), tapi berbagi `references.bib` — PDF lama di baseline tak berubah; bila baseline dikompilasi lagi, ia akan otomatis memakai referensi v200 (seSele senada). proposal.bbl lama (11-01 utk baseline) biarkan. | diinformasikan |

---

## D. TEMUAN YANG BELUM TERSELESAIKAN / CATATAN

1. *C1 literal frase tidak berada di naskah* — frasa `efektif berfungsi untuk menyingkirkan artefak` dan `tidak menggeser populasi label banjir secara substansial` tidak ditemukan; mitra paling dekat yang terjadi = dua ungkapan "menyingkirkan artefak" versi kernel (A3/A4). Pengganti verbatim instruksi `digunakan untuk mengurangi kemungkinan masuknya piksel dengan karakteristik lereng yang berpotensi menghasilkan artefak pada inventori banjir` lewat padanan ini diterapkan; sindukulan kalimat informatif (layover/foreshortening, pesisir) dipertahankan.
2. *C3 padana 4.7 pembahasan (A6)* — kalimatnya versi variasi dari frasa target; diubah ke formula deskriptif `dibandingkan` dengan angka (0,17 vs 0,01) dan kalimat hedging berikut dipertahankan; tidak duplikasi kalimat.
3. *Rule 3 pada C3 di blok akhir 4.2 (A5)* — dua pengganti instruksi mengandung makna mirip di kalimat sama; dipilih #2 ("menunjukkan bahwa hasil evaluasi perlu ditafsirkan dengan mempertimbangkan desain pengambilan sampel") karena menggabungkan keduanya (kalimat includedطلاق), diikuti dengan tetap "Seluruh hasil berikutnya berasal dari desain yang telah diperbaiki._▉**.
4. *Sensitivitas Spearman `|0,06|` dikoreksi ke `|0,07|`* — hitung dari artefak = 0,0604.
5. *Offset AW3D30 +0,39* berasal dari metode kernel (selisih rata-rata per piksel) sesuai log; nilai `dem_stats` diff-of-means = +0,74 adalah estimator lain, tidak diubah di naskah, tetapi tercatat.
6. *Pooled OOF (0,903/0,917/0,908)* tersimpan di artefak, tidak dikutip naskah — selaras permintaan F.11.
7. *P1 rerun label JRC* masih menunggu keputusan user (tidak dikerjakan oleh batch ini; instruksi eksplisit melarang rerun).
8. *Bridging 70% & 1.870 titik* (4.4) dikutip dari verifikasi v23 sebelumnya; tidak dihitung ulang di batch ini.
9. *JRC footprint 12,8%–14,4%* (keterbatasan) berasal dari probe `T04` (2026-10-20), tidak dihitung ulang di batch ini.

---

## E. DAFTAR FILE OUTPUT

| File | Status |
|---|---|
| `Proposal Baru\proposal_revisi-final.pdf` | 43 hlm, 747.731 B, 0 undefined, overfull 7 sama |
| `Proposal Baru\proposal_revisi-final.tex` | selesai diutak-atik (sumber aktual) |
| `Proposal Baru\proposal_revisi-final.bbl` | baru (biber, v200 di [21]) |
| `Proposal Baru\references.bib` | entri zanaga2021 dipermbu4 ke v200 (2022, DOI 7254221) |
| `docs\temuan\T07-laporan-revisi-final-instruksi.md` | laporan ini |
| `docs\STATUS.md` | diperbaharui menyesuaikan kondisi |
