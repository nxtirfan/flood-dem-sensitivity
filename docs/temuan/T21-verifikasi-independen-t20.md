# T21 — Verifikasi Independen terhadap T20 (Koreksi Targeted terhadap Audit T19)

**Tanggal:** 18 November 2026
**Sifat:** Verifikasi independen *read-only*. Tidak ada file repo yang diubah, tidak ada kompilasi ulang, tidak ada commit/push. Seluruh pemeriksaan numerik dijalankan dari skrip verifikasi mandiri yang disimpan di luar repo (`%TEMP%\opencode\t21_verify_workbook.py`, `check_hashes.py`, `inspect_manifest.py`).
**Acuan utama:** `docs/temuan/T20-koreksi-targeted-t19.md` (finalisasi 18 Nov 2026 00.57.46 WIB, commit `383cac0`).
**Metode:** klaim T20 TIDAK dianggap benar otomatis; setiap klaim diuji terhadap artefak aktual (XLSX dibaca ulang, CSV diurai ulang, sumber beku dibaca ulang, raster dibaca via `rasterio` dengan transform dari file, notebook diurai dari JSON, PDF diekstrak via `pypdf`, zip dibongkar, git dibandingkan per byte).

## 1. Executive Summary

T20 terbukti menyelesaikan pekerjaan intinya dengan benar: workbook 30 titik valid dan cocok dengan sumber beku; redaksi L1057 proposal akurat terhadap kode Cell 31 notebook v28; retraksi parameter Sentinel-1 lengkap; status PARTIALLY VERIFIED/BLOCKED dipertahankan; commit dan push terverifikasi (origin/main = HEAD = `383cac0`); artefak beku (`frozen`, `rasters`) terbukti tidak tersentuh (SHA-256 lokal = manifest).

Namun verifikasi menemukan **7 catatan** yang harus dicatat (tidak ada yang menggugurkan hasil T20):

1. XLSX diserialisasi openpyxl pada 16 digit signifikan (`%.16g`), bukan "15 digit" seperti redaksi T20; 106/420 sel float XLSX berbeda ≤ ~4,3e-14 (≤ ~2 ULP) dari CSV; CSV tetap presisi penuh `.17g` (VERIFIED, redaksi minor).
2. Sel `feat_slope`/`final_slope` XLSX Titik 17 tergeser 1 ULP ekstra oleh `%.16g`, membuat baris 17 XLSX inkonsisten internal (sel slope −2 ULP dari nilai T17, sel diff tetap 1 ULP); CSV benar. Belum didokumentasikan T20.
3. Tabel §3.1 T19 baris 17 masih menampilkan `|Δ| vs v28 = 0,0e+00 (Exact)` — kontradiktif dengan catatan 1 ULP di bawah tabel yang ditambahkan T20 (tabel tidak di-update, hanya catatan).
4. Klaim T19 §3.2(2) "vs `sample_main_raw.parquet` 29/30 bit-exact" **salah secara lokal**: parquet bit-exact 30/30 dengan CSV v28; selisih 1 ULP adalah antara CSV diagnostik T17 (`…549`) dan CSV v28/parquet (`…547`). T20 tidak mengoreksi §3.2(2).
5. Klaim identitas berkas di T19 §3.1 (SHA-256 `ac65fb6b…`/`6797d22f…`/`b57a1788…`, ukuran `2.094.828`/`3.556.012` B) **tidak cocok dengan file lokal mana pun** (lokal: `89b81d72…` 2.777.932 B; `948dbde…` 952.140 B; `fd9d2f1…` 2.798.221 B = manifest). Provenance hash T19 tidak dapat diverifikasi dari repo.
6. **Perubahan pasca-commit tidak terdokumentasi**: tex diedit 01.04 (nama penulis "M. Irfan" → "M Irfan", L173 & L201), zip dibangun ulang 01.08 (3.845.045 B, 14 berkas, tanpa `pdf`/`bbl`/`bcf`), PDF dikompilasi ulang 01.09 (3.929.038 B, 50 hlm, frasa baru utuh). Semua SETELAH commit `383cac0` (00.59.29) dan SETELAH laporan T20/STATUS/CONTEXT finalisasi (≤ 00.58). Worktree kini lebih baru dari commit.
7. `bbl`/`bcf` kini **terhapus di worktree** (tercatat di HEAD), padahal T20 §8 dan STATUS.md menyatakan "dipulihkan dari HEAD (identik)". PDF yang dikomit sudah aman (sitasi tuntas), tetapi kompilasi ulang tanpa `bbl` akan menghasilkan sitasi undefined.

