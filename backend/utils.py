import openai
import speech_recognition as sr
from PIL import Image
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
import langdetect
from deep_translator import GoogleTranslator
import PyPDF2

def process_audio(file_path):
    r = sr.Recognizer()
    try:
        with sr.AudioFile(file_path) as source:
            audio = r.record(source)
        return r.recognize_google(audio)
    except sr.UnknownValueError:
        return "Could not understand audio. Please try again with a clearer recording."
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"
    except Exception as e:
        return f"Audio processing error: {str(e)}"

def process_image(image_path):
    import pytesseract
    from PIL import Image, ImageOps
    import os
    import logging
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    try:
        img = Image.open(image_path)
        img = ImageOps.grayscale(img)
        img = img.point(lambda x: 0 if x < 140 else 255, '1')
        text = pytesseract.image_to_string(img)
        logging.info(f"OCR extracted text: {text}")
        if not text.strip():
            logging.warning(f"OCR returned empty text for image: {image_path}")
        return text
    except Exception as e:
        logging.error(f"OCR error for image {image_path}: {str(e)}")
        return f"Image OCR error: {str(e)}"

def detect_language(text):
    try:
        return langdetect.detect(text)
    except Exception:
        return "en"

def translate_to_english(text):
    try:
      
        return GoogleTranslator(source='auto', target='en').translate(text)
    except Exception:
        return text

def extract_text_from_pdf(pdf_path):
    try:
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
    except Exception:
        return ""
