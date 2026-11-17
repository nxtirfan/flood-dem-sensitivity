import sys, os, shutil, json, tempfile
sys.path.insert(0,'.')
import harness as H, numpy as np, pandas as pd
src_root=json.load(open('smoke_root.json'))['root']
def fresh():
    r=tempfile.mkdtemp(prefix='integ_')+'/Analisis Flood DEM Susceptibility'
    os.makedirs(r); shutil.copytree(src_root+'/data', r+'/data'); return r
cells=H.load_cells()
def boot(root, mode='USE_CACHED_DATA'):
    ns=H.base_ns(root,mode); H.run_cells(ns,cells,upto_pred=lambda o:o==6); H.run_cells(ns,[c for c in cells if c[1]==8]); return ns
def expect(ns, msg_part, label):
    try: ns['validate_artifacts']('all'); print('GAGAL UJI',label,': tidak ada error'); sys.exit(1)
    except ns['FrozenDataError'] as e:
        assert msg_part in str(e), (label, str(e)); print('OK',label,'->',str(e).split('\n')[1].strip()[:110])
# a. baseline lulus
r=fresh(); ns=boot(r); ns['validate_artifacts']('all'); print('OK baseline valid')
# b. file Parquet diubah 1 byte
r=fresh(); p=r+'/data/frozen/main/sample_main_raw.parquet'
b=bytearray(open(p,'rb').read()); b[100]^=0xFF; open(p,'wb').write(bytes(b)); expect(boot(r),'SHA-256 Parquet BERBEDA','parquet diubah')
# c. manifest hilang
r=fresh(); os.remove(r+'/data/manifest.json'); ns=boot(r)
try: ns['validate_artifacts']('all'); sys.exit(1)
except ns['FrozenDataError'] as e: assert 'manifest.json tidak ada' in str(e) and 'TIDAK akan mengambil data dari GEE' in str(e); print('OK manifest hilang -> pesan jelas, tanpa fallback GEE')
# d. file seed hilang
r=fresh(); os.remove(r+'/data/frozen/multiseed/sample_seed_2024_raw.parquet'); expect(boot(r),'[seed_2024] file hilang','seed hilang')
# e. seeds di manifest tidak cocok dengan notebook
r=fresh(); m=json.load(open(r+'/data/manifest.json')); m['seeds_multi']=[42,100,2024,7,98]; json.dump(m,open(r+'/data/manifest.json','w')); expect(boot(r),'seeds_multi manifest','seed beda')
# f. seed di entri tidak sesuai nama
r=fresh(); m=json.load(open(r+'/data/manifest.json')); m['datasets']['seed_7']['seed']=99; json.dump(m,open(r+'/data/manifest.json','w')); expect(boot(r),'seed di manifest (99) tidak sesuai','seed entri salah')
# g. kolom wajib hilang dari manifest? (struktur beda): ubah daftar kolom manifest
r=fresh(); m=json.load(open(r+'/data/manifest.json')); m['datasets']['main']['columns'][0]='x'; json.dump(m,open(r+'/data/manifest.json','w')); expect(boot(r),'nama/urutan kolom berbeda','kolom beda')
# h. CSV diubah
r=fresh(); p=r+'/data/frozen/main/sample_main_raw.csv'; open(p,'a').write('\n'); expect(boot(r),'SHA-256 CSV berbeda','csv diubah')
# i. PREPARE_DATA menolak menimpa
import types
for _m in ('ee','geemap','geemap.coreutils'): sys.modules[_m]=types.ModuleType(_m)   # stub: uji hanya guard overwrite
r=fresh(); ns=H.base_ns(r,'PREPARE_DATA')
try: H.run_cells(ns,cells,upto_pred=lambda o:o==6); print('GAGAL: PREPARE_DATA menimpa'); sys.exit(1)
except Exception as e: assert 'FrozenDataError' in type(e).__name__ and 'OVERWRITE_FROZEN' in str(e); print('OK PREPARE_DATA menolak menimpa dataset beku ->', type(e).__name__)
# j. sidik jari: catat (PREPARE_DATA) lalu cek (cached) lalu deteksi drift
r=fresh(); ns=boot(r)
tt=pd.read_csv(H.Z+'training_sample_features.csv'); X=tt.drop(columns=['flood','lon','lat']); yy=tt['flood']
ns['RUN_MODE']='PREPARE_DATA'; ns['record_or_check_fingerprint']('main',X,yy); ns['RUN_MODE']='USE_CACHED_DATA'
ns['record_or_check_fingerprint']('main',X,yy); assert ns['FINGERPRINT_STATUS']['main']=='cocok'
X2=X.copy(); X2.iloc[0,0]+=1e-9; ns['record_or_check_fingerprint']('main',X2,yy); assert ns['FINGERPRINT_STATUS']['main']=='BEDA'
print('OK sidik jari: dicatat -> cocok -> terdeteksi BEDA pada perubahan 1e-9')
print('SEMUA UJI INTEGRITAS LULUS')
