# T01 — Root Cause Bias Sampling "Sabuk JRC" (v20–v22 & baseline SMDS)

**Status**: DIAGNOSA SELESAI, terverifikasi dari empat arah (kode asli hasil
recover, audit sampel, probe piksel, angka label). Fix dieksekusi 17 Okt 2026
(§8). Dokumen koreksi naskah menunggu angka final v24 → `T03`.

## 1. Pemicu investigasi

Part A reanalisis lokal (rekonstruksi pipeline tanpa term mask JRC pada
sampling) menghasilkan sampel kelas-0 yang sangat beda dari sampel v22 Kaggle —
padahal sampel kelas-1 hampir identik. Elevasi mean kelas-0 melonjak 4,15 →
42,14 m; worldview-nya berpindah dari "sabuk pesisir basah" ke "se-AOI
termasuk perbukitan selatan".

## 2. Kode aktual v20–v22 (recover, verbatim)

Dipulihkan dari riwayat sesi (basis data opencode, edit part
`prt_10a2ba03c001EUEkZvJC6ZNCCG`, 10-05 10:46:33, `build_nb.py`; dump:
`C:\Users\ADMINI~1\AppData\Local\Temp\opencode\v20_sampling_edits.txt`).
Edit v21/v22 (10-06) tidak menyentuh sel sampling → kode di bawah berlaku
untuk v20 = v21 = v22:

```python
# Sampling per kelas v19 (revisi metodologis pasca-diagnostik v18):
#   Tahap 1: stratifiedSample pada SINGLE-BAND flood_label.
#   ...
#   Mask kelas-0 tetap mengecualikan perairan permanen (seperti baseline).
sampling_mask = flood_label.eq(1).Or(flood_label.eq(0).And(permanent_water.Not()))
label_for_sampling = flood_label.updateMask(sampling_mask)
locs_all = label_for_sampling.stratifiedSample(
    numPoints=SAMPLE_PER_CLASS, classBand='flood', region=roi, scale=SAMPLE_SCALE,
    seed=RANDOM_STATE, classValues=[0, 1], classPoints=[SAMPLE_PER_CLASS, SAMPLE_PER_CLASS],
    dropNulls=True, tileScale=TILE_SCALE, geometries=True).map(add_lon_lat)
```

Dengan `permanent_water = jrc_occurrence.gte(80)`; `jrc_occurrence` =
band `occurrence` dari `JRC/GSW1_4/GlobalSurfaceWater`.

**Ciri v22 vs baseline**: v22 mengecualikan air permanen HANYA dari kelas-0
(cabang `eq(1)` meng-unmask semua piksel banjir). Baseline SMDS memakai
mask multiband → dilihat T02.

## 3. Mekanisme akar masalah

Band `occurrence` JRC GSW adalah produk **sparse**: hanya valid (mapped) di
zona yang pernah terdeteksi berair (1984–2021). Di sembarang piksel tanpa
pemetaan (no-data):

1. `gte(80)` pada no-data → locked no-data (bukan FALSE),
2. `.Not()` atas no-data → **tetap no-data**,
3. `updateMask(sampling_mask)` → piksel itu **dibuang dari pool kandidat**.

Akibatnya kandidat kelas-0 bukan "seluruh AOI minus air permanen" melainkan
hanya **sabuk terpetakan JRC** (8,8% dari label=0, terverifikasi §4). Kelas-1
tidak terdampak.

## 4. Bukti piksel (probe GEE terverifikasi dari run §8, 17 Okt 2026)

Provider hist label AOI (log Part A): `{'0': 1.410.981, '1': 58.574}` px @30 m.

Nilai di bawah ini dihitung ulang oleh `sampling_probe()` di
`reanalisis_v24.py` **dalam pipeline yang persis sama** dengan sampling utama
(koneksi probe ≡ mask samplernya), jadi ini angka kunci yang final.
**Koreksi 20 Okt (T04)**: angka probe ad-hoc awal (63.499 px / 4,32%)
terverifikasi kembali SAHIH — itu definisi *piksel dengan nilai `occurrence`
(0..100)*; sedangkan 187.777 (12,78%) adalah ukuran Σ berbobot mask band
(fraksional 0..1) ≈ footprint 189.345 px (12,88%). Keduanya definisi berbeda,
bukan saling menggantikan; detail 3-lapis + bukti fresh:
`T04-audit-v26-label-jrc-probe.md`.

