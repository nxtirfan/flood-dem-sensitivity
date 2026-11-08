# T16 — Provenance dan integritas lintas artefak

Baseline Git: `7ab45a1d1d209f8b0d0570bee87dcf2e02daef28`. Working tree bersih sebelum T16. Inventaris awal memuat 388 berkas terlacak, termasuk 151 CSV, 36 GeoTIFF, 12 Parquet, dan 8 notebook. Pemeriksaan nama berkas ilmiah di luar inventaris tidak menemukan artefak penelitian tambahan; JSON runtime platform tidak termasuk sumber penelitian dan tidak dibaca isinya.

## Checksum manifest — FIX REQUIRED (metadata, bukan bukti korupsi raster)

`audit_provenance.py` memeriksa 45 referensi checksum aktif:
- 12 CSV/Parquet datasets pada manifest: cocok.
- 7 GEE-table CSV pada manifest: cocok.
- 13 raster pada export_status: cocok.
- 13 raster pada manifest.maps: 3 cocok, 10 tidak cocok dengan raster aktif.

Kesepuluh checksum yang tidak cocok dengan raster aktif **cocok dengan backup_unmasked**: tiga probabilitas, tiga delta, tiga agreement, dan proxy label. Ketiga risk-class raster tidak berubah. Dengan demikian, manifest.maps masih menunjuk fingerprint versi pramask, sedangkan export_status menunjuk raster aktif pascamask. Tidak ada bukti bahwa file aktif rusak hanya karena mismatch ini. Perbaikan yang disarankan setelah izin: manifest terversi membedakan hash asli dan hash pascaproses serta asal mask; jangan menimpa catatan provenance lama diam-diam. Tidak perlu melatih ulang model untuk perbaikan metadata ini.

Lihat `manifest_hash_audit.csv` (hash aktual, hash tercatat, dan kecocokan backup).

## Salinan hasil bukan satu versi yang dapat dipertukarkan

`artifact_copy_groups.csv` mencatat variasi byte untuk basename CSV/notebook yang sama. `audit_csv_copies.py` membandingkan 20 pasangan CSV hasil_kaggle vs delivery aktif, kolom demi kolom (urutan baris tetap, toleransi absolut 1e-10, rtol=0). Sebanyak 170 sel melampaui toleransi/berbeda pada 7 nama CSV:
- area_per_risk_class_km2.csv
- dem_stats.csv
- sensitivity_summary.csv
- tiga transition_*.csv
- worldcover_sensitivity.csv

Untuk area, selisih maksimum per DEM adalah 4,544356 / 4,554601 / 17,564393 km² (SRTM/GLO-30/AW3D30). Agreement maksimum berbeda 0,0031146101242161. Ini bukan sekadar format serialisasi. Sebaliknya CSV fitur, prediksi OOF, prediksi multiseed dan metrik model yang byte-nya berbeda tetap cocok secara numerik pada toleransi tersebut. Perbedaan ini adalah **antarversi hasil tersimpan**, tidak boleh dicampur dengan selisih **GEE vs raster lokal** pada versi yang sama.

Audit T16 memakai data/frozen dan data/gee_tables yang diverifikasi manifest serta raster aktif delivery untuk perbandingan utama. hasil_kaggle tetap dibaca sebagai artefak beku pembanding, bukan diubah atau ditimpa. Perbaikan yang disarankan: identitas versi/jalur sumber pada setiap statistik, bukan menyamakan semua berkas yang namanya sama.

## Notebook canon aktual

Dua salinan canon `Proposal Baru/Flood_DEM_Sensitivity_Notebook_v27_maskAOI.ipynb` dan salinan bernama sama di `v27_delivery/` mempunyai MD5 aktual `c0b8dcd4535183b086c4c161d86db30e`, bukan MD5 historis yang tertulis pada AGENTS.md. Nilai ini hanya fingerprint baseline yang diperiksa, bukan klaim kesalahan atau perubahan oleh T16. Hash SHA-256 file masing-masing tersedia pada inventaris. Pernyataan checksum historis tidak dipakai sebagai pengganti pembacaan berkas aktual.

## Integritas

`source_integrity_check.csv` harus diregenerasi paling akhir oleh `audit_provenance.py`. Kriteria penerimaan: seluruh 388 sumber tetap memiliki SHA-256 sama. Diagnostik dan laporan baru hanya berada di direktori ini. Tidak ada kompilasi proposal, perubahan angka/sampel/seed/model, notebook penuh atau panggilan GEE.
