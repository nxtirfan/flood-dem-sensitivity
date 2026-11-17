# ARSIP — ` Proposal Baru\olds\`

Folder ini berisi **file/folder yang TIDAK dipakai naskah final**, dipindahkan 4 Nov 2026 agar root `Proposal Baru\` benar-benar bersih. Tidak ada file di sini yang dirujuk oleh `proposal_revisi-final.tex` maupun oleh notebook final.

## Yang ADA di root `Proposal Baru\` (aktif)

| File/Folder | Peran |
|---|---|
| `proposal_revisi-final.tex` + `.pdf/.bbl/.aux/.bcf/.blg/.log/.out/.run.xml/.toc` | Naskah resmi 43 hlm + file build (jangan dihapus) |
| `references.bib` | Sumber pustaka bersama (entri [21] = WorldCover v200, DOI 10.5281/zenodo.7254221; key `zanaga2021` dipakai naskah) |
| `Flood_DEM_Sensitivity_Notebook_v28.ipynb` | Notebook kanonik final (72 sel): pipeline utama + block bootstrap 16 blok + multiseed 5 seed + rekomputasi Moran AW3D30 + verifikasi T17 & poligon AOI independen |
| `v28_delivery\` | Folder delivery aktif lengkap (`Analisis Flood DEM Susceptibility\` + `diagnostics_t17\` + `Laporan_v28.md`) |
| `figures\` | Dua gambar BAB IV (`fig_roc.png`, `fig_agreement.png`, konten sumber v26) — tex memakai path `figures/...` |
| `logo_unnes.png` | Logo cover (TETAP di root; di-`\includegraphics`) |
| `hasil_kaggle\` | SATU SUMBER KEBENARAN: 25 artefak v26 flat (v24 diarsip ke sini sebagai `hasil_kaggle_v24\`) |
| `proposal_revisi-final_source.zip` | ZIP sumber LaTeX (tex+bbl+pdf+bib+logo+figures) |
| `.credentials\` | Metadata kredensial kernel Kaggle (JANGAN dibagikan) |

## Isi arsip ini

| Item | Keterangan | Status |
|---|---|---|
| `proposal.tex` + `.pdf/.bbl/.bcf/.blg/.aux/.out/.run.xml/.toc` | Baseline proposal sebelum paket revisi 2 Nov | USANG — jangan diedit |
| `Flood_DEM_Sensitivity_Notebook_v23arsip.ipynb` | State notebook v22–v23 | Arsip |
| `Flood_DEM_Sensitivity_Notebook_v25arsip.ipynb` | State notebook dgn output (sebelum v26 dibersihkan) | Arsip |
| `draft_proposal.md` | Draft Bab I–III ringkas (pra-naskah penuh) | Arsip |
| `form_isian_google.md` | Isian Google Form pengguna + koreksi DOI baseline | Arsip |
| `fig_confusion_v24.png` | Gambar tidak dirujuk LaTeX final | Arsip |
| `fig_agreement_v24.png` | Realisasi grafik kesesuaian dari run v24 (dipakai sementara, diganti konten v26 4 Nov) | Arsip |
| `ORCID_iD.png` | Tidak dirujuk LaTeX final (simpan utk kebutuhan artikel) | Arsip |
| `v24_rebuild_recover.py` | Skrip pemulihan artefak v24 (10-17) | Arsip |
| `hasil_kaggle_v17\` | Pilot n=270 (diagnostik) | USANG — bukan acuan angka |
| `hasil_kaggle_v20\` | Pilot n=5872; spatial holdout INVALID | USANG — bukan acuan angka |
| `hasil_kaggle_v22\` | Run utama pra-fix MET-001 (label kelas-0 = sabuk JRC) | USANG — bukan acuan angka |
| `hasil_kaggle_v23\` | Bridging baseline (SRTM 0.802 vs 0.852) | ARSIP — angkanya masih dikutip 4.4/4.7 sebagai run terpisah |
| `v27_delivery\` | Bundle delivery v27 (pra-konsolidasi v28; 2 piksel pulau AW3D30 belum dikecualikan di Moran & manifest pra-sinkronisasi) | Arsip — digantikan `v28_delivery\` (13 Nov 2026) |
| `Flood_DEM_Sensitivity_Notebook_v27_maskAOI.ipynb` | Notebook v27 pasca-patch mask AOI (sebelum integrasi T16–T18) | Arsip — digantikan `Flood_DEM_Sensitivity_Notebook_v28.ipynb` |
| `hasil_kaggle_v26_legacy\` | 7 file CSV spasial pra-masking v26 + file sementara konversi | Arsip — `hasil_kaggle\` kini sinkron penuh dengan CSV pasca-masking `v28_delivery` |
| `colab_t17_fallback_output_arsip\` | Folder sementara hasil path fallback saat eksekusi Colab diagnostik T17 (isinya sudah disalin ke `v28_delivery/diagnostics_t17/`) | Arsip |

Catatan:
- **Angka resmi** naskah = `..\hasil_kaggle\` (25 file v26, flat — sumber TUNGGAL sejak 4 Nov).
- `hasil_kaggle_v22\` & `v23\` ada di sini hanya sebagai bukti forensik/bridging (lihat `docs\temuan\`); `hasil_kaggle_v24\` = run utama lama (digantikan v26; lihat `docs\temuan\T08-single-source-v26.md`).
- Tidak ada file yang dihapus; semua hanya dipindah.
