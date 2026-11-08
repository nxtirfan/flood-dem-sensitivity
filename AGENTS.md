# AGENTS.md — Aturan untuk agen editor (GPT) pada repo ini

> Repo ini ditulis untuk agen eksternal yang membaca/mengedit repo penuh
> (ChatGPT-6). Baca file ini SEBELUM mengedit apa pun. Status proyek, log
> keputusan, dan handoff dicek di `CONTEXT.md` (titik masuk utama) dan
> `docs/STATUS.md`.

## 1. Zona boleh edit vs zona beku

**Boleh edit:**
- `Proposal Baru/proposal_revisi-final.tex` — naskah utama (Bab I–V).
- `Proposal Baru/references.bib` — hanya metadata/fakta pustaka; **key sitasi jangan diubah** (naskah memakai key: `abidin2015`, `zanaga2021`, `tadono2016`, dll.).
- `docs/STATUS.md`, `docs/temuan/`, `CONTEXT.md` — dokumentasi proses (aturan pola: satu file laporan per sesi, mis. `T12-*.md`).
- `chatgpt.md` — handoff prompt (diperbarui per sesi).

**BEKU — jangan disentuh tanpa persetujuan eksplisit user:**
- `Proposal Baru/hasil_kaggle/` — satu sumber kebenaran angka (artefak v26/v27).
- `Proposal Baru/v27_delivery/` + salinan `Proposal Baru/olds/` — hasil rerun T10, md5 canon `6c656fce2066e934bfc589e3a19b262c`.
- `Proposal Baru/Flood_DEM_Sensitivity_Notebook_v27_maskAOI.ipynb` — notebook canon.
- `Proposal Baru/figures/` — berisi fig_roc.png, fig_agreement.png, fig_prob_maps.png (swap hanya kalau user minta).
- `Proposal Baru/logo_unnes.png`, `Proposal Baru/proposal_revisi-final_source.zip` (zip direbuild manual setelah edit selesai).
- Folder `Arsip Proposal Usang/`, `ARTIKEL REFERENCE - SMT 4/`, materi kuliah — historis, status USANG/diignore.
- Data hasil, sampel, seed, model, CSV, raster: **angka hasil tidak boleh diubah** — T11 dan seterusnya hanya koreksi teks. Klaim baru yang butuh eksperimen (label independen, buffer CV, koreksi geoid, penyamaan pipeline GEE/sklearn) = usulkan dulu ke user, jangan langsung dieksekusi.

## 2. Kondisi saat ini (8 Nov 2026, commit `0d3f864`)

- PDF 50 hlm, 0 undefined/0 warning, 7 overfull legacy (<15 pt, kebanyakan <8,7 pt — warisan paragraf user, TIDAK dikejar).
- T10 (surgery mask AOI) TUTUP; T11 (audit GPT-Astra: EGM96/dual-pipeline/label/multiseed/Tique/Meadows/aspect + bib) SELESAI dan menunggu verifikasi round-2 (daftar 13 titik ada di `chatgpt.md`).
- Git: `main`, remote `https://github.com/nxtirfan/flood-dem-sensitivity.git`, kredensial ter-ignore.
- Sisa agenda: (1) konsultasi Dr. Iqbal; (2) keputusan artikel SMDS (T02); (3) opsional: AOI polygon/geometry; (4) eksperimen baru selalu butuh persetujuan user.

## 3. Build & validasi wajib

Jalankan dari `Proposal Baru/`:
```
xelatex -interaction=nonstopmode proposal_revisi-final.tex   # 1
biber proposal_revisi-final        # hanya bila references.bib berubah
xelatex -interaction=nonstopmode proposal_revisi-final.tex   # 2
xelatex -interaction=nonstopmode proposal_revisi-final.tex   # 3 — TOC stabil
```
Kriteria lolos: `Output written ... (N pages)`; di `.log`: "undefined" = 0.
Validasi PDF (bila ada python/pypdf): sweep teks untuk klaim lama yang harus 0
(count = 0) dan angka acuan sesuai; contoh sweep T11: "EGM2008 pada Copernicus DEM
GLO-30 serta ALOS" harus 0; "226-240" = 1; "157-162" = 1.

## 4. Gaya penulisan naskah

- Bahasa Indonesia formal akademik; desimal koma di prosa (`0,39`), titik di
  persamaan/angka CSV; ribuan pakai titik (94.306).
- Bilangan langsung dari artefak; SATU sumber kebenaran = CSV di
  `hasil_kaggle/` (bootstrap & multiseed) dan `v27_delivery/` (Moran peta,
  transisi, WorldCover). Kutip persis (0,957714 dst.); jangan membulatkan
  beda dari CSV tanpa catatan.
- Istilah dijaga: tanpa anglikisme ("dikunci"→"ditetapkan/dipertahankan":
  pola polish 2026-11-01 di CONTEXT.md); tanpa superlatif; klaim proksi
  jujur (label kelas 0 = tidak diidentifikasi, bukan bukti non-banjir).
- Struktur: Bab 1–5; subbab 4.1–4.8; label TikZ `fig:kerangka-teori`;
  tabel pakai `Tabel`/`Gambar` caption Indonesia; sitasi biblatex numeric.
- `\includegraphics{figures/...}` — path relatif itu tetap.

## 5. Setelah edit

1. Kompilasi + validasi (Bag. 3).
2. Tulis laporan sesi: `docs/temuan/T12-<topik>.md` (format bebas, mirip T11).
3. Append `docs/STATUS.md` (seksi `## Update <tanggal> - <topik>`) dan baris
   baru `| <tanggal> | ... |` di tabel Log Keputusan `CONTEXT.md` + update
   bagian "Next action".
4. Commit konvensional pesan pendek (satu baris, tema + dampak),
   contoh: `T11: koreksi teks hasil audit GPT-Astra (EGM96, dual-pipeline,
   label, multiseed) - tanpa rerun; PDF 50 hlm`. Push ke `origin main`.
5. Rebuild zip bila tex/bib/figure berubah:
   `Compress-Archive ... (tex, bbl, bcf, references.bib, logo_unnes.png, figures/, pdf) → proposal_revisi-final_source.zip`.

## 6. Verifikasi round-2 (tugas pertama yang disarankan)

Ikuti tugas A–E di `chatgpt.md` (verifikasi 13 koreksi T11, efek samping,
redaksi offset 4.1, 5 topik konsultasi Dr. Iqbal). Bila menemukan isu,
perbaiki langsung di tex (dengan laporan T12), TANPA mengubah angka hasil.
