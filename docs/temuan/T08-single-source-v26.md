# T08 — Single-Source v26: konsolidasi sumber angka naskah ke satu run

Tanggal: 4 Nov 2026 (sore). Keputusan pengguna: "abaikan isi v24 lama, ganti pake v26"
— hanya SATU folder kebenaran (`Proposal Baru\hasil_kaggle\`, flat), isi v24 diarsipkan.

## A. Perubahan dada naskah (semua = jaluran desimal, tidak ada yang mengubah makna)

| Siruhan naskah | v24 (lama) | Well v26 (baru) | Lokasi |
|---|---|---|---|
| Sensitivitas tabel: kesesuaian SRTM vs AW3D30 | 83,9% | **84,0%** | Tabel sensitivitas (L1464) |
| Transisi kelas 2→1 (SRTM→GLO-30) | 94.348 | **94.318** | 4.5 aw cari transisi |
| Transisi kelas 1→2 (SRTM→GLO-30) | 36.959 | **36.935** | i(principal) |
| Transisi kelas 4→5 (SRTM→GLO-30) | 25.655 | **25.687** | i(fl) |
| Diag kelas 2 (SRTM↔AW3D30) | 174.013 | **173.994** | same |
| Diag kelas 5 (SRTM↔AW3D30) | 103.374 | **103.420** | same |
| Shrubland: kesesuaian GLO-30 vs ALOS | 54,0% | **55,0%** | 4.6 + Pembahasan |
| Shrubland: kesesuaian SRTM vs GLO-30 | 60,2% | **60,7%** | 4.6 |
| Shrubland: mean \|Δp\| paling tinggi | 0,095 | **0,094** | 4.6 |
| Bare/sparse: kesesuaian GLO-30 pasangan | 66,9% | **67,0%** | 4.6 |
| Mangrove: kesesuaian pasangan GLO-30 | 61,8%–64,3% | **62,0%–64,1%** | 4.6 |
| Air: rentang kesesuaian | 77,4%–82,7% | **77,5%–82,8%** | 4.6 |
| Wetland: rentang kesesuaian | 72,6%–78,3% | **72,5%–78,2%** | 4.6 |
| Pembahasan rentang semak | 54,0%–70,1% | **55,0%–69,4%** | Pembahasan (RM4) |
| Pembahasan rentang terbuka | 63,6%–75,4% | **63,6%–75,5%** | i(coin) |
| Pembahasan rentang mangrove | 61,8%–73,2% | **62,0%–73,0%** | i(kawasan) |
| Pembahasan rentang sensitivitas antarpeta | 79,4%–83,9% | **79,4%–84,0%** | i(antarpeta) |

Yang TIDAK berubah angkanya (terverifikasi sama pada v26): seluruh metrik model
(holdout 0,932/0,940/0,936 + metrik lainnya + Youden), spatial-CV per fold (0,870/0,890/0,875 dan
rerata), rerata |Δp| 0,056/0,037/0,048, pohon 95,6–96,8 & |Δp| 0,011–0,021, terbangun
87,2–90,4, populasi 1.410.981/58.573, offset +0,39, dem_stats, slope-statistik (median 1,35/0,28/0,96;
p99 4,92; maks 11,48; share 98,99/99,97/98,76), multiseed 5 seed + block bootstrap (sudah
memang dari v26), "2%–9%" pergeseran luas (rekomputasi manual dengan luas v26 tetap jatuh pada 2–9),
"12,8%–14,4%" pita JRC (garis probe log identik di kedua garis).

## B. Verifikasi target

1. **7 file md5-IDENTik antar run**: `dem_stats.csv`, `delta_metrics_vs_srtm.csv`,
   `sample_audit.csv`, `spatial_cv_metrics.csv`, `fig_flood_label.png`, `roc_curves.png`,
   `confusion_matrices.png` → ROC pada naskah sudah realisasi v26.
2. `training_sample_features.csv`: 5.956 baris identik level nilai (0 sel beda) → seluruh
   statistik slope/Spearman dari T07 tetap.
3. `spatial_cv_test_predictions.csv`: 17.868 prediksi identik numerik (0 sel beda).
4. `model_metrics.csv`: beda 1e-16 di satu kolom (format float) → supplied dulu sama.
5. Log kernel: histogram & probe identik (beda repr float pada desimal ke-15);
   offset pixelwise `aw3d30 +0,3949452763161183` / `glo30 −1,5601385335339437` → nilai
   kutipan naskah (+0,39) konsisten dengan v26.

## C. Struktur

- `hasi_kaggle\` → flat, 25 artefak v26 (tanpa subfolder).
- `hasi_kaggle\run_utama_v24\` → dipindah ke `olds\hasi_kaggle_v24\` (arsip, bukan acuan).
- `figures\` → `fig_roc.png` (berasal v24=identik v26) + `fig_agreement.png` (konten v26);
  `fig_agreement_v24.png` (realisasi v24) → diarsip `olds\`.
- ZIP sumber di-regenerasi (tex+bbl+pdf+bib+logo+figures, 854.628 B).
- Kompilasi ×2: **PDF 43 hlm**, 752.879 B, 0 undefined, 3 grafik termuat dari path baru.
- Komen pembuka tex baris 5: "kernel v24; audit v22 dua skala; bridging v23" → "sumber
  tunggal kernel v26; bridging v23".

## D. Kalimat sumber-run di 4.4 — TERSELESAIKAN (opsi a, 4 Nov sore)

Semula (bangkai "replikasi vs eksperimen utama"):
> "Pengujian multi-\textit{seed} beserta analisis \textit{block bootstrap} tersebut berasal
> dari replikasi dengan kode yang identik, sedangkan statistik deskriptif dan spasial
> lainnya berasal dari eksperimen utama, kecuali analisis pembanding yang memakai sampel
> dan pembagian data penelitian acuan."

Diganti (keputusan pengguna, opsi a; istilah "pipeline" tidak dipakai — naskah memakai
"alur pemodelan"):
> "Pengujian multi-\textit{seed} beserta analisis \textit{block bootstrap} tersebut
> dijalankan pada alur pemodelan yang sama dengan analisis lainnya, kecuali analisis
> pembanding yang memakai sampel dan pembagian data penelitian acuan."

Verifikasi lanjutan: kata "replikasi" kini hilang dari naskah; dua sisa "eksperimen utama"
(L1198 pembuka 4.1 dan L1431 kontras bridging-pembanding) tetap SAH — keduanya memakai
"utama" sebagai penanda run analisis, dan kontrast yang masih ada hanya utama-vs-pembanding
(bridging, run terpisah yang benar-benar ada). Rekompilasi ×2: **PDF 43 hlm** (752.816 B),
0 undefined, overfull 7 (legacy sama); zip 854.550 B.

## E. Daftar berkas output

- `Proposal Baru\proposal_revisi-final.tex/.pdf/.bbl/...` + `proposal_revisi-final_source.zip`
- `Proposal Baru\figures\fig_roc.png`, `fig_agreement.png`
- `Proposal Baru\hasil_kaggle\` (flat, 25 file v26) — SATU sumber kebenaran
- `Proposal Baru\olds\hasil_kaggle_v24\`, `olds\fig_agreement_v24.png` — arsip
- Script bantu: `%TEMP%\opencode\cmp_v24_v26*.py` (T08 eskport)
