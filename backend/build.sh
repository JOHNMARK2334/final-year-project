#!/usr/bin/env bash
# build.sh

apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev

# Verify Tesseract installation
tesseract --version || { echo "Tesseract installation failed or not found!"; exit 1; }

# Install Python dependencies
pip install -r requirements.txt

