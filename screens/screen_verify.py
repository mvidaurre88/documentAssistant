import json5, re, traceback, base64, streamlit as st
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
        texto_limpio = raw
        try:
            data = json5.loads(texto_limpio)
        except Exception as e:
            error_msg = str(e)
            print(f"[ERROR] Fallo al parsear JSON: {error_msg}")

            match = re.search(r'line (\d+) column (\d+) \(char (\d+)\)', error_msg)
            if match:
                line_num = int(match.group(1))
                col_num  = int(match.group(2))
                char_pos = int(match.group(3))
                lines    = texto_limpio.splitlines()

                context_start = max(0, line_num - 3)
                context_end   = min(len(lines), line_num + 2)

                print(f"[ERROR] Posición: línea {line_num}, columna {col_num} (char {char_pos})")
                print(f"[ERROR] Contexto:")
                for i, l in enumerate(lines[context_start:context_end], start=context_start + 1):
                    marker = " >>> " if i == line_num else "     "
                    print(f"{marker}línea {i:4d}: {l}")

                if 0 < line_num <= len(lines):
                    broken_line = lines[line_num - 1]
                    snippet     = broken_line[max(0, col_num - 20):col_num + 20]
                    print(f"[ERROR] Fragmento exacto (~40 chars): ...{snippet}...")

            st.error(f"Error al parsear la respuesta. Revisá los logs.\n\n`{error_msg}`")
            st.stop()

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
                generate_docx(sanitized, doc_type, None)
                go_to("final")
            except Exception as e:
                st.error(f"Error al generar: {e}")
                st.code(traceback.format_exc())
    
