#!/usr/bin/env bash
# build.sh
#!/bin/bash
# Install Tesseract OCR and dependencies
sudo apt-get update && sudo apt-get install -y \
    tesseract-ocr \
    libtesseract-dev
# Install Python dependencies
sudo pip install -r requirements.txt

