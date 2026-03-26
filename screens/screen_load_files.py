import streamlit as st
from components.top_bar import top_bar
from navigation import *

def screen_load_files():
    
    top_bar(title="Ingrese los archivos", back_to="select", show_stepper=True, step=1)

    st.markdown("<p style='text-align:center; color:#ccc;'>Screenshots, PDFs, textos, etc.</p>", unsafe_allow_html=True)

    files = st.file_uploader(
        "Subir archivos",
        accept_multiple_files=True
    )

    if files:
        st.markdown("### 📂 Archivos cargados")

        cols = st.columns(4)
        for i, f in enumerate(files):
            with cols[i % 4]:
                st.markdown(f"""
                <div class="card">
                    📄<br>
                    <small>{f.name}</small>
                </div>
                """, unsafe_allow_html=True)

        st.session_state.files = files

    if st.button("Avanzar paso"):
        if not files:
            st.warning("Cargá al menos un archivo")
        else:
            go_to("ai")