# FUNCION PARA RENDERIZAR EL PDD ----------------------------------------------------------------------
def render_pdd(data: dict) -> dict:
    
    for field in ["entradas", "salidas", "contactos"]:
        key = f"list_{field}"
        counter_key = f"{field}_counter"
        if key not in st.session_state:
            raw = st.session_state.form_data.get(field, [])
            st.session_state[key] = [
                {"_id": j, **item} if isinstance(item, dict)
                else {"_id": j, "value": str(item)}
                for j, item in enumerate(raw)
            ]
            st.session_state[counter_key] = len(st.session_state[key])
    
    key = "list_fases"
    if key not in st.session_state:
        raw = st.session_state.form_data.get("fases", [])
        items = []
        for j, item in enumerate(raw):
            if not isinstance(item, dict):
                item = {"tituloFase": str(item), "pasos": []}

            pasos_raw = item.get("pasos", [])
            if not isinstance(pasos_raw, list):
                pasos_raw = []
            pasos = []
            for p, paso in enumerate(pasos_raw):
                if not isinstance(paso, dict):
                    paso = {
                        "accion": str(paso),
                        "detalle": "",
                        "excepciones": ""
                    }
                paso_normalizado = {
                    "_id": f"{j}_{p}",
                    "accion": paso.get("accion", ""),
                    "detalle": paso.get("detalle", ""),
                    "excepciones": paso.get("excepciones", "")
                }
                pasos.append(paso_normalizado)
            item["pasos"] = pasos
            item["_id"] = j

            # FIX 1: Inicializar la key de session_state que usa _render_inline_list
            sublist_key = f"list_fases_{j}_pasos"
            if sublist_key not in st.session_state:
                st.session_state[sublist_key] = pasos
                st.session_state[f"{sublist_key}_counter"] = len(pasos)

            st.session_state[f"fases_{j}_pasos_counter"] = len(pasos)
            items.append(item)
        st.session_state[key] = items
    st.session_state["fases_counter"] = len(st.session_state[key])
    
    key = "list_excepciones"
    if key not in st.session_state:
        raw = st.session_state.form_data.get("excepciones", [])
        items = []
        for j, item in enumerate(raw):
            if not isinstance(item, dict):
                item = {"escenario": str(item), "numero": "", "tipo": "", "accion": ""}
            item["_id"] = j
            items.append(item)
        st.session_state[key] = items
    st.session_state["excepciones_counter"] = len(st.session_state[key])
    
    # RENDERIZO LOS CAMPOS COMUNES ENTRE PDD Y SDD -----------------------------------------------------
    render_common_fields(data)

    # PROPOSITO DEL BOT --------------------------------------------------------------------------------
    field_row("Objetivo del Bot", "propositoProceso", data, multiline=True, col_ratio=(1, 6.5))
      
    # INPUTS -------------------------------------------------------------------------------------------
    data["entradas"]  = list_text_input_section("Archivos Input", "entradas", "Entrada")
    
    # SALIDAS ------------------------------------------------------------------------------------------
    data["salidas"] = list_text_input_section("Archivos Output", "salidas", "Salida")
    
    # CARPETAS -----------------------------------------------------------------------------------------
    field_row("Ruta Compartida", "carpetaCompartida", data, col_ratio=(1, 6.5))
    field_row("Ruta Output", "carpetaOutput", data, col_ratio=(1, 6.5))
    field_row("Ruta Input", "carpetaInput", data, col_ratio=(1, 6.5))
    
    # CONTACTOS ----------------------------------------------------------------------------------------
    data["contactos"] = list_text_input_section("Contactos", "contactos", "Contacto")

    # FORMA DE EJECUCION -------------------------------------------------------------------------------
    field_row("Forma de Ejecución", "ejecucion", data, multiline=True, col_ratio=(1, 6.5))
    
    # FASES --------------------------------------------------------------------------------------------
    data["fases"] = list_dict_section(
        "Fases del Proceso", "fases", "Fases", "Fase",
        fields_config=[
            {"label": "Título de fase", "key": "tituloFase"},
            {
                "label": "Pasos de la fase",
                "key": "pasos",
                "type": "list",
                # FIX 3: definir los subfields para que _render_inline_list
                # sepa qué campos renderizar en cada paso
                "subfields": [
                    {"label": "Acción", "key": "accion"},
                    {"label": "Detalle", "key": "detalle", "multiline": True},
                    {"label": "Excepción / Escenario", "key": "excepciones", "multiline": True},
                ]
            }
        ],
        empty_item={"tituloFase": "", "pasos": []}
    )

    # EXCEPCIONES ---------------------------------------------------------------------------------------
    data["excepciones"] = list_dict_section(
        "Excepciones", "excepciones", "Excepciones", "Excepción",
        fields_config=[
            {"label": "Escenario de excepción", "key": "escenario"},
            {"label": "Tipo de excepción", "key": "tipo"},
            {"label": "Acción a tomar", "key": "accion", "multiline": True}
        ],
        empty_item={"escenario": "", "tipo": "", "accion": ""}
    )
    
    # DIAGRAMAS -----------------------------------------------------------------------------------------
    col_1, col_2, col_3, col_4 = st.columns([3, 1, 2, 2])
    with col_1:
        st.markdown("**Diagrama de Alto Nivel**")
    with col_2:
        img_bytes = st.session_state.get("diagramaAltoNivel", None)
        if img_bytes:
            show_img_overlay(img_bytes, key="alto_nivel")
    col_1, col_2, col_3, col_4 = st.columns([3, 1, 2, 2])
    with col_1:
        st.markdown("**Diagrama de Bajo Nivel**")
    with col_2:
        img_bytes = st.session_state.get("diagramaBajoNivel", None)
        if img_bytes:
            show_img_overlay(img_bytes, key="bajo_nivel")
        
