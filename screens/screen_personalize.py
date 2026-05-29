import streamlit as st
from components.top_bar import top_bar
from utils.navigation import *
from components.section_title import section_title
from docs import get_doc

# PANTALLA PERSONALIZACION
def screen_personalize():
    
    container = st.empty()
    with container.container():

        # BARRA DE NAVEGACION
        top_bar(title="", back_to="load", show_stepper=True, step=1)
        
        # PERSONALIZACIÓN
        document = get_doc(st.session_state.doc_type)
        if document:
            with st.columns([1, 1.5, 1])[1]:
                section_title("¿Qué información querés generar?", left=True)
                with st.container(key="personalizacion_container"):
                    document.get_personalization()
                    
        # BOTÓN AVANZAR
        with st.columns([3,1,3])[1]:
            clicked = st.button("Avanzar paso", use_container_width=True, type="primary")
    
    if clicked:
        container.empty()
        go_to("ai")