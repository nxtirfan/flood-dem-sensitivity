"""Harness uji notebook v27 (di sandbox, tanpa GEE).
Data uji = artefak v26 yang diubah menjadi tabel 'mentah-semu' HANYA untuk menguji jalur kode (smoke test).
Hasil smoke test TIDAK dipakai sebagai hasil penelitian."""
import json, os, sys, io, time, socket, contextlib, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')

NB = '/home/claude/v27_delivery/Flood_DEM_Sensitivity_Notebook_v27.ipynb'
MAP = '/tmp/claude-0/-home-claude/b722b6b3-0211-5390-b052-8e74f84418ea/scratchpad/build/v27.map.json'
Z = '/tmp/claude-0/-home-claude/b722b6b3-0211-5390-b052-8e74f84418ea/scratchpad/zipx/'
REF = '/home/claude/v27_delivery/Analisis Flood DEM Susceptibility/data/reference_v26'


def load_cells():
    nb = json.load(open(NB))
    mp = json.load(open(MAP))
    return [(t, o, ''.join(c['source'])) for (t, o), c in zip(mp, nb['cells'])]


def block_network():
    def _no(*a, **k):
        raise RuntimeError('JARINGAN DIBLOKIR (uji: mode cached tidak boleh menghubungi GEE/internet)')
    socket.socket.connect = _no
    socket.create_connection = _no


def run_cells(ns, cells, upto_pred=None, hooks=None, quiet=True, post=None):
    hooks = hooks or {}
    buf = io.StringIO()
    for typ, o, src in cells:
        if typ != 'code':
            continue
        src = '\n'.join(l for l in src.split('\n') if not l.startswith('!pip'))
        if upto_pred and upto_pred(o):
            break
        with contextlib.redirect_stdout(buf) if quiet else contextlib.nullcontext():
            exec(compile(src, f'<cell {o}>', 'exec'), ns)
        if post:
            post(ns, o, src)
        if o in hooks:
            hooks[o](ns)
    return buf.getvalue()


def base_ns(root, mode):
    os.environ['FLOOD_DEM_ROOT'] = root
    os.environ['FLOOD_DEM_RUN_MODE'] = mode
    import matplotlib.pyplot as plt
    return {'__name__': '__main__', 'display': lambda *a, **k: None}


def pseudo_raw(n_copy=None):
    # tabel 'mentah-semu' dari dataset terproses v26 (landcover dipulihkan dari one-hot). HANYA uji kode.
    t = pd.read_csv(Z + 'training_sample_features.csv', float_precision='round_trip')
    lc = [c for c in t.columns if c.startswith('lc_')]
    raw = t.drop(columns=lc).copy()
    raw['landcover'] = t[lc].idxmax(axis=1).str.replace('lc_', '', regex=False).astype(int)
    raw['rand_balance'] = np.linspace(0, 1, len(raw))
    raw['random'] = np.linspace(0, 1, len(raw))
    return raw


def make_frozen(root, trees=None):
    """Bekukan tabel mentah-semu memakai fungsi helper notebook (PREPARE-style) ke folder uji."""
    ns = base_ns(root, 'USE_CACHED_DATA')
    cells = load_cells()
    run_cells(ns, cells, upto_pred=lambda o: o == 6)        # cfg, colab, cell4, helpers, maps_utils, moran_utils
    run_cells(ns, [c for c in cells if c[1] == 8], quiet=True)   # parameter (8a)
    raw = pseudo_raw()
    fixed = ['hand', 'upa_log', 'river_width', 'dist_river', 'dist_perm_water', 'rain_7d', 'rain_30d',
             'ndvi', 'ndwi', 'mndwi', 'ndbi', 'landcover']
    dem = [c for n in ns['DEM_NAMES'] for c in ns['dem_cols'](n)] if 'dem_cols' in ns else \
          [f'{p}_{n}' for n in ns['DEM_NAMES'] for p in ('elevation', 'slope', 'aspect_sin', 'aspect_cos', 'aspect_valid')]
    ns['init_prepare_manifest']()
    ns['manifest_update'](required_columns=fixed + dem)
    ns['freeze_table'](raw, 'main', ns['PATHS']['frozen_main'], extra={'kind': 'main_evaluation', 'seed': 42})
    for sd in ns['SEEDS_MULTI']:
        ns['freeze_table'](raw, f'seed_{sd}', ns['PATHS']['frozen_multiseed'],
                           extra={'kind': 'multiseed', 'seed': int(sd), 'gee_counts': {'SMOKE': 'uji kode'}})
    return ns
