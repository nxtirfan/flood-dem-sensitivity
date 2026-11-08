"""Read-only provenance checks; writes only beside this script."""
import csv
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
DATA = ROOT / 'Proposal Baru/v27_delivery/Analisis Flood DEM Susceptibility/data'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else ''

def write(name, rows):
    with (OUT / name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

manifest = json.loads((DATA / 'manifest.json').read_text())
status = json.loads((DATA / 'export_status.json').read_text())
rows = []

def check(source, key, path, expected, backup=None):
    actual = digest(path)
    rows.append(dict(source=source, key=key, path=str(path.relative_to(ROOT)),
                     expected_sha256=expected, actual_sha256=actual,
                     matches=bool(actual and actual == expected),
                     matches_backup=bool(backup and digest(backup) == expected)))

for key, entry in manifest['datasets'].items():
    for ext in ['csv', 'parquet']:
        check('manifest.datasets', key, DATA / entry['file_' + ext], entry['sha256_' + ext])
for key, entry in manifest['gee_tables'].items():
    check('manifest.gee_tables', key, DATA / entry['file'], entry['sha256'])
for key, entry in manifest['maps']['rasters'].items():
    check('manifest.maps', key, DATA / 'rasters' / (key + '.tif'), entry['sha256'],
          DATA / 'rasters_backup_unmasked' / (key + '.tif'))
for key, entry in status['rasters'].items():
    check('export_status.rasters', key, DATA / entry['file'], entry['sha256'],
          DATA / 'rasters_backup_unmasked' / (key + '.tif'))
write('manifest_hash_audit.csv', rows)

baseline = list(csv.DictReader((OUT / 'source_inventory.csv').open()))
by_name = {}
for row in baseline:
    if row['extension'] in ['.csv', '.ipynb']:
        by_name.setdefault(Path(row['path']).name, []).append(row)
duplicates = []
for name, entries in sorted(by_name.items()):
    if len(entries) < 2:
        continue
    hashes = sorted({e['sha256'] for e in entries})
    for entry in entries:
        duplicates.append(dict(basename=name, path=entry['path'], sha256=entry['sha256'],
                               variant_count=len(hashes), hash_group=hashes.index(entry['sha256']) + 1))
write('artifact_copy_groups.csv', duplicates)
checks = []
for row in baseline:
    path = ROOT / row['path']
    actual = digest(path)
    checks.append(dict(path=row['path'], sha256_before=row['sha256'], sha256_after=actual,
                       unchanged=actual == row['sha256']))
write('source_integrity_check.csv', checks)
print(json.dumps(dict(manifest_checks=len(rows), manifest_mismatches=sum(not r['matches'] for r in rows),
                      source_checks=len(checks), source_changed=sum(not c['unchanged'] for c in checks)), indent=2))
for row in rows:
    if not row['matches']:
        print(row['source'], row['key'], 'matches_backup=', row['matches_backup'])
