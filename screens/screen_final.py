# IMPORTS DE TERCEROS
import streamlit as st

# IMPORTS PROPIOS
from utils.navigation import go_to
from components.top_bar import top_bar
from docs import get_doc

def screen_final():
    
    # OBTENGO EL TIPO DE DOCUMENTO SELECCIONADO
    document = get_doc(st.session_state.doc_type)
    
    # BARRA DE NAVEGACION
    top_bar(title="", back_to="verify", show_stepper=True, step=4)

    col_center = st.columns([1, 11, 1])[1]
    with col_center:    
        st.success("Documento generado correctamente 🎉")
        render_clarifications(document.get_aclaraciones())
    
    _, col_1, col_2, _ = st.columns([1,5.5,5.5,1])
    with col_1:    
        if "doc_buffer" in st.session_state:
            st.download_button(
                label="Descargar documento",
                data=st.session_state.doc_buffer,
                file_name=document.get_filename(),
                mime=document.mime,
                use_container_width=True,
                type="primary",
            )
    with col_2:
        if st.button("Generar nuevo documento", use_container_width=True, type="secondary"):
            go_to("select")

def render_clarifications(items: list[str]) -> None:
    if not items:
        return
    clarifications = "".join(f"<li>{item}</li>" for item in items)
    st.markdown(f"""<div class="aclaraciones">
                    <h3>⚠️ Aclaraciones</h3>
                    <ul>{clarifications}</ul>
                    </div>""",
                    unsafe_allow_html=True)