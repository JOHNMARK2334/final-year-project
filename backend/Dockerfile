FROM python:3.13

WORKDIR /app

ENV TESSERACT_CMD=/usr/bin/tesseract
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/tessdata

# Install system dependencies for PyAudio
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN apt-get update && apt-get install -y portaudio19-dev
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && \
    apt-get install -y tesseract-ocr && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip install pyaudioop
COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
