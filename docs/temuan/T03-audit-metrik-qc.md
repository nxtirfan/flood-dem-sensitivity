# T03 — Audit Metrik & Angka Naskah (B1–B3)

**Status**: KOREKSI TEREKSEKUSI 18 Okt 2026 — semua butir B1–B3 telah diterapkan
ke naskah BAB IV (angka kernel v24; prediktor 24; Youden ditandai; median grid
eksplisit; offset +0,39; agreement dilengkapi; fig ROC + agreement pakai PNG
v24). Basis naskah kini = versi "rapi" pengguna (cover + logo + 12pt) dengan
BAB IV v24 di-merge; file lama dihapus; `proposal_rapi.tex` -> `proposal.tex`.
Rujukan baris di tabel B3 (proposal.tex:nnn) merujuk file LAMA (11pt, sudah
terhapus) — jangan dipakai sebagai acuan lokasi.
PDF terkompilasi: 30 hlm, 0 undefined / 0 warning. Sisa B4 (multi-seed,
block bootstrap, RF 300-vs-400) = agenda skripsi.
Catatan lingkungan kompilasi MiKTeX ini (24.1, D:\MiKTeX): newtx hanya OTF
→ ganti font text ke `lmodern`; `microtype` dan `tocloft` dimati (kernel
mismatch); header pustaka disetelic "Daftar Pustaka" (biblatex default
REFERENCES). 4 overfull kecil (<15pt) tersisa dari paragraf Pengguna (tidak
disentuh).

## B1 — Kolom `auc_spatial_cv` v22 = pseudo-AUC dari prediksi biner

- **Bukti kode** (recover, `v20_sampling_edits.txt`): `_safe_metrics(_ys, _pred)`
  memakai `roc_auc_score(yt, yp)` dengan `yp = (_proba >= 0.5).astype(int)`
  → nilainya ≈ (recall_pos + (1−recall_neg))/2 = **balanced accuracy**, BUKAN
  ROC-AUC probabilitas.
- **Bukti angka** (`hasil_kaggle_v22/spatial_cv_metrics.csv`; mean 4 fold):
  kolom `auc_spatial_cv` = 0.6519 / 0.6512 / 0.6478 (srtm/glo30/aw3d30) — nilai
  ini yang dikutip proposal sebagai "AUC spatial" (sedangkan srtm: accuracy
  fold = 0.6580/0.6380/0.6545/0.6865 → mean 0.6592 ≈ 0.651+gap kecil —
  konsisten pseudo-AUC ≈ balanced acc).
- **Dampak**: Tabel `tab:spatial-cv` proposal.ktx (baris 1021–1029) menulis
  kolom "ROC-AUC 0,652/0,651/0,648" — salah makna metrik.
- **Perbaikan**: v24 (lokal) sudah menghitung AUC probabilitas per fold
  (`auc_spatial_cv_prob`) — angka final dari rerun v24, bukan dari kolom lama.
  AUC proba v22 Kaggle TIDAK bisa dihitung ulang offline: probabilitas fold
  tidak tersimpan di `hasil_kaggle_v22/` (hanya metrik).
- **Ekspektasi hasil v24-mode**: AUC proba spatial CV akan lebih tinggi dari
  0,65 (contoh Part A: 0,866/0,885/0,870 pada sampel uniform) karena (a) pseudo
  → proba, (b) sampel uniform menurunkan autokorelasi. Bila sampel terkoreksi
  masih menampilkan gap yang berarti terhadap random-split, kesimpulan
  "spatial CV lebih jujur" tetap berdiri, dengan angka baru.

## B2 — Angka Tabel `tab:spatial-cv` tidak cocok sumber

Sumber yang benar (`spatial_cv_metrics.csv` v22), mean 4 fold:

| Konfigurasi | accuracy | f1 | "auc_spatial_cv" legacy |
|---|---|---|---|
| SRTM | 0.6592 | 0.6553 | (pseudo) 0.6519 |
| GLO-30 | 0.6607 | 0.6569 | (pseudo) 0.6512 |
| AW3D30 | 0.6609 | 0.6558 | (pseudo) 0.6478 |

Naskah (proposal.tex:1025–1027) menulis Acc 0,659/0,657/0,656 dan
F1 **0,638/0,634/0,631** — F1 tidak cocok sumber (selisih ≈ −0,02; asal
kolom tak dikenal), Acc dua dari tiga salah. **Perbaikan**: gunakan tabel di
atas dgn f1 0,655/0,657/0,656 + AUC proba dari v24.

## B3 — Butir kalimat/statistik di naskah yang perlu koreksi

| # | Lokasi | Tulis sekarang | Terverifikasi jadi |
|---|---|---|---|
| 1 | proposal.tex:956 "(median $\pm$5--9~m)" | rancu; sebenarnya p50 grid | `dem_stats.csv` p50: SRTM **8,50 m / GLO-30 4,94 m / AW3D30 8,53 m** → tulis eksplisit "(median grid 8,50/4,94/8,53 m)" |
| 2 | proposal.tex:957 offset AW3D30 "+0,40 m" | salah pembulatan | offset rata-rata = **+0,3949 m** → "+0,39" (log run; identik v22+) |
| 3 | proposal.tex:945 "(12 non-DEM + 5 topografi per DEM)" | 12+5=17 ≠ 25 | fungsi non-DEM lokal = 19 (11 tetap + 8 lc), +5 topo = 24 lokal vs 25 kernel — audit daftar kolom saat edit; tulis "(11–12 non-DEM + 8 dummy WorldCover + 5 topografi)" sesuai verifikasi |
| 4 | proposal.tex:855/983 ambang "Youden" | tanpa penanda dihitung di TEST | tambah "(dihitung pada data uji — ambang optimistis, hanya untuk pelaporan)" atau pindah ke train-set di rerun |
| 5 | Tabel tab:spatial-cv AUC | pseudo-AUC (B1) | ganti dgn AUC proba v24 |
| 6 | proposal.tex:943 "master sample … acak se-AOI"? | cek frasa; domain v22 = sabuk | tulis ulang setelah v24 |

## B4 — Bias metodologis lain yang sudah dicatat (dari audit sebelumnya)

1. Ambang Youden diukur di data UJI (optimistis) — butir B3#4.
2. Peta probabilitas GEE dibuat dengan RF 300 trees (GEE) sementara metrik
   sklearn memakai 400 — samakan atau catat.
3. `landcover` dipakai SEKALIGUS sebagai prediktor dan stratifier dunia
   WorldCover (perhatikan saat interpretasi stratifikasi).
4. Denominator agreement AW3D30 kemaskini saat pair memakai mask berbeda —
   cek konsisten saat rerun.
5. `EXPORT_TO_DRIVE` belum di-guard (bisa diam-diam gagal di Kaggle).
6. v23: 150 baris drop saat impor baseline (1778 → 1720) tercatat — tidak
   masalah asal dilaporkan.

## Rencana eksekusi koreksi (urutan)

1. Jalankan v24 (T01 §8); kunci angka final (holdout + spatial CV proba +
   audit sampel).
2. Edit `temuan_empiris.md`: tambah §9 v24; koreksi B3#1/B3#2 yang menganggap
   "±5–9 m" & "+0,40" jika masih dikutip.
3. Edit `proposal.tex`: B2 (tabel), B3 (kalimat), frasa sampling (B3#6),
   ganti angka spatial-CV dgn v24; rekompilasi PDF; verifikasi nol
   overfull/sitasi hilang.
4. Catat keputusan di CONTEXT.md + STATUS.md.
