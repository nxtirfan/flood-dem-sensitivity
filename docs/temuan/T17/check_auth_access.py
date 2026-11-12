"""Check declared auth routes by presence only; never persist credentials."""
import importlib.metadata
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import ee

out = Path(__file__).resolve().parent
root = out.parents[2]
candidates = [
    '/kaggle/input/datasets/nxtirfan/gee-service-account-credential/gee-service-account.json',
    '/kaggle/input/gee-service-account-credential/gee-service-account.json',
    '/content/drive/MyDrive/GEE_DEM_Sensitivity_Semarang_Demak/gee-service-account.json',
    '/content/gee-service-account.json', '/kaggle/working/gee-service-account.json',
    str(root / 'gee-service-account.json'),
    '/content/drive/MyDrive/Analisis Flood DEM Susceptibility/gee-service-account.json',
    '/kaggle/working/Analisis Flood DEM Susceptibility/gee-service-account.json',
    str(root / 'Analisis Flood DEM Susceptibility/gee-service-account.json'),
    str(Path.home() / '.config/earthengine/credentials'),
    str(Path.home() / '.config/gcloud/application_default_credentials.json'),
]
result = {'checked_at_utc': datetime.now(timezone.utc).isoformat(),
          'environment_presence': {k: bool(os.environ.get(k)) for k in
                                   ['GOOGLE_APPLICATION_CREDENTIALS', 'GEE_SERVICE_ACCOUNT_JSON', 'FLOOD_DEM_ROOT']},
          'declared_file_presence': [{'path': p, 'exists': Path(p).is_file()} for p in candidates],
          'versions': {k: importlib.metadata.version(k) for k in ['earthengine-api', 'playwright']},
          'gee_computation_executed': False}
try:
    ee.Initialize(project='ee-irfan-banjir-2026')
    result['initialization'] = 'SUCCEEDED; no diagnostic computation requested by this probe'
except Exception as exc:
    # Record the category, not the full exception or auth redirect URLs.
    result['initialization'] = 'BLOCKED'
    result['exception_type'] = type(exc).__name__
    result['requests_authentication'] = 'authenticate' in str(exc).lower()
(out / 'auth_access.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k: result[k] for k in ['initialization', 'environment_presence', 'gee_computation_executed']}, indent=2))
