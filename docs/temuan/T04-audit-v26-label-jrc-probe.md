# T04 — Audit v26: Domain label banjir terkurung pita JRC (N-1) + probe verifikasi GEE

| Kolom | Isi |
|---|---|
| ID | T04 (temuan substantif; isu terkait: **MET-009**) |
| Tanggal | 20 Okt 2026 |
| Status | **TERKONFIRMASI** (probe fresh GEE, 5 skrip, 2 grid, 3 metode hitung) |
| Dampak ke hasil v26 | **Tidak mengubah** perbandingan antar-DEM (fairness terjaga); menambah satu keterbatasan cakupan label yang wajib dinyatakan di proposal |
| Artefak bukti | `docs/temuan/probe_v26/` (5 skrip + output), `Proposal Baru/hasil_kaggle_v26/kernel_log_v26.log` |
| Batasan sesi | Tidak dijalankan rerun; tidak mengubah notebook/proposal/sampel/split/RF |

---

## 0. Ringkasan singkat

Audit v26 menemukan bahwa konstruksi label pada sel 12 memakai
`permanent_water.Not()` **tanpa** `unmask(0)`. Probe GEE fresh (19–20 Okt)
mengonfirmasi secara numerik:

1. **Tidak ada satu piksel pun `flood=1` di area JRC no-data** — label banjir
   hanya bisa lahir di dalam pita `occurrence` JRC GSW (bukti: `flood=1 &
   JRC no-data = 0` pada **semua** metode hitung dan **kedua** grid).
2. Pita valid JRC itu menutup **~12,8–14,4% AOI** tergantung definisi
   ( footprint band mask ≈ 189.345 px = 12,88%; angka kernel 187.777 = 12,78%
   adalah ukuran Σ berbobot, bukan jumlah piksel; nilai `occurrence` yang
   benar-benar terbaca hanya di **63.499 px = 4,32% AOI**).
3. Angka "12,78%" yang selama ini dipakai (kernel log & STATUS) adalah
   **luas efektif berbobot mask**, bukan jumlah piksel — mask band `occurrence`
   JRC **fraksional 0..1** (bukan binari). Definisi "JRC valid" perlu
   dipisahkan jadi tiga lapis (Tabel C-2).
4. Angka lama T01 "63.499 px / 4,32%" (yang pernah dikoreksi sebagai
   "ad-hoc proyeksi beda" di T01 §8) **terverifikasi kembali sahih** — itu
   definisi *occ-bernilai*, proyeksinya tidak merusak angka.

## A. Kode aktual yang diperiksa (sel 12 notebook v26)

Konstruksi label banjir (persis dari `Flood_DEM_Sensitivity_Notebook_v26.ipynb`,
sel 12; konstanta dari sel 8):

```python
# sel 8 (parameter)
SLOPE_MAX_FOR_FLOOD = 5
MIN_CONNECTED_PIXELS = 8
S1_RATIO_THRESHOLD, AFTER_DB_THRESHOLD = 1.25, -18

# sel 12
dem_for_label = ee.Image('USGS/SRTMGL1_003').select('elevation').clip(roi)
slope_for_label = ee.Terrain.slope(dem_for_label).rename('slope')

jrc_water = ee.Image('JRC/GSW1_4/GlobalSurfaceWater').select('occurrence').clip(roi)
permanent_water = jrc_water.gte(80).rename('permanent_water')

flood_raw = (s1_ratio.gt(S1_RATIO_THRESHOLD)
             .And(after_pol_db.lt(AFTER_DB_THRESHOLD))
             .And(permanent_water.Not())          # <-- N-1: tanpa unmask(0)
             .And(slope_for_label.lt(SLOPE_MAX_FOR_FLOOD)))

flood_label = (flood_raw.selfMask()
               .connectedPixelCount(100, True)
               .gte(MIN_CONNECTED_PIXELS)
               .unmask(0)                          # unmask HANYA setelah connect-filter
               .rename('flood')
               .clip(roi))
```

