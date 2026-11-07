# Isian Google Form — Proposal Metopen (Desain Baru)

> Salinan verbatim untuk copy-paste ke Google Form.
> **KOREKSI pada Referensi Utama 5:** teks asli memakai DOI `10.1016/j.jenvman.2025.127128`,
> tetapi DOI itu milik Zerouali dkk. (2025, Jeddah) — BUKAN artikel SMDS.
> Artikel SMDS baseline (Al Hakim dkk., SMDS Vol. 1 No. 1, hlm. 22–47) ber-DOI
> `10.15294/smds.v1i1.62500`. DOI sudah dikoreksi di bawah.

---

## Email

`mirfanhakim25@students.unnes.ac.id`

## Nama

M Irfan Al Hakim

## NIM

2404220023

## Judul Penelitian

Analisis Sensitivitas Produk Elevasi Global terhadap Pemetaan Kerawanan Banjir Berbasis Machine Learning Menggunakan Google Earth Engine: Studi Komparatif SRTM, Copernicus DEM GLO-30, dan ALOS AW3D30 di Wilayah Pesisir Semarang-Demak

## Urgensi Penelitian

Pemetaan kerawanan banjir menggunakan machine learning membutuhkan faktor prediktor yang merepresentasikan kondisi fisik wilayah, salah satunya informasi topografi dari produk elevasi. Produk elevasi global memiliki sumber data, karakteristik sensor, dan proses pengolahan yang berbeda sehingga dapat menghasilkan representasi topografi yang berbeda. Perbedaan tersebut dapat memengaruhi hasil pemetaan kerawanan banjir, terutama pada wilayah pesisir yang relatif datar.

Penelitian terdahulu menunjukkan bahwa perbedaan produk DEM dapat memengaruhi hasil pemodelan banjir dan flood susceptibility. Selain itu, karakteristik kesalahan DEM dapat berbeda menurut kondisi terrain dan tutupan lahan. Oleh karena itu, penelitian ini dilakukan untuk menguji seberapa sensitif hasil pemetaan kerawanan banjir terhadap pemilihan sumber produk elevasi, dengan komponen pemodelan lainnya dibuat konsisten.

## Tujuan Penelitian

1. Membandingkan parameter topografi yang dihasilkan dari SRTM, Copernicus DEM GLO-30, dan ALOS AW3D30 di wilayah pesisir Semarang-Demak.
2. Membangun model pemetaan kerawanan banjir menggunakan Random Forest dengan flood inventory yang diperoleh dari Sentinel-1 SAR.
3. Menganalisis perbedaan hasil pemetaan kerawanan banjir ketika sumber produk elevasi diganti dengan SRTM, Copernicus DEM GLO-30, dan ALOS AW3D30 dalam eksperimen yang terkontrol.
4. Menganalisis sensitivitas spasial hasil pemetaan terhadap perubahan produk elevasi serta melihat perbedaannya berdasarkan kelas tutupan lahan.

## Data dan Deskripsinya

Data utama berupa tiga produk elevasi global, yaitu SRTM, Copernicus DEM GLO-30, dan ALOS AW3D30. Ketiga produk digunakan secara bergantian untuk menghasilkan parameter topografi yang digunakan sebagai prediktor.

Sentinel-1 GRD digunakan untuk membentuk flood inventory melalui perubahan nilai backscatter antara kondisi sebelum dan saat/setelah kejadian banjir. JRC Global Surface Water digunakan untuk membantu mengecualikan perairan permanen.

ESA WorldCover digunakan sebagai data pendukung untuk melakukan stratifikasi hasil berdasarkan kelas tutupan lahan.

Data prediktor non-elevasi dan komponen pemodelan lainnya dibuat sama pada seluruh eksperimen. Seluruh pengolahan dilakukan menggunakan Google Earth Engine.

## Metode Penelitian

Penelitian menggunakan eksperimen terkontrol untuk menguji sensitivitas sumber produk elevasi terhadap hasil pemetaan kerawanan banjir.

Tahap pertama adalah membentuk flood inventory menggunakan Sentinel-1 SAR dengan menganalisis perubahan backscatter antara kondisi sebelum dan saat/setelah kejadian banjir. Area perairan permanen dikeluarkan menggunakan JRC Global Surface Water.

Selanjutnya digunakan Random Forest untuk membangun model flood susceptibility. Eksperimen dilakukan sebanyak tiga konfigurasi berdasarkan sumber elevasi:

1. SRTM
2. Copernicus DEM GLO-30
3. ALOS AW3D30

Pada setiap konfigurasi, parameter topografi yang bergantung pada elevasi dihitung dari produk DEM yang digunakan. Sementara itu, flood inventory, prediktor non-elevasi, wilayah penelitian, prosedur sampling, Random Forest, dan parameter model dibuat sama. Dengan demikian, perlakuan utama yang dibandingkan adalah sumber produk elevasi.

Setiap konfigurasi menghasilkan peta probabilitas kerawanan banjir. Hasil model dibandingkan menggunakan accuracy, precision, recall, F1-score, dan ROC-AUC. Selain performa model, dilakukan analisis sensitivitas spasial dengan membandingkan perubahan probabilitas, kesesuaian spasial, dan perubahan kelas kerawanan antarproduk elevasi.

Selanjutnya, ESA WorldCover digunakan untuk melakukan stratifikasi sehingga dapat dianalisis apakah sensitivitas hasil pemetaan terhadap perubahan produk elevasi berbeda pada kelas tutupan lahan tertentu.

## Referensi Utama 1

`https://doi.org/10.1007/s11069-025-07868-y`

Tique et al. (2026), *A comparative assessment of data-driven flood susceptibility mapping in Nigeria.*

## Referensi Utama 2

`https://doi.org/10.1080/17538947.2024.2308734`

Meadows et al. (2024), *Vertical accuracy assessment of freely available global DEMs (FABDEM, Copernicus DEM, NASADEM, AW3D30 and SRTM) in flood-prone environments.*

## Referensi Utama 3

`https://doi.org/10.3390/w14142208`

Fatdillah et al. (2022), *Spatial Estimates of Flood Damage and Risk Are Influenced by the Underpinning DEM Resolution: A Case Study in Kuala Lumpur, Malaysia.*

## Referensi Utama 4

`https://doi.org/10.3390/w18101203`

Fikri et al. (2026), *Influence of DEM Spatial Resolution on the Accuracy and Computational Efficiency of HEC-RAS 1D and 2D Flood Inundation Modelling: A Case Study of the Cimanceuri Basin, Indonesia.*

## Referensi Utama 5

`https://doi.org/10.15294/smds.v1i1.62500`  ← (DIKOREKSI; teks asli salah pakai `10.1016/j.jenvman.2025.127128`)

Al Hakim et al. (2026), *Comparative explainable ensemble learning for flood susceptibility mapping using Sentinel-1-derived flood inventory and multi-source geospatial data: A case study of the Semarang-Demak coastal area.* Statistical Modeling and Data Science, 1(1), 22–47. Artikel SMDS sebelumnya yang menjadi baseline penelitian, khususnya untuk penggunaan Sentinel-1 dan machine learning dalam pemetaan kerawanan banjir di wilayah Semarang-Demak serta dasar pemilihan Random Forest.

---

**Catatan sebelum kirim:** versi ini sengaja TIDAK menyebut multi-event, DEMNAS, atau NASADEM
sebagai bagian eksperimen. Desain yang disepakati: **3 DEM → RF dikontrol → susceptibility →
spatial sensitivity → WorldCover stratification.**
