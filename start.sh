#!/bin/bash
set -e

DB_FILE="civil_registry_clean.db"
DB_GZ="${DB_FILE}.gz"
DB_URL="${DB_URL:-https://github.com/DeFrag01/GjendjaCiv2008Remake/releases/download/v1/civil_registry_clean.db.gz}"

if [ -f "$DB_FILE" ]; then
    echo "Database found."
else
    echo "Downloading database..."
    python3 -c "
import urllib.request, sys, gzip
url = '$DB_URL'
print(f'Downloading from {url}', flush=True)
resp = urllib.request.urlopen(url)
data = resp.read()
print(f'Downloaded {len(data)} bytes, decompressing...', flush=True)
with open('$DB_FILE', 'wb') as f:
    f.write(gzip.decompress(data))
print('Database ready.', flush=True)
"
fi

echo "Starting server..."
exec python3 server.py