| Kuantitas | Nilai |
|---|---|
| Total piksel AOI @30 m | **1.469.555 px** ≈ 1323 km² |
| Hist label: 0 + 1 | 1.410.981 + 58.574 = 1.469.555 ≈ cocok total AOI |
| JRC `occurrence` valid — luas efektif berbobot (Σ mask) | 187.777 px ≈ 169,0 km² (**12,78 %** AOI; footprint count 189.345 = 12,88 %) |
| JRC `occurrence` — piksel dengan nilai terbaca (0..100) | 63.499 px (**4,32 %** AOI) |
| `occ ≥ 80` & valid (= air permanen) | 28.948 px ≈ 26,1 km² (Σ berbobot) |
| Pool kelas-0 mode sabuk (v22): `label=0 & NOT pw_sparse` | **123.616 px** (8,76 % dari label=0) |
| Pool kelas-0 mode fix (v24): `label=0 & NOT pw_dense(unmask 0)` | **1.382.033 px** (97,95 % dari label=0) |

Konsistensi aditif yang menutup kasus: label pool kelas-0 penuh ada
1.410.981 px, tetapi kandidat yang DILEWATI sampai sampler hanya 123.616 px
(8,76%) — sisanya (termasuk SELURUH perbukitan & kebun selatan) tersaring
diam-diam oleh no-data JRC. Jumlah label hist juga persis = total piksel AOI
(1.469.555 ≈ 1.469.555), jadi tidak ada piksel yang "hilang misterius".

## 5. Bukti audit sampel (kelas-0 terperangkap, kelas-1 selamat)