**Keputusan: B — T20 dapat diterima dengan catatan.**

## 2. Verifikasi Workbook 30 Titik

Skrip verifikasi: `t21_verify_workbook.py` (memuat ulang XLSX, mengurai CSV, dan **menghitung ulang seluruh 39 kolom × 30 baris langsung dari sumber beku**: `outputs/training_sample_features.csv`, `data/frozen/main/sample_main_raw.{parquet,csv}`, `diagnostics_t17/t17_slope_30point_diagnostic.csv`, `docs/temuan/T16/slope/slope_points_audit.csv`, `rasters/proxy_flood_label_sentinel1.tif`).

| # | Klaim yang diperiksa | Sumber & lokasi | Hasil pemeriksaan independen | Status |
|---|---|---|---|---|
| 2.1 | XLSX 30 baris × 39 kolom, bisa dibuka | `docs/temuan/T19/t19_30point_row_by_row_verification.xlsx` | `max_row=31, max_column=39`; header = skema 39 kolom skrip; sheet `T19 30-point verification`; dibuat openpyxl 2026-11-17T17:58:50Z (= 00.58.50 WIB, konsisten mtime). Seluruh sel float bertipe numerik (bukan string/bool); tidak ada nilai berskala 10^14–10^16; lon/lat 30/30 dalam rentang Semarang–Demak. | **VERIFIED** |
| 2.2 | Tipe data benar (angka, bukan string bergeser desimal) | seluruh 30×39 | Semua 14 kolom float numerik di 30 baris. Workbook lama-rusak (arsip) memuat `lon_tf = 1,10660809820595e+16` — kontras menegaskan perbaikan. | **VERIFIED** |
| 2.3 | Seluruh 30 titik diperiksa, bukan sampel | seluruh 30×39 | Rekonsiliasi penuh 30 baris; 0 sel melenceng terhadap rekomputasi independen (toleransi 1e-12; jarak cocok hingga 3,55e-15 m). | **VERIFIED** |
| 2.4 | XLSX & CSV cocok dengan sumber asli T20 | sumber beku (daftar di atas) | Semua nilai (koordinat, slope 4 rute, historic, baris/kolom/nilai raster, 3 kolom jarak Geod, flag bit-exact) cocok dengan rekomputasi mandiri. `audit_id`/`physical_line` mapping 30/30 cocok (mis. Titik 1 = `physical_line_128`, baris raw `5919`). | **VERIFIED** |
| 2.5 | CSV mempertahankan presisi `.17g` | `t19_…verification.csv` (12.733 B) | 14 kolom float: `format(float(x),'.17g') == x` untuk **420/420** sel (0 gagal). Kolom string (`tf_slp_str` dll.) dipertahankan verbatim dari CSV asli. | **VERIFIED** |
| 2.6 | "Excel menyimpan maksimum 15 digit" (T20 §2) | XML internal XLSX (`xl/worksheets/sheet1.xml` E2) | Tergamak `<v>110.6608098205957</v>` vs CSV `110.66080982059569`: openpyxl menulis **`%.16g` = 16 digit signifikan**, bukan 15. 106/420 sel float XLSX ≠ CSV, selisih maks `4,26e-14` abs / `3,93e-16` rel (≤ ~2 ULP). Substansi klaim (XLSX kehilangan presisi; CSV penuh) benar; angka "15 digit" tidak tepat. | **PARTIALLY VERIFIED** (redaksi) |
| 2.7 | Titik 17: konsistensi 1 ULP lintas T17/CSV/workbook | T17 CSV route `feat`; `training_sample_features.csv` L742; workbook `Z18`/`AC18` | T17 diagnostik `11.483837127685549` (`0x1.6f7b980000001p+3`); CSV v28/parquet/raw `11.483837127685547` (`0x…000000p+3`) — selisih tepat 1 ULP (`1,7763568394002505e-15`). Workbook sel `feat_diff_vs_tf`/`final_diff_vs_tf` = `1.7763568394002505e-15` (1 ULP) ✓. **Tetapi** sel `feat_slope`/`final_slope` XLSX = `11.48383712768555` (`0x…000002p+3`, hasil `%.16g` = 1 ULP ekstra di atas nilai T17), sehingga `abs(sel − slp_tf) = 3,55e-15 ≠ sel diff 1,78e-15` — inkonsisten internal baris 17 di XLSX (CSV benar). Tidak didokumentasikan T20. | **PARTIALLY VERIFIED** |
| 2.8 | Klaim "29/30 bit-exact feat/final vs CSV v28" | 30 baris | feat 29/30 & final 29/30 bit-exact; satu-satunya Titik 17. ✓ | **VERIFIED** |
| 2.9 | Baris/kolom raster proxy cocok sumber raster | `proxy_flood_label_sentinel1.tif` (EPSG:32749, 1592×2074, transform terbaca dari file, bukan hardcoded) | 30/30 baris & kolom & nilai cocok dengan rekomputasi dari `ds.transform`; 7 titik bernilai 1: **{1, 2, 6, 8, 15, 27, 28}** — persis klaim T19 §2.2(6). | **VERIFIED** |
| 2.10 | Skrip menghasilkan workbook yang diaudit | `build_t19_workbook.py` + XLSX | Verifikasi nilai-level: rekomputasi logika skrip yang ditulis ulang secara independen = isi XLSX (30×39). Eksekusi ulang skrip TIDAK dilakukan (batasan read-only), sehingga "reproducibility byte-level" tidak diuji; kesetaraan nilai penuh terbukti. | **PARTIALLY VERIFIED** |
| 2.11 | Workbook arsip = file rusak, bukan tertukar | `arsip/…BROKEN-serialisasi.xlsx` (13.950 B) | `lon_tf` baris 1 = `1.10660809820595e+16` (integer berskala) → benar file rusak; SHA-256 `0abfa07b…` ≠ workbook baru `cbea249b…`; struktur internal berbeda (tanpa `docProps/core.xml`). | **VERIFIED** |