# FUNCION PARA RENDERIZAR EL SDD ----------------------------------------------------------------------
def render_sdd(data: dict) -> dict:
    
    key = f"list_solucionTecnicaAltoNivel"
    if key not in st.session_state:
        raw = st.session_state.form_data.get("solucionTecnicaAltoNivel", [])
        st.session_state[key] = [{"_id": j,**(item if isinstance(item, dict) else {"nombreTarea": str(item), "descripcionTarea": ""})} for j, item in enumerate(raw)]
    st.session_state[f"solucionTecnicaAltoNivel_counter"] = len(st.session_state[key])
       
    key = "list_solucionTecnicaDetallada"
    if key not in st.session_state:
        raw = st.session_state.form_data.get("solucionTecnicaDetallada", [])
        items = []
        for j, item in enumerate(raw):
            if not isinstance(item, dict):
                item = {"nombreTarea": str(item), "descripcionExacta": "", "excepciones": []}
            
            # Normalizar excepciones con _id únicos globales
            exc_raw = item.get("excepciones", [])
            if not isinstance(exc_raw, list):
                exc_raw = []
            item["excepciones"] = [
                {
                "_id": f"{j}_{e}",
                "value": v if isinstance(v, str) else v.get("value", v.get("evento", ""))
                }
                for e, v in enumerate(exc_raw)
            ]
            item["_id"] = j
            st.session_state[f"solucionTecnicaDetallada_{j}_excepciones_counter"] = len(item["excepciones"])

            # Inicializar la key de session_state para la sublista de excepciones
            sublist_key = f"list_solucionTecnicaDetallada_{j}_excepciones"
            if sublist_key not in st.session_state:
                st.session_state[sublist_key] = item["excepciones"]
                st.session_state[f"{sublist_key}_counter"] = len(item["excepciones"])

            items.append(item)
        
        st.session_state[key] = items
    st.session_state["solucionTecnicaDetallada_counter"] = len(st.session_state[key])
    
    key="list_excepciones"
    if key not in st.session_state:
        raw = st.session_state.form_data.get("excepciones", [])
        items = []
        for j, item in enumerate(raw):
            if not isinstance(item, dict):
                item = {"evento": str(item), "detalle": "", "accion": "", "responsable": ""}
            item["_id"] = j
            items.append(item)
        st.session_state[key] = items
    st.session_state["excepciones_counter"] = len(st.session_state[key])
    
    key="list_aplicaciones"
    if key not in st.session_state:
        raw = st.session_state.form_data.get("aplicaciones", [])
        items = []
        for j, item in enumerate(raw):
            if not isinstance(item, dict):
                item = {"nombre": str(item), "version": "", "comentarios": ""}
            item["_id"] = j
            items.append(item)
        st.session_state[key] = items
    st.session_state["aplicaciones_counter"] = len(st.session_state[key])

    key="list_archivos"
    if key not in st.session_state:
        raw = st.session_state.form_data.get("archivos", [])
        items = []
        for j, item in enumerate(raw):
            if not isinstance(item, dict):
                item = {"nombre": str(item), "comentarios": "", "nomenclatura": ""}
            item["_id"] = j
            items.append(item)
        st.session_state[key] = items
    st.session_state["archivos_counter"] = len(st.session_state[key])
    
    key="list_requisitos"
    if key not in st.session_state:
        raw = st.session_state.form_data.get("requisitos", [])
        st.session_state[key] = [{"_id": j, "value": str(item)} for j, item in enumerate(raw)]
    st.session_state["requisitos_counter"] = len(st.session_state[key])
    
    # RENDERIZO LOS CAMPOS COMUNES ENTRE PDD Y SDD -----------------------------------------------------
    render_common_fields(data)
    
    # PROPOSITO DEL BOT --------------------------------------------------------------------------------
    field_row("Objetivo del Bot", "procesoNegocioAltoNivel", data, multiline=True, col_ratio=(1, 6.5))
    
    # SOLUCION TECNICA ALTO NIVEL ----------------------------------------------------------------------
    data["solucionTecnicaAltoNivel"] = list_dict_section(
        "Solucion Técnica de Alto Nivel", "solucionTecnicaAltoNivel", "Tareas", "Tarea",
        fields_config=[
            {"label": "Nombre de tarea", "key": "nombreTarea"},
            {"label": "Descripción de tarea", "key": "descripcionTarea", "multiline": True}
        ],
        empty_item={"nombreTarea": "", "descripcionTarea": ""}
    )
    
    # SOLUCION TECNICA DETALLADA ----------------------------------------------------------------------
    data["solucionTecnicaDetallada"] = list_dict_section(
        "Solución Técnica Detallada", "solucionTecnicaDetallada", "Tareas", "Tarea",
        fields_config=[
            {"label": "Nombre de tarea", "key": "nombreTarea"},
            {"label": "Descripción exacta de tarea", "key": "descripcionExacta", "multiline": True},
            {"label": "Excepciones", "key": "excepciones", "type": "list"}
        ],
        empty_item={"nombreTarea": "", "descripcionExacta": "", "excepciones": []}
    )
    
    # EXCEPCIONES ---------------------------------------------------------------------------------------
    data["excepciones"] = list_dict_section(
        "Excepciones", "excepciones", "Excepciones", "Excepción",
        fields_config=[
            {"label": "Evento", "key": "evento"},
            {"label": "Detalle", "key": "detalle", "multiline": True},
            {"label": "Acción", "key": "accion", "multiline": True},
            {"label": "Responsable", "key": "responsable"}
        ],
        empty_item={"evento": "", "detalle": "", "accion": "", "responsable": ""}
    )
    
    # APLICACIONES ---------------------------------------------------------------------------------------
    data["aplicaciones"] = list_dict_section(
        "Aplicaciones", "aplicaciones", "Aplicaciones", "Aplicación",
        fields_config=[
            {"label": "Nombre", "key": "nombre"},
            {"label": "Version", "key": "version"},
            {"label": "Comentarios", "key": "comentarios", "multiline": True}
        ],
        empty_item={"nombreAplicacion": "", "version": "", "comentarios": ""}
    )

    # ARCHIVOS -----------------------------------------------------------------------------------------
    data["archivos"] = list_dict_section(
        "Archivos", "archivos", "Archivos", "Archivo",
        fields_config=[
            {"label": "Nombre", "key": "nombre"},
            {"label": "Comentarios", "key": "comentarios", "multiline": True},
            {"label": "Nomenclatura", "key": "nomenclatura"}
        ],
        empty_item={"nombreArchivo": "", "comentarios": "", "nomenclatura": ""}
    )

    # PREREQUISITOS TECNICOS ----------------------------------------------------------------------------------
    data["requisitos"] = list_text_input_section("Pre-requisitos Técnicos", "requisitos", "Requisito", multiline=True)
    
    # EJECUCION Y REEJECUCION ----------------------------------------------------------------------------------
    field_row("Forma de Ejecución", "ejecucion", data, multiline=True, col_ratio=(1, 6.5))
    field_row("Forma de Re-ejecución", "reejecucion", data, multiline=True, col_ratio=(1, 6.5))
    
    # MACROS EXCEL -----------------------------------------------------------------------------------------
    
    # CODIGO PYTHON -----------------------------------------------------------------------------------------
    
    # DIAGRAMAS -----------------------------------------------------------------------------------------
    col_1, col_2, col_3, col_4 = st.columns([3, 1, 2, 2])
    with col_1:
        st.markdown("**Diagrama de tasks**")
    with col_2:
        img_bytes = st.session_state.get("diagrama_pasos", None)
        if img_bytes:
            show_img_overlay(img_bytes, key="pasos")
    col_1, col_2, col_3, col_4 = st.columns([3, 1, 2, 2])
    with col_1:
        st.markdown("**Diagrama a detalle**")
    with col_2:
        img_bytes = st.session_state.get("diagrama_detalle", None)
        if img_bytes:
            show_img_overlay(img_bytes, key="detalle")

