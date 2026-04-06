import streamlit as st
import json, re, traceback, base64
from datetime import date
from utils.navigation import *
from components.top_bar import top_bar
from utils.docx_generator import *

def screen_verify():
    st.markdown("""
    <style>
        /* Espacio entre filas de campos */
        div[data-testid="stHorizontalBlock"] {
            margin-bottom: 8px;
        }
        
        /* Espacio entre expanders */
        div[data-testid="stExpander"] {
            margin-bottom: 10px;
        }
        
        /* Espacio interno de los expanders */
        div[data-testid="stExpander"] > div > div {
            padding-top: 8px;
        }

        /* Alinea verticalmente el label con el input */
        div[data-testid="stHorizontalBlock"] > div:first-child p {
            padding-top: 10px !important;
            margin: 0 !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    top_bar(title="Los datos generados son los siguientes", back_to="load", show_stepper=True, step=3)

    raw = st.session_state.response
    if isinstance(raw, str):
        texto_limpio = re.sub(r"```json|```", "", raw).strip()
        texto_limpio = re.sub(r'\\(?!n)', r'\\\\', texto_limpio)
        data = json.loads(texto_limpio)
        data = add_current_date(data)
        data = generate_modify(data)
    else:
        data = raw

    if "form_data" not in st.session_state:
        st.session_state.form_data = data

    #Muestro segun el tipo de documento
    doc_type = st.session_state.doc_type
    if(doc_type == "PDD"):
        render_pdd(st.session_state.form_data)
    elif(doc_type == "SDD"):
        render_sdd(st.session_state.form_data)

    col_center = st.columns([3,1,3])[1]
    with col_center:
        if st.button("Avanzar paso", key="btn_generar", type="primary"):
            try:
                sanitized = sanitize_none(st.session_state.form_data)
                generate_docx(sanitized, doc_type, st.session_state.mode)
                go_to("final")
            except Exception as e:
                st.error(f"Error al generar: {e}")
                st.code(traceback.format_exc())

# FUNCION PARA RENDERIZAR EL PDD ----------------------------------------------------------------------
def render_pdd(data: dict) -> dict:
    
    for field in ["entradas", "salidas", "contactos"]:
        key = f"list_{field}"
        if key not in st.session_state:
            st.session_state[key] = st.session_state.form_data.get(field, [])
    
    # RENDERIZO LOS CAMPOS COMUNES ENTRE PDD Y SDD -----------------------------------------------------
    render_common_fields(data)

    # PROPOSITO DEL BOT --------------------------------------------------------------------------------
    field_row("Objetivo del Bot", "propositoProceso", data, multiline=True, col_ratio=(1, 6.5))
      
    # INPUTS -------------------------------------------------------------------------------------------
    st.markdown("<p style='margin: 0 0 25px 0;'><b>Archivos Input</b></p>", unsafe_allow_html=True)
    with st.expander("Entradas", expanded=False):
        to_delete = None
        for i, entrada in enumerate(st.session_state.list_entradas):
            col_field, col_btn = st.columns([6, 1])
            with col_field:
                st.session_state.list_entradas[i] = st.text_input(f"Entrada {i + 1}", value=entrada, key=f"entrada_{i}_input", label_visibility="collapsed")
            with col_btn:
                if st.button("✕", key=f"del_entrada_{i}", type="secondary"):
                    to_delete = i
        if to_delete is not None:
            st.session_state.list_entradas.pop(to_delete)
            st.rerun()
        if st.button("+ Agregar entrada", key="add_entrada", type="secondary"):
            st.session_state.list_entradas.append("")
            st.rerun()
    data["entradas"] = st.session_state.list_entradas
    
    # SALIDAS ------------------------------------------------------------------------------------------
    st.markdown("<p style='margin: 0 0 25px 0;'><b>Archivos Output</b></p>", unsafe_allow_html=True)
    with st.expander("Salidas", expanded=False):
        to_delete = None
        for i, salida in enumerate(st.session_state.list_salidas):
            col_field, col_btn = st.columns([6, 1])
            with col_field:
                st.session_state.list_salidas[i] = st.text_input(
                    f"Salida {i + 1}", value=salida,
                    key=f"salida_{i}_input", label_visibility="collapsed"
                )
            with col_btn:
                if st.button("✕", key=f"del_salida_{i}"):
                    to_delete = i
        if to_delete is not None:
            st.session_state.list_salidas.pop(to_delete)
            st.rerun()
        if st.button("+ Agregar salida", key="add_salida"):
            st.session_state.list_salidas.append("")
            st.rerun()
    data["salidas"] = st.session_state.list_salidas
    
    # CARPETAS -----------------------------------------------------------------------------------------
    field_row("Ruta Compartida", "carpetaCompartida", data, col_ratio=(1, 6.5))
    field_row("Ruta Output", "carpetaOutput", data, col_ratio=(1, 6.5))
    field_row("Ruta Input", "carpetaInput", data, col_ratio=(1, 6.5))
    
    # CONTACTOS ----------------------------------------------------------------------------------------
    st.markdown("<p style='margin: 0 0 25px 0;'><b>Contactos</b></p>", unsafe_allow_html=True)
    with st.expander("Contactos", expanded=False):
        to_delete = None
        for i, contacto in enumerate(st.session_state.list_contactos):
            col_field, col_btn = st.columns([6, 1])
            with col_field:
                st.session_state.list_contactos[i] = st.text_input(
                    f"Contacto {i + 1}", value=contacto,
                    key=f"contacto_{i}_input", label_visibility="collapsed"
                )
            with col_btn:
                if st.button("✕", key=f"del_contacto_{i}"):
                    to_delete = i
        if to_delete is not None:
            st.session_state.list_contactos.pop(to_delete)
            st.rerun()
        if st.button("+ Agregar contacto", key="add_contacto"):
            st.session_state.list_contactos.append("")
            st.rerun()

    data["contactos"] = st.session_state.list_contactos

    # FORMA DE EJECUCION -------------------------------------------------------------------------------
    field_row("Forma de Ejecución", "ejecucion", data, multiline=True, col_ratio=(1, 6.5))
    
    # FASES --------------------------------------------------------------------------------------------
    st.markdown("<p style='margin: 0 0 25px 0;'><b>Ejecución paso a paso</b></p>", unsafe_allow_html=True)
    fases = data.get("fases", [])
    for i, fase in enumerate(fases):
        with st.expander(f"Fase {i + 1} - {fase.get('tituloFase', '')}", expanded=False):
            pasos = fase.get("pasos", [])
            for j, paso in enumerate(pasos):
                with st.expander(f"Paso {j + 1} - {paso.get('accion', '')}", expanded=True):
                    field_row("Detalle", "detalle", paso, key_prefix=f"fase_{i}_paso_{j}_", multiline=True, col_ratio=(1, 7))
                    field_row("Excepción", "excepcion_escenario", paso, key_prefix=f"fase_{i}_paso_{j}_", col_ratio=(1, 7))

    # EXCEPCIONES ---------------------------------------------------------------------------------------
    st.markdown("<p style='margin: 0 0 25px 0;'><b>Excepciones</b></p>", unsafe_allow_html=True)
    for i, excepcion in enumerate(data.get("excepciones", [])):
        with st.expander(f"Excepción {i + 1} - {excepcion.get('escenario', '')}", expanded=False):
            double_field_row("Numero", "numero", "Tipo", "tipo", excepcion, key_prefix=f"excepcion_{i}_")
            field_row("Descripción", "accion", excepcion, key_prefix=f"excepcion_{i}_", multiline=True, col_ratio=(1, 6.5))
    
    # DIAGRAMAS -----------------------------------------------------------------------------------------
    col_1, col_2, col_3, col_4 = st.columns([2, 2, 2, 2])
    
    with col_1:
        st.markdown("<p style='padding-top: 8px; margin: 0;'><b>Diagrama de Alto Nivel</b></p>", unsafe_allow_html=True)
    with col_2:
        img_bytes = st.session_state.get("diagramaAltoNivel")
        if(img_bytes):
            show_img(img_bytes)
    with col_3:
        st.markdown("<p style='padding-top: 8px; margin: 0;'><b>Diagrama de Bajo Nivel</b></p>", unsafe_allow_html=True)
    with col_4:
        img_bytes = st.session_state.get("diagramaBajoNivel")
        if(img_bytes):
            show_img(img_bytes)

# FUNCION PARA RENDERIZAR EL SDD ----------------------------------------------------------------------
def render_sdd(data: dict) -> dict:
    
    # RENDERIZO LOS CAMPOS COMUNES ENTRE PDD Y SDD -----------------------------------------------------
    render_common_fields(data)
    
    # PROPOSITO DEL BOT --------------------------------------------------------------------------------
    field_row("Objetivo del Bot", "procesoNegocioAltoNivel", data, multiline=True, col_ratio=(1, 6.5))
    
    # SOLUCION TECNICA ALTO NIVEL ----------------------------------------------------------------------
    

# FUNCION PARA ESTANDARIZAR FILAS DE DOS CAMPOS -------------------------------------------------------
def double_field_row(label1, key1, label2, key2, data, key_prefix=""):
    col_left, col_right = st.columns([1, 1])
    with col_left:
        field_row(label1, key1, data, key_prefix=key_prefix)
    with col_right:
        field_row(label2, key2, data, key_prefix=key_prefix)
        
# FUNCION PARA ESTANDARIZAR FILAS DE UN SOLO CAMPO ----------------------------------------------------
def field_row(label, key, data, col_ratio=None, multiline=False, height=None, key_prefix=""):
    ratio = col_ratio if col_ratio is not None else (1, 2.5)
    if data is None:
        data = {}
    value = data.get(key, "") or ""
    col1, col2 = st.columns(ratio)
    with col1:
        st.markdown(f"<p style='padding-top: 8px; margin: 0;'><b>{label}</b></p>", unsafe_allow_html=True)
    with col2:
        unique_key = f"field_{key_prefix}{key}" if key_prefix else f"field_{key}"
        if multiline:
            if height is None:
                lines = (len(value) // 60) + value.count("\n") + 1
                height = max(100, lines * 22) + 5
            data[key] = st.text_area("", value=value, key=unique_key, label_visibility="collapsed", height=height)
        else:
            data[key] = st.text_input("", value=value, key=unique_key, label_visibility="collapsed")
        return data[key]  

# FUNCION PARA AGREGAR LA FECHA ACTUAL -----------------------------------------------------------------
def add_current_date(json):
    today = date.today().strftime("%d/%m/%Y")
    json["fecha"] = today
    for field in ["modificaciones", "revision"]:
        if field in json and isinstance(json[field], list):
            for item in json[field]:
                if isinstance(item, dict):
                    item["fecha"] = today
    return json
            
# FUNCION PARA REEMPLAZAR LOS VALORES NONE POR STRING VACIOS -------------------------------------------
def sanitize_none(data):
    if isinstance(data, dict):
        return {k: sanitize_none(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_none(i) for i in data]
    elif data is None:
        return ""
    return data

# FUNCION PARA MOSTRAR DIAGRAMA ------------------------------------------------------------------------
def show_img(img_bytes):
    if not img_bytes:
        return

    img_base64 = base64.b64encode(img_bytes).decode()

    html = f"""
    <div class="img-container">
        <img src="data:image/png;base64,{img_base64}" />
    </div>

    <style>
    .img-container {{
        display: flex;
        justify-content: center;
        align-items: center;
        overflow: visible;
    }}

    .img-container img {{
        width: 250px;
        border-radius: 12px;
        border: 10px solid white;
        box-shadow: -8px 8px 15px rgba(0,0,0,0.25);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        cursor: pointer;
        transform-origin: right center
        margin-bottom: 20px;
    }}

    .img-container img:hover {{
        transform: scale(2);
        box-shadow: -12px 12px 25px rgba(0,0,0,0.35);
        position: relative;
        z-index: 999;
    }}
    </style>
    """

    st.markdown(html, unsafe_allow_html=True)

# FUNCION PARA GENERAR LA SECCION DE MODIFICACIONES ----------------------------------------------------      
def generate_modify(data):
    modificaciones = data.get("modificaciones", [])
    fecha = data.get("fecha", "")
    desarrollador = data.get("desarrollador", "")
    
    if modificaciones == []:
        new_version = "0.0"
        modificaciones.append({ "version": "0.0", "fecha": fecha, "paginas": "todas", "sector": "RPA", "autor": desarrollador, "motivo": "Creación de documento"})
    else:
        last_mod = modificaciones[-1]
        new_version = str(float(last_mod.get('version', '0.0')) + 1)
        modificaciones.append({ "version": new_version, "fecha": fecha, "paginas": "todas", "sector": "RPA", "autor": desarrollador, "motivo": "Actualización de documento"})    
    
    data["version"] = new_version
    data["modificaciones"] = modificaciones
    return data

# FUNCION PARA RENDERIZAR LOS CAMPOS COMUNES ENTRE PDD Y SDD -------------------------------------------
def render_common_fields(data):
    # CODIGO Y NOMBRE DEL BOT --------------------------------------------------------------------------
    double_field_row("Código del Bot", "codigoBot", "Nombre del Bot", "nombreBot", data)

    # CLIENTE Y DESARROLLADOR --------------------------------------------------------------------------
    double_field_row("Cliente", "cliente", "Desarrollador", "desarrollador", data)
    
    # VERSION Y FECHA ----------------------------------------------------------------------------------
    double_field_row("Versión", "version", "Fecha", "fecha", data)
    
    # MODIFICACIÓN ACTUAL ------------------------------------------------------------------------------
    st.markdown(f"<p style='margin: 0 0 25px 0;'><b>Modificación Actual</b></p>", unsafe_allow_html=True)
    modificaciones = data.get("modificaciones", [])
    if modificaciones:
        with st.expander(f"Modificación", expanded=True):
            double_field_row("Versión", "version", "Fecha", "fecha", modificaciones[-1], key_prefix="mod_last_")
            double_field_row("Sector", "sector", "Autor", "autor", modificaciones[-1], key_prefix="mod_last_")
            field_row("Motivo modificación", "motivo", modificaciones[-1], multiline=True, key_prefix="mod_last_")