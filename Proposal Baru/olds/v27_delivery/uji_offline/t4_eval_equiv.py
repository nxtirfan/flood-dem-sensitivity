"""T4: jalankan cell evaluasi utama (v27 cell 28 dan 30, guard RUN_EVALUATION) pada dataset terproses v26.
Bandingkan dengan CSV hasil v26 (Kaggle). Mengukur: (a) kode v27 = v26, (b) efek lingkungan (versi library)."""
import json, os, sys, time, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, roc_curve, confusion_matrix, ConfusionMatrixDisplay)
from sklearn.ensemble import RandomForestClassifier
Z='/tmp/claude-0/-home-claude/b722b6b3-0211-5390-b052-8e74f84418ea/scratchpad/zipx/'
OUT=sys.argv[1]; os.makedirs(OUT,exist_ok=True)
nb=json.load(open('/home/claude/v27_delivery/Flood_DEM_Sensitivity_Notebook_v27.ipynb')); mp=json.load(open('v27.map.json'))
cells={o:''.join(c['source']) for (t,o),c in zip(mp,nb['cells']) if t=='code' and str(o).isdigit()}
t=pd.read_csv(Z+'training_sample_features.csv',float_precision='round_trip')
DEM_NAMES=['srtm','glo30','aw3d30']
DEM_CONFIGS={'srtm':{'label':'SRTM'},'glo30':{'label':'Copernicus GLO-30'},'aw3d30':{'label':'ALOS AW3D30'}}
RANDOM_STATE=42
RF_SKLEARN=dict(n_estimators=400,min_samples_leaf=2,class_weight='balanced',random_state=RANDOM_STATE,n_jobs=-1)
def dem_cols(name): return [f'elevation_{name}',f'slope_{name}',f'aspect_sin_{name}',f'aspect_cos_{name}',f'aspect_valid_{name}']
data=t[['flood','lon','lat']].copy(); X_all=t.drop(columns=['flood','lon','lat']); y=t['flood'].astype(int)
fixed_feature_cols=[c for c in X_all.columns if not (c.startswith('elevation_') or c.startswith('slope_') or c.startswith('aspect_'))]
ns=dict(globals()); ns.update(dict(RUN_EVALUATION=True,OUTPUT_DIR=OUT,display=lambda *a,**k:None))
t0=time.time()
exec(cells[28],ns); print('cell28 selesai %.0f s'%(time.time()-t0))
exec(cells[30],ns); print('cell30 selesai %.0f s'%(time.time()-t0))
