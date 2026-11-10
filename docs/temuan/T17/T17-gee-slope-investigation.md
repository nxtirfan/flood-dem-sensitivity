# T17 — Investigasi slope 30 titik melalui GEE

**Tanggal:** 10 November 2026. **Baseline:** `f5d825371d2f824703f3cb26546147562a2762ca`.

## Keputusan utama: BLOCKED pada akses GEE; tidak ada hasil slope baru

Browser automation dapat dijalankan menggunakan Playwright/Chromium terisolasi. Pembukaan langsung `https://code.earthengine.google.com/` **berhasil mencapai halaman login Google**, bukan editor terautentikasi. Redirect berhenti di host `accounts.google.com`, path `/v3/signin/identifier`, judul “Sign in - Google Accounts”. HTTP 200 adalah keberhasilan halaman login, **bukan** izin mengakses aset atau menjalankan GEE.

Tidak ada sesi Google pengguna yang disediakan pada konteks browser ini. Tidak ada login, perubahan skrip Code Editor, atau pengiriman kata sandi yang dilakukan. Pemeriksaan juga tidak menemukan kredensial pada lokasi eksplisit notebook, credential Earth Engine lokal, atau ADC lokal. Variabel `GOOGLE_APPLICATION_CREDENTIALS` dan `GEE_SERVICE_ACCOUNT_JSON` tidak tersedia. `ee.Initialize(project='ee-irfan-banjir-2026')` menghasilkan `EEException` yang meminta autentikasi. Tidak ada komputasi slope/GEE yang berhasil dievaluasi.

**Bukti:** `browser_access.json`, `auth_access.json`, dan `gee_access.png` (halaman login kosong, diperiksa visual). Skrip pemeriksaan disertakan. Tidak ada token, cookie, alamat akun pengguna, atau isi kunci kredensial dalam artefak ini.

## Cakupan yang selesai dan yang belum

| Permintaan | Status | Bukti / batas |
|---|---|---|
| Periksa browser dan Code Editor | VERIFIED untuk pengujian akses; BLOCKED untuk editor | Chromium berjalan; dialihkan ke login |
| Periksa notebook canon dan konfigurasi | VERIFIED sebagai artefak repositori | Notebook lokal tersedia; versi yang benar-benar dieksekusi historis tidak bisa dibuktikan hanya dari file saat ini |
| Gunakan 30 koordinat T16 | VERIFIED pada input diagnostik lokal | Tidak mengambil sampel baru; nilai slope beku hanya pembanding, bukan hasil GEE T17 |
| Reproduksi kedua jalur di server GEE | BLOCKED / NOT_EXECUTED | Tidak ada sesi/kredensial; kode diagnostik terpisah disiapkan tetapi belum tervalidasi runtime GEE |
| Ekspor slope, CRS, affine, scale, mask/validity aktual | BLOCKED / NOT_EXECUTED | Tidak ada CSV nilai kedua jalur hasil GEE yang dibuat; jangan menganggap template/input sebagai ekspor |
| Membuktikan sebab 30 kasus | BLOCKED | Tidak ada nilai filter aktual maupun uji pasangan kedua jalur; hipotesis T16 belum menjadi sebab terbukti |
| Memastikan aset historis masih sama/tersedia | BLOCKED | Metadata historis lokal tersedia; izin, ketersediaan, dan metadata aset saat ini belum teruji |

## Provenance: apa yang diketahui, apa yang tidak

Notebook canon lokal adalah `Proposal Baru/Flood_DEM_Sensitivity_Notebook_v27_maskAOI.ipynb`; CSV titik adalah `docs/temuan/T16/slope/slope_points_audit.csv`. Kedua sumber dibaca tanpa perubahan. Laporan rinci sumber/config dan kode diagnostik terpisah ada dalam `diagnostic/`.

Manifest delivery mencatat:

- `USGS/SRTMGL1_003`, band elevation; metadata historis `updateTime=2022-01-12T12:32:47.055141Z`, version null.
- `FAO/GAUL/2015/level2`, metadata historis `updateTime=2023-12-04T09:37:14.012831Z`, version null. Kode memakai Kota Semarang + Demak dengan fallback yang harus dicatat bila terjadi.
- `COPERNICUS/S1_GRD`, metadata koleksi historis `updateTime=2026-11-05T11:24:23.189041Z`. Periode before 25 Februari–12 Maret 2024; after 15–31 Maret 2024; filter IW dan VV/VH; tidak ada filter orbit pada panggilan yang dipakai.
- Snapshot koleksi S1 before: n=2, SHA-256 ID `ab9b9e1d6943585b35fdc70a509eed1e0d78051102068d62e263df492413baa8`.
- Snapshot S1 after: n=3, SHA-256 ID `f6e5e0609364e0e31acd295d1531d2d08117d91e607363a6ef3e01cb2e4e40ce`.
- `JRC/GSW1_4/GlobalSurfaceWater`, band occurrence, permanent-water threshold 80; metadata historis `updateTime=2025-06-05T20:36:52.798175Z`.
- Manifest dibuat `2026-11-05T12:16:25Z`, diperbarui `2026-11-07T17:56:21Z`.

