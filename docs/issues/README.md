# Isu — Indeks

> Detail tiap isu: `log.md`. Tambah baris baru untuk isu baru (ID `MET-0xx` urut).
> Status: `OPEN` / `DIAGNOSED` (akar ditemukan, fix/rencana siap) / `IN PROGRESS`
> / `FIXED` / `ACCEPTED` (risiko diterima) / `DECIDED`.

| ID | Judul | Status | Prevalensi berulang |
|---|---|---|---|
| MET-001 | Mask JRC-GSW sparse menyaring training image → sampel "sabuk air" (v20–v22 & baseline SMDS) | DIAGNOSED (fix v24 dijalankan 17 Okt; detail T01) | Tiap kode yang memakai `permanent_water.Not()` atau mask multiband |
| MET-002 | Kolom metrik legacy salah makna + angka naskah tidak cocok artefak (T03: B1/B2/B3) | DIAGNOSED (koreksi naskah menunggu hasil v24) | Tiap kutip angka ke proposal/temuan/artikel |
| MET-003 | Sampel artikel SMDS terbit = sabuk air; implikasi ke artikel terbit | DECIDED menunggu keputusan co-author (detail T02) | Konsultasi apa pun soal artikel terbit |
| MET-004 | Arsip S1 GEE bergeser — label-match CSV vs inventory ulang hanya 69,9% | ACCEPTED (klaim "inventory identik" dilunakkan) | Bridging/reproduksi lintas waktu ke GEE arsip historis |
| MET-005 | Spatial holdout v20 terkontaminasi train→test (leakage) | FIXED (4-fold spatial CV retrain per fold, v22) | Tiap validasi spasial baru |
| MET-006 | `Image.sample` `numPixels` = perkiraan, bukan kuota (v18: minta 3000 → 244/135) | FIXED (`stratifiedSample` + `classPoints`, v20–v22) | Tiap sampling besar di GEE |
| MET-007 | Visualisasi tile (`Map.addLayer` → getMapId) timeout SETELAH sains selesai, CSV ikut hilang (v21) | FIXED (seluruh cell viz dibungkus try/except, v22+) | Tiap notebook yang punya tile render |
| MET-008 | Notebook JSON penyebut byte invalid `0x97` peninggalan edit encoding | FIXED (patch `raw.replace(b"\x97", b"-")`) | Tiap manipulasi byte notebook lama |
| MET-009 | Konstruksi label (sel 12) memakai pita JRC terkurung - flood=1 mustahil di luar pita; 12,78% = Σ berbobot bukan count; mask occ fraksional | DIAGNOSED (probe T04 20 Okt; detail T04) | Tiap run yang membentuk label via mask JRC (v20–v26) |
