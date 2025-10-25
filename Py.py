import streamlit as st
from PIL import Image
import pytesseract
import re

# --- ⚙️ Configurare Loto ---
NUMERE_PER_RAND = 12       
DOMENIU_MAXIM = 66         
CUSTOM_TESSERACT_CONFIG = r'--psm 6'

def extrage_numere_loto_validat(cale_imagine):
    """
    Extrage toate numerele (1-66) din textul brut și le grupează în rânduri 
    cu lungimea exactă de 12, ignorând spațiile, virgulele și celelalte coloane.
    """
    try:
        img = Image.open(cale_imagine)
        # Extrage textul din imagine
        text_extras = pytesseract.image_to_string(img, config=CUSTOM_TESSERACT_CONFIG)
        
        linii_rezultate = []
        
        # 1. Procesează textul rând cu rând
        for linie_text in text_extras.split('\n'):
            linie_text = linie_text.strip()
            if not linie_text:
                continue

            # 2. Extrage TOATE numerele de 1 sau 2 cifre din rând (ignorând virgulele și literele)
            # Această metodă este mult mai rezistentă la erorile de OCR
            numere_gasite_raw = re.findall(r'\b\d{1,2}\b', linie_text)
            
            numere_validate = []
            
            # 3. Validare Numerică și Domeniu (1-66)
            for n_str in numere_gasite_raw:
                try:
                    numar = int(n_str)
                    # Verifică domeniul Loto 1-66
                    if 1 <= numar <= DOMENIU_MAXIM:
                        numere_validate.append(numar)
                except ValueError:
                    pass # Ar trebui să nu se întâmple din cauza regex-ului
            
            # 4. Extragem doar numerele de la Loto și le grupăm
            # Ne așteptăm ca numerele de loto să apară ca un set compact de 12,
            # după numărul extragerii, dată și oră.
            
            # Știm că rândul începe cu numărul extragerii (ex: 3866690) urmat de 4 numere (ziua, luna, anul, ora).
            # Asta înseamnă că setul valid de 12 numere ar trebui să înceapă după primele 5 numere extrase din rând.
            
            if len(numere_validate) >= NUMERE_PER_RAND:
                
                # Căutăm secvența de 12 numere de loto (încercare de a sări peste primele coloane)
                
                # Încercăm să presupunem că numerele loto încep după numerele datei/orei (care sunt de obicei 5)
                # Exemplu: 3866690, 24, 10, 2025, 23, 38, [12 numere Loto]
                # Sărim peste primele 5-8 numere, care ar putea fi numărul extragerii, data și ora.
                
                # Încercăm să găsim o secvență de 12 numere consecutive (fără a ține cont de începutul rândului)
                # Aceasta este o abordare mai simplă: dacă avem cel puțin 12 numere în rând, 
                # luăm ultima secvență de 12, presupunând că primele sunt cele de control.
                
                if len(numere_validate) >= 12:
                    # Rândul Loto este aproape întotdeauna ultima secțiune din rând
                    numere_loto_finale = numere_validate[-NUMERE_PER_RAND:]
                    
                    if len(numere_loto_finale) == NUMERE_PER_RAND:
                        # Găsit un rând valid (doar 12 numere între 1 și 66)
                        linii_rezultate.append(sorted(numere_loto_finale))

        return linii_rezultate, text_extras

    except Exception as e:
        return f"A apărut o eroare la procesare: {e}", ""

# ... (Restul interfeței Streamlit rămâne neschimbat) ...
