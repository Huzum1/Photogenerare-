import streamlit as st
import pandas as pd
import re

# Configurare pagină
st.set_page_config(page_title="Generator Numere Italy 20/90", page_icon="🎲", layout="wide")

# Titlu principal
st.title("🎲 Aplicație Gestionare Runde - Italy Keno 20/90")

# Inițializare session state
if 'rounds' not in st.session_state:
    st.session_state.rounds = []

# Sidebar pentru navigare
option = st.sidebar.selectbox(
    "Alege o opțiune:",
    ["📝 Adaugă Runde", "🎯 Extrage Numere"]
)

# ========== OPȚIUNEA 1: ADAUGĂ RUNDE ==========
if option == "📝 Adaugă Runde":
    st.header("Adaugă Runde Italy 20/90")
    
    st.write("**Lipește rundele în formatul următor:**")
    st.code("24-05-2026 00:39:59 | 3,6,17,21,24,42,48,49,53,54,56,57,58,60,61,63,65,69,73,77\n24-05-2026 00:34:59 | 1,5,6,13,18,19,25,32,36,41,44,47,49,52,73,74,82,83,86,90")
    
    # Text area mare pentru multiple runde
    rounds_input = st.text_area(
        "Lipește toate rundele din fișier:",
        placeholder="Lipește liniile aici...",
        height=300
    )
    
    col1, col2, col3 = st.columns([1, 1, 3])
    
    with col1:
        if st.button("➕ Adaugă Rundele", type="primary"):
            if rounds_input.strip():
                lines = rounds_input.strip().split('\n')
                added_count = 0
                error_count = 0
                
                i = 0
                while i < len(lines):
                    line = lines[i].strip()
                    
                    if line:
                        try:
                            # Verifică dacă linia conține caracterul separator |
                            if '|' in line:
                                timestamp_part, numbers_part = line.split('|', 1)
                                timestamp_part = timestamp_part.strip()
                                numbers_part = numbers_part.strip()
                                
                                # Extrage data și ora din timestamp (ex: "24-05-2026 00:39:59")
                                timestamp_segments = timestamp_part.split(' ')
                                if len(timestamp_segments) >= 2:
                                    round_date = timestamp_segments[0].strip()
                                    round_time = timestamp_segments[1].strip()
                                else:
                                    round_date = timestamp_part
                                    round_time = "--:--:--"
                                
                                # Înlocuiește virgulele dintre numere cu spațiu simplu
                                clean_numbers = numbers_part.replace(",", " ").strip()
                                
                                # Identifică ID-ul rundei (opțional). Deoarece formatul tău nu are ID explicit,
                                # folosim ora extragerii ca ID, sau generăm o numerotare logică bazată pe poziție.
                                round_id = f"R-{round_time.replace(':', '')}"
                                
                                # Creare obiect rundă
                                round_data = {
                                    'Id': round_id,
                                    'Data': round_date,
                                    'Ora': round_time,
                                    'Numere': clean_numbers
                                }
                                
                                st.session_state.rounds.append(round_data)
                                added_count += 1
                            else:
                                error_count += 1
                        except Exception as e:
                            error_count += 1
                    
                    # Trecem la linia următoare
                    i += 1
                
                if added_count > 0:
                    st.success(f"✅ {added_count} runde adăugate cu succes!")
                if error_count > 0:
                    st.warning(f"⚠️ {error_count} linii nu au putut fi adăugate (format incorect sau nerecunoscut)")
                
                st.rerun()
            else:
                st.error("⚠️ Te rog introdu cel puțin o rundă!")
    
    with col2:
        if st.session_state.rounds:
            if st.button("🗑️ Șterge Tot"):
                st.session_state.rounds = []
                st.rerun()
    
    # Afișare toate rundele salvate în memorie
    if st.session_state.rounds:
        st.divider()
        total_rounds = len(st.session_state.rounds)
        st.subheader(f"📊 Total Runde Salvate: {total_rounds}")
        
        # Secțiune de extragere rapidă direct în prima pagină
        col_extract1, col_extract2, col_extract3 = st.columns([1, 1, 3])
        
        with col_extract1:
            if st.button("🔍 Extrage Numerele", type="primary"):
                all_numbers = [round_data['Numere'] for round_data in st.session_state.rounds]
                st.session_state.extracted_numbers = "\n".join(all_numbers)
                st.session_state.show_extraction = True
        
        with col_extract2:
            if st.button("❌ Ascunde Extragere"):
                st.session_state.show_extraction = False
        
        # Afișare text area cu numerele finale
        if hasattr(st.session_state, 'show_extraction') and st.session_state.show_extraction:
            st.divider()
            st.success(f"✅ Toate cele {total_rounds} seturi de numere au fost extrase!")
            
            st.text_area(
                f"Numerele extrase ({total_rounds} runde):",
                value=st.session_state.extracted_numbers,
                height=300
            )
            
            st.download_button(
                label=f"📥 Descarcă Numerele ({total_rounds} runde)",
                data=st.session_state.extracted_numbers.encode('utf-8'),
                file_name="numere_extrase.txt",
                mime="text/plain",
            )
        
        st.divider()
        
        # Tabelul interactiv cu structura datelor
        df_all = pd.DataFrame(st.session_state.rounds)
        st.dataframe(df_all, use_container_width=True, hide_index=True)
        
        # Export fișier tabelar .csv complet
        col_export1, col_export2 = st.columns([1, 4])
        with col_export1:
            csv = df_all.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=f"📥 Descarcă CSV ({total_rounds} runde)",
                data=csv,
                file_name="runde_complete_italy.csv",
                mime="text/csv",
            )

# ========== OPȚIUNEA 2: EXTRAGE NUMERE ==========
elif option == "🎯 Extrage Numere":
    st.header("Extrage Numere Curate pentru Backtesting")
    
    if not st.session_state.rounds:
        st.warning("⚠️ Nu ai nicio rundă adăugată! Mergi la 'Adaugă Runde' mai întâi.")
    else:
        total_rounds = len(st.session_state.rounds)
        st.write(f"**Total runde disponibile în sistem: {total_rounds}**")
        
        st.divider()
        
        if st.button("🔍 Generează fișierul text final", type="primary"):
            all_numbers = [round_data['Numere'] for round_data in st.session_state.rounds]
            extracted_count = len(all_numbers)
            
            if extracted_count == total_rounds:
                st.success(f"✅ Toate cele {extracted_count} seturi de numere au fost extrase cu succes!")
            else:
                st.error(f"⚠️ Eroare: S-au procesat doar {extracted_count} din {total_rounds} runde!")
            
            st.divider()
            st.subheader(f"📋 Numerele Extrase ({extracted_count} runde)")
            
            numbers_text = "\n".join(all_numbers)
            
            st.text_area(
                f"Format curat (gata de pus în scriptul de analiză):",
                value=numbers_text,
                height=400
            )
            
            col_download1, col_download2 = st.columns([1, 4])
            with col_download1:
                st.download_button(
                    label=f"📥 Descarcă Fișierul Text ({extracted_count} runde)",
                    data=numbers_text.encode('utf-8'),
                    file_name="runde15.txt",
                    mime="text/plain",
                )

# Footer aplicație
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    Adaptat pentru Italia Keno 20/90 | Made with ❤️ using Streamlit
</div>
""", unsafe_allow_html=True)
