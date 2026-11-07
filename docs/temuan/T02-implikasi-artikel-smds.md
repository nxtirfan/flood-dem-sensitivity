# T02 — Implikasi Bias Sampling bagi Artikel SMDS yang Sudah Terbit

**Status**: analisis selesai 17 Okt 2026. Keputusan tindakan = milik 6
co-author (belum ada korespondensi jurnal). Pertanyaan pemicu user:
"waduh, berarti artikel SMDS saya yang sudah terbit jadi masalah dong?"

Artikel: *Flood Susceptibility Mapping … Semarang-Demak* (SMDS Vol. 1 No. 1,
2026, DOI `10.15294/smds.v1i1.62500`; 6 penulis). Naskah LaTeX:
`D:\Kuliah\1_Metopen\ARTIKEL REFERENCE - SMT 4\Flood Susceptibility Mapping\main.tex`.
Kontributor: kernel Kaggle `flood-susceptibility-semarang-demak-revision`;
dataset publik `semarang-demak-flood-training-and-results` (16 file) &
`semarang-demak-flood-training-data` (3 file, berisi CSV mentah 3.935 titik
berkoordinat).

## 1. Keputusan singkat (jawaban bagi user)

**Bukan kasus retraksi — tapi ada temuan yang perlu dikelola, dan bisa jadi
nilai jual artikel metopen.** Rinciannya:

1. Perbandingan 7 model tetap sah — semua model dilatih & diuji pada sampel
   yang sama (perbandingan internal-valid).
2. Naskah sudah sangat berhati-hati (kutipan di §3) — banyak dampak bias
   sudah "tertutup" oleh caveat yang dipublikasikan.
3. Yang belum akurat: atribusi penyebab "935 sampel banjir" + domain sampling
   tidak dinyatakan eksplisit di Bab metode.
4. Dataset & notebook publik → pola sabuk dapat ditemukan siapa pun yang
   mengaudit; "diamkan buat selamanya" bukan opsi tanpa risiko, tapi tidak ada
   yang memaksa koreksi sekarang juga.

## 2. Fakta yang terverifikasi tentang sampel terbit

- Kode baseline (kernel revision, mirror lokal:
  `C:\Users\Administrator\Downloads\flood-susceptibility-semarang-demak-revision.ipynb`
  cell sampling): `training_image = predictor_stack.addBands(flood_label)
  .updateMask(permanent_water.Not())` — mask JRC diterapkan ke **semua** band,
  termasuk band banjir (varian MET-001 yang lebih parah).
- Akibat (mekanisme T01): kandidat **kedua kelas** terkurung sabuk JRC
  (`occurrence` valid ≈ 4,3% AOI).
- Angka artikel: raw 3.935 = 3.000 non-flood + **935 flood**
  (main.tex:377–378; Tabel 403) → kandidat banjir tersedia ≈ **935 px ≈
  0,84 km² @30 m**. Kontradiksi internal naskah: artikel itu sendiri melaporkan
  luas banjir **44–56 km²** (main.tex:368–370) — 935 px tidak mungkin
  seluruh inventori; 935 = **artefak mask**, bukan kelangkaan piksel banjir.
- Re-ekstraksi titik terbit (v23, titik+split identik;
  `Proposal Baru/hasil_kaggle_v23/sample_audit.csv`): non-flood **58,95%**
  kelas WorldCover "water" (+14,8% wetland); flood **62,1% water** (+20,1%
  wetland); titik paling selatan hanya −7,03° (perbukitan selatan nol titik).
- Penjelasan internal yang turut tertipu: naskah menulis 935 "karena wilayah
  Semarang-Demak lebih kecil daripada ROI sekitarnya" (main.tex:378–380; lihat
  juga catatan komentar baris 293 tentang trade-off ROI) — mekanisme aslinya
  mask, bukan luas ROI.

## 3. Bantalan kejujuran yang SUDAH ada di naskah

- main.tex:384–390: dataset seimbang diinterpretasi sebagai *"modelling design
  for fair classification rather than a representation of natural flood
  prevalence"* + pengakuan *"reduces the diversity of non-flood samples"*.
- main.tex:881–882 (bagian SHAP, menjelaskan anomali dependence
  `dist_perm_water`): *"Permanent water is explicitly excluded from the flood
  label, and the sampling grid starts at the edge of the permanent-water
  mask"* — naskah **sudah menyentuh** hubungan sampling ↔ mask air (setengah
  benar; versi lengkapnya di T01).
- Framing hasil: "within-domain discrimination estimates", spatial CV sebagai
  "more conservative bound", "preliminary screening" — klaim generalisasi luas
  tidak pernah dibuat.

## 4. Risiko realistis

- Kategori: **keterbatasan metode + satu kalimat atribusi yang salah mekanisme**
  → cocok "clarification/corrigendum", BUKAN kehancuran kesimpulan.
- Bila ada pihak eksternal mengplotkan CSV publik 3.935 titik → pola sabuk
  terlihat jelas → ini bukti "ketertarukan audit" maksimum; transparan
  lebih baik dari ketemu sendiri.
- Anomali SHAP `dist_perm_water` (dependence non-monotonik, penjelasan
  "susah" di naskah) kini justru punya penjelasan mekanistik penuh (T01).

## 5. Opsi & rekomendasi

| Opsi | Isi | Kelebihan | Risiko/biaya |
|---|---|---|---|
| **A (disarankan)** | tidak mengubah artikel terbit; tangani eksplisit di **artikel baru** (metopen): "studi sebelumnya — juga milik kami — memakai domain sampel sabuk; ini kami identifikasi & koreksi" | tanpa drama; kontribusi metodologis; melindungi dari "ketauan" oleh pembaca kritis | artikel terbit tetap memuat atribusi salah (minor) |
| B | corrigendum/clarification singkat ke SMDS (1 paragraf: domain sampling + koreksi atribusi 935) | catatan aman di rekam | prosedur editorial; komando 6 penulis; bisa berjalan paralel dgn A |
| C | tidak melakukan apa pun | nol kerja | risikonya bila ditemukan pihak ketiga; belum fungsional vs keduanya |

Draf teks (paragraf klarifikasi/artikel baru) disiapkan setelah keputusan
co-author. KLAUSUL PENTING: keputusan final = semua co-author; sampaikan
netral + "kami menemukan ini saat audit metodologis untuk kelanjutan studi".

## 6. Bahan bicara untuk konsultasi co-author

1. Faktanya terjadi apa (T01 §1–§5 + tabel audit).
2. Peta sabuk (buat gambar partisipatif dari koordinat publik) — tiger
   evidence utama untuk diskusi internal.
3. Kedua jalan: manual (A) vs formal jurnal (B), bisa digabung.
4. Tetap jaga posisi: temuan datang dari audit mandiri, bukan dari
   tuntutan pihak lain — naskah berhak atas kejujuran proaktif, bukan
   "kena temukan lalu mengaku".
