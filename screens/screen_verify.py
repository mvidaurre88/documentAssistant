import streamlit as st
import os
from datetime import date
import json
from navigation import *
from components.top_bar import top_bar
from docx_generator import *

# -- PASO 4 ----------------------------------------------------------------------------------------
def screen_verify():
    top_bar(title="Verifique los datos generados", back_to="ai", show_stepper=True, step=3)

    import re

    # Limpiar el JSON si viene con ```json ... ```
    raw = st.session_state.response
    if isinstance(raw, str):
        texto_limpio = re.sub(r"```json|```", "", raw).strip()
        data = json.loads(texto_limpio)
        data = fix_fechas(data)
    else:
        data = raw

    # Guardar el data editable en session_state
    if "form_data" not in st.session_state:
        st.session_state.form_data = data

    # Renderizar el formulario dinámico
    st.session_state.form_data = render_form(st.session_state.form_data)

    if st.button("Generar documento", use_container_width=True):
        try:
            generate_docx(json.dumps(st.session_state.form_data), st.session_state.doc_type, st.session_state.mode)
            go_to("final")
        except Exception as e:
            st.error(f"Error al generar: {e}")


def render_form(data, prefix=""):
    result = {}

    for key, value in data.items():
        label = f"{prefix}{key}"
        field_key = f"field_{label}"

        MULTILINE_THRESHOLD = 60  # caracteres

        if isinstance(value, str):
            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown(f"**{key}**")
            with col2:
                if len(value) > MULTILINE_THRESHOLD:
                    lines = (len(value) // 60) + value.count("\n") + 1  # estima líneas
                    height = max(100, lines * 22)  # mínimo 100px, ~25px por línea
                    result[key] = st.text_area("", value=value, key=field_key, label_visibility="collapsed", height=height)
                else:
                    result[key] = st.text_input("", value=value, key=field_key, label_visibility="collapsed")

        elif isinstance(value, (int, float)):
            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown(f"**{key}**")
            with col2:
                result[key] = st.number_input("", value=value, key=field_key, label_visibility="collapsed")

        elif isinstance(value, bool):
            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown(f"**{key}**")
            with col2:
                result[key] = st.checkbox("", value=value, key=field_key, label_visibility="collapsed")

        elif isinstance(value, list):
            if value and isinstance(value[0], dict):
                st.markdown(f"**{key}**")
                items = []
                for i, item in enumerate(value):
                    with st.expander(f"{key} [{i + 1}]", expanded=True):
                        items.append(render_form(item, prefix=f"{label}[{i}]."))
                result[key] = items

            # Lista simple → expander con inputs numerados adentro
            else:
                items = []
                with st.expander(f"**{key}**", expanded=True):
                    for i, item in enumerate(value):
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            st.markdown(f"**{i + 1}**")
                        with col2:
                            items.append(st.text_input("", value=str(item), key=f"{field_key}_{i}", label_visibility="collapsed"))
                result[key] = items
                
        elif isinstance(value, dict):
            st.markdown(f"**{label}**")
            with st.expander(label):
                result[key] = render_form(value, prefix=f"{label}.")

        else:
            result[key] = value

    return result


def fix_fechas(data: dict) -> dict:
    hoy = date.today().strftime("%d/%m/%Y")

    def _recorrer(obj):
        if isinstance(obj, dict):
            for key in obj:
                if "fecha" in key.lower():
                    obj[key] = hoy
                else:
                    _recorrer(obj[key])
        elif isinstance(obj, list):
            for item in obj:
                _recorrer(item)

    _recorrer(data)
    return data