**Bagaimana `flood_raw` terbentuk** (urutan gate AND):

| Gate | Sumber | Perilaku mask |
|---|---|---|
| `s1_ratio.gt(1.25)` | komposit median S1 (pra 25 Feb–12 Mar; pasca 15–31 Mar 2024), VH | ter-mask bila komposit tak ada |
| `after_pol_db.lt(-18)` | idem | idem |
| `permanent_water.Not()` | JRC GSW1_4 occ≥80 | **ter-mask bila band JRC tak bernilai ATAU mask band JRC = 0** → inilah N-1 |
| `slope_for_label.lt(5)` | Terrain.slope(SRTM EGL1) | tak ada no-data di AOI (3.306 px luar footprint SRTM tepi ROI) |

Konsekuensi semantik: `flood_raw` **ter-mask** di setiap piksel yang
`permanent_water.Not()`-nya tidak dapat dievaluasi (JRC no-data). Karena
`flood_label` hanya me-unmask **setelah** filter `connectedPixelCount >= 8`
pada `flood_raw.selfMask()`, piksel banjir (flood=1) **tidak mungkin berada
di luar pita valid JRC**. `flood_label` sendiri PENUH 0/1 di seluruh AOI
(`unmask(0)`) — jadi kelas-0 tidak terpengaruh domain ini, hanya kelas-1.

## B. Metode probe dan perlakuan mask

**Lima probe kecil dijalankan** (lihat file & output di `probe_v26/`):

| Skrip | Fungsi | Hasil inti |
|---|---|---|
| `probe_label_jrc.py` | replika persis sel 8+10+12; unmask(-9999) sentinel + reduceRegion sum; grid WGS-default & EPSG:32749, scale 30 m, tileScale 8 | (c)=0 di kedua grid; dekomposisi kategori |
| `probe_label_jrc2.py` | taksonomi footprint vs nilai occ vs occ≥80 vs occ 1..79 vs occ=0; replika persis ukuran kernel (`constant(1).updateMask(occ)`) | replika tepat 187.777 (12,78%); flood=1 100% di dalam footprint |
| `probe_label_jrc3.py` | proyeksi native band occ (EPSG:4326, transform ≈ 30 m) + threshold mask band 0/0,25/0,5/0,75/1 | **mask band JRC = FRAKSIONAL 0..1** |
| `probe_label_jrc4.py` | Reducer.count vs Reducer.sum pada replika & occ-sentinel | sum ≠ count: bukti weighting |
| `probe_label_jrc5.py` | histogram frekuensi band kode kategori (flood × status-JRC) — count paling sahih, tanpa bobot | (c)=0 lagi; kategorinya sahih di dalam pita occ |

**Perlakuan mask** (dinyatakan eksplisit):

1. **"JRC no-data" didefinisikan** bukan sebagai nilai nol, melainkan:
   (a) piksel di mana band `occurrence` tidak bernilai (0..100) — diukur
   dengan sentinel `unmask(-9999).neq(-9999)`; plus
   (b) piksel di mana mask band JRC = 0 — diukur dengan `mask().gt(0)` /
   `updateMask` (count).
2. **Tidak menyamakan no-data dengan nol**: nilai `occurrence = 0`
   ("tidak pernah ada air, sahih") adalah piksel yang ada (≈150-160 px di
   AOI-nya), bukan no-data. Replika ukuran kernel
   `constant(1).updateMask(occ)` (probe 2 & 4) terverifikasi = **Σ mask
   fraksional** band occ (Σ = 187.777; count = 189.345), BUKAN jumlah piksel
   yang punya nilai occ (63.499) — sehingga interpretasi akurat dari angka
   187.777 adalah *luas efektif berbobot* (≈ footprint, ~12,8–12,9% AOI).
