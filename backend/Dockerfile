FROM python:3.11-slim

WORKDIR /app

ENV TESSERACT_CMD=/usr/bin/tesseract
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/tessdata

# Install system dependencies needed to build audio-related C extensions and for pydub/ffmpeg usage.
# This includes portaudio headers (for PyAudio), build tools for compiling C extensions, and ffmpeg for pydub.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libsndfile1-dev \
    portaudio19-dev \
    ffmpeg \
    tesseract-ocr \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
