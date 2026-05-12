#!/bin/bash
set -e

DB_FILE="civil_registry_clean.db"
# Set this to your Google Drive file ID
GOOGLE_DRIVE_FILE_ID="${GOOGLE_DRIVE_FILE_ID:-13Lc3BFcdE7Lnqszbw91GhuWrjIIzPEyt}"

if [ ! -f "$DB_FILE" ]; then
    echo "Database not found. Downloading from Google Drive..."
    gdown "https://drive.google.com/uc?id=${GOOGLE_DRIVE_FILE_ID}" -O "$DB_FILE"
    echo "Download complete."
fi

echo "Starting server..."
python3 server.py
