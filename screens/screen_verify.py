import streamlit as st
import os
from datetime import date
import json
import re
from navigation import *
from components.top_bar import top_bar
from docx_generator import *
import traceback


def screen_verify():
    top_bar(title="Los datos generados son los siguientes", back_to="ai", show_stepper=True, step=3)

    raw = st.session_state.response
    if isinstance(raw, str):
        texto_limpio = re.sub(r"```json|```", "", raw).strip()
        texto_limpio = re.sub(r'\\(?!n)', r'\\\\', texto_limpio)
        data = json.loads(texto_limpio)
        data = add_current_date(data)
    else:
        data = raw

    if "form_data" not in st.session_state:
        st.session_state.form_data = data

    #Muestro segun el tipo de documento
    doc_type = st.session_state.doc_type
    if(doc_type == "PDD"):
        st.session_state.form_data = render_pdd(st.session_state.form_data)
    elif(doc_type == "SDD"):
        st.session_state.form_data = render_sdd(st.session_state.form_data)


    if st.button("Generar documento", use_container_width=True):
        try:
            sanitized = sanitize_none(st.session_state.form_data)
            generate_docx(json.dumps(sanitized), doc_type, st.session_state.mode)
            go_to("final")
        except Exception as e:
            st.error(f"Error al generar: {e}")
            st.code(traceback.format_exc())


