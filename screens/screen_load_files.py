import streamlit as st
from components.top_bar import top_bar
from utils.navigation import *

def screen_load_files():
    
    # BARRA DE NAVEGACION
    top_bar(title="Ingrese los archivos para analizar", back_to="select", show_stepper=True, step=1)
        
    # CARGADOR DE ARCHIVOS
    files = st.file_uploader("Subir archivos",type=["pdf", "png", "txt", "docx", "py", "xlsm"],accept_multiple_files=True,label_visibility="collapsed")
    st.session_state.files = files

    # TEXTO INFORMATIVO
    st.markdown(f"<h5 style='margin-top: 20px; margin-bottom: 10px;'>¿Que podes subir?</h5>", unsafe_allow_html=True)
    st.markdown(f"<ul style='font-size: 13px;'><li>Documentación ya existente como el PDD/SDD anterior que quieras actualizar.</li><li>Transcripciones de entrevistas o reuniones relevantes.</li><li>Screenshots de sistemas, procesos o diagramas actuales.</li><li>Macros o codigo python que quieras incluir.</li></ul>", unsafe_allow_html=True)
    
    # BOTÓN AVANZAR
    col_center = st.columns([3,1,3])[1]
    with col_center:
        clicked = st.button("Avanzar paso", use_container_width=True, type="primary")
    if clicked:
        if not files:
            st.warning("Cargá al menos un archivo")
        else:
            st.session_state.processing = True
            st.empty()
            go_to("ai")
