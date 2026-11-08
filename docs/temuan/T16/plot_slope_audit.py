"""Plot the frozen predictor values, not unobserved filter-time slope."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

out = Path(__file__).resolve().parent
root = out.parents[2]
table = pd.read_csv(root / 'Proposal Baru/hasil_kaggle/training_sample_features.csv')
slope = table.loc[table.flood.eq(1), 'slope_srtm']
high = slope[slope.ge(5)]
fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), layout='constrained')
axes[0].hist(slope, bins=np.arange(0, 12.5, 0.5), color='#267c97', edgecolor='white')
axes[0].axvline(5, color='#b83235', ls='--', label='Ambang kode filter: 5°')
axes[0].set(xlabel='Slope SRTM pada tabel prediktor (°)', ylabel='Jumlah titik positif', title=f'Seluruh {len(slope):,} titik positif'.replace(',', '.'))
axes[0].legend(fontsize=8)
axes[1].plot(range(1, len(high) + 1), np.sort(high), 'o-', color='#b83235', markersize=3)
axes[1].axhline(5, color='grey', ls='--')
axes[1].set(xlabel='Urutan nilai (bukan ID titik)', ylabel='Slope SRTM prediktor (°)', title=f'{len(high)} titik ≥5°; maksimum {high.max():.6f}°')
fig.suptitle('T16 — Konflik nilai slope terverifikasi; sebab belum terverifikasi', fontsize=12)
fig.text(0.5, -0.055, 'Nilai slope saat filtering dan raster slope sumber tidak tersedia. Grafik ini bukan bukti filter gagal.', ha='center', fontsize=9)
fig.savefig(out / 'slope_audit_overview.png', dpi=150, bbox_inches='tight')
print('Wrote slope_audit_overview.png; high/positive=', len(high), '/', len(slope))
