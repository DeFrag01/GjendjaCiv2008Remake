#!/bin/bash
set -e

DB_FILE="civil_registry_clean.db"
DB_GZ="${DB_FILE}.gz"
RAW_ID="${GOOGLE_DRIVE_FILE_ID:-13d6iXY9i4icko7Rl0OjKrkvGARjePsmn}"

if [[ "$RAW_ID" == *"drive.google.com"* ]]; then
    FILE_ID=$(echo "$RAW_ID" | sed 's/.*\/d\/\([^/]*\).*/\1/')
else
    FILE_ID="$RAW_ID"
fi

if [ -f "$DB_FILE" ]; then
    echo "Database found."
elif [ -f "$DB_GZ" ]; then
    echo "Decompressing existing archive..."
    gunzip -k "$DB_GZ"
else
    echo "Downloading database from Google Drive (ID: $FILE_ID)..."
    gdown --id "$FILE_ID" --fuzzy -O "$DB_GZ" || {
        echo "gdown failed, trying alternative method..."
        curl -L -b /tmp/gdcookie -c /tmp/gdcookie \
            "https://drive.usercontent.google.com/download?id=${FILE_ID}&confirm=t" \
            -o "$DB_GZ"
    }
    echo "Decompressing..."
    gunzip -k "$DB_GZ"
    echo "Download complete."
fi

echo "Starting server..."
python3 server.py
