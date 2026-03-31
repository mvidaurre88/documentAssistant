import streamlit as st
from components.top_bar import top_bar
from navigation import *

def screen_load_files():
    
    # BARRA DE NAVEGACION
    top_bar(title="Ingrese archivos para analizar", back_to="select", show_stepper=True, step=1)

    # VERIFICO SI ES UN ARCHIVO NUEVO O SE BUSCA MODIFICAR UNO EXISTENTE
    if st.session_state.mode == "Modificar existente":     
        file = st.file_uploader("Subí acá el archivo a modificar o actualizar (PDD o SDD):", type=["pdf", "docx"], accept_multiple_files=False)
        st.session_state.file = file
        
    # CARGADOR DE ARCHIVOS
    files = st.file_uploader("Subí acá los demas archivos (screenshots, transcripciones, etc):", type=["pdf", "png", "txt", "docx"], accept_multiple_files=True)
    st.session_state.files = files

    print(st.session_state.doc_type)
    print(st.session_state.mode)

    col_center = st.columns([3,1,3])[1]

    with col_center:
        if st.button("Avanzar paso", use_container_width=True):
            if not files:
                st.warning("Cargá al menos un archivo")
            else:
                    go_to("ai")