3. Percobaan `unmask(-9999, False)` (perluas footprint) membuat arena
   komputasi memelebar ke global dan time-out — dibatalkan; tidak dipakai
   untuk angka final (default `sameFootprint=True` juga tidak dipakai
   untuk definisi "luar pita": diukur via `mask().gt(0)` Not, konsisten).
4. `ee.Reducer.sum()` di GEE **memberatkan nilai dengan mask band** — pada
   band boolean dengan mask fraksional, sum = Σ(nilai×mask). Karena itu
   angka-angka bergaya "sum" kernel dilaporkan sebagai *luas efektif
   berbobot*; jumlah piksel sahih memakai `Reducer.count()`/histogram.

## C. Tabel hasil aktual

### C-1. Jawaban langsung atas permintaan hitungan (grid 30 m)

| Kuantitas | Metode | Grid WGS-default (≈ grid kernel) | Grid EPSG:32749 |
|---|---|---|---|
| AOI piksel (acuan kernel, mask penuh) | histogram label v26 (kernel_log) | **1.469.555** | 1.448.210¹ |
| (a) JRC valid — *occ bernilai* (0..100) | sentinel sum | **63.499 px = 4,32%** | 62.543 = 4,32% |
| (a') JRC valid — *footprint mask>0* | Reducer.count | 189.345 px = **12,88%** | n.a.² |
| (a'') "JRC valid" versi kernel | Σ berbobot (updateMask) | 187.777 px = **12,78%** | 185.098 = 12,78% |
| (b) flood=1 & JRC valid | probe 2 (footprint) / probe 5 (occ) | 58.574 (semuanya) / 10.615³ | 57.566 / 10.360 |
| **(c) flood=1 & JRC no-data** | semua probe (1, 2, 5) × kedua grid × sum & histogram | **0** | **0** |
| (d) flood=0 & dalam pita JRC | probe 2 | 152.564 px | 150.604 |
| (d') flood=0 & luar pita JRC | probe 2 | 1.258.417 px | 1.240.040 |
| flood=0 total (acuan kernel) | histogram label v26 | **1.410.981** | — |
| (e) flood_raw masked (kandidat hilang) | probe 1 | 1.259.427 px = **85,70% AOI** | 1.241.092 = 85,70% |
| (e1) ...karena JRC no-data | probe 1 | 1.258.417 (99,92% dari masked) | 1.240.040 |
| (e2) ...karena S1 komposit no-data | probe 1 | **0** | **0** |
| (e3) ...karena slope no-data | probe 1 | 3.306 (overlap dgn e1 = 2.296) | 3.709 |
| flood_raw valid-true | probe 1 | 13.625 Σ-berbobot⁴ | 13.250 |
| flood_raw valid-false | probe 1 | 48.574 | 47.973 |
| flood=1 total (label final) | histogram label v26 | **58.574** | 57.566 |

¹ beda grid: jumlah piksel AOI di 32749-30m sedikit beda karena resampling;
² count di 32749 tidak diukur (sum-variant-nya 185.098 = 12,78%).
³ probe 5 terukur pada subset yang turut terbuka pada mask komb (lih. catatan output);
angka penuh = 58.574.
⁴ Σ berbobot mask fraksional; count-nya sedikit lebih tinggi; selisih terhadap
58.574 flood=1 final diselamatkan di catatan output probe 1/5 (tidak memengaruhi (c)).

### C-2. Tiga definisi "JRC valid" (WAJIB dibedakan mulai sekarang)

| Definisi | Ukuran | Piksel | % AOI | Status |
|---|---|---|---|---|
| **occ bernilai** (band 0..100) | sentinel sum (≈ count; mask ≈ 1 di sana) | 63.499 | 4,32% | definisi lama T01; **sahih kembali** (T01 dikoreksi) |
| **footprint mask>0** | Reducer.count | 189.345 | 12,88% | definisi paling dekat "produk terpetakan" |
| **Σ luas efektif berbobot** | sum (probe kernel) | 187.777 | 12,78% | **yang dipakai log/STATUS sekarang** — bukan jumlah piksel |

Catatan taksonomis (bukti probe 3): mask band occ = fraksional; threshold
mask>0 = 211.137 (Σ), >0,25 = 86.637, >0,5 = 58.222, >0,75 = 32.520,
≥1 = 1.001 → selisih footprint-vs-nilai (≈ 147.640 px) menunjuk piksel
dengan mask>0 namun nilai occ tidak terbaca; piksel-piksel ini juga ter-mask
pada `occ.gte(80)` dan masuk kategori kandidat hilang (e) pada konstruksi
gate saat ini.

### C-3. Baseline kernel v26 (dari `kernel_log_v26.log`) — reproduksi probe

| Ukuran | Log kernel v26 | Probe fresh (metode sama) |
|---|---|---|
| AOI px (grid 30 m) | 1.469.555 | 1.469.555 ✓ |
| "JRC valid" | 187.777 (12,78%) | 187.777 ✓ (Σ berbobot) |
| histogram label {0;1} | 1.410.981; 58.574 | 1.410.981; 58.574 ✓ |
| pool kelas-0 v22 (sabuk) | 123.616 (8,76%) | (bukan target probe N-1; T01) |
| pool kelas-0 v24 (unmask 0) | 1.382.033 (97,95%) | (bukan target probe N-1; T01) |

## D. Kesimpulan

### D-1. Apakah label flood=1 memang tidak mungkin muncul di area JRC no-data?

**Ya — terbukti, bukan asumsi.** Nol piksel flood=1 pada *pita luar* JRC,
konsisten pada 4 jalur eksekusi (probe 1, 2, 5; sum & histogram) dan 2 grid
(def WGS ≈ grid kernel; EPSG:32749 eksplisit). Mekanisme: gate
`permanent_water.Not()` pada sel 12 memask px JRC-no-data → `flood_raw`
masked → `selfMask()` membuang → `connectedPixelCount` tak pernah menjangkau
→ `flood_label.unmask(0)` mengembalikan **0** di sana (bukan banjir).

### D-2. Apakah ini keterbatasan cakupan label yang perlu dinyatakan di proposal?

**Ya.** Dua fakta kunci yang sebaiknya jujur dinyatakan:

1. **Label banjir hanya bisa lahir di dalam pita occ JRC** (~13% AOI pada
   footprint; nilai occ benar-benar terbaca ~4,3%). Artinya area luas
   (perbukitan, kebun di selatan AOI, sawah datar non-pantai) **tidak
   pernah bisa menerima label banjir dari prosedur ini** — hal ini harus
   dinyatakan sebagai *domain label*, bukan kelemahan prosedur.
2. **flood_raw memask 85,7% AOI** untuk kondisi banjir-raw — `flood_label`
   PENUH 0/1 di seluruh AOI berkat `unmask(0)`, sehingga **kelas-0 bebas
   menyebar se-AOI (97,95% pool setelah fix sampling v24)** sementara
   **kelas-1 terkurung pita JRC**. Sampel yang dipakai v24 (2.978/kelas)
   berisi kelas-0 se-AOI dan kelas-1 di pita JRC — asimetri domain sampel
   seperti ini perlu diakui di bagian keterbatasan.

Keterbatasan ini **tidak membatalkan** hasil v24/v26 karena ketiga DEM
mendapat sampel/split/model yang identik — hanya perlu dinyatakan bahwa
inventory hanya menandai dugaan genangan **di dalam pita terobservasi JRC**.

### D-3. Apakah fairness perbandingan antar-3 DEM berubah?

**Tidak berubah.** (i) Label identik & seluruh gate label TIDAK memakai
variabel DEM (kecuali slope mask SRTM — empiris dan terjustifikasi di
3.5/4.2 naskah). (ii) Sampel, split, seed, prediktor non-DEM, RF semuanya
disamakan; selisih metrik/peta murni berasal dari 5 kolom DEM. (iii) Ketiga
konfigurasi menerima keterbatasan domain label yang sama → perbandingan
internal (sensitivitas SUMBER) tetap apples-to-apples.

Yang **tidak bisa disimpulkan** dari hasil ini (perlu dinyatakan):

- Perilaku RF/konfigurasi DEM untuk **piksel banjir di luar pita JRC**:
  tidak ada contoh kelas-1 di sana dalam dataset → peta probabilitas di
  luar pita adalah ekstrapolasi domain, tanpa bukti kalibrasi banjir
  di sana. (Peta tetap dibangun se-AOI; yang terbedakan adalah
  interpretasi, bukan angka metrik.)
- Klaim "inventory mewakili seluruh genangan kejadian Maret 2024" — tidak
  tersedia bukti; inventory hanya mencakup banjir **yang terdeteksi di
  pita JRC**.
- Perbandingan luas kelas-5 antar-DEM **tetap sah** (domain sama), tetapi
  luas ABSOLUT kelas sangat-tinggi harus dibaca sebagai luas *di dalam
  domain label* — di luar pita tidak ada contoh kelas-1, sehingga luas
  genangan fisik penuh tidak dapat diklaim dari peta.

## E. Rekomendasi tindakan minimal berikutnya

1. **TEKS proposal (tidak mengubah desain)** — tambahkan 1 kalimat
   keterbatasan di Bab IV (kandidat: 4.7 atau 4.2), mis.:
   > *Gate air-permanen pada konstruksi label memakai pita terpetakan JRC
   > GSW (footprint mask ≈ 12,8–14,4% AOI; nilai `occurrence` terbaca hanya
   > pada ± 4,3% AOI), sehingga label banjir (flood=1) hanya mungkin lahir
   > di dalam pita tersebut. Keterbatasan ini identik untuk ketiga produk
   > elevasi sehingga tidak memengaruhi perbandingan antar-DEM; implikasinya,
   > luas inventory banjir dan peta di luar pita merupakan ekstrapolasi
   > domain dan tidak mengklaim mewakili seluruh genangan kejadian.*
   > (draf; **DIAPLIKASIKAN ke `proposal.tex` 20 Okt 2026**: dua kalimat ini
   > masuk 4.7 Pembahasan hampir verbatim, ditambah satu kalimat sumber-run
   > WorldCover (v24 = run utama) di subbab WorldCover, satu kalimat
   > dual-model (peta GEE 300 vs evaluasi sklearn 400) di subbab pemodelan,
   > dan label "AUC CV terpooled" diganti "rerata AUC pada resample blok";
   > PDF direkompilasi 32 hlm, 0 undefined, 5 overfull legacy)
2. **Jangan ubah konstruksi label** pada run ini (sesuai batasan). Jika
   kelak desain dipilih diubah, perubahan minimnya adalah menambah
   `permanent_water.unmask(0)` **sebelum** `.Not()` pada sel 12 — sama pola
   dgn fix sampling v24. Konsekuensi: inventory berubah (flood=1 bisa muncul
   di luar pita) → WAJIB rerun penuh kernel + perumusan ulang angka Bab IV +
   konsultasi dosen. Belum dijalankan, menunggu keputusan.
3. **Koreksi definisi angka "12,78%"** di dokumen internal: itu Σ berbobot
   (≈ footprint 12,88%), bukan occ-bernilai (4,32%). T01 dikoreksi bersamaan.
4. **Tidak perlu v27.** Pertanyaan audit ini sudah terjawab; audit lain
   (N-2 wobble peta WC antar-run, N-3 konsistensi angka 4.5) tetap seperti
   laporan audit terdahulu.
5. Bila dosen menyetujui, tambahkan juga 1 kalimat yang memplementasikan
   item (ii) D-3 di bagian "Klaim yang belum dapat dibuat".

## Lampiran A — temuan audit v26 lainnya (N-2 / N-3 / N-4; mencatat, belum diperluas)

| ID | Temuan | Bukti | Dampak |
|---|---|---|---|
| **N-2** | Wobble statistik **peta** antar-run: ulang kernel dengan kode identik memberi statistik map-level yang sedikit berbeda — `worldcover_sensitivity.csv` v24 vs v26 per kelas tutupan beda hingga ±0,95 pp (shrubland: g−a 0,5402→0,5497; s−a 0,7014→0,6943; s−g 0,6018→0,6066; mangrove g−a 0,6182→0,6200); `area_per_risk_class_km2` ≤0,06 km²; `transition_*` ≤±100 px; `sensitivity_summary` beda di desimal ke-3 | diff `hasil_kaggle_v24` vs `hasil_kaggle_v26` | Pola/ranking stabil; angka persis run-dependent. Model-level metrik (sampling/split/RF/holdout/CV/bootstrap) **identik** antar-run → nondeterminisme hanya di jalur peta GEE (mosaic/cycle). Sumber belum diisolasi |
| **N-3** | Angka WorldCover 4.5 naskah = CSV **v24** (54,0/60,2/61,8–64,3; |Δp| shrubland 0,095) sedangkan CSV **v26** memberi 54,97/60,66/62,0–64,1 (|Δp| 0,094) | Tabel C-1/CSV dalam N-2 | Perlu keputusan: pertahankan v24 dgn catatan "run utama" atau quote v26; pola sama, beda ≤1 pp |
| **N-4** | Satu ukuran bootstrap blok di proposal 4.4 dilabel *“AUC CV terpooled”* (0,894/0,910/0,899) — itu rerata pada resample blok, ~0,009 di bawah pooled OOF klasik (0,9032/0,9174/0,9080) | `block16/bootstrap CSV` vs `spatial_cv_test_predictions.csv` | Perbaikan wording 4.4; bukan kesalahan angka |

Keputusan terkait (masuk kartu keputusan di STATUS/CONTEXT): N-2/N-3/N-4 = perbaikan teks; N-1 = keterbatasan Menunggu keputusan user.

**Status pasca-keputusan (20 Okt 2026)**: user memilih — 4.5/4.6 WorldCover
**pertahankan angka v24** (run utama) + satu kalimat sumber-run; tidak
mengubah angka demi menyamakan v26; pastikan 4.4 & subbab WorldCover tidak
berkesan berbagi run yang sama (solved via kalimat sumber-run di 4.4 dan
di subbab WC); perbedaan v24-vs-v26 tetap dicatat transparan di lampiran
ini (N-2/N-3); N-4 label diperbaiki di 4.4; kalimat keterbatasan N-1
(T04 E-1) masuk 4.7. Semua perubahan = teks + 1 kalimat; angka tak tersentuh.

## Lampiran — daftar file bukti

| File | Isi |
|---|---|
| `probe_v26/probe_label_jrc.py` + `.txt` output | replika sel 12; kedua grid; dekomposisi e1/e2/e3 |
| `probe_v26/probe_label_jrc2.py` + output | taksonomi kategori JRC; replika 187.777 tepat |
| `probe_v26/probe_label_jrc3.py` + output | proyeksi native; distribusi mask fraksional |
| `probe_v26/probe_label_jrc4.py` + output | count vs sum pada replika (bukti weighting) |
| `probe_v26/probe_label_jrc5.py` + output | histogram kode kategori 0-3 (count sahih) |
| `hasil_kaggle_v26/kernel_log_v26.log` | baseline kernel: probe 12,78%, hist label, pool v22/v24 |

**Quota note**: GEE project dalam *restricted mode* (kuota noncommercial
exceeded) — probe berukuran kecil tetap berhasil; tidak ada task raster diekspor.
