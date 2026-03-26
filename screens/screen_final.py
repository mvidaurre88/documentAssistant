import streamlit as st
import os
from navigation import *
from components.top_bar import top_bar
from docx_generator import *

# -- PASO 5 ----------------------------------------------------------------------------------------
def screen_final():
    
    top_bar(title="", back_to="verify", show_stepper=True, step=4)

    st.success("Documento generado correctamente 🎉")
    
    if "output_path" in st.session_state:
        path = st.session_state.output_path
        nombre_archivo = os.path.basename(path)

        with open(path, "rb") as f:
            st.download_button(
                label="⬇️ Descargar documento",
                data=f,
                file_name=nombre_archivo,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
    
    
    
    