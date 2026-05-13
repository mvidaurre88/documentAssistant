import os
import re
import traceback
import base64
import json5
import logging
import streamlit as st
import graphviz

from utils.navigation import *
from components.top_bar import top_bar
from components.section_title import section_title
from utils.AIConnector import send_to_ai

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logger = logging.getLogger(__name__)


def screen_connect_ai():
    
    # CONSISTENCIA DE ARCHIVOS EN SESION ----------------------------------------------------------
    file = st.session_state.get("file", None)
    files = st.session_state.get("files", None)
    if file is not None:
        try:
            extension = os.path.splitext(file.name)[1]
            file.name = st.session_state.doc_type + extension
            files.append(file)
            st.session_state.files = files
        except Exception as e:
            logger.error(f"No se pudo renombrar el archivo: {e}")
    
    container = st.empty()
    with container.container():
        env = st.secrets.get("ENV")
        top_bar(back_to="load", show_stepper=True, step=2, key="ai")
        render_loading_frame("Procesando con IA...")
        
        # ACTUO SEGUN EL AMBIENTE Y ARCHIVO -------------------------------------------------------
        response = None
        if env == "DESA":
            doc_type = st.session_state.get("doc_type", "")
            if doc_type != "":
                with open(os.path.join(BASE_DIR, "prompts", doc_type + "_example.json"), "r", encoding="utf-8") as f:
                    response = f.read()
        elif env == "PROD":
            with st.spinner(""):
                response = process_with_ai(st.session_state.files)
    
    # PARSEO DE LA RESPUESTA --------------------------------------------------------------------
    try:
        file_content = response
        file_content_clean = file_content.replace("```json", "").replace("```", "").strip()
        file_content_clean = fix_encoding(file_content_clean)
        data = json5.loads(file_content_clean)
    except Exception as e:
        logger.error(f"Fallo al parsear JSON: {e}")
        logger.error(f"Contenido recibido:\n{file_content_clean[:2000]}")
        st.error(f"Error al procesar la respuesta de la IA.\n\n`{e}`")
        st.stop()

    st.session_state.response = file_content_clean
        
    # GENERACION DE DIAGRAMAS -------------------------------------------------------------------
    container.empty()
    with container.container():
        top_bar(back_to="load", show_stepper=True, step=2, key="diag")
        render_loading_frame("Generando diagramas...")
        with st.spinner(""):
            if st.session_state.doc_type == "PDD":
                st.session_state.diagramaAltoNivel = generate_mermaid_img(data.get("diagramaAltoNivel", ""))
                st.session_state.diagramaBajoNivel = generate_mermaid_img(data.get("diagramaBajoNivel", ""))
            elif st.session_state.doc_type == "SDD":
                st.session_state.diagrama_pasos = generate_mermaid_img(data.get("diagrama_pasos", ""))
                st.session_state.diagrama_detalle = generate_mermaid_img(data.get("diagrama_detalle", ""))
    go_to("verify")


# FUNCION PARA LLAMADA A LA API ---------------------------------------------------------------
def process_with_ai(files):
    try:
        type = st.session_state.doc_type
        prompt_path = os.path.join(BASE_DIR, "prompts", type + ".txt")
        response = send_to_ai(promptPath=prompt_path, files=files, maxTokens=65536)
        return response

    except Exception as e:
        st.error(f"Error IA: {e}")
        st.code(traceback.format_exc())
        st.stop()


def get_gif_base64(path):
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    return data


# ============================================================================================
# RENDER DE DIAGRAMAS CON GRAPHVIZ LOCAL
# Soporta: A -->|label| B  y  A -- label --> B  (ambos estilos de Mermaid)
# ============================================================================================

NODE_PATTERN = re.compile(
    r"(\w+)(?:\(\[(.*?)\]\)|\[(.*?)\]|\{(.*?)\}|\((.*?)\))"
)
EDGE_PATTERN_PIPE = re.compile(r"(\w+)\s*-->\s*\|(.*?)\|\s*(\w+)")
EDGE_PATTERN_INLINE = re.compile(r"(\w+)\s*--\s*([^>\-][^-]*?)\s*-->\s*(\w+)")
EDGE_PATTERN_PLAIN = re.compile(r"(\w+)\s*-->\s*(\w+)")
DIRECTION_PATTERN = re.compile(r"^\s*(?:graph|flowchart)\s+(TD|TB|LR|RL|BT)", re.IGNORECASE)


def _extract_node_label_and_shape(match):
    if match.group(2) is not None:
        return match.group(2), "oval"
    if match.group(3) is not None:
        return match.group(3), "box"
    if match.group(4) is not None:
        return match.group(4), "diamond"
    if match.group(5) is not None:
        return match.group(5), "ellipse"
    return match.group(1), "box"


