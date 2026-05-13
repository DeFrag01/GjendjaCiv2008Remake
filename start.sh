#!/bin/bash
set -e

DB_FILE="civil_registry_clean.db"
DB_URL="${DB_URL:-https://github.com/DeFrag01/GjendjaCiv2008Remake/releases/download/v1/civil_registry_clean.db.gz}"

if [ -f "$DB_FILE" ]; then
    echo "Database found."
else

echo "Downloading database..."
python3 << 'PYEOF'
import urllib.request, gzip, shutil, sys, os

url = os.environ.get('DB_URL', 'https://github.com/DeFrag01/GjendjaCiv2008Remake/releases/download/v1/civil_registry_clean.db.gz')
db_file = 'civil_registry_clean.db'

print(f'Downloading...', flush=True)
req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0 (compatible; Render/1.0)',
    'Accept': '*/*',
})
resp = urllib.request.urlopen(req, timeout=300)
print(f'Decompressing...', flush=True)
with gzip.GzipFile(fileobj=resp) as gz, open(db_file, 'wb') as f:
    shutil.copyfileobj(gz, f)
size = os.path.getsize(db_file)
print(f'Ready ({size/1e9:.1f}GB).', flush=True)
PYEOF
fi

echo "Starting server..."
exec python3 server.py
