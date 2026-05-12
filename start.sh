#!/bin/bash
set -e

DB_FILE="civil_registry_clean.db"
DB_GZ="${DB_FILE}.gz"
DB_URL="${DB_URL:-https://github.com/DeFrag01/GjendjaCiv2008Remake/releases/download/v1/civil_registry_clean.db.gz}"

if [ -f "$DB_FILE" ]; then
    echo "Database found."
elif [ -f "$DB_GZ" ]; then
    echo "Decompressing existing archive..."
    gunzip "$DB_GZ"
else
    echo "Downloading database..."
    curl -L -o "$DB_GZ" "$DB_URL"
    echo "Decompressing..."
    gunzip "$DB_GZ"
    echo "Download complete."
fi

echo "Starting server..."
exec python3 server.py