## 3. Verifikasi Proposal TEX dan PDF

### 3.A Sampling L1057

| Klaim | Bukti | Status |
|---|---|---|
| Redaksi baru: target 3.000/kelas → ekstraksi prediktor → `notNull` → penyeimbangan → 2.978+2.978 | `proposal_revisi-final.tex` **L1057–1063** (teks persis seperti T20 §5); frasa muncul 1× di PDF hlm. 24 | **VERIFIED** |
| Urutan sesuai kode aktual | `Flood_DEM_Sensitivity_Notebook_v28.ipynb` Cell 31: L59 kuota `min(TARGET, n_nonflood, n_flood)`; L78–88 `stratifiedSample(numPoints=SAMPLE_PER_CLASS, classPoints=[…, …], seed=RANDOM_STATE, scale=SAMPLE_SCALE, geometries=True)`; L93–97 `sampleRegions`; L104–108 `filter(ee.Filter.notNull(predictor_bands_all))`; L128–135 `min(SAMPLE_PER_CLASS, raw_n0, raw_n1)` + `randomColumn('rand_balance', RANDOM_STATE).sort().limit()`; manifest `SAMPLE_PER_CLASS_FINAL: 2978` | **VERIFIED** |
| Seed 42 dipakai pada tahap yang tepat; tidak menyesatkan "satu seed untuk semua" | `RANDOM_STATE = 42` (Cell 8 L50); `stratifiedSample(seed=42)` Cell 31 L84; `randomColumn('rand_balance', 42)` L129; `randomColumn('random', 42)` L135 — **semua tahap sampling memang satu seed yang sama (42)**, sehingga "(\textit{seed}~42)" pada L1058 akurat. Multi-seed (5 seed) tercantum terpisah di L1108, L1583–1584, dan dinyatakan sebagai pengujian ketahanan, bukan sampling utama. Paragraf sebelum (L1037–1040: "seed sampling … dipertahankan identik antarperlakuan") dan sesudah (L1064–1066: CV spasial/bootstrap) konsisten. | **VERIFIED** |
| Angka 2.978 konsisten di seluruh proposal | L1061, L1302, L1360 (Tabel 4), L1365, L1401, L1416, L1436 — semua `2.978`; frasa "2.978 sampel banjir dan 2.978 sampel nonbanjir" muncul 1× di PDF (multiline). `1,01%` di L1416 = 30/2.978 = 1,008% ✓ | **VERIFIED** |
| Teks lama ("mengikuti jumlah populasi berlabel") hilang | `mengikuti jumlah populasi berlabel` = 0 di PDF; tidak ada di tex | **VERIFIED** |

### 3.B Parameter Sentinel-1

