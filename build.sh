#!/bin/bash
# Flaxon Account Manager - Local build script
set -e

echo "[Flaxon] Installing dependencies..."
pip install -r requirements.txt --quiet
pip install pyinstaller --quiet

echo "[Flaxon] Building binary..."
pyinstaller \
  --onefile \
  --name "flaxon-account" \
  --clean \
  --noconfirm \
  src/main.py

echo "[Flaxon] Done! Binary is at: dist/flaxon-account"
