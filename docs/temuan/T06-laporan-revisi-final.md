# T06 — Laporan Eksekusi Paket Revisi Final

Tanggal: 2026-11-02 · Berkas kerja: `Proposal Baru\proposal_revisi-final.tex` (salinan; `proposal.tex` sumber TIDAK diubah)

## 1. Bagian yang direvisi

**Bab I–II (C)**
- 1.3 Rumusan masalah: kalimat pengantar singkatan RM ("Selanjutnya, rumusan masalah disingkat RM.") + tabel pemetaan RM→Tujuan dihapus, diganti kalimat sinkron nomor ("Setiap tujuan penelitian dirumuskan untuk menjawab rumusan masalah dengan nomor yang sama.").
- 1.5 Manfaat: manfaat akademis diperhalus ("Menyediakan contoh kajian empiris … dalam desain eksperimen terkontrol.").
- Bab II: "satellite"→satelit; dekorrelasi→dekorelasi; modul terain→modul terrain; interprestasi→interpretasi; mekanisme pohon RF ditulis ulang deskriptif ("membuat pohon-pohon relatif kurang berkorelasi"); "pilihan DEM"→"karakteristik dan resolusi DEM" (mencantumkan penjelasan utama); strategi riset "sebab-akibat"→"alur" (introduksi, caption, dan simpulan).
- 2.8 Paragraf Tique ditulis ulang: tanpa superlatif "rujukan terbaru paling relevan" dan tanpa klaim "kombinasi Copernicus DEM dengan metode hidrologi tertentu menghasilkan performa tertinggi"; faktanya hanya "membandingkan empat DEM, metode hidrologi, dan tiga model ML → desain multi-komponen menyulitkan penelusuran".

**Bab III (B)**
- 3.3: paragraf pengantar Tabel data ("dirangkum pada Tabel~\ref{tab:data}").
- 3.5: kalimat determinisme diganti ("Seluruh parameter ambang dan periode kejadian ditetapkan mengikuti konfigurasi penelitian acuan \cite{hakim2026} dan diterapkan identik pada ketiga eksperimen" + "Label dibentuk satu kali … perbedaan hasil antarperlakuan berasal dari sumber elevasi dan bukan dari perbedaan label"); akhir paragraf slope: acuan lereng berasal dari SRTM → label tidak sepenuhnya independen → Subbab 4.7.
- 3.6: heading "Prediktor non-elevasi dan dummy tutupan lahan" + paragraf caveat MERIT Hydro (turunan DEM luar perlakuan; konstan antarperlakuan; implikasi interpretasi) + pembersihan istilah "non-DEM"→"non-elevasi" (8 posisi: tabel kerangka teori, prosa kerangka berpikir, baris tab:desain, 3 deskripsi eksperimen, intro Bab IV).
- 3.8 menulis ulang: ROC-AUC + metrik pada ambang 0,5; Youden hanya informasi lanjutan dengan formula $J(t)=\mathrm{Sens}(t)+\mathrm{Spec}(t)-1$ + peringatan optimistis; jembatan autokorelasi (Robert dkk. / Michael-Jacques) menghubungkan ke tiga skema validasi (CV spasial 4-fold 16 blok; block bootstrap 1.000 kali berpasangan; multi-seed 5 seed).
- 3.9 menulis ulang: 3.9.1 (perubahan metrik + selang kepercayaan rujukan Subbab 3.8); 3.9.2 (definisi $\overline{|\Delta p|}$, tingkat kesesuaian kelas 5 kelas pada ambang tetap, luas per kelas, matriks transisi; penutup "di mana perubahan terkonsentrasi secara spasial"); perbaikan typo "ambang klasifikasi tetap".

**Bab IV (D)**
- 4.1 pembuka: hapus klaim "selisih vertikal relatif kecil" → deskripsi pola gambar lahan, perbedaan menonjol di median dataran rendah.
- Paragraf slope: mediana ($|\Delta\text{slope}|$) 0,85–1,24°, Spearman $|r|\le 0{,}06$; share <5° 98,99% / 99,97% / 98,76%; hapus klaim "tidak menggeser populasi label banjir secara substansial" → batasan independensi label–SRTM identik pada perlakuan → Subbab 4.7.
- 4.4 bootstrap: klaim "bersifat konsisten secara statistik" → "konsisten pada sampel ulang blok dalam eksperimen ini" (penegasan maksimal $\approx$0,016); pasangan SRTM–AW3D30: "peringkat belum dapat dipisahkan" (penghilang kata "marginal"); comparison tingkat piksel dituding dengan catatan (piksel dependen; lebih sempit; "tidak menjadikan dasar inferensi utama").
- 4.4 multiseed: "selalu berada di atas"→"tercatat di atas pada kelima seed (CV)" + kalimat bahwa pemisahan peringkat AW3D30–SRTM bergantung skema evaluasi (CV vs holdout $-\Delta$ berbeda).
- 4.5: hapus "selalu" pada klaim tiga skema persampelan; "4,25 juta piksel" → "sekitar 1,47 juta piksel" (AAU 1.469.555 px).
- 4.6: rentang badan air/lahan basah yang campur ("73%–83%") dipecah: air 77,4–82,7%; lahan basah 72,6–78,3%.
- 4.7 Pembahasan RM3-RM4: "secara statistik"→"konsisten pada sampel ulang blok" (maks 0,016); rentang kesesuaian per kategori: semak 54,0–70,1%; lahan terbuka 63,6–75,4%; mangrove 61,8–73,2% (pengganti "54,0%–66,9%" yang campur); pergeseran luas kelas ekstrem "4–12%"→"terhadap SRTM 2% hingga 9%" (denominator tunggal); atribusi note hanya Meadows (klaim Tique rilis).
- 4.7 Keterbatasan restrukturisasi 4 paragraf: (i) cakupan satu kejadian/satu wilayah/satu peta seed; (ii) label proksi S1 + tidak independen (slope-SRTM, pita JRC 12,8–14,4%/occ 4,3%, kecocokan 70%, DSM, datum tanpa koreksi); (iii) prediktor MERIT Hydro + tumpang tindih NDWI/MNDWI–label; (iv) 16 blok + implementasi dual-model (300 pohon GEE / 400 pohon scikit-learn) + penutup Subbab 5.2.

