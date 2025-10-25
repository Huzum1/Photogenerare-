import streamlit as st
from PIL import Image
import pytesseract
import re

# Setările Loto:
NUMERE_PER_RAND = 12       
DOMENIU_MAXIM = 66         

def extrage_numere_loto_validat(cale_imagine):
    """
    Procesează imaginea și extrage numerele.
    Validare strictă bazată pe SPLIT-ul după virgulă (implică 11 virgule).
    """
    try:
        img = Image.open(cale_imagine)
        # Extrage textul, tratând fiecare rând ca entitate separată
        # Adaugă configurarea Tesseract pentru a trata imaginea ca un bloc de text (opțional, dar util pentru tabele)
        custom_config = r'--psm 6' # Modul 6 este bun pentru blocuri uniforme de text
        text_extras = pytesseract.image_to_string(img, config=custom_config)
        
        linii_rezultate = []
        
        for linie_text in text_extras.split('\n'):
            linie_text = linie_text.strip()
            if not linie_text:
                continue

            # 1. Curățare și Splitare
            # Înlocuim orice spațiu din jur pentru a ne asigura că split-ul funcționează corect.
            # Ex: '1, 10, 44' devine ['1', '10', '44']
            
            # Folosim o expresie regulată pentru a izola coloana de numere 
            # (aceasta este o estimare, poate necesita ajustări)
            # Ne concentrăm pe partea finală a rândului care începe cu un număr.
            match = re.search(r'[\d, ]+$', linie_text) 
            if match:
                linie_curatata = match.group(0).replace(' ', '')
            else:
                continue
            
            # Splitare după virgulă
            elemente = linie_curatata.split(',')
            
            # 2. Aplică restricția strictă: Exact 12 elemente (implică 11 virgule)
            if len(elemente) == NUMERE_PER_RAND:
                
                numere_validate = []
                valid = True
                
                # 3. Validare Numerică și Domeniu (1-66)
                for element_str in elemente:
                    try:
                        numar = int(element_str)
                        # Verificarea domeniului
                        if 1 <= numar <= DOMENIU_MAXIM:
                            numere_validate.append(numar)
                        else:
                            valid = False # Numărul este în afara domeniului (ex: 67)
                            break
                    except ValueError:
                        valid = False # Elementul nu este un număr (ex: Tesseract a citit '1O')
                        break
                
                if valid and len(numere_validate) == NUMERE_PER_RAND:
                    linii_rezultate.append(sorted(numere_validate))
                
        return linii_rezultate, text_extras

    except Exception as e:
        return f"A apărut o eroare la procesare: {e}", ""

# ... (Restul interfeței Streamlit rămâne neschimbat) ...
