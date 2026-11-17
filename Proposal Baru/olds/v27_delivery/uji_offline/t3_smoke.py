import sys, os, shutil, tempfile, time, json
sys.path.insert(0,'.')
import harness as H
import pandas as pd, numpy as np
root=tempfile.mkdtemp(prefix='smoke_')+'/Analisis Flood DEM Susceptibility'
os.makedirs(root+'/data'); shutil.copytree(H.REF, root+'/data/reference_v26')
t0=time.time(); H.make_frozen(root); print('pembekuan uji selesai %.0fs'%(time.time()-t0))
cells=H.load_cells()
def post(ns,o,src):
    if 'RF_SKLEARN = dict' in src: ns['RF_SKLEARN']['n_estimators']=15
    if 'MORAN_B_POINTS = ' in src: ns['MORAN_B_POINTS']=199; ns['MORAN_B_MAP']=49
H.block_network()
ns=H.base_ns(root,'USE_CACHED_DATA')
t0=time.time(); log=H.run_cells(ns,cells,post=post); print('notebook cached (smoke) selesai tanpa error: %.0fs'%(time.time()-t0))
print('ee diimpor?', ns.get('ee') is not None, '| geemap?', ns.get('geemap') is not None, '| GEE_REQUIRED', ns['GEE_REQUIRED'])
for f in ['model_metrics.csv','spatial_cv_metrics.csv','spatial_cv_delta_auc_bootstrap.csv','multiseed_holdout.csv','multiseed_summary.csv','moran_oof_global.csv','moran_oof_points.csv','validation_v26_vs_v27.csv','run_environment.json','roc_curves.png']:
    print(' ', f, os.path.isfile(root+'/outputs/'+f))
print('fingerprint:',ns['FINGERPRINT_STATUS'])
print('--- cuplikan log ---'); print('\n'.join(l for l in log.split('\n') if any(k in l for k in ['Validasi','OK |','sidik jari','Peta GeoTIFF','BELUM','Moran','Raster probabilitas']))[:2500])
print(open(root+'/outputs/validation_v26_vs_v27.csv').read()[:600])
json.dump({'root':root},open('smoke_root.json','w'))
