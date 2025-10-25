import streamlit as st
from PIL import Image
import pytesseract
import re
import os

# --- ⚙️ Configurare Loto ---
NUMERE_PER_RAND = 12       
DOMENIU_MAXIM = 66         
CUSTOM_TESSERACT_CONFIG = r'--psm 6'

# **NOU:** Setează calea către executabilul Tesseract
# Verificăm dacă suntem pe Streamlit Cloud (verificăm variabilele de mediu)
if os.environ.get('STREAMLIT_SERVER_ENABLE_CORS') is not None:
    # Dacă rulează pe Streamlit Cloud (Linux), setăm calea standard
    # Dacă aceasta nu funcționează, încearcă r'/usr/bin/tesseract'
    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
else:
    # Dacă rulează local (Windows/Mac), trebuie setată manual calea locală
    # DECOMENTEAZĂ și completează calea locală DACA rulezi local:
    # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    pass # Lasă-l să detecteze automat dacă nu e specificat

# ... (restul funcției extrage_numere_loto_validat rămâne la fel)
# ...
