# T17 — GEE slope 30 titik

Mulai dari [laporan T17](T17-gee-slope-investigation.md).

**Status: BLOCKED autentikasi. Tidak ada nilai slope baru hasil GEE.** Halaman login berhasil dibuka; editor terautentikasi tidak tersedia. Tidak ada script asli atau data penelitian ditimpa.

- `browser_access.json`, `gee_access.png`: bukti browser, tanpa login/akun.
- `auth_access.json`: keberadaan kredensial yang diperiksa dan hasil inisialisasi; tidak memuat secret.
- `check_browser_access.py`, `check_auth_access.py`: probe akses saja, bukan komputasi slope.
- `diagnostic/`: JavaScript terpisah dan builder input tepat 30 koordinat T16; **belum dijalankan di GEE**. Baca batas prosedur di dalamnya sebelum eksekusi.
- `source_integrity.csv`, `source_integrity_final.csv`: integritas seluruh sumber sebelum/sesudah T17.
- `setup_diagnostics.sh`: pemasangan alat terisolasi dan version-pinned; tidak login otomatis.

Reproduksi probe akses (dari root repositori):

```sh
sh docs/temuan/T17/setup_diagnostics.sh
/tmp/t17-venv/bin/python docs/temuan/T17/check_browser_access.py
/tmp/t17-venv/bin/python docs/temuan/T17/check_auth_access.py
```

Browser probe memakai konteks Chromium baru; sesi browser pribadi pengguna tidak otomatis tersedia di sini. Skrip auth hanya memeriksa rute yang dinyatakan notebook dan mencoba inisialisasi resmi; tidak meminta password atau menyalin private key. Setelah autentikasi resmi tersedia, hasil slope tetap harus diuji provenance-nya sebelum diperlakukan sebagai kondisi historis.

Rujukan API yang dipakai untuk review diagnostik:
- https://developers.google.com/earth-engine/apidocs/ee-image-reduceregion
- https://developers.google.com/earth-engine/apidocs/ee-image-sampleregions
- https://developers.google.com/earth-engine/apidocs/ee-projection-transform — `Projection.transform()` mengembalikan String WKT, bukan array affine; enam koefisien affine diperoleh dari metadata proyeksi.
- https://playwright.dev/python/docs/intro
