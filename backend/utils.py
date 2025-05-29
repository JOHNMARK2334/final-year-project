import openai
import speech_recognition as sr
from PIL import Image
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
import langdetect
from deep_translator import GoogleTranslator
import PyPDF2
import logging
import os
import pytesseract
#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
from pdf2image import convert_from_path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load BLIP model and processor once for efficiency
try:
    BLIP_PROCESSOR = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base", use_fast=True)
    BLIP_MODEL = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
except Exception as e:
    logger.error(f"Failed to load BLIP model/processor: {str(e)}")
    BLIP_PROCESSOR = None
    BLIP_MODEL = None

# Improve audio processing robustness
def process_audio_file(audio_path):
    try:
        # Validate audio file
        if not os.path.exists(audio_path):
            raise ValueError("Audio file not found")
        
        # Check file size
        if os.path.getsize(audio_path) > 10 * 1024 * 1024:  # 10MB limit
            raise ValueError("Audio file too large (max 10MB)")
        
        r = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio = r.record(source)
            text = r.recognize_google(audio)
            return translate_to_english(text)
    except sr.UnknownValueError:
        return "Could not understand audio"
    except Exception as e:
        logger.error(f"Audio Processing Error: {str(e)}")
        return "Error processing audio"
    
# Function to process images using BLIP model
def process_image(image_path):
    if BLIP_PROCESSOR is None or BLIP_MODEL is None:
        logger.error("BLIP model/processor not loaded.")
        return "Error: BLIP model/processor not loaded."
    try:
        raw_image = Image.open(image_path).convert('RGB')
        inputs = BLIP_PROCESSOR(raw_image, return_tensors="pt")
        out = BLIP_MODEL.generate(**inputs)
        return BLIP_PROCESSOR.decode(out[0], skip_special_tokens=True)
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        return f"Error: Failed to process image - {str(e)}"

def detect_language(text):
    try:
        return langdetect.detect(text)
    except Exception:
        return "en"

def translate_to_english(text):
    try:
        return GoogleTranslator(source='auto', target='en').translate(text)
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        return text

def extract_image_text(image_path):
    try:
        text = pytesseract.image_to_string(Image.open(image_path))
        return translate_to_english(text)
    except Exception as e:
        logger.error(f"OCR Error: {str(e)}")
        return "Error extracting text from image"

def extract_pdf_text(pdf_path):
    text = ""
    try:
        # Text extraction from PDF
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
        
        # OCR for image-based PDFs
        if not text.strip():
            images = convert_from_path(pdf_path)
            for img in images:
                text += pytesseract.image_to_string(img)
        
        return translate_to_english(text)
    except Exception as e:
        logger.error(f"PDF Processing Error: {str(e)}")
        return "Error processing PDF"

def process_audio_file(audio_path):
    try:
        r = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio = r.record(source)
            text = r.recognize_google(audio)
            return translate_to_english(text)
    except sr.UnknownValueError:
        return "Could not understand audio"
    except Exception as e:
        logger.error(f"Audio Processing Error: {str(e)}")
        return "Error processing audio"

def extract_text_from_file(file_path, file_type):
    try:
        if file_type == 'pdf':
            return extract_pdf_text(file_path)
        elif file_type in ['png', 'jpg', 'jpeg']:
            return extract_image_text(file_path)
        elif file_type in ['wav', 'mp3']:
            return process_audio_file(file_path)
        else:
            return "Unsupported file type"
    except Exception as e:
        logger.error(f"File Processing Error: {str(e)}")
        return "Error processing file"
