import json, ast
v26=json.load(open('/mnt/user-data/attachments/b722b6b3-0211-5390-b052-8e74f84418ea/7d2ec9f9-Flood_DEM_Sensitivity_Notebook_v26.ipynb'))
v27=json.load(open('/home/claude/v27_delivery/Flood_DEM_Sensitivity_Notebook_v27.ipynb'))
mp=json.load(open('v27.map.json'))
old=[''.join(c['source']) for c in v26['cells']]
new=[''.join(c['source']) for c in v27['cells']]
d=lambda nodes:[ast.dump(n) for n in nodes]
res={}
for (typ,o),src in zip(mp,new):
    if typ!='code' or o=='new' or not str(o).isdigit(): continue
    o=int(o)
    if o in (3,): continue
    tree=ast.parse(src)
    ifs=[n for n in tree.body if isinstance(n,ast.If)]
    orig=ast.parse(old[o]).body
    if o in (12,14,16,18,22,26,28,30,33,39,42,44):
        ok = len(tree.body)==1 and d(tree.body[0].body)==d(orig)
        res[o]='IDENTIK(bungkus guard saja)' if ok else 'BEDA'
    elif o==20:
        ok = d(tree.body[0].body[:-1])==d(orig); res[o]='IDENTIK + 1 baris freeze' if ok else 'BEDA'
    elif o==10:
        res[o]='IDENTIK' if src.strip()==old[o].strip() else 'BEDA'
for k in sorted(res): print('cell v26 #%d:'%k,res[k])
# cell tanpa perubahan sama sekali
same=[o for (t,o),s in zip(mp,new) if t=='code' and str(o).isdigit() and s.strip()==old[int(o)].strip()]
print('cell kode v26 yang tidak diubah sama sekali:',same)
