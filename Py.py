import streamlit as st
from PIL import Image
import pytesseract
import re
import os

# --- ⚙️ Configurare Loto ---
NUMERE_PER_RAND = 12       
DOMENIU_MAXIM = 66         
# Setare Tesseract: Folosim psm 6 pentru blocuri uniforme de text, optim pentru tabele
CUSTOM_TESSERACT_CONFIG = r'--psm 6'

# ⚠️ Atenție: Trebuie să specifici calea către Tesseract dacă rulezi local!
# Pe Streamlit Cloud nu este necesar, deoarece este instalat via packages.txt.
# Dacă rulezi pe Windows, decomentează și ajustează:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def extrage_numere_loto_validat(cale_imagine):
    """
    Procesează imaginea și extrage numerele.
    Validare strictă: 12 numere valide (1-66), separate prin 11 virgule.
    """
    try:
        img = Image.open(cale_imagine)
        
        # Extrage textul, folosind configurarea specifică
        text_extras = pytesseract.image_to_string(img, config=CUSTOM_TESSERACT_CONFIG)
        
        linii_rezultate = []
        
        # Procesează textul rând cu rând
        for linie_text in text_extras.split('\n'):
            linie_text = linie_text.strip()
            if not linie_text:
                continue

            # Încercăm să izolăm doar coloana de numere (cea mai din dreapta)
            # Caută o secvență de numere, virgule și spații la finalul rândului
            match = re.search(r'[\d, ]+$', linie_text) 
            
            if match:
                # Curățăm spațiile și ne concentrăm doar pe numere și virgule
                linie_curatata = match.group(0).replace(' ', '')
            else:
                continue
            
            # Splitare după virgulă. Acesta forțează structura cu 11 virgule.
            elemente = linie_curatata.split(',')
            
            # Aplică restricția strictă: trebuie să fie exact NUMERE_PER_RAND elemente
            if len(elemente) == NUMERE_PER_RAND:
                
                numere_validate = []
                valid = True
                
                # Validare Numerică și Domeniu (1-66)
                for element_str in elemente:
                    try:
                        numar = int(element_str)
                        # Verificarea domeniului 1-66
                        if 1 <= numar <= DOMENIU_MAXIM:
                            numere_validate.append(numar)
                        else:
                            valid = False # Număr în afara domeniului
                            break
                    except ValueError:
                        valid = False # Nu e număr (ex: '1O' sau element vid)
                        break
                
                # Dacă validarea a trecut și avem numărul corect de elemente
                if valid and len(numere_validate) == NUMERE_PER_RAND:
                    linii_rezultate.append(sorted(numere_validate))
                
        return linii_rezultate, text_extras

    except Exception as e:
        # Afișează eroarea în Streamlit
        return f"A apărut o eroare la procesare: {e}", ""

# --- Interfața Streamlit ---
st.set_page_config(page_title="Extractor Loto 1-66", layout="wide")
st.title("🔢 Extractor Automat de Numere Loto (1-66)")
st.markdown("""
Încărcați un screenshot cu rezultatele extragerilor. 
Aplicația va extrage doar rândurile care conțin **exact 12 numere** valide (între 1 și 66), separate prin virgule.
""")

uploaded_file = st.file_uploader("Alege o imagine (screenshot)", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Imagine încărcată", use_column_width=True)
    
    with st.spinner('Procesare imagine și rulare OCR...'):
        rezultate_valide, text_raw = extrage_numere_loto_validat(uploaded_file)
    
    st.subheader("Rezultate Extrase și Validate")
    
    if rezultate_valide:
        st.success(f"✅ S-au găsit {len(rezultate_valide)} rânduri valide (cu exact {NUMERE_PER_RAND} numere):")
        
        # Afișează fiecare rând valid
        for i, r in enumerate(rezultate_valide):
            st.code(f"Extragerea nr. {i+1}: {', '.join(map(str, r))}")
    else:
        st.warning(f"❌ Nu s-au găsit rânduri care să conțină exact {NUMERE_PER_RAND} numere valide (1-{DOMENIU_MAXIM}). Verificați imaginea și textul brut.")
        
    with st.expander("Vizualizați textul brut extras de OCR (Debug)"):
        if isinstance(text_raw, str):
            st.code(text_raw)
        else:
            st.error(f"Eroare la procesare: {text_raw}")
