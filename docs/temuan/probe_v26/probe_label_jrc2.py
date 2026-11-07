# Probe 2 - taksonomi mask JRC: footprint vs nilai vs occ=0, grid WGS & 32749.
# Tujuan: menjelaskan kenapa probe kernel = 187.777 (12,78%) sementara
# unmask(-9999) = 63.499 (4,32%), dan menetapkan definisi "JRC no-data"
# yang benar untuk label (permanent_water = gte(80) masked di luar footprint).
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


def px_sum(cond_img, name, crs=None, ts=8):
    img = cond_img.unmask(0).rename(name)
    kw = dict(reducer=ee.Reducer.sum(), geometry=roi, scale=30, maxPixels=1e13, tileScale=ts)
    if crs:
        kw['crs'] = crs
    return int(round(float(img.reduceRegion(**kw).get(name).getInfo())))


jrc_fp = jrc_water.mask().gt(0)
jrc_nd = jrc_fp.Not()
occ_zero = jrc_water.eq(0)
occ_pos = jrc_water.gt(0)
occ_pw = jrc_water.gte(80)
flood1 = flood_label.eq(1)

for crs in [None, 'EPSG:32749']:
    tag = crs or 'default(WGS)'
    print(f'===== GRID reduceRegion scale=30 tileScale=8, crs={tag} =====')
    a0 = px_sum(ee.Image.constant(1), 'px', crs)
    fp = px_sum(jrc_fp, 'fp', crs)
    nd = px_sum(jrc_nd, 'nd', crs)
    z0 = px_sum(occ_zero, 'occ0', crs)
    zpos = px_sum(occ_pos, 'occpos', crs)
    zpw = px_sum(occ_pw, 'occpw', crs)
    repl = px_sum(ee.Image.constant(1).updateMask(jrc_water), 'replika_kernel', crs)
    b = px_sum(flood1.And(jrc_fp), 'f1_fp', crs)
    c = px_sum(flood1.And(jrc_nd), 'f1_nd', crs)
    d1 = px_sum(flood1.eq(0).And(jrc_fp), 'f0_fp', crs)
    d2 = px_sum(flood1.eq(0).And(jrc_nd), 'f0_nd', crs)
    f1s = px_sum(flood1, 'flood1', crs)
    print(f'AOI px                        : {a0}')
    print(f'footprint JRC (occ ada)       : {fp} ({100.0 * fp / a0:.2f}%)')
    print(f'luar footprint (label n.d.)   : {nd} ({100.0 * nd / a0:.2f}%)')
    print(f'occ = 0   (valid, tdk air)    : {z0} ({100.0 * z0 / a0:.2f}%)')
    print(f'occ 1..79 (valid, episodic)   : {zpos - zpw} ({100.0 * (zpos - zpw) / a0:.2f}%)')
    print(f'occ >= 80 (air permanen)      : {zpw} ({100.0 * zpw / a0:.2f}%)')
    print(f'replika probe kernel occ>0    : {repl} ({100.0 * repl / a0:.2f}%)  <- harus 187.777 (12,78%)')
    print(f'footprint+nd = {fp + nd} (harus {a0})')
    print(f'occ0+occpos+luar = {z0 + zpos + nd} (harus {a0})')
    print(f'flood=1 total        : {f1s}')
    print(f'flood=1 & footprint  : {b}')
    print(f'flood=1 & luar fp    : {c}  {"<- NOL: label=1 mustahil di luar pita JRC" if c == 0 else "<- BUKAN NOL"}')
    print(f'flood=0 & footprint  : {d1}')
    print(f'flood=0 & luar fp    : {d2}')
    print(f'flood1 fp+nd = {b + c} (harus {f1s})')
    print()
