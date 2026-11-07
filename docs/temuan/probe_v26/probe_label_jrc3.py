# Probe 3 - diagnosis akhir: mask band JRC bernilai apa, proyeksi native,
# dan perbandingan reduksi. Menjelaskan tiga angka: 187.777 / 211.137 / 63.499.
import ee

CRED = r"D:\Kuliah\1_Metopen\Proposal Baru\.credentials\ee-irfan-banjir-2026-44c092a9f72b.json"
PROJECT = "ee-irfan-banjir-2026"
ee.Initialize(credentials=ee.ServiceAccountCredentials(email=None, key_file=CRED), project=PROJECT)

wilayah_indonesia = ee.FeatureCollection('FAO/GAUL/2015/level2').filter(ee.Filter.eq('ADM0_NAME', 'Indonesia'))
semarang_demak = wilayah_indonesia.filter(ee.Filter.inList('ADM2_NAME', ['Kota Semarang', 'Demak']))
roi = semarang_demak.geometry()

jrc = ee.Image('JRC/GSW1_4/GlobalSurfaceWater').select('occurrence').clip(roi)

print('--- proyeksi native band occurrence ---')
proj = jrc.projection().getInfo()
print('crs      :', proj.get('crs'))
print('transform:', proj.get('transform'))


def px_sum(cond_img, name, crs=None, ts=8):
    img = cond_img.unmask(0).rename(name)
    kw = dict(reducer=ee.Reducer.sum(), geometry=roi, scale=30, maxPixels=1e13, tileScale=ts)
    if crs:
        kw['crs'] = crs
    return int(round(float(img.reduceRegion(**kw).get(name).getInfo())))


print('--- histogram & threshold mask band (grid WGS default) ---')
maskband = jrc.mask()
mx = maskband.reduceRegion(reducer=ee.Reducer.minMax(), geometry=roi, scale=30, maxPixels=1e13, tileScale=8).getInfo()
print('min/max mask:', mx)
for thr, nm in [(0.000001, 'mask_gt0'), (0.25, 'mask_gt025'), (0.5, 'mask_gt05'), (0.75, 'mask_gt075'), (0.999999, 'mask_ge1')]:
    print(f'  {nm:>10}: {px_sum(maskband.gt(thr), nm)}')

print('--- banding: mask() vs nilai occ vs unmask, grid WGS & 32749 ---')
occ_ada = jrc.unmask(-9999).neq(-9999)
for crs in [None, 'EPSG:32749']:
    tag = crs or 'WGS'
    a0 = px_sum(ee.Image.constant(1), 'px', crs)
    a = px_sum(jrc.mask().gt(0), 'fpm', crs)
    b = px_sum(occ_ada, 'occval', crs)
    c = px_sum(ee.Image.constant(1).updateMask(jrc), 'replika', crs)
    d = px_sum(ee.Image.constant(1).updateMask(jrc.mask()), 'replika_mask', crs)
    print(f'[{tag}] AOI={a0} | mask>0={a} ({100.0*a/a0:.2f}%) | occ bernilai={b} ({100.0*b/a0:.2f}%) | updateMask(occ)={c} ({100.0*c/a0:.2f}%) | updateMask(mask)={d} ({100.0*d/a0:.2f}%)')
