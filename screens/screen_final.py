import streamlit as st
import os
from utils.navigation import *
from components.top_bar import top_bar
from utils.docx_generator import *

# -- PASO 5 ----------------------------------------------------------------------------------------
def screen_final():
    
    top_bar(title="", back_to="verify", show_stepper=True, step=4)

    st.success("Documento generado correctamente 🎉")
    
    if "doc_buffer" in st.session_state:
        st.download_button(
            label="⬇️ Descargar documento",
            data=st.session_state.doc_buffer,
            file_name="output.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
            type="primary"
        )
        
    if(st.session_state.doc_type == "PDD"):
        st.markdown("""
            ### ⚠️ Aclaraciones
            - Diagramas: Son generados y pueden contener imprecisiones. Utilicelos como guía y validelos antes de su uso final.
            - Pasos: Son poco exhaustivos y no contienen imágenes. Se recomienda completarlos con información adicional.
            - Notificaciones: Se mantienen las del template. Ajustarlas según corresponda junto con los criterios de aceptación.
            """)
    elif(st.session_state.doc_type == "SDD"):
        st.markdown("""
            ### ⚠️ Aclaraciones
            - Diagramas: son generados y pueden contener imprecisiones. Utilicelos como guía y validelos antes de su uso final.
            """)
    