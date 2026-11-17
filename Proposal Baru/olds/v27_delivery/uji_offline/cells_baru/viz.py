# =========================================================
# v27 - VISUALISASI LOKAL PETA (semua mode, tanpa GEE)
# Membaca GeoTIFF dari data/rasters. Jika belum ada, tampilkan pesan, evaluasi tidak terpengaruh.
# =========================================================
from matplotlib.colors import ListedColormap, LinearSegmentedColormap


def _load_local(name):
    arr, valid = _raster_array(name)
    rasterio = _rio()
    with rasterio.open(os.path.join(PATHS['rasters'], name + '.tif')) as ds:
        b = ds.bounds
    return np.ma.masked_where(~valid, arr), (b.left, b.right, b.bottom, b.top)


def _panel(ax, name, title, cmap, vmin, vmax):
    img, ext = _load_local(name)
    im = ax.imshow(img, extent=ext, cmap=cmap, vmin=vmin, vmax=vmax, interpolation='nearest')
    ax.set_title(title, fontsize=10)
    ax.set_xlabel('Easting (m, UTM 49S)', fontsize=8)
    ax.set_ylabel('Northing (m)', fontsize=8)
    ax.tick_params(labelsize=7)
    ax.ticklabel_format(style='plain')
    return im


def show_local_maps():
    st = status_load() if os.path.isfile(PATHS['export_status']) else None
    need = ([f'prob_{d}' for d in DEM_NAMES] + [f'risk_class_{d}' for d in DEM_NAMES] +
            [f'delta_abs_{a}_vs_{b}' for a, b in MAP_PAIRS] + [f'agreement_{a}_vs_{b}' for a, b in MAP_PAIRS])
    missing = [n for n in need if not st or st['rasters'].get(n, {}).get('status') != 'COMPLETED'
               or not os.path.isfile(os.path.join(PATHS['rasters'], n + '.tif'))]
    if missing:
        print('Peta GeoTIFF belum tersedia lengkap (' + str(len(missing)) + ' raster belum COMPLETED).')
        print('Jalankan notebook dengan RUN_MODE = \'PREPARE_MAPS\' untuk membentuknya. '
              'Bagian evaluasi tidak terpengaruh.')
        return False
    for n in need:     # integritas file sebelum dipakai
        if sha256_file(os.path.join(PATHS['rasters'], n + '.tif')) != st['rasters'][n]['sha256']:
            raise FrozenDataError(f'Raster {n}.tif berubah sejak diekspor (SHA-256 berbeda).')
    cm_prob = LinearSegmentedColormap.from_list('prob', PROB_VIS['palette'])
    cm_risk = ListedColormap(RISK_VIS['palette'])
    cm_delta = LinearSegmentedColormap.from_list('delta', DELTA_VIS['palette'])
    cm_agree = ListedColormap(['#7f0000', '#1a9850'])

    def row(title, items, cmap, vmin, vmax, fname, cbar_label):
        fig, axes = plt.subplots(1, 3, figsize=(17, 5.2))
        for ax, (nm, tt) in zip(axes, items):
            im = _panel(ax, nm, tt, cmap, vmin, vmax)
        fig.colorbar(im, ax=list(axes), shrink=0.8, label=cbar_label)
        fig.suptitle(title)
        fig.savefig(os.path.join(PATHS['maps_local'], fname), dpi=200, bbox_inches='tight')
        plt.show()

    lab = {d: DEM_CONFIGS[d]['label'] for d in DEM_NAMES}
    row('Probabilitas banjir (RF GEE, 300 pohon)', [(f'prob_{d}', lab[d]) for d in DEM_NAMES],
        cm_prob, 0, 1, 'local_prob_maps.png', 'Probabilitas')
    row('Kelas kerawanan (batas kelas sama untuk ketiga peta)', [(f'risk_class_{d}', lab[d]) for d in DEM_NAMES],
        cm_risk, 1, 5, 'local_risk_class_maps.png', 'Kelas (1 sangat rendah - 5 sangat tinggi)')
    row('Selisih absolut probabilitas', [(f'delta_abs_{a}_vs_{b}', f'{a} vs {b}') for a, b in MAP_PAIRS],
        cm_delta, 0, 0.5, 'local_delta_maps.png', '|delta probabilitas|')
    row('Kesesuaian kelas (1 = sama)', [(f'agreement_{a}_vs_{b}', f'{a} vs {b}') for a, b in MAP_PAIRS],
        cm_agree, 0, 1, 'local_agreement_maps.png', 'Agreement')
    print('Figure peta lokal tersimpan di:', PATHS['maps_local'])
    return True


LOCAL_MAPS_SHOWN = show_local_maps()
