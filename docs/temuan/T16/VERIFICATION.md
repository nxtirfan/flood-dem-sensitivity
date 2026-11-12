# Verifikasi akhir T16

- Baseline sumber: 388 berkas; SHA-256 seluruhnya tetap sama.
- Skrip slope dijalankan ulang: 30/30 locator cocok unik; lon/lat, label, dan slope raw cocok tepat; 2.978 positif; maksimum 11,4838371276855°.
- Skrip mask dijalankan ulang: 36 GeoTIFF diinventarisasi, kelas/luas/transisi dan dua mismatch agreement direproduksi. Geometri AOI independen tetap tidak tersedia.
- Skrip statistik dijalankan ulang: 21/21 I Moran OOF cocok pada toleransi 1e-12; p OOF cocok; 6 baris bootstrap (tiga pasangan × dua sumber) cocok. Enam Moran raster diamati (aktif/backup), termasuk audit island. Permutasi peta tidak diulang.
- Verifikasi Moran independen dengan float64/convolution mereproduksi dua island AW3D30 dan I sesuai kode yang mengecualikannya.
- Audit provenance: 45 hash referensi; 10 mismatch manifest maps cocok backup, seluruh export_status cocok aktif.
- Audit salinan: 20 pasangan CSV dibandingkan; 170 sel berbeda melampaui toleransi 1e-10 pada tujuh nama file.
- Tujuh skrip Python lolos pemeriksaan sintaks AST; tautan Markdown lokal tersedia.
- Grafik slope dibangkitkan dari data beku dan diperiksa visual; tidak menggambarkan slope filter yang tidak tersedia.
- Tidak ada source diff, perubahan proposal/T15, pelatihan, notebook penuh, GEE, atau cache bytecode di luar T16.

Log eksekusi: `verification_run.log`, `mask/verification_run.log`, `statistics/verification_run.log`. Bukti integritas per berkas: `source_integrity_check.csv`. Semua keluaran berada di direktori T16.
