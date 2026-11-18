# T22 — Audit ketertinggalan artikel SMDS vs proposal v28 + koreksi klaim MSK AW3D30

Tanggal: 2026-11-18. Sifat: koreksi teks artikel (`Proposal Baru/smds/`), tanpa menyentuh data/eksperimen.
Latar: artikel EN (`main.tex`) dan ID (`main_id.tex`) terakhir disunting 13 Nov 2026 06.07, lebih tua
dari koreksi proposal T18 (15 Nov) dan T20 (18 Nov). Audit membandingkan klaim artikel terhadap
artefak beku `v28_delivery/` dan naskah `proposal_revisi-final.tex` (50 hlm, baseline T20/T21).

## 1. Hasil audit — bagian yang SUDAH sinkron (tidak diubah)

1. **Protokol flood inventory** (ID L224, EN L269): VH, `VH_after < -18 dB`, klaster minimum 8 piksel
   terhubung, rasio daya >1,25, slope <5°, JRC occurrence >=80% — persis Cell 15 notebook v28 dan
   `manifest.json.config`. Retraksi `VV/-16 dB/4 piksel` T20 tidak pernah masuk artikel; tidak ada
   yang perlu ditarik.
2. **Moran's I raster** (ID Tabel L495, EN L577): 0,9577 / 0,9531 / 0,9544 dengan n 1.444.085 /
   1.444.085 / 1.429.580 dan catatan kaki "2 piksel terisolasi berderajat-0 dikeluarkan"
   (`n_valid = 1.429.582`) — cocok dengan `moran_prob_map_global.csv` (I = 0,954422, T18) dan tabel
   `tab:moran-raster` proposal L1921–1932.
3. **Narasi sampling** (EN L278 eksplisit: target 3.000/kelas -> ekstraksi multi-band -> complete-case
   filtering -> balancing -> n = 5.956; ID L233 setara): sejalan dengan redaksi L1057 hasil koreksi
   T20; tidak memuat frasa salah "mengikuti jumlah populasi berlabel".
4. **Framing jujur**: kelas 0 = "tidak teridentifikasi", bukan bukti non-banjir; label terbatas
   dukungan JRC 12,78% — konsisten dengan batas klaim proposal.
5. **SMDSBib.bib `hakim2026`**: pages 22--47 + DOI 10.15294/smds.v1i1.62500 — sudah benar (sumber yang
   mengoreksi typo slide PPT lama).
6. `N = 1.469.555` piksel grid pra-masking (ID L159/L258, EN L204): konsisten dengan proposal, tetapi
   klaim ini memang **masih terbuka di kedua dokumen** (T20 §7); artikel tidak memperkuatnya.

## 2. Temuan yang KETINGGALAN — dikoreksi

**Klaim MSK AW3D30** (ID L167, EN L212): kalimat lama menyatakan piksel valid `MSK=0` mencakup
**1.292,84 km² (99,1%)** dan piksel pengisian `MSK=3`/`48` seluas **1,44 km² / 10,07 km²**.

Masalah:
- Bertentangan dengan artefak beku: valid AW3D30 = **1.429.582 piksel = 1.286,79 km² sferis (99,0%**
  dari 1.444.085 piksel grid AOI**)** — `v28_delivery/.../data/export_status.json` dan proposal L1710.
- Kontradiksi internal artikel sendiri: L159/L204 menyatakan 1.429.582 piksel valid; dan
  1.292,84 + 1,44 + 10,07 = 1.304,35 km² > luas AOI 1.299,84 km² — mustahil.
- Proposal terbaru (pasca T18) menghapus klaim angka MSK dan hanya menyebut void mask kualitatif
  (proposal L570). Typo `99,1% / 1.292,84 km²` pada PPT lama bersumber dari kalimat artikel ini.

**Koreksi diterapkan** (teks saja, tanpa rerun):
- ID: "Pita void mask resmi (MSK) dievaluasi di wilayah kajian: pemodelan hanya mempertahankan piksel
  observasi valid (MSK=0), yang mencakup 1.429.582 piksel (1.286,79 km² sferis; 99,0% dari 1.444.085
  piksel grid AOI pada SRTM/GLO-30), sedangkan piksel pengisian awan/void (MSK=3 dan 48) tidak
  dipertahankan dalam pemodelan."
- EN: padanan langsung (`1,429,582 pixels`, `1,286.79 km² spheroidal`, `99.0% of the 1,444,085-pixel
  AOI grid on SRTM/GLO-30`; `MSK=3` dan `48` tidak dipertahankan).
- Rincian luas `MSK=3`/`48` dibuang karena tidak ada CSV artefak pendukung.

## 3. Validasi

- Grep pasca-edit: `1.292|1,292|99,1|99.1|10,07|10.07|1,44\text` = 0 temuan di kedua file;
  `1.429.582` hadir di 8 baris yang diharapkan (ID: 159/167/415/509; EN: 204/212/489/591).
- Encoding: byte-level `U+00C2` = 0 pada kedua file (UTF-8 bersih).
- Kompilasi penuh (pdflatex + biber + pdflatex ×2): `main_id.pdf` 16 hlm, `main.pdf` 22 hlm,
  0 undefined citation, 0 error. Build artefak dibersihkan.
- Deliverable dibangun ulang: `smds_dem_sensitivity_article.pdf` (EN, 22 hlm),
  `smds_dem_sensitivity_artikel_id.pdf` (ID, 16 hlm), `smds_dem_sensitivity_source.zip`
  (13 entri: main.tex, main_id.tex, SMDSBib.bib, ORCID_iD.png, 9 figure — tanpa PDF, mengikuti
  struktur zip lama).

## 4. Batas

- Audit bersifat perbandingan klaim; tidak mengeksekusi ulang eksperimen apa pun.
- Isu terbuka yang sama-sama dibawa artikel dan proposal (bukan ketertinggalan): `N=1.469.555`,
  reproduksi graph historis (BLOCKED), presisi T17, mismatch 2 piksel, denominator `~1,41%`.
- Perubahan PPT di `Proposal Baru/ppt/` (folder `agent/`, `ARSIP/`, `catatan-revisi-gemini.md`,
  file Gemini) tidak disertakan commit ini sesuai keputusan pengguna.
