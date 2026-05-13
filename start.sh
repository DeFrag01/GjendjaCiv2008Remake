#!/bin/bash

DB_FILE="civil_registry_clean.db"
DB_GZ="civil_registry_clean.db.gz"
DB_URL="${DB_URL:-https://github.com/DeFrag01/GjendjaCiv2008Remake/releases/download/v1/civil_registry_clean.db.gz}"

if [ ! -f "$DB_FILE" ]; then
    echo "Downloading database..."
    curl -L --connect-timeout 10 --max-time 120 -H "User-Agent: Mozilla/5.0" --retry 2 --retry-delay 5 "$DB_URL" -o "$DB_GZ" && {
        gunzip "$DB_GZ"
        echo "Database ready."
    } || echo "Download failed, server will start without DB."
fi

echo "Starting server..."
exec python3 server.py
