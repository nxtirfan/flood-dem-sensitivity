# Paket audit T16

Mulai dari [T16-technical-investigation.md](T16-technical-investigation.md). Rencana sebelum analisis: [INVESTIGATION_PLAN.md](INVESTIGATION_PLAN.md). Semua sumber tetap read-only; file pada direktori ini adalah **audit baru**, bukan pengganti hasil penelitian.

## Reproduksi

Dari root repositori, gunakan Python 3.12 dan virtualenv di luar direktori sumber:

```sh
python -m venv /tmp/t16-venv
/tmp/t16-venv/bin/pip install -r docs/temuan/T16/diagnostic-requirements.txt
export PYTHONDONTWRITEBYTECODE=1
/tmp/t16-venv/bin/python docs/temuan/T16/audit_csv_copies.py
/tmp/t16-venv/bin/python docs/temuan/T16/slope/audit_slope_provenance.py
/tmp/t16-venv/bin/python docs/temuan/T16/mask/audit_masks.py
/tmp/t16-venv/bin/python docs/temuan/T16/statistics/recompute_statistics.py
/tmp/t16-venv/bin/python docs/temuan/T16/verify_raster_moran.py
/tmp/t16-venv/bin/python docs/temuan/T16/plot_slope_audit.py
/tmp/t16-venv/bin/python docs/temuan/T16/audit_provenance.py
```

Perintah statistik paling mahal: 21 kombinasi Moran titik × 9.999 permutasi dan bootstrap berpasangan 1.000 draw atas dua salinan prediksi. Ini **bukan** training, CV baru, atau notebook penuh. Moran raster hanya I deterministik: 999 permutasi peta **tidak diulang**. Jangan menganggap p peta yang disimpan telah direproduksi oleh skrip ini.

`diagnostic-requirements.txt` merekam lingkungan audit lengkap, termasuk paket yang terpasang tetapi tidak dipakai diagnostik; versi historis dan versi audit dibandingkan dalam `statistics/runtime_versions.csv`. Tidak perlu kredensial atau jaringan untuk menjalankan diagnostik setelah dependensi tersedia.

## Keluaran penting

- `source_inventory.csv`, `source_integrity_check.csv`: hash sebelum/sesudah semua 388 sumber.
- `manifest_hash_audit.csv`: 45 pemeriksaan checksum metadata; 10 mismatch yang diharapkan pada manifest maps stale, bukan pada export_status aktif.
- `artifact_copy_groups.csv`, `result_copy_numeric_audit.csv`: perbedaan versi/salinan sumber.
- `slope/slope_points_audit.csv`: 30 titik; NA_BLOCKED berarti data tidak tersimpan, bukan nilai nol atau perkiraan.
- `mask/raster_inventory.csv`: semua 36 GeoTIFF; CSV lain pada folder mask memuat grid, pencarian geometri, area, agreement, transisi, dan dampak backup.
- `statistics/moran_oof_recomputed.csv`: 21 kombinasi, I/p serta pembanding tersimpan.
- `statistics/moran_raster_recomputed.csv`: domain aktif dan backup, kebijakan island, pembanding cache/CSV; p raster tidak direplikasi.
- `statistics/block_bootstrap_recomputed.csv`: tiga pasangan pada dua salinan prediksi, mean/SD/CI.
- `independent_raster_moran_check.csv`, `isolated_raster_pixels.csv`: pemeriksaan independen konvolusi float64 dan lokasi dua island AW3D30.
- `slope_audit_overview.png`: visual nilai fitur slope; tidak menggambarkan nilai filter yang tidak tersedia.
- `slope/findings.md`, `mask/findings.md`, `statistics/findings.md`, `PROVENANCE_FINDINGS.md`: detail metode dan bukti.

Status VERIFIED pada hitungan lokal tidak memvalidasi geometri AOI. File `geometry_candidates.csv` dengan hanya header berarti pencarian tidak menemukan kandidat, bukan bahwa sumber AOI tidak pernah ada di GEE. Tabel transisi GEE berbobot yang di-cast integer tidak boleh diperlakukan sebagai pixel count raster final.

Tidak ada usulan perbaikan pada sumber yang diterapkan. Data/akses berikutnya yang diperlukan dijabarkan pada bagian 8 laporan utama.
