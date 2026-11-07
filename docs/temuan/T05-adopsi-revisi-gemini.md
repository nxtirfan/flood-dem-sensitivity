# T05 — Adopsi Revisi Gemini (Bab IV + sisipan 3.5) ke `proposal.tex` utama

> Tanggal: 2026-10-22 · Status: SELESAI · Sumber: `Proposal Baru\revisi-gemini-argon\`
> (catatan-revisi.md + snapshot tex/bib dari Gemini "Argon")

## 1. Apa yang dilakukan Gemini

Menulis ulang seluruh prosa **BAB IV** (4.1–4.7) + satu paragraf akhir
Subbab 3.5 ke gaya akademik formal Bab I–III, karena dugaan: (a) kalimat
telegrafis bergaya log/`debugging` termos & em-dash 17×, (b) calque — mis.
"validasi kewarasan lolos", "menggelembungkan kedua ekor", "label banjir
mungkin lahir", "keunggulan tidak dapat ditegakkan", (c) kode internal
("se-AOI", "run v22/v24/v26") tanpa pembingkaian, (d) penyusunan angka
a/b/c. Ditambah koreksi notasi ΔAUC dan metadata bib terbatas.

## 2. Verifikasi korektness (hasil pemeriksaan kita)

1. **Angka**: seluruh nilai dipertahankan (dicek beruntun 4.1–4.7: 40,62/39,06/
   41,36; 8,50/4,94/8,53; −1,56/+0,39; 3,03/2,46/3,13; 1.410.981/58.573; 70%;
   median slope & elevasi 4.2; 0,932/0,940/0,936 + tabel holdout/CV + CI
   bootstrap + ± multiseed + bridging 0,802/0,852/0,795/0,792; luas kelas
   105,2/114,2/113,4 & 756,7/822,6/772,5; transisi 94.348/36.959/25.655 +
   diagonal 174.013/103.374; WC 95,6–96,8 dll.) — tidak ada fabrikasi.
2. **Koreksi aritmetika baru oleh Gemini (SAH)**: "rentang ROC-AUC ≈0,009" →
   **0,008** (0,940−0,932 = 0,008); angka lama kami salah.
3. **Koreksi label ΔAUC (SAH, terbukti dari CSV)**: CSV
   `spatial_cv_delta_auc_bootstrap.csv` memakai pair `srtm-minus-glo30`
   (positive: −0,0155 [−0,0250;−0,0072]) dan `srtm-minus-aw3d30`
   (−0,0047); tulisan sebelumnya "ΔAUC GLO-30−SRTM = −0,0155" membalik
   semantik pengurangan. Gemini menyeragamkan subscript:
   ΔAUC_SRTM−GLO-30 = −0,0155; ΔAUC_GLO-30−AW3D30 = +0,0108;
   ΔAUC_SRTM−AW3D30 = −0,0047 — 100% konsisten arah pengurangan dan
   TIDAK mengubah kesimpulan ranking (GLO-30 unggul; AW3D30 vs SRTM
   marginal; kedua klaim CI sama persis). Multiseed (per CSV
   `multiseed_delta_auc.csv`, semuanya 5/5 tanda konsisten): holdout
   srtm−glo30 = −0,0082±0,0048; holdout srtm−aw3d30 = −0,0012±0,0021;
   holdout glo30−aw3d30 = +0,0070±0,0027; spatial CV srtm−glo30 =
   −0,0200±0,0039; spatial CV srtm−aw3d30 = −0,0079±0,0034; spatial CV
   glo30−aw3d30 = +0,0121±0,0055.
4. **Struktur bab** (38 judul section/subsection) identik; Bab I–III tidak
   berubah kecuali paragraf 3.5.
5. **Kalimat audit T04/keputusan user** dipertahankan dalam prosa baru:
   dual-model 4.3; sumber-run v26-vs-v24 di 4.4; WC = run utama v24; dua
   kalimat keterbatasan JRC di 4.7 (12,8–14,4% / 4,3%; fairness; ekstrapolasi).
   Patch kecil kita saat merge: kalimat v24 diberi klausul "kecuali analisis
   pembanding yang menggunakan sampel dan pembagian data penelitian acuan"
   (bridging = run terpisah) — Gemini melupakan pengecualian jembatan.

## 3. Bagian Gemini yang TIDAK diadopsi (regresi, disengaja)

| Item | Alasan |
|---|---|
| Preamble stub `\relax` + `\ifhavebiblatex=false` + `\usepackage{cite}` + `\let\parencite\cite` | mematikan biblatex (numeric-comp + biber akan hilang; 22 bibitem manual vs basis 31 entri) — naskah user sudah teruji biblatex |
| `\ifhavetikz=false` + fbox placeholder | menggantikan kerangka teori TikZ (Gambar kerangka) dan logo cover dengan kotak teks |
| fbox placeholder untuk `fig_roc_v24.png` & `fig_agreement_v24.png` | gambar asli ada dan menempel di PDF; placeholder menurunkan kualitas |
| thebibliography manual (22 entri) | diadopsinya biblatex artinya daftar pustaka regenerasi otomatis; 31 entri jadi sumber tunggal |
| `avand2022` journal "Hydro-environment" → "Hydro-Environment" | entri tidak dikutip di naskah (tidak tercetak); kapitalisasi resmi jurnal (Elsevier) memakai "Journal of Hydro-environment Research" — perlu verifikasi situs jurnal sebelum berubah |
| gambar `.eps` versi Gemini | tidak ada (fig PNG dipertahankan) |

## 4. Yang diadopsi ke bib utama

- `references.bib`: `note` esa_glo30 dibersihkan → "Dataset, Copernicus
  Contributing Missions" (catatan internal Indonesia sebelumnya tercetak
  di Daftar Pustaka; terverifikasi hilang dari PDF).
- Tidak diubah: nama penulis hakim2026 (giveninits sudah menampilkan
  "M. I. A. Hakim"), pembagian `and` per baris (cosmetic, tidak berpengaruh).

## 5. Merge + kompilasi

- Merge oleh opencode: slope 3.5 (18 baris) + Bab IV (baris diperbaiki
  dari versi revisi dengan 2 restorasi includegraphics + 1 klausul).
- `pdflatex → biber → pdflatex ×2`: **PDF 37 hlm, 0 undefined, 4 overfull**
  (semua 4 di Bab I–III warisan; Bab IV revisi = 0 overfull baru).
- Verifikasi pdftotext: semua frasa kunci ada; "terpooled"/"merentang"/
  "validasi kewarasan"/"memproses ulang pipeline" = 0 kemunculan; dua
  gambar termuat (fig_roc hlm line 1162, fig_agreement 1348).

## 6. Gelombang item struktur B–E — EKSEKUSI PENUH (22 Okt; keputusan user "Semua A+B+C+D")

- **A (ringan)**: "Tique dkk." di 6 titik (1.1, 2.2, 2.6, 2.8, Tabel 2,
  kerangka); Tabel 2 urut kronologis (Fatdillah 2022 → Tique 2026);
  kepanjangan akronim saat kemunculan pertama (DEM, FABDEM, SRTM, LiDAR,
  SAR, ALOS/AW3D30, TanDEM-X, PRISM, ESA, JRC, SMDS, ROC/ROC-AUC, MERIT,
  CHIRPS, EGM96/EGM2008, AOI, VH, GRD; sel ML → \textit{machine
  learning}); kerangka teori dijadikan Gambar ber-caption
  (`fig:kerangka-teori`); Tabel Tahapan + kolom Orientasi RM.
- **B (kritis)**: 2.4 → "telah dikunci" (merujuk 3.6); 3.6.1 merinci lima
  fitur per DEM (elevation, slope, aspect sin/cos + valid; alasan kontinuitas sudut); 3.6.2 merinci 11 non-DEM (yamazaki2019, pekel2016,
  funk2015, saha2021) + 8 dummy WorldCover (kode 10/30/40/50/60/80/90/95,
  referensi kelas 20; zanaga2021) = 24 prediktor; 3.7 konfigurasi RF
  terkunci (smileRF 300 utk peta GEE; sklearn 400/min_leaf 2/balanced
  utk evaluasi; sampling 2978/kelas seed 42; split 75:25); 3.8 tiga
  skema pengecekan (CV 4-fold 16 blok; block bootstrap 1.000 iter;
  multi-seed 5 seed); 3.5 threshold kompleks final (median VH pra 25
  Feb–12 Mar 2024 / pasca 15–31 Mar 2024; ratio>1,25; post<−18 dB; occ≥80%;
  slope SRTM<5°; konektivitas≥8 piksel); 3.3 batas wilayah FAO GAUL
  level-2 identik dengan SMDS.
- **C**: teori one-by-one — 2.3.1 SRTM (pita-C 5,6 cm; EGM96; mendekati
  DSM), 2.3.2 GLO-30 (TDX bistatik single-pass pita-X 3,1 cm; EGM2008),
  2.3.3 AW3D30 (PRISM stereo 3 arah; void + void mask), 2.5 mekanisme RF
  (bagging + random subspace → decorrelation → varians turun; proba =
  proporsi suara), 2.6 motivasi evaluasi blok (autokorelasi; roberts2017,
  ploton2020); matriks data Tabel 4 diubah 6 kolom — **dikoreksi dari
  draf Gemini** (V4.1 bukan V3.2; v200 bukan v100).
- **D**: 1.4 diperkaya (paragraf implikasi operasional baru); RM 1–2
  dibuat lebih operasional + Tujuan 1–2 disinkronkan (penomoran RM 1–4
  dan Tabel 1 tidak berubah); **Bab V baru** "Kesimpulan dan Saran"
  (5.1 = 4 poin per RM kerangka; 5.2 = 4 saran agenda skripsi) — catatan:
  contoh proposal dosen memuat Bab I–III; contoh dosen tidak memuat
  Bab V, ditambahkan karena user memilih gelombang penuh.

Kompilasi final: **PDF 43 hlm, 0 undefined, 0 LaTeX warning**; overfull:
3 legacy paragraf (215–225, 674, 819–825) + 4 mikro ≤3 pt di dalam sel
Tabel (teredam scale `adjustbox`, tidak tampak). Angka hasil (AUC,
bootstrap, multi-seed, sensitivitas, WorldCover) tidak diubah sama
sekali.
