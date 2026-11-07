# Probe 5 - PENGHITUNGAN FINAL metode count-sahih: band kode kategori 0-3
# (flood_state x jrc_state) + ee.Reducer.frequencyHistogram, TANPA ambiguitas
# mask fraksional (mask dibuka dengan unmask(0); jumlah piksel dihitung dari
# ukuran histogram, bukan sum berbobot).
#   kj: 0 = flood=0 & JRC no-data | 1 = flood=0 & JRC ada-occ | 2 = flood=1 & JRC no-data | 3 = flood=1 & JRC ada-occ
#   kr: 0 = flood_raw valid-false | 1 = flood_raw valid-true | 9 = flood_raw masked (kandidat hilang)
# CATATAN HASIL (lihat output): band komb masih mewarisi mask dari operand
# (footprint JRC), sehingga AOI dari histogram komb = piksel bermask >0 saja
# (~1,32 juta, bukan 1,469.555). Dampaknya: hitung rasio di dalam histogram
# konsisten, tapi pembilang-penyebut AOI PENUH tetap ambil angka kernel
# (AOI=1.469.555; flood=1=58.574; flood=0=1.410.981). (c)=0 tetap definitif
# karena ketegori 2 (flood=1 & JRC no-data) KOSONG pada histogram.
import ee

CRED = r"D:\Kuliah\1_Metopen\Proposal Baru\.credentials\ee-irfan-banjir-2026-44c092a9f72b.json"
PROJECT = "ee-irfan-banjir-2026"
ee.Initialize(credentials=ee.ServiceAccountCredentials(email=None, key_file=CRED), project=PROJECT)


def db_to_power(img_db):
    return ee.Image(10).pow(img_db.divide(10))


def get_s1_median(start, end, roi):
    col = (ee.ImageCollection('COPERNICUS/S1_GRD')
           .filterBounds(roi)
           .filterDate(start, end)
           .filter(ee.Filter.eq('instrumentMode', 'IW'))
           .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
           .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'))
           .select(['VV', 'VH']))
    return col.median().clip(roi)


wilayah_indonesia = ee.FeatureCollection('FAO/GAUL/2015/level2').filter(ee.Filter.eq('ADM0_NAME', 'Indonesia'))
semarang_demak = wilayah_indonesia.filter(ee.Filter.inList('ADM2_NAME', ['Kota Semarang', 'Demak']))
roi = semarang_demak.geometry()

s1_before = get_s1_median('2024-02-25', '2024-03-12', roi)
s1_after = get_s1_median('2024-03-15', '2024-03-31', roi)
before_pol_db = s1_before.select('VH')
after_pol_db = s1_after.select('VH')
s1_ratio = db_to_power(before_pol_db).divide(db_to_power(after_pol_db)).rename('s1_ratio')

dem_for_label = ee.Image('USGS/SRTMGL1_003').select('elevation').clip(roi)
slope_for_label = ee.Terrain.slope(dem_for_label).rename('slope')

jrc_water = ee.Image('JRC/GSW1_4/GlobalSurfaceWater').select('occurrence').clip(roi)
permanent_water = jrc_water.gte(80).rename('permanent_water')

flood_raw = (s1_ratio.gt(1.25)
             .And(after_pol_db.lt(-18))
             .And(permanent_water.Not())
             .And(slope_for_label.lt(5)))
flood_label = (flood_raw.selfMask()
               .connectedPixelCount(100, True)
               .gte(8)
               .unmask(0)
               .rename('flood')
               .clip(roi))

jrc_ada = jrc_water.unmask(-9999).neq(-9999)   # occ band punya nilai (0..100)
flood1 = flood_label.eq(1)                      # flood_label sudah unmask(0)
flood0 = flood_label.eq(0)

komb = (flood1.unmask(0).multiply(2).add(jrc_ada.unmask(0)).unmask(0)).rename('kj')
NO_DATA = -9999
valid_raw = flood_raw.unmask(NO_DATA).neq(NO_DATA)
kr = (valid_raw.unmask(0).multiply(1).add(flood_raw.unmask(0)).unmask(0).where(valid_raw.Not(), 9)).rename('kr')


def hist_counts(band, name, crs):
    kw = dict(reducer=ee.Reducer.frequencyHistogram(), geometry=roi, scale=30, maxPixels=1e13, tileScale=8)
    if crs:
        kw['crs'] = crs
    h = band.reduceRegion(**kw).get(name).getInfo() or {}
    return {int(float(k)): int(float(v)) for k, v in h.items()}


for crs in [None, 'EPSG:32749']:
    tag = crs or 'default(WGS, seperti probe kernel)'
    hk = hist_counts(komb, 'kj', crs)
    hr = hist_counts(kr, 'kr', crs)
    aoi = sum(hk.values())
    f1_nd = hk.get(2, 0)
    f1_val = hk.get(3, 0)
    print(f'===== GRID {tag} =====')
    print(f'AOI piksel (dari histogram komb)  : {aoi}')
    print(f'(a) JRC ada-occ (piksel sahih)    : {hk.get(1,0) + hk.get(3,0)} = {100.0*(hk.get(1,0)+hk.get(3,0))/aoi:.2f}% AOI')
    print(f'    JRC no-data / luar pita       : {hk.get(0,0) + hk.get(2,0)} = {100.0*(hk.get(0,0)+hk.get(2,0))/aoi:.2f}% AOI')
    print(f'(b) flood=1 & JRC ada-occ         : {f1_val}')
    print(f'(c) flood=1 & JRC no-data         : {f1_nd}  {"<- NOL: konfirmasi N-1" if f1_nd==0 else "<- BUKAN NOL"}')
    print(f'(d) flood=0 & JRC ada-occ         : {hk.get(1,0)}')
    print(f'    flood=0 & JRC no-data         : {hk.get(0,0)}')
    print(f'total flood=1                    : {f1_val+f1_nd} (semua di pita JRC: {100.0*f1_val/max(f1_val+f1_nd,1):.2f}%)')
    print(f'(e) flood_raw masked (tidak berlabel): {hr.get(9,0)} = {100.0*hr.get(9,0)/aoi:.2f}% AOI')
    print(f'    flood_raw valid-true          : {hr.get(1,0)}')
    print(f'    flood_raw valid-false         : {hr.get(0,0)}')
    print(f'sanity raw masked+true+false     : {hr.get(9,0)+hr.get(1,0)+hr.get(0,0)} (harus {aoi})')
    print()
