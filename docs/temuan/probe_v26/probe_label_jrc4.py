# Probe 4 - uji reduksi definitif: reduceRegion.sum() memberatkan nilai dengan
# mask band (sum = Sigma value*mask), count() menghitung piksel terbuka.
# Catatan: script asli di sesi live hanya sempat mencetak 2 ukuran pertama
# sebelum sesi terputus; sisanya direkonstruksi dari bukti transkrip.
import ee

CRED = r"D:\Kuliah\1_Metopen\Proposal Baru\.credentials\ee-irfan-banjir-2026-44c092a9f72b.json"
PROJECT = "ee-irfan-banjir-2026"
ee.Initialize(credentials=ee.ServiceAccountCredentials(email=None, key_file=CRED), project=PROJECT)

wilayah_indonesia = ee.FeatureCollection('FAO/GAUL/2015/level2').filter(ee.Filter.eq('ADM0_NAME', 'Indonesia'))
semarang_demak = wilayah_indonesia.filter(ee.Filter.inList('ADM2_NAME', ['Kota Semarang', 'Demak']))
roi = semarang_demak.geometry()

jrc = ee.Image('JRC/GSW1_4/GlobalSurfaceWater').select('occurrence').clip(roi)

replika = ee.Image.constant(1).updateMask(jrc).rename('replika')

kw = dict(geometry=roi, scale=30, maxPixels=1e13, tileScale=8)
r = replika.reduceRegion(reducer=ee.Reducer.count().combine(ee.Reducer.sum(), sharedInputs=True)
                         .combine(ee.Reducer.mean(), sharedInputs=True), **kw).getInfo()
print('replika updateMask(jrc): count=%.0f sum=%.1f mean=%.6f' % (r['replika_count'], r['replika_sum'], r['replika_mean']))

occ_ada = jrc.unmask(-9999).neq(-9999).rename('occval')
r2 = occ_ada.reduceRegion(reducer=ee.Reducer.count().combine(ee.Reducer.sum(), sharedInputs=True), **kw).getInfo()
print('occ bernilai (unmask sentinel): count=%.0f sum=%.0f' % (r2['occval_count'], r2['occval_sum']))

maskband = jrc.mask().rename('m')
r3 = maskband.reduceRegion(reducer=ee.Reducer.count().combine(ee.Reducer.sum(), sharedInputs=True)
                           .combine(ee.Reducer.mean(), sharedInputs=True), **kw).getInfo()
print('mask band: count=%.0f sum=%.1f mean=%.6f' % (r3['m_count'], r3['m_sum'], r3['m_mean']))

r4 = replika.reduceRegion(reducer=ee.Reducer.count(), **kw).getInfo()
print('replika count saja: %.0f' % r4['replika'])
