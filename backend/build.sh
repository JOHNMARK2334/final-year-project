#!/usr/bin/env bash
# build.sh
#!/bin/bash
# Install Tesseract OCR and dependencies
apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev
# Install Python dependencies
pip install -r requirements.txt

# Add to build.sh
echo "Tesseract version: $(tesseract --version)"