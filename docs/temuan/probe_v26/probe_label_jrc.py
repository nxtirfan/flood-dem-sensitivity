# Probe 1 - replikasi persis sel 8+10+12 notebook v26 (tanpa mengubah notebook).
# Pertanyaan: bisakah flood=1 lahir di area JRC no-data?
# Dijalankan 19-20 Okt 2026, ee 1.7.42, project ee-irfan-banjir-2026 (restricted mode).
# Bukti di T04. Catatan: angka sum pada band boolean = Sigma nilai*piksel (reduceRegion
# memberatkan dengan mask band bawaan; mask JRC fraksional 0..1, lihat probe 3/4).
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


# ---- sel 8 (parameter) ----
wilayah_indonesia = ee.FeatureCollection('FAO/GAUL/2015/level2').filter(ee.Filter.eq('ADM0_NAME', 'Indonesia'))
semarang_demak = wilayah_indonesia.filter(ee.Filter.inList('ADM2_NAME', ['Kota Semarang', 'Demak']))
roi = semarang_demak.geometry()
BEFORE_START, BEFORE_END = '2024-02-25', '2024-03-12'
AFTER_START, AFTER_END = '2024-03-15', '2024-03-31'
S1_POLARIZATION = 'VH'
S1_RATIO_THRESHOLD = 1.25
AFTER_DB_THRESHOLD = -18
SLOPE_MAX_FOR_FLOOD = 5
MIN_CONNECTED_PIXELS = 8

# ---- sel 12 (label) ----
s1_before = get_s1_median(BEFORE_START, BEFORE_END, roi)
s1_after = get_s1_median(AFTER_START, AFTER_END, roi)
before_pol_db = s1_before.select(S1_POLARIZATION)
after_pol_db = s1_after.select(S1_POLARIZATION)
before_pol_power = db_to_power(before_pol_db)
after_pol_power = db_to_power(after_pol_db)
s1_ratio = before_pol_power.divide(after_pol_power).rename('s1_ratio')

dem_for_label = ee.Image('USGS/SRTMGL1_003').select('elevation').clip(roi)
slope_for_label = ee.Terrain.slope(dem_for_label).rename('slope')

jrc_water = ee.Image('JRC/GSW1_4/GlobalSurfaceWater').select('occurrence').clip(roi)
permanent_water = jrc_water.gte(80).rename('permanent_water')

flood_raw = (s1_ratio.gt(S1_RATIO_THRESHOLD)
             .And(after_pol_db.lt(AFTER_DB_THRESHOLD))
             .And(permanent_water.Not())
             .And(slope_for_label.lt(SLOPE_MAX_FOR_FLOOD)))

flood_connected = (flood_raw.selfMask()
                   .connectedPixelCount(100, True)
                   .gte(MIN_CONNECTED_PIXELS)
                   .unmask(0)
                   .rename('flood'))
flood_label = flood_connected.rename('flood').clip(roi)


def px_sum(cond_img, name, crs=None):
    img = cond_img.unmask(0).rename(name)
    kw = dict(reducer=ee.Reducer.sum(), geometry=roi, scale=30, maxPixels=1e13, tileScale=8)
    if crs:
        kw['crs'] = crs
    return int(round(float(img.reduceRegion(**kw).get(name).getInfo())))


NO_DATA = -9999
jrc_nd = jrc_water.unmask(NO_DATA).eq(NO_DATA)
jrc_valid = jrc_nd.Not()
s1_nd = (before_pol_db.unmask(NO_DATA).eq(NO_DATA)
         .Or(after_pol_db.unmask(NO_DATA).eq(NO_DATA)))
slope_nd = slope_for_label.unmask(NO_DATA).eq(NO_DATA)
flood1 = flood_label.eq(1)
flood0 = flood_label.eq(0)
raw_masked = flood_raw.unmask(NO_DATA).eq(NO_DATA)
raw_true = flood_raw.unmask(0).eq(1).And(flood_raw.unmask(NO_DATA).neq(NO_DATA))
raw_false = flood_raw.unmask(0).eq(0).And(flood_raw.unmask(NO_DATA).neq(NO_DATA))

for crs in [None, 'EPSG:32749']:
    tag = crs or 'default(WGS)'
    print(f'===== GRID reduceRegion scale=30 tileScale=8, crs={tag} =====')
    a0 = px_sum(ee.Image.constant(1), 'px', crs)
    a1 = px_sum(jrc_valid, 'jrcv', crs)
    a2 = px_sum(jrc_nd, 'jrcnd', crs)
    b = px_sum(flood1.And(jrc_valid), 'f1jrcv', crs)
    c = px_sum(flood1.And(jrc_nd), 'f1jrcnd', crs)
    d1 = px_sum(flood0.And(jrc_valid), 'f0jrcv', crs)
    d2 = px_sum(flood0.And(jrc_nd), 'f0jrcnd', crs)
    e0 = px_sum(raw_masked, 'rawmasked', crs)
    e1 = px_sum(raw_masked.And(jrc_nd), 'masked_jrcnd', crs)
    e2 = px_sum(raw_masked.And(s1_nd), 'masked_s1nd', crs)
    e3 = px_sum(raw_masked.And(slope_nd), 'masked_slpend', crs)
    t1 = px_sum(raw_true, 'rawtrue', crs)
    t0 = px_sum(raw_false, 'rawfalse', crs)
    print(f'AOI px                 : {a0}')
    print(f'(a) JRC valid px       : {a1}  ({100.0 * a1 / a0:.2f}% AOI)')
    print(f'    JRC no-data px     : {a2}  ({100.0 * a2 / a0:.2f}% AOI)')
    print(f'(b) flood=1 & JRC valid: {b}  ({100.0 * b / max(a1,1):.4f}% dari JRC valid)')
    print(f'(c) flood=1 & JRC n.d. : {c}  {"<- NOL (konfirmasi N-1)" if c == 0 else "<- BUKAN NOL (N-1 GUGUR)"}')
    print(f'(d) flood=0 & JRC valid: {d1}')
    print(f'    flood=0 & JRC n.d. : {d2}')
    print(f'(e) flood_raw masked   : {e0} ({100.0 * e0 / a0:.2f}% AOI = kandidat hilang)')
    print(f'    karena JRC no-data : {e1}')
    print(f'    karena S1 no-data  : {e2}')
    print(f'    karena slope n.d.  : {e3}')
    print(f'    flood_raw true     : {t1}')
    print(f'    flood_raw false    : {t0}')
    print(f'sanity masked+true+false = {e0 + t1 + t0} (harus = {a0})')
    print()
