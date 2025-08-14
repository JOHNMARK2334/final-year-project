#!/usr/bin/env bash
# build.sh

#!/bin/bash
pip install pytesseract pillow
pip install -r requirements.txt
#verify installation
tesseract --version || { echo "Tesseract installation failed or not found!"; exit 1; }

# Install Python dependencies
pip install -r requirements.txt