**Bab V (E)**
- Kesimpulan item 3: "bersifat konsisten secara statistik pada resampling blok" → "konsisten pada sampel ulang blok"; "masih memuat nol dan bersifat marginal" → "selang kepercayaan … masih memuat nol sehingga peringkat keduanya belum dapat dipisahkan" (rujukan subbab dipertahankan).

**Infra**
- Node TikZ kerangka berpikir (geo): hapus `\item` nyasar (korupsi edit lama; tidak ada di baseline) → fix error fatal kompilasi.

## 2. Inkonsistensi angka yang ditemukan + solusi

| # | Temuan | Nilai benar | Solusi |
|---|---|---|---|
| 1 | "sekitar 4,25 juta piksel" | populasi valid AAU = 1.469.555 px | "sekitar 1,47 juta piksel" |
| 2 | "73% hingga 83%" mencampur badan air & lahan basah | air 77,4–82,7% (0,7735–0,8272); wetland 72,6–78,3% (0,7261–0,7828) | dipecah dua rentang (4.6) |
| 3 | "54,0%–66,9%" mencampur semak (54,0) & lahan terbuka (66,9) | semak 54,0–70,1; terbuka 63,6–75,4; mangrove 61,8–73,2 | rentang per kategori (Pembahasan) |
| 4 | "pergeseran luas kelas ekstrem sekitar 4% hingga 12%" (tidak cocok basis mana pun) | vs SRTM: kelas 5 +8,6/+8,0%; kelas 1 +8,7/+2,1% (kelas menengah negatif hingga −18,5%) | "terhadap SRTM sebagai peta acuan … 2% hingga 9%" khusus kelas ekstrem |
| 5 | "0,095" $|\Delta p|$ semak dicurigai salah bulat dari 0,0942 (v26) | v24 = 0,094822 → 0,095 SAHIH | tidak diubah |
| 6 | share <5° 98,76/99,97% (versia dulu dianggap "bocoran") | terverifikasi lokal: SRTM 98,99%, GLO-30 99,97%, AW3D30 98,76% | dipertahankan dengan narasi rationale |

## 3. Hal yang tidak terverifikasi / dicatat

- Teks paket instruksi (D/E) tidak tersimpan di sesi → eksekusi berupa parafrase yang setia pada intent; di sini didokumentasikan.
- 43 halaman (baseline 42) akibat paragraf keterbatasan & definisi baru; 0 undefined, 0 kesalahan sitasi.
- Overfull 7 = 3 legacy (215–225: 8,18pt; 660: 6,45pt; 804–810: 8,67pt) + 4 mikro (870–876, ≤3pt) — semuanya <15pt, tidak meledak.
- Overfull baris 660 ("karakteristik/resolusi") muncul dari C3 (referensi \cite{fatdillah2022,fikri2026}) — layak diperbaiki bila dosen tidak setuju.
- `references.bib` tidak diubah; `proposal_revisi-final.bbl` disalin dari baseline (tidak ada sitasi baru).
- `zanaga2021` bib menghisalkan WorldCover v100 (makalah) sementara runtime memakai v200 — hanya masalah versi produk; judul diinformasikan; rerun tidak diperlukan; upgrade paper v200 opsional (keputusan user).
- "Tique" kini hanya di Bab I & II (sisi rujukan sah); Pembahasan hanya Meadows.

## 4. Menunggu keputusan user

1. **P1**: rerun label JRC (`chatgpt.md`) — bila ya, seluruh angka Bab IV dihitung ulang dan revisi M/B ini harus diulang pada angka baru.
2. Keputusan hasil P2 (audit angka Bab IV vs CSV v26) bila P1 memilih pertahankan.
3. Konsultasi progres ini ke Dr. Iqbal; `git init` + isi repositori.
4. Keputusan artikel SMDS (T02).
