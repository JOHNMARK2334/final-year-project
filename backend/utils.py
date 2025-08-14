import openai
import pytesseract
import speech_recognition as sr
from PIL import Image
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
import langdetect
from deep_translator import GoogleTranslator
import PyPDF2
import logging

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
    # Make Tesseract path configurable via environment variable
    #if os.name == 'nt':  # Windows
        #pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    #else:  # Linux (Render)
    tesseract_path = os.getenv("TESSERACT_PATH", "/usr/bin/tesseract")
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    try:
        img = Image.open(image_path)
        img = ImageOps.grayscale(img)
        # Optionally allow threshold to be set via env var
        threshold = int(os.getenv("OCR_THRESHOLD", "140"))
        img = img.point(lambda x: 0 if x < threshold else 255, '1')
        text = pytesseract.image_to_string(img)
        logging.info(f"OCR extracted text: {text}")
        if not text.strip():
            logging.warning(f"OCR returned empty text for image: {image_path}")
        return text
    except FileNotFoundError:
        logging.error(f"Tesseract executable not found at {tesseract_path}. Set TESSERACT_PATH environment variable correctly.")
        return f"Tesseract executable not found at {tesseract_path}. Set TESSERACT_PATH environment variable correctly."
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
        import pytesseract
        from PIL import Image
        import io
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text() or ""
                text += page_text
                # If no text, try OCR on page image
                if not page_text.strip() and '/XObject' in page.get('/Resources', {}):
                    xObject = page['/Resources']['/XObject'].get_object()
                    for obj in xObject:
                        if xObject[obj]['/Subtype'] == '/Image':
                            data = xObject[obj]._data
                            img = Image.open(io.BytesIO(data))
                            ocr_text = pytesseract.image_to_string(img)
                            text += ocr_text
            # If still empty, try OCR on entire PDF as images (fallback)
            if not text.strip():
                try:
                    from pdf2image import convert_from_path
                    images = convert_from_path(pdf_path)
                    for img in images:
                        ocr_text = pytesseract.image_to_string(img)
                        text += ocr_text
                except Exception as e:
                    logging.warning(f"OCR fallback failed: {e}")
            return text
    except Exception as e:
        logging.error(f"PDF extraction error: {e}")
        return ""
