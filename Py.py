import streamlit as st
from PIL import Image
import pytesseract
import re
import os

# --- ⚙️ Configurare Loto ---
NUMERE_PER_RAND = 12       
DOMENIU_MAXIM = 66         
CUSTOM_TESSERACT_CONFIG = r'--psm 6'

# **CRITIC:** Setarea căii Tesseract pentru Streamlit Cloud
# Verificăm dacă suntem pe mediul Streamlit Cloud
if os.environ.get('STREAMLIT_SERVER_ENABLE_CORS') is not None:
    try:
        # Calea standard pe serverele bazate pe Debian/Ubuntu (folosite de Streamlit)
        pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
    except Exception as e:
        # Nu putem continua fără Tesseract, dar permitem aplicației să pornească
        st.error(f"Eroare la setarea căii Tesseract pe Cloud: {e}")
        pytesseract.pytesseract.tesseract_cmd = '' # Setează gol pentru a evita crash-ul total la import
else:
    # Setare pentru rulare locală (decomentează dacă rulezi pe propriul PC)
    # Ex: pe Windows: pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    pass


def extrage_numere_loto_validat(cale_imagine):
    """
    Extrage toate numerele (1-66) din textul brut și le grupează în rânduri 
    cu lungimea exactă de 12, ignorând delimitatorii și coloanele de control.
    """
    if not pytesseract.pytesseract.tesseract_cmd:
        return ["Tesseract nu a putut fi inițializat. Verificați packages.txt!"], ""

    try:
        img = Image.open(cale_imagine)
        
        # Extrage textul din imagine
        text_extras = pytesseract.image_to_string(img, config=CUSTOM_TESSERACT_CONFIG)
        
        linii_rezultate = []
        
        # Procesează textul rând cu rând (fiecare rând de text citit de OCR)
        for linie_text in text_extras.split('\n'):
            linie_text = linie_text.strip()
            if not linie_text:
                continue

            # 1. Extrage TOATE numerele de 1 sau 2 cifre din rând
            numere_gasite_raw = re.findall(r'\b\d{1,2}\b', linie_text)
            
            numere_validate = []
            
            # 2. Validare Numerică și Domeniu (1-66)
            for n_str in numere_gasite_raw:
                try:
                    numar = int(n_str)
                    # Verifică domeniul Loto 1-66
                    if 1 <= numar <= DOMENIU_MAXIM:
                        numere_validate.append(numar)
                except ValueError:
                    pass
            
            # 3. Găsirea setului de 12 numere Loto
            if len(numere_validate) >= NUMERE_PER_RAND:
                numere_loto_finale = numere_validate[-NUMERE_PER_RAND:]
                    
                if len(numere_loto_finale) == NUMERE_PER_RAND:
                    linii_rezultate.append(sorted(numere_loto_finale))

        return linii_rezultate, text_extras

    except Exception as e:
        return f"A apărut o eroare la procesare: {e}", ""


# --- Interfața Streamlit ---
st.set_page_config(page_title="Extractor Loto 1-66", layout="wide")
st.title("🔢 Extractor Automat de Numere Loto (1-66)")
st.markdown("""
Încărcați un screenshot cu rezultatele extragerilor. 
Aplicația va extrage doar rândurile care conțin **exact 12 numere** valide (între 1 și 66).
""")

uploaded_file = st.file_uploader("Alege o imagine (screenshot)", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Imagine încărcată", use_column_width=True)
    
    with st.spinner('Procesare imagine și rulare OCR...'):
        rezultate_valide, text_raw = extrage_numere_loto_validat(uploaded_file)
    
    st.subheader("Rezultate Extrase și Validate")
    
    if rezultate_valide and isinstance(rezultate_valide, list):
        st.success(f"✅ S-au găsit {len(rezultate_valide)} rânduri valide:")
        
        # MODIFICAREA 1: Afișăm doar numerele (fără textul descriptiv)
        for r in rezultate_valide:
            st.code(', '.join(map(str, r))) 
    else:
        st.warning(f"❌ Nu s-au găsit rânduri care să conțină exact {NUMERE_PER_RAND} numere valide (1-{DOMENIU_MAXIM}).")
        
    # MODIFICAREA 2: Curățarea textului brut din expanderul de debug
    with st.expander("Vizualizați textul brut extras de OCR (Debug)"):
        if isinstance(text_raw, str):
            # 1. Încercăm să găsim începutul datelor relevante
            start_marker_1 = "Rychlé kodky" # Marcaj tipic din textul brut
            start_marker_2 = "MENU S LOTERIE"
            
            start_index_1 = text_raw.find(start_marker_1)
            start_index_2 = text_raw.find(start_marker_2)
            
            # Alegem cel mai mic index pozitiv
            if start_index_1 != -1 and start_index_2 != -1:
                start_index = min(start_index_1, start_index_2)
            elif start_index_1 != -1:
                start_index = start_index_1
            elif start_index_2 != -1:
                start_index = start_index_2
            else:
                start_index = -1
                
            text_filtru = text_raw
            if start_index != -1:
                text_filtru = text_raw[start_index:]
                
            # 2. Încercăm să găsim sfârșitul datelor relevante
            end_marker = "Rezultate Extrase si Validate"
            end_index = text_filtru.find(end_marker)
            
            if end_index != -1:
                # Taie tot ce este de la markerul de sfârșit în jos
                text_filtru = text_filtru[:end_index]
            
            st.code(text_filtru.strip())
        else:
            st.error(f"Eroare la procesare: {rezultate_valide}")
