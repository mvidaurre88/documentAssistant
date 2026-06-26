# IMPORTS DE PYTHON
import traceback
import logging

# IMPORTS DE TERCEROS
import streamlit as st

# IMPORTS PROPIOS
from utils.navigation import *
from utils.docx_generator import *
from components.top_bar import top_bar
from components.section_title import section_title

logger = logging.getLogger(__name__)

def screen_verify():
    
    # BARRA DE NAVEGACIÓN
    top_bar(title="", back_to="load", show_stepper=True, step=3)
    
    #col1, col2 = st.columns([4, 1])
    #with col2:
    #    with st.container(key="css_injector_verify"):
    #        st.write("alalallala")
    #
    #with col1:
    with st.columns([1,9,1])[1]:
        # TITULO
        section_title("Revisá y editá los datos antes de generar el documento final", left=True)

        # CARGO LA RESPUESTA COMO JSON
        data = st.session_state.get("response", None)
        if data is None:
            st.error("Ocurrió un error al cargar la respuesta de la IA")
            logger.error("No se encontró 'response' en session_state al cargar screen_verify")
            st.stop()

        # RENDERIZO LOS CAMPOS SEGUN EL TIPO DE DOCUMENTO
        document = get_doc(st.session_state.doc_type)
        if document:
            document.render_form(st.session_state.response)

        # BOTÓN PARA AVANZAR
        col_center = st.columns([3,1.5,3])[1]
        with col_center:
            if st.button("Avanzar paso", key="btn_generar", type="primary"):
                try:
                    sanitized = sanitize(st.session_state.response)
                    generate_docx(sanitized, None)
                    go_to("final")
                except Exception as e:
                    st.error(f"Error al generar: {e}")
                    logger.error(f"Error al generar documento: {e}\n{traceback.format_exc()}")
                    st.code(traceback.format_exc())

LIST_OF_STRINGS_FIELDS = {
    "entradas", "salidas", "contactos", "requisitos", "inputsProceso"
}

# REEMPLAZA LOS VALORES NONE POR STRING VACIOS
def sanitize(data):
    if isinstance(data, dict):
        for field in LIST_OF_STRINGS_FIELDS:
            if field in data and isinstance(data[field], list):
                data[field] = denormalize_list_field(data[field])
        return {k: sanitize(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize(i) for i in data]
    return data

def denormalize_list_field(items):
    """Convierte [{"value": x, "_id": ...}, ...] a [x, ...]"""
    return [item["value"] if isinstance(item, dict) else item for item in items]