# T16 — Inventaris dan rencana sebelum analisis mendalam

Baseline: `7ab45a1d1d209f8b0d0570bee87dcf2e02daef28`. AGENTS.md, CONTEXT.md, docs/STATUS.md dan laporan T15 telah dibaca. Instruksi khusus pengguna mengatasi kewajiban pembaruan dokumen global: hanya direktori T16 boleh ditulis; proposal, data, snapshot, log global dan notebook tidak diubah.

## Inventaris awal
`source_inventory.csv` mencatat jalur, ukuran dan SHA-256 semua berkas terlacak sebelum analisis. Kandidat utama: notebook canon v27 maskAOI; data/frozen, data/gee_tables, manifest dan export_status; 13 raster aktif beserta backup unmasked; outputs di delivery; hasil_kaggle. Varian old/arsip adalah pembanding provenance, bukan pengganti canon. Belum ada klaim bahwa geometri AOI independen tersedia atau tidak tersedia sampai penelusuran berkas, notebook dan arsip selesai.

## Rencana dan kriteria bukti
1. Telusuri kode label → filter slope → predictor stack → ekspor sampel. Identifikasi ulang semua titik positif >=5 derajat. Cocokkan ID/koordinat/tabel mentah; bila raster DEM/slope asli tidak tersedia, kosongkan nilai yang tidak dapat diukur dan tandai BLOCKED, bukan memperkirakan.
2. Temukan sumber AOI dan geometrinya dalam berkas/notebook/manifest/arsip. Audit CRS, affine, batas, NoData, domain valid, grid dan backup semua raster. Uji geografis outside-AOI hanya jika poligon asli tersedia; jangan membangun poligon dari mask.
3. Hitung ulang statistik dari artefak tersedia tanpa melatih model: luas kelas, agreement, transisi, Moran OOF/peta, block bootstrap berdasarkan kode tersimpan. Pisahkan prosedur, domain, denominator, area planar/geodesik dan hasil GEE. Bedakan rekonstruksi deterministik dari uji hipotesis/perbedaan estimasi.
4. Buat matriks temuan dengan VERIFIED / FIX REQUIRED / ACCEPTABLE DIFFERENCE / BLOCKED; sertakan bukti, akar sebab yang terbukti, hipotesis alternatif, dampak, usulan perbaikan/wording dan kebutuhan izin atau data lanjutan.
5. Jalankan diagnostik terpisah di T16, tinjau hasil dan diff, verifikasi ulang seluruh checksum baseline. Tidak menjalankan notebook penuh, GEE, training, regenerasi sampel atau proposal build.

## Pembagian audit
- Slope: penelusuran label, tabel 30 titik dan provenance nilai.
- Mask: pencarian geometri independen, metadata/domain raster dan dampak mask pada statistik peta.
- Statistik: audit OOF, Moran dan bootstrap serta provenance GEE.
- Koordinator: inventaris, integrasi bukti, verifikasi silang dan laporan utama.
