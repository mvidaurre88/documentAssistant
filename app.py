import os, logging, streamlit as st
from utils.router import get_screens

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "errors.log")
SCREENS = get_screens(BASE_DIR)

def inject_css():
    st.markdown("""
    <style>

    /*App general*/
    .stApp { background-color: #3c3c3c; font-family: Consolas, monospace;}

    .main .block-container {
        padding-bottom: 0rem !important;
        padding-top: 1rem !important;
        max-width: 100% !important;
    }

    section[data-testid="stMain"] {
        overflow-y: auto !important;
        overflow-x: hidden !important;
    }
    
    .block-container {
        padding-bottom: 0 !important;
    }

    div[data-testid="stVerticalBlock"] {
        gap: 0rem !important;
    }

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

    section[data-testid="stMain"] div[data-testid="stButton"] button[kind="secondary"] {
        background-color: transparent !important;
        color: #aaa !important;
        border: 1px solid #aaa !important;
        padding: 4px 10px !important;
    }
    
    section[data-testid="stMain"] div[data-testid="stButton"] button[kind="secondary"]:hover {
        color: #e68200 !important;
        border-color: #e68200 !important;
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

    div[data-testid="stAlert"] {
        margin-top: 15px !important;
        margin-bottom: 10px !important;
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
        padding: 40px;
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
    
    div.btn-delete button {
        background-color: transparent !important;
        color: #aaa !important;
        border: 1px solid #ddd !important;
        font-size: 12px !important;
    }
    
    div.btn-delete button:hover {
        color: red !important;
        border-color: red !important;
    }
    
    </style>
    """, unsafe_allow_html=True)

# -- CSS GLOBAL PARA LA APP ------------------------------------------------------------------------
inject_css()

# CONFIGURACIÓN DE LOGGEO --------------------------------------------------------------------------
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[ logging.FileHandler(LOG_FILE, encoding="utf-8") ])
logger = logging.getLogger(__name__)

# -- CONFIGURACIÓN INICIAL -------------------------------------------------------------------------
st.set_page_config(page_title="IA Documentation Assistant", layout="wide")
st.session_state.setdefault("current_screen", "init")
st.session_state.setdefault("response", None)
st.session_state.setdefault("processing", False)

# -- ROUTER PARA ACCEDER A LAS PAGINAS -------------------------------------------------------------
SCREENS[st.session_state.current_screen]()