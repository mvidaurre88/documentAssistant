import streamlit as st
from navigation import go_to
from components.top_bar import top_bar

def screen_select_document():

    # BARRA DE NAVEGACION
    top_bar(back_to="init", show_stepper=True, step=0)

    # ESTADO
    st.session_state.setdefault("doc_type", None)
    st.session_state.setdefault("mode", None)

    # TITULO 1
    st.markdown("<h3 style='text-align:center;'>Seleccione el tipo de documento</h3>", unsafe_allow_html=True)
    
    # BOTON TIPO DOCUMENTO
    col_center = st.columns([1,2,1])[1]
    types = {"📄 PDD": "PDD","📄 SDD": "SDD",}
    with col_center:
        doc_type = st.radio("Tipo de documento", list(types.keys()), horizontal=True, label_visibility="collapsed")
    

    # TITULO 2
    st.markdown("<h3 style='text-align:center; margin-top: 10px;'>¿Qué desea hacer?</h3>", unsafe_allow_html=True)
    
    # BOTON MODO
    col_center = st.columns([1,2,1])[1]
    modes = {"Generar nuevo documento": "new","Modificar existente": "modify",}
    with col_center:
        mode = st.radio("modo", list(modes.keys()), horizontal=True, label_visibility="collapsed")

    st.session_state.doc_type = types[doc_type]
    st.session_state.mode = modes[mode]

    # BOTÓN AVANZAR
    st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)

    col_center = st.columns([3,1,3])[1]

    with col_center:
        if st.button("Avanzar paso", use_container_width=True):
            go_to("load")