def render_form(data, doc_type="", prefix=""):
    result = {}
    MULTILINE_THRESHOLD = 60

    for key, value in data.items():
        label_text = ""   # ← label legible
        field_key = f"field_{prefix}{key}"

        if value is None:
            value = ""

        if isinstance(value, str):
            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown(f"**{label_text}**")
            with col2:
                if len(value) > MULTILINE_THRESHOLD:
                    lines = (len(value) // 60) + value.count("\n") + 1
                    height = max(100, lines * 22)
                    result[key] = st.text_area("", value=value, key=field_key,
                                               label_visibility="collapsed", height=height)
                else:
                    result[key] = st.text_input("", value=value, key=field_key,
                                                label_visibility="collapsed")

        elif isinstance(value, (int, float)):
            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown(f"**{label_text}**")
            with col2:
                result[key] = st.number_input("", value=value, key=field_key,
                                              label_visibility="collapsed")

        elif isinstance(value, bool):
            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown(f"**{label_text}**")
            with col2:
                result[key] = st.checkbox("", value=value, key=field_key,
                                          label_visibility="collapsed")

        elif isinstance(value, list):
            if value and isinstance(value[0], dict):
                st.markdown(f"**{label_text}**")
                items = []
                for i, item in enumerate(value):
                    with st.expander(f"{label_text} [{i + 1}]", expanded=True):
                        items.append(render_form(item, doc_type=doc_type,
                                                 prefix=f"{prefix}{key}[{i}]."))
                result[key] = items
            else:
                items = []
                with st.expander(f"**{label_text}**", expanded=True):
                    for i, item in enumerate(value):
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            st.markdown(f"**{i + 1}**")
                        with col2:
                            items.append(st.text_input("", value=str(item),
                                                       key=f"{field_key}_{i}",
                                                       label_visibility="collapsed"))
                result[key] = items

        elif isinstance(value, dict):
            st.markdown(f"**{label_text}**")
            with st.expander(label_text, expanded=False):
                result[key] = render_form(value, doc_type=doc_type,
                                          prefix=f"{prefix}{key}.")
        else:
            result[key] = value

    return result  # las claves siguen siendo las del JSON original ✓

# Funcion para agregar la fecha actual
def add_current_date(json):
    today = date.today().strftime("%d/%m/%Y")
    json["fecha"] = today
    for field in ["modificaciones", "revision"]:
        if field in json and isinstance(json[field], list):
            for item in json[field]:
                if isinstance(item, dict):
                    item["fecha"] = today
    return json

# Funcion para sanitizar los valores None
def sanitize_none(data):
    if isinstance(data, dict):
        return {k: sanitize_none(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_none(i) for i in data]
    elif data is None:
        return ""
    return data

def render_pdd(data: dict) -> dict:
    result = {}
    
    # Codigo y Nombre del Bot
    col_left, col_right = st.columns([1,1])
    with col_left:
        field_row("Código del Bot", "codigoBot", data, result)
    with col_right:
        field_row("Nombre del Bot", "nombreBot", data, result)
    
    # Cliente y Desarrollador
    col_left, col_right = st.columns([1,1])
    with col_left:
        field_row("Cliente", "cliente", data, result)
    with col_right:
        field_row("Desarrollador", "desarrollador", data, result)
    
    # Versión y Fecha
    col_left, col_right = st.columns([1,1])
    with col_left:
        field_row("Versión", "version", data, result)
    with col_right:
        field_row("Fecha", "fecha", data, result)
        
    # Historial de Modificaciones
    st.markdown(f"<p style='margin: 0 0 6px 0;'><b>Historial de Modificaciones</b></p>", unsafe_allow_html=True)
    modificaciones_result = []
    for i, mod in enumerate(data.get("modificaciones", [])):
        with st.expander(f"Modificación {i + 1}", expanded=False):
            mod_result = {}
            
            col_left, col_right = st.columns([1, 1])
            with col_left:
                field_row("Versión", "version", mod, mod_result, key_prefix=f"mod{i}_")
            with col_right:
                field_row("Fecha", "fecha", mod, mod_result, key_prefix=f"mod{i}_")
        
            col_left, col_right = st.columns([1, 1])
            with col_left:
                field_row("Área o sector", "sector", mod, mod_result, key_prefix=f"mod{i}_")
            with col_right:
                field_row("Autor", "autor", mod, mod_result, key_prefix=f"mod{i}_")
            
            field_row("Motivo modificación", "motivo", mod, mod_result, multiline=True, height=150, key_prefix=f"mod{i}_")

            for key in mod:
                if key not in mod_result:
                    mod_result[key] = mod[key]
            
            modificaciones_result.append(mod_result)

    result["modificaciones"] = modificaciones_result

    # Historial de Revisión
    if data.get("revision"):
        st.markdown(f"<p style='margin: 0 0 6px 0;'><b>Historial de Revisión</b></p>", unsafe_allow_html=True)
        revisiones_result = []
        for i, mod in enumerate(data.get("revision", [])):
            with st.expander(f"Revisión {i + 1}", expanded=False):
                mod_result = {}
            
                # Versión y Aprobador    
                col_left, col_right = st.columns([1, 1])
                with col_left:
                    field_row("Versión", "version", mod, mod_result, key_prefix=f"mod{i}_")
                with col_right:
                    field_row("Aprobador", "aprobador", mod, mod_result, key_prefix=f"mod{i}_")
            
                # Comentarios
                field_row("Comentarios", "comentarios", mod, mod_result, multiline=True, height=150, key_prefix=f"mod{i}_")

                for key in mod:
                    if key not in mod_result:
                        mod_result[key] = mod[key]
            
                revisiones_result.append(mod_result)
        result["revision"] = revisiones_result

    # Proposito del Bot
    field_row("Objetivo del Bot", "propositoProceso", data, result, multiline=True, col_ratio=(1, 7))
    
    # Diagramas de Alto y Bajo Nivel
    #col_label1, col_img1, col_label2, col_img2 = st.columns([1, 3, 1, 3])
    #with col_label1:
    #    st.markdown("<p style='padding-top: 8px; margin: 0;'><b>Diagrama de Alto Nivel</b></p>", unsafe_allow_html=True)
    #with col_img1:
    #    preview_mermaid(data.get("diagramaAltoNivel"))
    #with col_label2:
    #    st.markdown("<p style='padding-top: 8px; margin: 0;'><b>Diagrama de Bajo Nivel</b></p>", unsafe_allow_html=True)
    #with col_img2:
    #    preview_mermaid(data.get("diagramaBajoNivel"))  

def field_row(label, key, data, result, col_ratio=None, multiline=False, height=None, key_prefix=""):
    ratio = col_ratio if col_ratio is not None else (1, 3)
    col1, col2 = st.columns(ratio)
    with col1:
        st.markdown(f"<p style='padding-top: 8px; margin: 0;'><b>{label}</b></p>", unsafe_allow_html=True)
    with col2:
        unique_key = f"field_{key_prefix}{key}" if key_prefix else f"field_{key}"
        value = data.get(key, "") or ""
        if multiline:
            if height is None:
                lines = (len(value) // 60) + value.count("\n") + 1
                height = max(100, lines * 22) + 5
            result[key] = st.text_area("", value=value,
                                        key=unique_key, label_visibility="collapsed", height=height)
        else:
            result[key] = st.text_input("", value=value,
                                         key=unique_key, label_visibility="collapsed")
            
def preview_mermaid(field, label=None):
    mermaidCode = field
    
    if not mermaidCode:
        return

    if label:
        st.markdown(f"<p style='margin: 0 0 6px 0;'><b>{label}</b></p>", unsafe_allow_html=True)
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            mmd_path = f"{tmpdir}/diagrama.mmd"
            png_path = f"{tmpdir}/diagrama.png"

            with open(mmd_path, "w", encoding="utf-8") as f:
                f.write('%%{init: {"theme": "neutral", "flowchart": {"curve": "stepAfter", "rankSpacing": 40}}}%%\n' + mermaidCode + "\nlinkStyle default stroke-width:4px;")

            subprocess.run(
                f"mmdc -i {mmd_path} -o {png_path} -w 1200 -H 600",
                shell=True, check=True
            )

            st.image(png_path, use_container_width=True)
    except Exception as e:
        st.warning(f"No se pudo generar el preview: {e}")