Sumber: `Proposal Baru/hasil_kaggle_v22/sample_audit.csv` (v22 Kaggle) vs
Part A lokal uniform (tanpa term JRC; artefak kini diarsip di
`Temp\opencode\reanalisis_v24\run_A_uniform_arsip\`):

| Ukuran audit | v22 Kaggle (sabuk) | Part A (tanpa term JRC) |
|---|---|---|
| n per kelas | 2936 | 2956 |
| elevasi SRTM mean ± std, kelas-0 | **4,15 ± 15,69 m** | **42,14 ± 77,50 m** |
| lat range kelas-0 | −7,0924 .. −6,7103 | −7,1369 .. −6,7097 |
| lc kelas-0 (40/10/50/80/90) | 43,6/1,0/2,1/30,3/16,9 % | 44,1/22,9/20,5/4,8/1,5 % |
| slope SRTM mean kelas-0 | 1,93° | 3,03° |
| elevasi SRTM mean, kelas-1 | 3,25 m | 3,26 m |
| lc kelas-1 (40/80/90) | 52,6/30,8/15,4 % | 52,3/31,0/15,4 % |
| lat range kelas-1 | −7,0420 .. −6,7127 | −7,0420 .. −6,7127 (identik) |

Kelas-1 identik ⇒ sampler & pool banjir bersih dari bug; hanya kelas-0
yang terperangkap pada sabuk. Slope mean turut mengonfirmasi: sabuk landai
(1,93°), AOI penuh landai-bukit (3,03°).

## 6. Implikasi terhadap hasil yang sudah ada

1. Semua metrik v17–v22 (random-split + spatial CV) = estimasi **dalam
   domain sabuk**, bukan ke-AOI. Masih VALID sebagai perbandingan **antar-DEM**
   (ketiganya memakai sampel sama), analog `within-domain` dari baseline.
2. **Sensitivitas spasial** (peta penuh: agreement/Δp/transisi/WorldCover)
   TIDAK ikut ter-korup (hitungannya pada seluruh piksel se-ROI, sample-free).
3. Klaim "non-flood acak se-AOI" TIDAK boleh dipertahankan — TEKS DESAIN
   harus dikoreksi (lihat `T03`).
4. Lagi-lagi kerentanan yang sama (varian lebih parah) ada di artikel SMDS
   terbit → `T02`.

## 7. Fix

```python
pw_for_sampling = permanent_water.unmask(0).rename('permanent_water')
sampling_mask  = flood_label.eq(1).Or(flood_label.eq(0).And(pw_for_sampling.Not()))
```

Semantik: no-data JRC (bukan air terdeteksi sama sekali) diperlakukan **BUKAN
air** — pool kelas-0 kembali = seluruh AOI minus air permanen sungguhan
(`occ ≥ 80`). Desain non-flood "acak se-AOI kecuali air permanen besar"
akhirnya sejalan tulisan metode. `SAMPLING_MODE='v22'` dipertahankan untuk
audit bias; `SAMPLING_MODE='v24'` = mode utama.

Referensi reproduksi: digunakan `reanalisis_v24.py` (mode `v22` dan `v24`
dengan mask berbeda, analisis RF identik proba-corrected: MET-002).

## 8. Hasil verifikasi & run v24 (17 Okt 2026) — TEREKSEKUSI

Setup: `reanalisis_v24.py` (LOKAL, sklearn, seed 42; `SAMPLING_MODE=v22` dan
`=v24`, REUSE=0; dua run penuh 7,1 + 7,6 menit; artefak per mode di
`Temp\opencode\reanalisis_v24\run_v22sabuk\` dan `run_v24fix\`). Probe piksel
kedua mode identik (lihat §4). Log: `log_v22sabuk.txt`, `log_v24fix.txt`;
audit gabungan ketiga sumber: `audit_duamode_lokal.xlsx`.

### 8.1 Mode v22 — verifikasi mekanisme: REPRODUKSI PERSIS

| Ukuran | v22 lokal (replika) | v22 Kaggle | Status |
|---|---|---|---|
| Stage-1 → stage-2 → mentah | 6000 → 5921 → **2936/2985** | 2936/2936 (final) | kuota sabuk terpenuhi |
| n final per kelas | 2936 | 2936 | identik |
| elev SRTM kelas-0 | **4,1546 ± 15,6915** | 4,1546 ± 15,6915 | **identik penuh** |
| lat range kelas-0 | −7,092424..−6,710280 | −7,092424..−6,710280 | **identik penuh** |
| lc_40/80/90/10/50 kelas-0 | 0,4356/0,3025/0,1693/0,0095/0,0208 | sama (4 dp) | **identik penuh** |
| kelas-1 | elev 3,2572; lc_40 0,5225 | 3,2531; 0,5255 | drift kecil (MET-004) |

⇒ Seed 42 + mask sabuk = **sampler sama-sampel** dengan Kaggle v22. Bias sabuk
kini TERBUKTI pada level reproduksi, bukan hanya inferensi audit. Drift arsip
S1 (MET-004) ternyata hanya menyentuh pool kelas-1 (elev beda 0,004 m; n tetap).

Metrik mode v22 lokal vs Kaggle:

| Metrik | SRTM | GLO-30 | AW3D30 | referensi Kaggle v22 |
|---|---|---|---|---|
| AUC holdout | 0,8267 | 0,8205 | 0,8187 | 0,8302/0,8281/0,8289 |
| AUC spatial CV (proba) | 0,6979 | 0,6999 | 0,6954 | legacy pseudo 0,652/0,651/0,648 |
| ΔAUC bootstrap (semua) | | | | CI memuat 0 — tak terbedakan |

### 8.2 Mode v24 (fix unmask 0) — sampel terkoreksi

Audit kelas-0: **kini se-AOI** — lat −7,136890..−6,709741; elev SRTM
**42,67 ± 77,93 m**; slope 3,08°; lc 40/10/50 = 44,9/23,1/20,8%, lc_90 hanya
1,6% (vs sabuk: elev 4,15 m, lc_80+lc_90 = 47,2%). Kelas-1 tetap identik
(domain banjir tak berubah oleh fix).

| Metrik (mode v24) | SRTM | GLO-30 | AW3D30 |
|---|---|---|---|
| AUC holdout | 0,9312 | **0,9399** | 0,9355 |
| acc@0,5 holdout | 0,870 | 0,885 | 0,878 |
| AUC spatial CV (proba) | 0,8694 | **0,8895** | 0,8747 |
| acc / F1 spatial CV | 0,798 / 0,791 | 0,827 / 0,828 | 0,805 / 0,801 |
| ΔAUC vs SRTM (bootstrap, 95%) | — | +0,0161 [+0,0128, +0,0194] | +0,0054 [+0,0027, +0,0080] |

Ordering **GLO-30 > AW3D30 > SRTM** konsisten holdout + 4-fold; gap kecil
(~0,01). Identik dengan arah Part A uniform lama (arsip: 0,9402/0,9497/0,9438;
ΔAUC −0,0165/+0,0114) — fix hanya pergeseran ~0,01 dari uniform penuh.

### 8.3 CAVEAT keputusan dokumen

1. **Angka v24 = estimasi se-AOI**: sampel kelas-0 kini acak se-AOI (puncak
   perbukitan masuk pool) → AUC naik ke 0,87–0,94 sebagian karena pemisahan
   yang lebih mudah. Angka sabuk v22 (spatial CV ~0,70) = skala pemisahan
   DALAM domain banjir; angka v24 = skala se-AOI. Dua skala ini HARUS
   dilaporkan berdampingan — jangan hanya satu.
2. CI bootstrap ΔAUC TIDAK memperhitungkan autokorelasi spasial → gap
   ~0,01 antar-DEM belum layak dijadikan ranking mutlak; perlu rerun kernel
   (bootstrap blok/kelompok) sebelum klaim peringkat.
3. Pipeline lokal sklearn v24 drop 1 kolom konstan (24 prediktor aktif) vs 25
   di kernel Kaggle — rerun kernel tetap rujukan angka final.
4. Sensitivitas spasial peta-penuh dari model v24 (Δp/agreement/transisi/
   WorldCover) BELUM dihitung — perlu rerun kernel; pola lama v22 tak
   otomatis berlaku.

Artefak run (LOKAL):
- `run_v22sabuk\` : `v22sabuk_sample_raw.csv` (5872×32) + `*_features/model/spatial_cv/test_predictions/delta`
- `run_v24fix\`   : `v24fix_sample_raw.csv` (5956×32) + idem
- audit gabungan: `audit_duamode_lokal.xlsx` (12×3 = 6 baris lokal + 4 baris Kaggle)

> Catatan 18 Okt: workspace temp ter-wipe; artefak lokal di atas HILANG.
> Semua angka kunci §8 telah terdokumentasi di sini dan
> `docs\temuan_empiris.md` §9 — tidak perlu recreate kecuali diminta.

## 9. Rerun kernel v24 (FINAL, 18 Okt 2026)

Kernel `nxtirfan/flood-dem-sensitivity-notebook-v24-fix-sabuk-jrc` (versi 25,
GPU T4, ~50 menit; catatan: title metadata berubah → slug bergeser dari
`...srtm-vs-glo-30-vs-aw3d30`). Dua kendala yang lalu: (1) push pertama
ERROR at `print('... test 25%...' % ...)` — tanda `%` di "25%" dianggap
karakter format; sudah difix jadi f-string; (2) slug bergeser karena title.
Artefak (19 file) disalin ke `Proposal Baru\hasil_kaggle_v24\`
(termasuk `kernel_log.log`).

Replikasi kernel vs LOKAL: probe (§4) identik semua 6 angka; n 2.978/kelas
identik; audit kelas-0 identik 6 dp; fold spasial identik. Pipeline sampai
ekspor 12 peta ke Drive SELESAI. Angka hasil akhir (25 prediktor):

| Metrik | SRTM | GLO-30 | AW3D30 |
|---|---|---|---|
| AUC holdout | 0,9318 | 0,9404 | 0,9360 |
| AUC spatial-CV proba | 0,8699 | 0,8899 | 0,8747 |
| AUC pooled 4-fold | 0,9032 | 0,9174 | 0,9080 |
| ΔAUC bootstrap vs SRTM | — | +0,0141 [+0,0109, +0,0173] | +0,0048 [+0,0023, +0,0074] |
| Agreement peta | — (ref) | 79,42% | 83,95% |
| mean abs Δprob peta | — (ref) | 0,0555 | 0,0371 |

→ Semua caveat §8.3 nomor 2-4 terjawab: rerun sukses, kernel = angka
final, sensitivitas spasial peta-penuh + WorldCover + transisi tersedia.
Frase "sabuk vs se-AOI" dua-skala tetap wajib di laporan. Bootstrap masih
piksel-level (bukan blok) — satu-satunya caveat tersisa. Mode v22 (sabuk)
kini hanya jadi materi diskusi perbandingan; angka utama proposal = tabel
di atas.
