#!/bin/bash
set -e

DB_FILE="civil_registry_clean.db"
RAW_ID="${GOOGLE_DRIVE_FILE_ID:-13Lc3BFcdE7Lnqszbw91GhuWrjIIzPEyt}"

# Extract file ID if full URL was given
if [[ "$RAW_ID" == *"drive.google.com"* ]]; then
    FILE_ID=$(echo "$RAW_ID" | sed 's/.*\/d\/\([^/]*\).*/\1/')
else
    FILE_ID="$RAW_ID"
fi

if [ ! -f "$DB_FILE" ]; then
    echo "Downloading database from Google Drive (ID: $FILE_ID)..."
    gdown --id "$FILE_ID" --fuzzy -O "$DB_FILE" || {
        echo "gdown failed, trying alternative method..."
        curl -L -b /tmp/gdcookie -c /tmp/gdcookie \
            "https://drive.usercontent.google.com/download?id=${FILE_ID}&confirm=t" \
            -o "$DB_FILE"
    }
    echo "Download complete."
fi

echo "Starting server..."
python3 server.py