Angka before=2 dan after=3 adalah **dua periode berbeda**, bukan bukti perubahan koleksi antar-run. Manifest menyimpan jumlah dan hash daftar ID, bukan daftar ID lengkap pada field tersebut. Metadata koleksi atau nama aset saja tidak membuktikan bahwa seluruh piksel, membership koleksi, urutan operasi, serta geometri identik dengan run historis.

T17 belum mengakses versi skrip tersimpan di akun Code Editor. Notebook Python lokal bukan otomatis script JavaScript Code Editor yang sama. Tanpa sumber eksekusi historis/identitas aset dan grid aktual, run baru kelak harus dilabeli **rekonstruksi saat ini**, bukan bukti kondisi historis.

## Hipotesis teknis yang tetap terbuka

Kode label menghitung slope atas SRTM yang di-clip ke ROI, sedangkan kode fitur mereproyeksi DEM ke EPSG:32749 skala nominal 30 m sebelum menghitung slope. Sampling label dan ekstraksi fitur juga merupakan dua operasi terpisah dengan proyeksi yang perlu dicatat. Komposit median S1, operasi power berbasis konstanta, dan proyeksi yang diminta saat sampling dapat memengaruhi evaluasi graph secara lazy.

Itu alasan mengukur beberapa konteks evaluasi **secara terpisah**, bukan alasan menyimpulkan salah satunya penyebab. Nilai “slope native pada koordinat” tidak otomatis sama dengan slope efektif saat filter label dievaluasi. Diagnostik harus mempertahankan perbedaan tersebut, mengukur mask/validity, dan tidak membuang titik yang masked.

Tidak tersedia bukti baru untuk mengubah kesimpulan T16: 30 nilai fitur >=5° terkonfirmasi pada data beku, tetapi penyebab per titik belum terbukti. Tidak ada threshold diubah, label dihapus, atau training Random Forest dilakukan.

## Langkah minimum agar investigasi dapat dilanjutkan

1. Sediakan sesi Google/GEE terautentikasi yang memang dapat diakses lingkungan ini, atau autentikasi API resmi pada project GEE yang diizinkan melalui mekanisme kredensial aman. Login di browser pribadi lain tidak otomatis menjadi sesi sandbox. **Jangan kirim password, refresh token, atau private key ke chat/repositori.**
2. Setelah akses tersedia, verifikasi izin/ketersediaan metadata aset, geometri AOI, membership S1 dengan algoritme fingerprint notebook, dan keterkaitan notebook dengan run beku. Kesamaan metadata belum cukup untuk menjamin identitas piksel historis.
3. Jalankan hanya diagnostik terpisah pada 30 koordinat tersimpan. Simpan tabel nilai, validity/mask, CRS/affine/nominalScale, posisi piksel/pusat sampling, waktu eksekusi, input hash, dan metadata aset aktual ke T17.
4. Uji dulu apakah slope fitur hasil rekonstruksi cocok dengan slope beku. Jika tidak, hentikan klaim kausal historis dan telusuri provenance. Jika cocok, bandingkan filter pada grid evaluasi label vs fitur serta kontrol grid, tanpa menyamakan pengukuran native dengan nilai filter efektif.
5. Nyatakan sebab terbukti hanya bila pola per titik dapat direproduksi dan alternatif perbedaan provenance/mask/sampling dieliminasi. Jika run baru berbeda, laporkan sebagai hasil baru yang belum ekuivalen historis.

## Verifikasi lokal dan integritas

`setup_diagnostics.sh` memasang alat pada virtualenv `/tmp/t17-venv`, bukan mengubah konfigurasi penelitian. Browser probe nyata dilakukan; API gagal pada autentikasi. Kode diagnostik hanya melalui pemeriksaan lokal, bukan eksekusi server GEE. Bukti integritas semua berkas sebelum T17 dicatat pada `source_integrity.csv`; pemeriksaan akhir pada `source_integrity_final.csv`.

Semua keluaran baru berada di `docs/temuan/T17/`. Proposal, T15, T16, notebook canon, label, sampel, raster, model, seed, threshold, serta hasil eksperimen beku tidak berubah. Tidak ada hasil simulasi yang diberi label sebagai hasil GEE.
