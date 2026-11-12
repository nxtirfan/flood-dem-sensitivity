"""Independent float64 convolution check of the observed raster Moran statistic."""
from pathlib import Path
import numpy as np
import pandas as pd
import rasterio
from scipy.ndimage import convolve

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
BASE = ROOT / 'Proposal Baru/v27_delivery/Analisis Flood DEM Susceptibility'
rows, islands = [], []
for dem in ['srtm', 'glo30', 'aw3d30']:
    with rasterio.open(BASE / f'data/rasters/prob_{dem}.tif') as src:
        a = src.read(1).astype(float)
        valid = (src.read_masks(1) > 0) & np.isfinite(a)
        kernel = np.ones((3, 3), dtype=float)
        kernel[1, 1] = 0
        neighbors = convolve(valid.astype(float), kernel, mode='constant', cval=0)
        use = valid & (neighbors > 0)
        z = np.zeros_like(a)
        z[use] = a[use] - a[use].mean()
        lag = convolve(z, kernel, mode='constant', cval=0) / np.maximum(neighbors, 1)
        result = float((z[use] * lag[use]).sum() / (z[use] ** 2).sum())
        rows.append(dict(dem=dem, method='float64 queen row-standardized; islands excluded',
                         n=int(use.sum()), isolated=int((valid & ~use).sum()), I=result))
        for r, c in np.argwhere(valid & ~use):
            x, y = src.xy(int(r), int(c))
            islands.append(dict(dem=dem, row_zero_based=int(r), col_zero_based=int(c),
                                x=x, y=y, crs=src.crs.to_string(), probability=a[r, c]))
pd.DataFrame(rows).to_csv(OUT / 'independent_raster_moran_check.csv', index=False)
pd.DataFrame(islands).to_csv(OUT / 'isolated_raster_pixels.csv', index=False)
assert [r['isolated'] for r in rows] == [0, 0, 2]
assert [r['n'] for r in rows] == [1444085, 1444085, 1429580]
print(pd.DataFrame(rows).to_string(index=False))