| Klaim | Bukti | Status |
|---|---|---|
| Proposal & kode: VH, < −18 dB, 8 piksel | tex L915, L918, L923, L1384 (`VH`, `$<-18$~dB`, `8 piksel`); notebook v28 Cell 15 L19–23 (`S1_POLARIZATION='VH'`, `AFTER_DB_THRESHOLD=-18`, `MIN_CONNECTED_PIXELS=8`); Cell 21 L29–36 (`flood_raw = s1_ratio.gt(1.25).And(after_pol_db.lt(-18))… connectedPixelCount(100, True).gte(8)`); manifest `config` sama persis; dua salinan notebook SHA-256 `CAAF9080…06DF9` identik (terhitung ulang) | **VERIFIED** |
| Tidak ada sisa klaim `VV`/`-16 dB`/`4 piksel` di proposal | grep tex: `VV` = 0 kecocokan; `-16` hanya muncul di `tadono2016` sitasi (`157–162`, L2223) — bukan parameter; tidak ada "4 piksel" | **VERIFIED** |
| Tidak ada sisa klaim VV/-16/4 yang belum dikoreksi di T19 | T19: semua kemunculan `VV`/`-16` kini berada di dalam konteks retraksi (ringkasan eksekutif Prioritas 7 L25, §2.1 catatan koreksi L39, §8.1 baris 1 L325, §8.3 L339/L348) | **VERIFIED** |

### 3.C PDF (independen, bukan dari log)

| Klaim | Bukti | Status |
|---|---|---|
| 50 halaman | `pypdf`: **50 pages** (PDF worktree 3.929.038 B, 01.09; PDF terkomit 4.001.765 B juga 50 pages) | **VERIFIED** |
| Teks L1057 ada, teks lama tidak | frasa baru 1× hlm. 24; lama 0× | **VERIFIED** |
| Tidak ada teks terpotong / layout rusak | tidak ada `??` (0×); "Daftar Pustaka" ada; entri bibliografi utuh di halaman akhir (snippet ESA WorldCover 2022 utuh); paragraf sampling utuh dalam satu blok hlm. 24 | **VERIFIED** |
| Isi PDF = TEX terbaru | PDF worktree memuat "M Irfan" (nama pasca-edit) dan frasa L1057 baru; PDF terkomit memuat "M. Irfan" + frasa baru; kedua PDF 50 hlm — konsisten dengan tex masing-masing versi (lihat catatan 6.3 tentang perubahan pasca-commit) | **VERIFIED** |

### 3.D ZIP

| Klaim | Bukti | Status |
|---|---|---|
| Memuat TEX terbaru; tidak ada versi lama bertentangan | `proposal_revisi-final.tex` di dalam zip **identik byte-level** dengan tex di disk (terverifikasi SHA-256) | **VERIFIED** |
| Bibliografi, logo, gambar lengkap | `references.bib`, `logo_unnes.png`, 11 `figures/*.png` semuanya ada; isi figures/bib/logo **identik** antara zip terkomit dan zip worktree (hanya tex yang berbeda, 124.263 → 124.261 B = edit nama) — klaim T20 "tidak ada perubahan isi figures" ✓ | **VERIFIED** |
| Memuat `bbl`/`bcf`/`pdf` (resep AGENTS.md §5.5: "tex, bbl, bcf, references.bib, logo, figures/, pdf") | **TIDAK ADA**: baik zip terkomit (4.020.179 B, 14 entri) maupun zip worktree (3.845.045 B, 14 berkas + 1 entri direktori) tidak memuat `proposal_revisi-final.pdf`, `.bbl`, `.bcf`. Deviasi dari resep rebuild yang terdokumentasi. | **FAILED → diperbaiki 18 Nov**: zip kanonis dibangun ulang sesuai resep (17 entri: tex, bbl, bcf, bib, logo, pdf, 11 figure; 7.718.356 B) |

## 4. Verifikasi Parameter Sentinel-1 (ringkasan)

- Notebook v28 (root & `v28_delivery`) Cell 15 + manifest `config` + arsip: `VH` / `-18` / `8` / target `3000` → final `2978`. **VERIFIED** (detail di 3.B).
- Cell 21 L29–42 rantai `flood_raw → selfMask → connectedPixelCount(100, True) → gte(MIN_CONNECTED_PIXELS) → unmask(0).clip(roi)` sesuai deskripsi T19 §2.1 baris 5 pasca-koreksi (konstanta, bukan literal). **VERIFIED**.
- Cell 27 L36/L83: `reproject(crs=ANALYSIS_CRS, scale=ANALYSIS_SCALE)` tanpa `.resample('bilinear')` — konsisten dengan penarikan klaim bilinear pada narasi T18 (T19 Prioritas 1). **VERIFIED** (klaim "bilinear" di proposal L1423 tetap ADA dan memang dilaporkan terbuka oleh T20 §7 — lihat §8 laporan ini).

## 5. Verifikasi Koreksi T19

