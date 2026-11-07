# =========================================================
# v27 - GLOBAL MORAN'S I pada PETA probabilitas kerawanan (raster GEE 300 pohon) per DEM.
# Membaca GeoTIFF dari data/rasters. Jika raster belum ada (PREPARE_MAPS belum dijalankan),
# hasil dinyatakan BELUM TERSEDIA dan TIDAK dihitung. Peta berasal dari model yang dilatih pada
# seluruh sampel, jadi ini ukuran struktur spasial permukaan prediksi, bukan ukuran kinerja OOF.
# W = queen 8 tetangga, row-standardized, grid yang sama untuk ketiga DEM.
# =========================================================
RUN_MORAN_MAP = True


def run_moran_map():
    st = status_load() if os.path.isfile(PATHS['export_status']) else None
    names = [f'prob_{d}' for d in DEM_NAMES]
    if not st or any(st['rasters'].get(n, {}).get('status') != 'COMPLETED' for n in names):
        print('Raster probabilitas belum COMPLETED. Moran\'s I peta BELUM DIHITUNG (hasil belum tersedia). '
              'Jalankan PREPARE_MAPS lebih dulu.')
        return None
    rows = []
    for d in DEM_NAMES:
        p = os.path.join(PATHS['rasters'], f'prob_{d}.tif')
        if sha256_file(p) != st['rasters'][f'prob_{d}']['sha256']:
            raise FrozenDataError(f'prob_{d}.tif berubah sejak diekspor (SHA-256 berbeda).')
        arr, valid = _raster_array(f'prob_{d}')
        t0 = time.time()
        r = moran_raster(arr, valid)
        r.update({'scope': 'peta_probabilitas', 'dem': d, 'weights': 'queen 8 tetangga, row-standardized',
                  'perm_method': 'permutasi kondisional (acak nilai lintas piksel valid)', 'seed': MORAN_SEED})
        rows.append(r)
        print(f'{d}: I={r["I"]:.4f} (E[I]={r["E_I"]:.2e}), n={r["n"]}, B={r["n_perm"]}, '
              f'p_dua_sisi={r["p_two_sided"]:.4f} ({time.time() - t0:.0f} s)')
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUTPUT_DIR, 'moran_prob_map_global.csv'), index=False)
    print('Catatan: pada n sangat besar, p permutasi hampir selalu mencapai batas resolusi 1/(B+1). '
          'Yang informatif adalah besar I, bukan p.')
    return df


moran_map_df = run_moran_map() if RUN_MORAN_MAP else None