def _parse_edges(line: str):
    """Extrae aristas probando los tres formatos en orden."""
    clean = NODE_PATTERN.sub(r"\1", line)
    edges = []

    for m in EDGE_PATTERN_PIPE.finditer(clean):
        edges.append((m.group(1), m.group(3), m.group(2).strip()))
        clean = clean.replace(m.group(0), "")

    for m in EDGE_PATTERN_INLINE.finditer(clean):
        edges.append((m.group(1), m.group(3), m.group(2).strip()))
        clean = clean.replace(m.group(0), "")

    for m in EDGE_PATTERN_PLAIN.finditer(clean):
        edges.append((m.group(1), m.group(2), ""))

    return edges


def _mermaid_to_graphviz(mermaid_code: str):
    mermaid_code = mermaid_code.replace("\\n", "\n").strip()

    direction = "TB"
    for line in mermaid_code.split("\n"):
        m = DIRECTION_PATTERN.match(line)
        if m:
            direction = m.group(1).upper()
            if direction == "TD":
                direction = "TB"
            break

    dot = graphviz.Digraph(format="png")
    dot.attr(
        rankdir=direction,
        bgcolor="white",
        fontname="Arial",
        nodesep="0.6",
        ranksep="0.8",
        splines="polyline",
        pad="0.3",
    )
    dot.attr("node", fontname="Arial", fontsize="11", style="filled",
             fillcolor="#E8F0FE", color="#4A6FA5", margin="0.15,0.08")
    dot.attr("edge", fontname="Arial", fontsize="9", color="#4A6FA5", arrowsize="0.8")

    nodes_seen = {}

    for line in mermaid_code.split("\n"):
        line = line.strip()
        if not line or line.startswith("%%") or DIRECTION_PATTERN.match(line):
            continue
        for m in NODE_PATTERN.finditer(line):
            node_id = m.group(1)
            if node_id not in nodes_seen:
                label, shape = _extract_node_label_and_shape(m)
                nodes_seen[node_id] = (label, shape)

    edges = []
    for line in mermaid_code.split("\n"):
        line = line.strip()
        if not line or line.startswith("%%") or DIRECTION_PATTERN.match(line):
            continue
        for src, dst, edge_label in _parse_edges(line):
            edges.append((src, dst, edge_label))
            for nid in (src, dst):
                if nid not in nodes_seen:
                    nodes_seen[nid] = (nid, "box")

    if not nodes_seen and not edges:
        logger.warning("No se pudo parsear el diagrama Mermaid")
        return None

    for node_id, (label, shape) in nodes_seen.items():
        is_terminal = label.upper() in ("START", "END", "INICIO", "FIN")
        if is_terminal:
            dot.node(node_id, label, shape="oval", fillcolor="#D4E4F7", penwidth="2")
        elif shape == "diamond":
            dot.node(node_id, label, shape="diamond", fillcolor="#FFF4E0", color="#C8932F")
        else:
            dot.node(node_id, label, shape=shape)

    for src, dst, edge_label in edges:
        if edge_label:
            dot.edge(src, dst, label=f"  {edge_label}  ")
        else:
            dot.edge(src, dst)

    return dot


@st.cache_data(show_spinner=False)
def generate_mermaid_img(diagram: str) -> bytes | None:
    if not diagram:
        return None

    diagram = diagram.replace("\\n", "\n")
    num_lines = diagram.count("\n") + 1
    num_chars = len(diagram)
    logger.info(f"Diagrama Mermaid: {num_lines} líneas, {num_chars} caracteres")

    try:
        dot = _mermaid_to_graphviz(diagram)
        if dot is None:
            return None
        png_bytes = dot.pipe(format="png")
        logger.info(f"PNG generado con Graphviz local ({len(png_bytes)} bytes)")
        return png_bytes
    except graphviz.backend.ExecutableNotFound:
        logger.error("Graphviz no está instalado. Agregá 'graphviz' a packages.txt en Streamlit Cloud.")
        return None
    except Exception as e:
        logger.error(f"Error renderizando diagrama: {e}")
        return None


def fix_encoding(text: str) -> str:
    try:
        return text.encode('latin1').decode('utf-8')
    except (UnicodeDecodeError, UnicodeEncodeError):
        return text


def render_loading_frame(title: str):
    gif = get_gif_base64(os.path.join(BASE_DIR, "icons", "loading.gif"))
    st.markdown(
        f'<div style="text-align:center; margin-top: 40px;">'
        f'<img src="data:image/gif;base64,{gif}" width="120"></div>',
        unsafe_allow_html=True
    )
    section_title(title)