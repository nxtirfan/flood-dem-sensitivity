# Temuan — Indeks

> Temuan substantif hasil forensik/audit. Update status di kolom terakhir
> bila fix terverifikasi. Detail keputusan proses: `../STATUS.md`.

| ID | Judul | Ringkas | Status |
|---|---|---|---|
| T01 | Root cause bias sampling "sabuk JRC" | Mask JRC-GSW sparse + `.Not()` memasang kandidat kelas-0 ke sabuk air (4,3% AOI) di seluruh run v20–v22; fix `unmask(0)` | DIAGNOSED — fix v24 dieksekusi 17 Okt 2026 (hasil §8) |
| T02 | Implikasi ke artikel SMDS terbit | Sampel baseline mengidap varian multiband; naskah sudah ber-hedge; bukan retraksi; opsi A/B/C | Analisis selesai — keputusan co-author |
| T03 | Audit metrik & angka naskah (B1–B3) | Kolom `auc_spatial_cv` = pseudo-AUC biner; angka tabel & kalimat rancu di proposal; daftar koreksi per baris | DIAGNOSED — koreksi menunggu v24 final |
| T04 | Domain label banjir terkurung pita JRC (audit v26, N-1) | `permanent_water.Not()` tanpa unmask pada SEL 12 (label): flood=1 mustahil di luar pita JRC (probe fresh c=0, 4 jalur × 2 grid); pita ≈ 12,8–14,4% AOI (footprint)/4,32% (occ-bernilai); angka 12,78% kernel = Σ berbobot, bukan count; fairness antar-DEM terjaga | TERKONFIRMASI + kalimat keterbatasan MASUK 4.7 (keputusan user 20 Okt; adopsi prosa Gemini 22 Okt); isu MET-009 |
| T05 | Adopsi revisi wording Gemini ke naskah utama | Bab IV (+3.5) ditulis ulang gaya akademik; verified: 0 fabrikasi angka; koreksi sah rentang AUC 0,009→0,008 & subscript ΔAUC sesuai CSV (`srtm-minus-glo30`); regresi ditolak (biblatex/TikZ/fig/dll.) | SELESAI 22 Okt — PDF 37 hlm; gelombang A+B+C+D dieksekusi (T05 bag.6) 22 Okt — PDF 43 hlm, 0 undefined, 3 legacy + 4 mikro overfull; detail T05 |
