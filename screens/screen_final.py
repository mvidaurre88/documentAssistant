import streamlit as st
import os
from navigation import *
from components.top_bar import top_bar
from docx_generator import *

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
        )
        
    st.markdown("""
        ### ⚠️ Aclaraciones

        - Los diagramas generados son automáticos y pueden contener imprecisiones.  
        - Se recomienda utilizarlos como guía y validarlos antes de su uso final.
        """)
    
    
    
    