import streamlit as st
import os
import json

# Imports tuyos (los vamos a adaptar después)
from datetime import date
from builder import *
from docx_generator import *
from AIConnector import *
from router import get_screens

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCREENS = get_screens(BASE_DIR)

def inject_css():
    st.markdown("""
    <style>

    /*App general*/
    .stApp { background-color: #3c3c3c; font-family: Consolas, monospace;}

    /* Botones */
    .stButton>button {
        background-color: #e68200;
        color: white;
        font-weight: bold;
        font-size: 15px;
        padding: 6px 12px;
        border-radius: 3px;
        border: none;
    }

    a[aria-label="Link to heading"] {
        display: none !important;
    }

    .stButton>button:hover {
        background-color: #ff9500;
    }

    .stButton>button:active {
        background-color: #b36500;
    }

    /* Inputs */
    input, textarea {
        background-color: #2d2d2d !important;
        color: #d4d4d4 !important;
        border: 1px solid #555 !important;
    }

    /* Labels */
    label, .stMarkdown {
        color: #ffffff !important;
    }

    /* Cards */
    .card {
        background-color: #2d2d2d;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
        transition: 0.2s;
    }

    .card:hover {
        border: 1px solid #e68200;
        cursor: pointer;
    }

    /* Stepper */
    .step-active {
        color: #e68200;
        font-weight: bold;
    }

    .step-inactive {
        color: #888;
    }
    
    button[title="View fullscreen"],
    button[title="Fullscreen"],
    button[aria-label="View fullscreen"],
    button[aria-label="Fullscreen"] {
        display: none !important;
    }
    

    div[data-testid="stElementContainer"] {
        margin-bottom: 0rem !important;
    }

    /* Markdown spacing */
    .stMarkdown {
        margin-bottom: 0rem !important;
    }

    .top-bar {
        position: sticky;
        top: 0;
        background-color: #3c3c3c;
        padding: 10px 10px;
        z-index: 999;
        border-bottom: 1px solid #555;
    }

    .top-bar h3 {
        margin: 0;
    }
    
    div[role="radiogroup"] label > div:first-child {
        display: none;
    }

    /* Cada opción */
    div[role="radiogroup"] label {
        background-color: #2d2d2d;
        padding: 20px;
        margin: 5px;
        border-radius: 10px;
        border: 2px solid transparent;
        cursor: pointer;
        text-align: center;
        transition: 0.2s;
        flex: 1;
        width: 400px;
        justify-content: center;
    }

    /* Hover */
    div[role="radiogroup"] label:hover {
        border: 2px solid #e68200;
        transform: scale(1.02);
    }

    /* Seleccionado */
    div[role="radiogroup"] label:has(input:checked) {
        border: 2px solid #e68200;
        background-color: #3a2a10;
    }
        
    div[data-testid="stRadio"] {
        display: flex;
        justify-content: center;
    }

    /* Centrar el contenedor padre */
    div[data-testid="stElementContainer"]:has(div[data-testid="stRadio"]) {
        display: flex;
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)

inject_css()

# -- CONFIGURACIÓN INICIAL -------------------------------------------------------------------------
st.set_page_config(page_title="IA Documentation Assistant", layout="wide")
st.session_state.setdefault("current_screen", "init")
st.session_state.setdefault("response", None)

def card(title):
    return f"""
    <div class="card">
        <h3>{title}</h3>
    </div>
    """

# -- PASO 5 ----------------------------------------------------------------------------------------
def screen_final():
    render_stepper(st)
    st.success("Documento generado correctamente 🎉")

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

# -- ROUTER ----------------------------------------------------------------------------------------
SCREENS[st.session_state.current_screen]()