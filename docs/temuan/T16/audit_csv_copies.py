"""Compare archived result copies without replacing either source."""
from pathlib import Path
import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
BASE = ROOT / 'Proposal Baru/v27_delivery/Analisis Flood DEM Susceptibility/outputs'
rows = []
for p in sorted((ROOT / 'Proposal Baru/hasil_kaggle').glob('*.csv')):
    q = BASE / p.name
    if not q.exists():
        continue
    a, b = pd.read_csv(p), pd.read_csv(q)
    same_schema = a.shape == b.shape and list(a) == list(b)
    if not same_schema:
        rows.append(dict(file=p.name, column='ALL', same_shape_columns=False,
                         byte_identical=p.read_bytes() == q.read_bytes(), max_abs_difference=None,
                         different_cells=None, equal_at_1e_10=False))
        continue
    for col in a:
        numeric = pd.api.types.is_numeric_dtype(a[col]) and pd.api.types.is_numeric_dtype(b[col])
        if numeric:
            close = np.isclose(a[col], b[col], rtol=0, atol=1e-10, equal_nan=True)
            difference = (a[col].astype(float) - b[col].astype(float)).abs().max()
        else:
            close = a[col].fillna('').eq(b[col].fillna('')).to_numpy()
            difference = None
        rows.append(dict(file=p.name, column=col, same_shape_columns=True,
                         byte_identical=p.read_bytes() == q.read_bytes(), max_abs_difference=difference,
                         different_cells=int((~close).sum()), equal_at_1e_10=bool(close.all())))
pd.DataFrame(rows).to_csv(OUT / 'result_copy_numeric_audit.csv', index=False)
print('Compared', len(set(r['file'] for r in rows)), 'CSV pairs;', sum(r['different_cells'] or 0 for r in rows), 'cells differ above tolerance')