# FUNCION PARA ESTANDARIZAR FILAS DE DOS CAMPOS -------------------------------------------------------
def double_field_row(label1, key1, label2, key2, data, key_prefix="", multiline=False):
    col_left, col_right = st.columns([1, 1])
    with col_left:
        field_row(label1, key1, data, key_prefix=key_prefix, multiline=multiline)
    with col_right:
        field_row(label2, key2, data, key_prefix=key_prefix, multiline=multiline)
        
# FUNCION PARA ESTANDARIZAR FILAS DE UN SOLO CAMPO ----------------------------------------------------
def field_row(label, key, data, col_ratio=None, multiline=False, height=None, key_prefix=""):
    ratio = col_ratio if col_ratio is not None else (1, 2.5)
    if data is None:
        data = {}
    value = data.get(key, "") or ""
    if(label is not None):
        col1, col2 = st.columns(ratio)
        with col1:
            st.markdown(f"<p style='padding-top: 8px; margin: 0;'><b>{label}</b></p>", unsafe_allow_html=True)
        with col2:
            unique_key = f"field_{key_prefix}{key}" if key_prefix else f"field_{key}"
            if multiline:
                if height is None:
                    lines = (len(value) // 60) + value.count("\n") + 1
                    height = max(100, lines * 22) + 5
                data[key] = st.text_area(" ", value=value, key=unique_key, label_visibility="collapsed", height=height)
            else:
                data[key] = st.text_input(" ", value=value, key=unique_key, label_visibility="collapsed")
            return data[key]
    else:
        unique_key = f"field_{key_prefix}{key}" if key_prefix else f"field_{key}"
        if multiline:
            if height is None:
                lines = (len(value) // 60) + value.count("\n") + 1
                height = max(100, lines * 22) + 5
            data[key] = st.text_area(" ", value=value, key=unique_key, label_visibility="collapsed", height=height)
        else:
            data[key] = st.text_input(" ", value=value, key=unique_key, label_visibility="collapsed")
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

# FUNCION PARA RENDERIZAR CAMPOS EDITABLES (LISTAS) CON BOTONES DE AGREGAR/ELIMINAR ITEMS --------------
def list_text_input_section(title, field, label_singular, expanded=False, multiline=False):
    key = f"list_{field}"
    st.markdown(f"<p style='margin: 0 0 25px 0;'><b>{title}</b></p>", unsafe_allow_html=True)
    with st.expander(label_singular + "s", expanded=expanded):
        for item in st.session_state[key]:
            uid = item["_id"]
            col_field, col_btn = st.columns([6, 1])
            with col_field:
                item["value"] = field_row(label= None,key="value",data=item, key_prefix=f"{field}_{uid}_", multiline=multiline)
            with col_btn:
                if st.button("✕", key=f"del_{field}_{uid}"):
                    st.session_state[key] = [
                        e for e in st.session_state[key] if e["_id"] != uid
                    ]
                    st.rerun()
        if st.button(f"+ Agregar {label_singular.lower()}", key=f"add_{field}"):
            counter = st.session_state.get(f"{field}_counter", 0)
            st.session_state[key].append({"_id": counter, "value": ""})
            st.session_state[f"{field}_counter"] = counter + 1
            st.rerun()
    
    return [e["value"] for e in st.session_state[key]]

# FUNCION PARA RENDERIZAR CAMPOS EDITABLES (LISTAS DE DICCIONARIOS) CON BOTONES DE AGREGAR/ELIMINAR ITEMS --------------
def list_dict_section(title, field, expander_label, item_label, fields_config, empty_item, expanded=False):
    key = f"list_{field}"
    st.markdown(f"<p style='margin: 0 0 25px 0;'><b>{title}</b></p>", unsafe_allow_html=True)
    with st.expander(expander_label, expanded=expanded):
        for i, item in enumerate(st.session_state[key]):
            uid = item["_id"]
            col_expander, col_btn = st.columns([10, 1])
            with col_expander:
                with st.expander(f"{item_label} {i + 1}", expanded=True):
                    for fc in fields_config:
                        if fc.get("type") == "list":
                            st.markdown(f"<p style='margin: 0 0 25px 0;'><b>{fc['label']}</b></p>", unsafe_allow_html=True)
                            st.markdown("&nbsp;", unsafe_allow_html=True)
                            _render_inline_list(item, fc, field, uid)
                        else:
                            field_row(fc["label"], fc["key"], item,
                                    key_prefix=f"{field}_{uid}_{fc['key']}",
                                    multiline=fc.get("multiline", False))
            with col_btn:
                if st.button("✕", key=f"del_{field}_{uid}", type="secondary"):
                    st.session_state[key] = [t for t in st.session_state[key] if t["_id"] != uid]
                    st.rerun()
        if st.button(f"+ Agregar {item_label.lower()}", key=f"add_{field}", type="secondary"):
            counter = st.session_state.get(f"{field}_counter", 0)
            new_item = {"_id": counter, **empty_item}
            # Inicializar counter de sublistas para el item nuevo
            for fc in fields_config:
                if fc.get("type") == "list":
                    sublist_key = f"list_{field}_{counter}_{fc['key']}"
                    st.session_state[sublist_key] = []
                    st.session_state[f"{sublist_key}_counter"] = 0
            st.session_state[key].append(new_item)
            st.session_state[f"{field}_counter"] = counter + 1
            st.rerun()

    return st.session_state[key]

def show_img_overlay(img_bytes, key="overlay"):
    if not img_bytes:
        return
    
    img_base64 = base64.b64encode(img_bytes).decode()

    # Inyectar overlay UNA sola vez (siempre, en cada render)
    # El overlay arranca oculto, el botón de Streamlit lo muestra
    html = f"""
    <script>
    (function() {{
        const doc = window.parent.document;

        // Si ya existe, no reinyectar
        if (doc.getElementById('overlay_{key}')) return;

        const overlay = doc.createElement('div');
        overlay.id = 'overlay_{key}';
        overlay.style.cssText = `
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.85);
            z-index: 999999;
            display: none;
            align-items: center;
            justify-content: center;
        `;

        overlay.innerHTML = `
            <button id="close_{key}" style="
                position: fixed;
                top: 20px;
                right: 20px;
                background: white;
                border: none;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                font-size: 20px;
                cursor: pointer;
                z-index: 1000000;
                box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            ">✕</button>
            <img id="img_{key}" src="data:image/png;base64,{img_base64}" style="
                max-width: 90vw;
                max-height: 90vh;
                border-radius: 8px;
                cursor: grab;
                user-select: none;
            "/>
        `;

        doc.body.appendChild(overlay);

        const img = doc.getElementById('img_{key}');
        const closeBtn = doc.getElementById('close_{key}');
        let scale = 1, posX = 0, posY = 0, dragging = false, startX, startY;

        function update() {{
            img.style.transform = `translate(${{posX}}px, ${{posY}}px) scale(${{scale}})`;
        }}

        img.addEventListener('wheel', (e) => {{
            e.preventDefault();
            scale = Math.min(Math.max(0.5, scale - e.deltaY * 0.001), 6);
            update();
        }});

        img.addEventListener('mousedown', (e) => {{
            dragging = true;
            startX = e.clientX - posX;
            startY = e.clientY - posY;
            img.style.cursor = 'grabbing';
        }});

        doc.addEventListener('mousemove', (e) => {{
            if (!dragging) return;
            posX = e.clientX - startX;
            posY = e.clientY - startY;
            update();
        }});

        doc.addEventListener('mouseup', () => {{
            dragging = false;
            img.style.cursor = 'grab';
        }});

        closeBtn.onclick = () => {{
            overlay.style.display = 'none';
            scale = 1; posX = 0; posY = 0;
            update();
        }};

        overlay.addEventListener('click', (e) => {{
            if (e.target === overlay) {{
                overlay.style.display = 'none';
                scale = 1; posX = 0; posY = 0;
                update();
            }}
        }});

        // Escuchar evento custom para abrir
        doc.addEventListener('open_overlay_{key}', () => {{
            overlay.style.display = 'flex';
        }});
    }})();
    </script>
    """
    st.html(html)

    # Botón que dispara el evento custom en el padre
    open_html = f"""
    <button onclick="window.parent.document.dispatchEvent(new Event('open_overlay_{key}'))" style="
        background-color: transparent !important;
        color: #aaa !important;
        border: 1px solid #aaa !important;
        padding: 4px 16px !important;
        margin-bottom: 10px !important;
        cursor: pointer;
        font-size: 14px;
        border-radius: 4px;
    ">Ver</button>
    """
    st.html(html)

# FIX COMPLETO de _render_inline_list
# Corrige bugs 1, 2, 3 y 4: inicialización de session_state, sincronización
# bidireccional, renderizado de campos reales y creación correcta de items nuevos.
def _render_inline_list(item, fc, parent_field, parent_uid):
    subfield = fc["key"]
    label = fc["label"]
    subfields = fc.get("subfields", None)  # FIX 3: leer subfields del config
    key = f"list_{parent_field}_{parent_uid}_{subfield}"
    counter_key = f"{key}_counter"

    # FIX 1: Sincronizar session_state con el item real si no existe la key
    if key not in st.session_state:
        raw = item.get(subfield, [])
        if not isinstance(raw, list):
            raw = []
        # Normalizar items: asegurar que tengan _id
        normalized = []
        for idx, s in enumerate(raw):
            if not isinstance(s, dict):
                s = {"value": str(s)}
            if "_id" not in s:
                s = {"_id": f"{parent_uid}_{idx}", **s}
            normalized.append(s)
        st.session_state[key] = normalized
        st.session_state[counter_key] = len(normalized)

    for subitem in st.session_state[key]:
        uid = subitem["_id"]

        # FIX 3: si hay subfields definidos, renderizar cada campo nombrado
        if subfields:
            col_exp, col_btn = st.columns([10, 1])
            with col_exp:
                with st.expander(f"{label.rstrip('s')} {uid}", expanded=True):
                    for sf in subfields:
                        field_row(
                            sf["label"],
                            sf["key"],
                            subitem,
                            key_prefix=f"{key}_{uid}_",
                            multiline=sf.get("multiline", False)
                        )
            with col_btn:
                if st.button("✕", key=f"del_{key}_{uid}"):
                    st.session_state[key] = [
                        s for s in st.session_state[key] if s["_id"] != uid
                    ]
                    # FIX 2: propagar cambios al item padre
                    item[subfield] = st.session_state[key]
                    st.rerun()
        else:
            # Comportamiento original para sublistas simples (solo "value")
            col_field, col_btn = st.columns([6, 1])
            with col_field:
                subitem["value"] = field_row(
                    label=None,
                    key="value",
                    data=subitem,
                    key_prefix=f"{key}_{uid}_",
                    multiline=True
                )
            with col_btn:
                if st.button("✕", key=f"del_{key}_{uid}"):
                    st.session_state[key] = [
                        s for s in st.session_state[key] if s["_id"] != uid
                    ]
                    # FIX 2: propagar cambios al item padre
                    item[subfield] = st.session_state[key]
                    st.rerun()

    # FIX 4: crear el nuevo item con los campos correctos según subfields
    if st.button(f"+ Agregar {label.lower()}", key=f"add_{key}"):
        counter = st.session_state.get(counter_key, 0)
        new_id = f"{parent_uid}_{counter}"

        if subfields:
            # Crear item con todos los campos definidos en subfields
            new_item = {"_id": new_id}
            for sf in subfields:
                new_item[sf["key"]] = [] if sf.get("type") == "list" else ""
        elif st.session_state[key]:
            # Inferir campos del primer item existente
            template = {k: "" for k in st.session_state[key][0] if k != "_id"}
            new_item = {"_id": new_id, **template}
        else:
            new_item = {"_id": new_id, "value": ""}

        st.session_state[key].append(new_item)
        # FIX 2: propagar cambios al item padre
        item[subfield] = st.session_state[key]
        st.session_state[counter_key] = counter + 1
        st.rerun()