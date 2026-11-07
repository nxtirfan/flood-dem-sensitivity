# =========================================================
# v27 - PREAMBLE GOOGLE COLAB / DRIVE (terpisah dari preamble Kaggle di cell 1.)
# Hanya aktif jika ENV == 'colab'. Di Kaggle/lokal cell ini tidak melakukan apa pun.
# =========================================================
if ENV == 'colab':
    from google.colab import drive          # aman: hanya diimpor di Colab
    drive.mount('/content/drive')
    if not os.path.isdir(PATHS['root']):
        print('Folder utama belum ada, dibuat:', PATHS['root'])
    ensure_dirs()                           # data/{frozen,gee_tables,rasters,...} dan outputs/{maps_local}

    # Service account hanya wajib bila mode memakai GEE.
    if GEE_REQUIRED:
        _sa = PATHS['sa_json']
        if os.path.isfile(_sa):
            try:
                with open(_sa, 'r', encoding='utf-8') as _fh:
                    _info = json.load(_fh)
                if _info.get('type') == 'service_account':
                    print('Service account ditemukan:', _info.get('client_email'),
                          '| project:', _info.get('project_id'))
                else:
                    print('PERINGATAN: file ada tetapi bukan key service account:', _sa)
            except Exception as _e:
                print('PERINGATAN: service account JSON tidak bisa dibaca:', _e)
        else:
            print('PERINGATAN: service account JSON tidak ditemukan di:', _sa)
            print('            Cell autentikasi akan jatuh ke login interaktif (ee.Authenticate).')
    else:
        print('Mode cached: service account tidak diperlukan.')
else:
    print(f'Preamble Colab dilewati (ENV={ENV}).')
