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
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
    raw_image = Image.open(image_path).convert('RGB')
    inputs = processor(raw_image, return_tensors="pt")
    out = model.generate(**inputs)
    return processor.decode(out[0], skip_special_tokens=True)

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