| # | Klaim yang diperiksa | Lokasi | Hasil | Status |
|---|---|---|---|---|
| 5.1 | Klaim parameter VV/-16/4 ditarik penuh | T19 ringkasan eksekutif Prioritas 7 (L25), §2.1 (L39), §8.1 baris 1 (L325), §8.3 (L337–348) | Retraksi lengkap dengan bukti; tidak ada kemunculan VV/-16 di luar konteks retraksi | **VERIFIED** |
| 5.2 | §6.1 tidak lagi menyatakan penyebab terbukti | L211 (judul "(HIPOTESIS — belum direproduksi)"), L236 "indikasi kuat (bukan pembuktian)", L239 blok "Batas klaim (koreksi T20)" + daftar pekerjaan (a)–(c) | Redaksi hipotesis utuh; angka forensik (`1.464.458` vs `1.444.085`, `+20.373`, `+1,41079%`) dipertahankan | **VERIFIED** |
| 5.3 | §6.2 tidak lagi menyatakan mekanisme terbukti | L243 "tetap HIPOTESIS", L263 "(HIPOTESIS)", L274 "Batas klaim (koreksi T20)" + kebutuhan eksperimen reproduksi identik | Redaksi hipotesis utuh; rekonstruksi `0,59915–0,59993` dipertahankan sebagai fakta turunan | **VERIFIED** |
| 5.4 | Status PARTIALLY VERIFIED/BLOCKED dipertahankan | §2.3 (BLOCKED), §3.3, §4.3, §5.3, §6.3, §9 klaim 1–7 | Tidak ada isu yang dinaikkan statusnya menjadi selesai; tidak ada pernyataan T16–T18 tuntas | **VERIFIED** |
| 5.5 | Baris Prioritas 5 ringkasan eksekutif lengkap | L23 | 5A (angka + indikasi kuat ≠ pembuktian) dan 5B (lokasi piksel + rekonstruksi + hipotesis) lengkap | **VERIFIED** |
| 5.6 | Tabel AOI membedakan 1.448.338 / valid pusat / boundary-intersecting | L149–154 ("Pembeda jumlah piksel yang sering tertukar (koreksi T20)") + tabel L146–147 | `1.448.338` (total pusat dalam poligon), `1.444.077`/`1.429.575` (pusat valid dalam poligon), `8`/`7` (boundary-intersecting, di luar kategori NoData), aritmetika `1.448.338 − 1.444.077 = 4.261` dan `− 1.429.575 = 18.763` benar | **VERIFIED** |
| 5.7 | Konsistensi angka/istilah lintas laporan | ringkasan vs §6 vs §9 | `~1,41%`, `58.573`, `2.978`, `1.429.580`, `0,9544217226`, Queen/Rook konsisten. **Dua pengecualian**: tabel §3.1 baris 17 masih `0,0e+00 (Exact)` (kontradiksi dengan catatan 1 ULP L73 yang memang ditambahkan T20 — tabel tidak di-update); §3.2(2) L115 masih mengklaim "vs parquet 29/30" — kontradiksi dengan bukti lokal (parquet bit-exact 30/30; lihat 5.9) | **PARTIALLY VERIFIED** |
| 5.8 | Koreksi T20 tidak menghapus bukti penting T19 | seluruh T19 | Angka forensik dipertahankan: tabel §3.1 (30 baris), daftar 8 piksel batas §4.2 (L158–165), 4.261/18.763, detail Moran §5, tabel transisi §6.1, diff cell-by-cell §7, matriks status §9. Retraksi hanya menargetkan klaim parameter; §8.3 memuat tabel bukti pengganti | **VERIFIED** |
| 5.9 | (Temuan baru) klaim parquet §3.2(2) | L115 | Lokal: `sample_main_raw.parquet` slope Titik 17 repr = `11.483837127685547` = bit-exact dengan string CSV v28 (30/30 titik, bukan 29/30). Selisih 1 ULP yang nyata adalah **CSV diagnostik T17 (`…549`) vs CSV v28/parquet (`…547`)** — persis seperti didokumentasikan T20 §6.1, tetapi kalimat §3.2(2) tidak dikoreksi dan kini bertentangan dengan workbook kolom `float_exact_slp_tf_pq` (Titik 17 = True) | **FAILED → dikoreksi in-place 18 Nov** (§3.2(1)–(2) dan tabel baris 17 T19 kini memuat bukti lokal: feat/final 29/30 + 1 ULP; parquet/raw bit-exact 30/30) |
| 5.10 | (Temuan baru) identitas berkas §3.1 | L66–69 | Klaim SHA-256/ukuran (`ac65fb6b…` 2.777.932 B; `6797d22f…` 2.094.828 B; `b57a1788…` 3.556.012 B) tidak cocok dengan file lokal mana pun di repo (8 salinan diperiksa): lokal/manifest = `89b81d72…` (2.777.932 B), `948dbde…` (952.140 B), `fd9d2f1…` (2.798.221 B). Hash T19 kemungkinan dari salinan Drive dan tidak dapat diverifikasi dari repo | **PARTIALLY VERIFIED → dikoreksi in-place 18 Nov** (§3.1 T19 kini mencantumkan hash lokal yang identik dengan `manifest.json`, dengan catatan provenance) |
| 5.11 | (Temuan baru) formatting | akhir file L375 | Karakter ` ``` ` liar setelah tabel §9 (sisa fence) | **PARTIALLY VERIFIED** (kosmetik) |

## 6. Verifikasi ZIP dan Repository

| # | Klaim | Bukti | Status |
|---|---|---|---|
| 6.1 | Semua file yang dilaporkan T20 tercatat di commit | `git show --stat 383cac0`: 11 file — CONTEXT.md, tex, pdf, zip, STATUS.md, T19_VERIFICATION.md, arsip xlsx, build script, csv, xlsx, T20 report. `bbl`/`bcf` tidak masuk commit (klaim: identik dengan HEAD → tidak ada diff, wajar) | **VERIFIED** |
| 6.2 | Tidak ada perubahan tak disengaja pada notebook/raster/dataset/hasil | SHA-256 lokal vs `manifest.json`: `datasets/main/sha256_parquet = 948dbde…` ✓, `sha256_csv = fd9d2f1…` ✓, `maps/rasters/proxy_flood_label_sentinel1 = 45f090…` ✓, `prob_srtm = d0a50cf…` ✓ (semua byte-exact). v27_delivery salinan lama di `olds/v27_delivery/` juga identik hash-nya. Notebook dua salinan SHA `CAAF9080…` identik. Tidak ada M/D pada berkas hasil di status git (semua D/M yang tampil adalah reorganisasi v28 pra-eksisting) | **VERIFIED** |
| 6.3 | (Temuan baru) perubahan pasca-commit di worktree | `git diff HEAD`: tex ±2 baris (nama penulis "M. Irfan Al Hakim" → "M Irfan Al Hakim" di L173 & L201; mtime tex 01.04.51, zip 01.08.17, PDF 01.09.27 — semua > commit 00.59.29). PDF worktree = 3.929.038 B (50 hlm, frasa baru ✓, `??` = 0, nama "M Irfan"); zip worktree = 3.845.045 B (hanya tex berbeda vs zip terkomit). Laporan T20 (00.57.46), STATUS (00.58.09), CONTEXT (00.58.35) semua finalisasi SEBELUM edit ini → perubahan pasca-commit tidak terdokumentasi di mana pun. Edit nama berada di luar cakupan T20 (T20 hanya melaporkan L1057) | **PARTIALLY VERIFIED** → **terjawab 18 Nov**: perubahan pasca-commit tersebut merupakan perubahan manual oleh pengguna (nama penulis, PDF, ZIP) dan kini didokumentasikan di STATUS.md/CONTEXT.md; perubahan manual dipertahankan, tidak dibatalkan |
| 6.4 | `bbl`/`bcf` "dipulihkan dari HEAD (identik)" (T20 §8 L110; STATUS.md) | `git diff HEAD --stat -- bbl bcf` = **2 files deleted (4.058 baris)**; `git status` = `D` untuk keduanya. Klaim pemulihan tidak berlaku pada keadaan worktree saat ini (PDF yang terkomit aman — sitasi tuntas terverifikasi; namun kompilasi ulang tanpa `bbl` akan gagal sitasi) | **FAILED → diperbaiki 18 Nov**: `bbl` (64.580 B) dan `bcf` (114.514 B) dipulihkan dari HEAD |
| 6.5 | Push benar-benar terjadi | `git ls-remote origin main` = `383cac028e47…` = `git rev-parse HEAD` ✓; `git log origin/main` berisi `383cac0` | **VERIFIED** |
| 6.6 | (Temuan baru) residu | `docs/temuan/T19/__pycache__/` untracked (hasil import modul build saat verifikasi/sesi T20); tidak terkomit | **PARTIALLY VERIFIED** (housekeeping) |

## 7. Kontradiksi atau Kesalahan Baru

1. **T19 §3.2(2)** — klaim "vs `sample_main_raw.parquet` 29/30 bit-exact (Titik 17 …549 vs …547)" bertentangan dengan bukti lokal: parquet bit-exact 30/30 dengan CSV v28 (`…547`); 1-ULP adalah T17-diagnostik vs v28. Workbook sendiri (kolom `float_exact_slp_tf_pq` = True) membantah kalimat ini. T20 mengoreksi narasi serupa di §3.1 (catatan) tetapi melewatkan §3.2(2).
2. **T19 §3.1 tabel baris 17** — `|Δ| vs v28 = 0,0e+00 (Exact)` tidak di-update setelah catatan 1 ULP ditambahkan di bawah tabel; tabel dan catatan kontradiktif dalam satu subbab.
3. **T19 §3.1 daftar berkas** — SHA-256/ukuran tidak cocok dengan file lokal/manifest mana pun (lihat 5.10); sebagai klaim identitas berkas, tidak terverifikasi dan berpotensi menyesatkan.
4. **XLSX Titik 17** — sel slope tergeser 1 ULP ekstra oleh serialisasi `%.16g`, membuat baris 17 XLSX inkonsisten internal (slope −2 ULP vs diff 1 ULP). CSV benar. Belum dicatat T20.
5. **Redaksi "15 digit"** — aktualnya 16 digit signifikan (`%.16g` openpyxl); dampak substantif nol (selisih ≤ ~2 ULP), tetapi angka di T20 §2 dan STATUS.md tidak tepat.
6. **Perubahan pasca-commit** (nama penulis + recompile + rebuild zip) di luar cakupan T20 dan tidak terdokumentasi; zip tidak mengikuti resep AGENTS.md §5.5 (tanpa pdf/bbl/bcf) — berlaku untuk versi terkomit maupun versi worktree.
7. **`bbl`/`bcf` terhapus di worktree** padahal T20 §8/STATUS menyatakan dipulihkan — deskripsi tidak berlaku lagi untuk keadaan kini.

**Penanganan (cleanup 18 November 2026):** temuan 1–4 telah dikoreksi in-place di `T19_VERIFICATION.md` (tabel §3.1 baris 17, daftar berkas + catatan presisi §3.1, §3.2(1)–(2), §9 baris 3) dengan verifikasi lokal: `feat/final` 29/30 bit-exact + Titik 17 1 ULP; `sample_main_raw.parquet` dan `.csv` **bit-exact 30/30** terhadap CSV v28; selisih 1 ULP bersumber dari CSV diagnostik T17 (`…549`) terhadap CSV v28 (`…547`), bukan dari berkas beku. Temuan 5 dikoreksi di T19 dengan penanda "(koreksi T21)" — redaksi "15 digit" pada laporan T20 dibiarkan sebagai catatan historis. Temuan 6–7 diproses: `bbl`/`bcf` dipulihkan dari HEAD, zip kanonis dibangun ulang sesuai resep AGENTS.md §5.5, dan perubahan manual pengguna (nama penulis, PDF, ZIP pasca-commit) didokumentasikan di STATUS.md/CONTEXT.md tanpa dibatalkan.

## 8. Daftar Isu yang Masih Terbuka

| Isu | Status | Sumber |
|---|---|---|
| Reproduksi penuh graph historis `flood_label` | **BLOCKED** (dipertahankan) | T19 §2.3, T20 §7 |
| `max_abs_diff = 0,0` kolom historis T17 (`.round(6)`, 1 ULP Titik 17) | **PARTIALLY VERIFIED** (dipertahankan; diperkuat bukti T21) | T19 §3.3, T20 §7 |
| Provenance & NoData AOI (`4.261`/`18.763`) | **PARTIALLY VERIFIED** (dipertahankan) | T19 §4.3, T20 §7 |
| Moran Queen vs Rook + permutasi hanya AW3D30 | **PARTIALLY VERIFIED** (dipertahankan); proposal L1921 memakai "queen contiguity" — konsisten | T19 §5.3, T20 §7 |
| Denominator transisi `~1,41%` | **PARTIALLY VERIFIED** — hipotesis; reproduksi CRS terkunci belum dilakukan | T19 §6.1, T20 §7 |
| 2-pixel agreement mismatch `(525, 1332)` | **PARTIALLY VERIFIED** — mekanisme hipotesis | T19 §6.2, T20 §7 |
| Klaim "reproyeksi bilinear" (L1423) dan `N = 1.469.555` Tabel 4 (L1360/1365) | **NOT ADDRESSED** — memang di luar cakupan T20, dilaporkan jujur sebagai terbuka di T20 §7, T19 Prioritas 7(4), STATUS.md, CONTEXT.md | — |
| Presisi XLSX ("15 digit") & inkonsistensi baris 17 XLSX | **BARU (T21)** — minor, lihat §7.4–7.5 | — |
| Identitas hash §3.1 T19 & klaim parquet §3.2(2) | **BARU (T21)** — perlu koreksi teks T19 (tanpa sentuh data) | — |
| Perubahan pasca-commit worktree + bbl/bcf + resep zip | **BARU (T21)** — perlu keputusan user (commit terpisah / dokumentasi) | — |

## 9. Kesimpulan dan Rekomendasi

**Verdict: B — T20 dapat diterima dengan catatan.**

Hasil inti T20 terverifikasi independen: workbook valid dan selaras dengan sumber beku (2.1–2.5, 2.8–2.9, 2.11), redaksi L1057 akurat terhadap kode (3.A), retraksi parameter lengkap (3.B, 5.1), status isu dipertahankan jujur (5.2–5.6, §8), artefak beku tidak tersentuh (6.2), commit/push nyata (6.1, 6.5). Tidak ada indikasi perubahan data, sampel, model, atau parameter eksperimen.

Rekomendasi (semua koreksi teks/dokumentasi, tanpa menyentuh data; **tidak dieksekusi dalam T21**):
1. Koreksi kalimat T19 §3.2(2) tentang parquet (jadi: parquet bit-exact 30/30; 1-ULP = T17 vs CSV v28) dan update sel tabel §3.1 baris 17 (`|Δ| vs v28` → `1,78e-15 (1 ULP)`). — **DIEKSEKUSI 18 Nov**
2. Anotasi klaim SHA-256/ukuran §3.1 T19 sebagai "hash salinan audit eksternal, bukan file lokal" atau ganti dengan hash lokal/manifest (`89b81d72…`, `948dbde…`, `fd9d2f1…`). — **DIEKSEKUSI 18 Nov**
3. Catat di T20/T19: XLSX memakai 16 digit signifikan (`%.16g`); sel `feat_slope`/`final_slope` Titik 17 XLSX tergeser 1 ULP oleh pembulatan tersebut (CSV = acuan presisi). — **DIEKSEKUSI di T19 18 Nov** (redaksi "15 digit" pada laporan T20 dibiarkan historis)
4. Putuskan perlakuan atas perubahan pasca-commit (edit nama penulis, PDF 01.09, zip 01.08): commit terpisah dengan dokumentasi, atau kembalikan — sesuai kebijakan user; sertakan `bbl`/`bcf`/`pdf` pada zip bila mengikuti resep AGENTS.md §5.5, dan pastikan `bbl`/`bcf` tersedia lagi di worktree sebelum kompilasi berikutnya. — **DIEKSEKUSI 18 Nov**: perubahan manual dikonfirmasi pengguna dan didokumentasikan; `bbl`/`bcf` dipulihkan; zip kanonis dibangun ulang sesuai resep (17 entri)
5. Hapus `docs/temuan/T19/__pycache__/` dan fence ` ``` ` liar di akhir T19 (housekeeping). — **DIEKSEKUSI 18 Nov**

