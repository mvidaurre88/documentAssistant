import streamlit as st
from utils.navigation import go_to
from components.top_bar import top_bar

def screen_select_document():

    # BARRA DE NAVEGACION
    top_bar(title="Seleccione el tipo de documento", back_to="init", show_stepper=True, step=0)

    # ESTADO
    st.session_state.setdefault("doc_type", None)
    
    # BOTON TIPO DOCUMENTO
    col_center = st.columns([1,2,1])[1]
    types = {"📄 PDD": "PDD","📄 SDD": "SDD",}
    with col_center:
        doc_type = st.radio("Tipo de documento", list(types.keys()), horizontal=True, label_visibility="collapsed")
    st.session_state.doc_type = types[doc_type]

    # BOTÓN AVANZAR
    st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)

    col_center = st.columns([3,1,3])[1]

    with col_center:
        if st.button("Avanzar paso", use_container_width=True, type="primary"):
            go_to("load")