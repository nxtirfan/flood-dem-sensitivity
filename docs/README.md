# Aturan Proses Kerja — Metodologi Penelitian (Metopen)

Folder ini berisi **aturan proses kerja & pusat temuan** untuk pekerjaan
eksperimen/audit dokumen. Substansi topik & keputusan desain tetap di
`CONTEXT.md` (root = titik masuk utama session). Naskah proposal ada di
`Proposal Baru/`.

## WAJIB DIBACA SEBELUM BEKERJA

Sebelum mengerjakan apa pun (koreksi proposal, rerun, koreksi artikel):
baca **`CONTEXT.md`** (root), lalu **`STATUS.md`** di sini, lalu file temuan/isu
yang relevan. Ada masalah (error tak dikenal, angka aneh)? Cek `issues/` dulu —
kalau cocok, ikuti resolusinya; kalau tidak, diagnosis baru lalu **catat entri
isu baru**.

## Peta isi

```
docs/
├── README.md            ← kamu di sini (peta + protokol)
├── STATUS.md            ← kondisi/progress + titik lanjut (handoff)
├── temuan_empiris.md    ← laporan angka eksperimen v17–v23 (+v24 bila ada)
├── temuan/              ← temuan forensik/audit substantif (deep-dive)
│   ├── README.md        ← indeks temuan (status)
│   ├── T01-sampling-bias-jrc-sparse.md   ← root cause bias sampling + fix
│   ├── T02-implikasi-artikel-smds.md     ← dampak ke artikel terbit + opsi
│   └── T03-audit-metrik-qc.md            ← audit metrik & angka naskah
└── issues/
    ├── README.md        ← indeks isu (status + prevalensi)
    └── log.md           ← detail tiap isu (gejala → diagnosis → resolusi)
```

## Aturan main folder ini

1. **Satu isu = satu entri** di `issues/log.md` + satu baris di
   `issues/README.md`. Entri wajib: gejala, diagnosis, resolusi, file terkait,
   **status**, **prevalensi**.
2. **Temuan substantif** (mengubah klaim hasil/angka) ditulis di `temuan/`
   dengan ID `T0xx` + dicatat di `STATUS.md`.
3. **Setiap angka yang dikutip ke naskah** (proposal/temuan/artikel) harus
   telusur ke artefak (`hasil_kaggle_*/`, `docs/temuan/*`), bukan dari ingatan.
   Lembar audit: `temuan/T03-audit-metrik-qc.md`.
4. Perubahan arah/run baru → perbarui `STATUS.md` (handoff) + `CONTEXT.md`
   (log keputusan) di akhir sesi.
5. Jangan simpan token/rahasia di sini.

## Prinsip umum

1. **Satu file, edit di tempat** — menduplikasi file resmi lalu mengedit
   di dalamnya, bukan membuat file tiruan gaya sama.
2. **Klaim jujur untuk reviewer** — sampel tidak diklaim "acak se-AOI"
   sampai fix sampling terverifikasi (lihat T01/MET-001); semua keterbatasan
   dilaporkan apa adanya.
3. **Angka dari artefak, bukan ingatan** — pemeriksaan akhir angka
   `proposal.tex` selalu lewat T03 + file CSV asalnya.
