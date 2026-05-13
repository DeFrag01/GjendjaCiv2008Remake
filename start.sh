#!/bin/bash
set -e

DB_FILE="civil_registry_clean.db"
DB_URL="${DB_URL:-https://github.com/DeFrag01/GjendjaCiv2008Remake/releases/download/v1/civil_registry_clean.db.gz}"

if [ -f "$DB_FILE" ]; then
    echo "Database found."
else
    echo "Downloading and decompressing database..."
    curl -fL "$DB_URL" | gunzip > "$DB_FILE"
    echo "Database ready ($(du -h "$DB_FILE" | cut -f1))."
fi

echo "Starting server..."
exec python3 server.py