## 10. Cleanup dan Arsip (18 November 2026)

Inventarisasi arsip lama, duplikat, dan berkas sementara dilakukan dengan pemeriksaan provenance (SHA-256/isi) sebelum penghapusan:

- **Dipertahankan (kanonis/bukti audit):** workbook T19 XLSX + CSV (satu-satunya salinan, terverifikasi), arsip rusak `arsip/…BROKEN-serialisasi.xlsx` (bukti serialisasi, dirujuk T19 §8.1), `probe_v26/`, `T16/`, `T17/` (bukti audit ter-track), `olds/hasil_kaggle_v26/hasil_kaggle.zip` (arsip v26, SHA berbeda dari zip ter-track — provenance tersendiri), `olds/v27_delivery/…/outputs.zip` (zona beku AGENTS.md), `smds/smds_dem_sensitivity_source.zip` (artikel SMDS, agenda aktif T02), seluruh `v28_delivery/` (sumber kebenaran angka).
- **Dihapus:** `docs/temuan/T19/__pycache__/` (residu build, tidak dirujuk dokumen mana pun) dan `olds/arsip_draft_proposal/Outdated_proposal_revisi-final_source.zip` (duplikat usang: tex lama 102.997 B tanpa frasa L1057, tergantikan zip kanonis).
- **Dipulihkan/dibangun ulang:** `proposal_revisi-final.bbl` + `.bcf` dari HEAD; `proposal_revisi-final_source.zip` dibangun ulang sesuai resep AGENTS.md §5.5 (tex, bbl, bcf, references.bib, logo_unnes.png, proposal_revisi-final.pdf, 11 figure di `figures/` — 17 entri, 7.718.356 B).

Laporan ini tidak melakukan perubahan apa pun pada data hasil dan tidak di-commit, sesuai instruksi.
