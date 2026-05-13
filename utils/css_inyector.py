# IMPORTS DE TERCEROS
import streamlit as st

def inject_css():
    st.markdown("""<style>

    /* LAYOUT GENERAL */
    section[data-testid="stMain"] {
        overflow-y: auto !important;
        overflow-x: hidden !important;
    }

    [data-testid="stMainBlockContainer"] {
        padding: 2rem 3rem 0 3rem !important;
        max-width: 100% !important;
    }

    div[data-testid="stElementContainer"] {
        margin-bottom: 0rem !important;
    }

    /* BOTONES */
    .stButton>button {
        background-color: #e68200;
        color: white;
        font-weight: bold;
        font-size: 15px;
        padding: 6px 12px;
        border-radius: 3px;
        border: none;
    }
    .stButton>button:hover { background-color: #ff9500; }
    .stButton>button:active { background-color: #b36500; }

    section[data-testid="stMain"] div[data-testid="stButton"] button[kind="secondary"] {
        background-color: transparent !important;
        color: #aaa !important;
        border: 1px solid #aaa !important;
        padding: 1px 10px !important;
    }
    section[data-testid="stMain"] div[data-testid="stButton"] button[kind="secondary"]:hover {
        color: #e68200 !important;
        border-color: #e68200 !important;
    }

    /* INPUTS */
    input, textarea {
        background-color: #2d2d2d !important;
        color: #d4d4d4 !important;
        border: 1px solid #555 !important;
    }

    /* RADIO BUTTONS */
    div[role="radiogroup"] label > div:first-child {
        display: none;
    }
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
    div[role="radiogroup"] label:hover {
        border: 2px solid #e68200;
        transform: scale(1.02);
    }
    div[role="radiogroup"] label:has(input:checked) {
        border: 2px solid #e68200;
        background-color: #3a2a10;
    }
    div[data-testid="stRadio"] {
        display: flex;
        justify-content: center;
    }
    div[data-testid="stElementContainer"]:has(div[data-testid="stRadio"]) {
        display: flex;
        justify-content: center;
    }

    /* ALERTAS */
    div[data-testid="stAlert"] {
        margin-top: 15px !important;
        margin-bottom: 10px !important;
    }

    /* COMPONENTES CUSTOM */
    .top-bar {
        position: sticky;
        top: 0;
        background-color: #3c3c3c;
        padding: 10px 10px;
        z-index: 999;
        border-bottom: 1px solid #555;
    }

    .seccion-titulo {
        text-align: center;
        font-size: 26px;
        font-weight: 600;
        color: #ffffff !important;
        margin: 20px 80px 20px 80px;
        padding: 0 20px;
    }

    .aclaraciones {
        background-color: #2d2d2d;
        border-radius: 4px;
        padding: 15px 20px;
        margin: 0 0 30px 0;
    }
    .aclaraciones h3 { margin: 0 0 10px 0; font-size: 16px; }
    .aclaraciones ul { padding-left: 10px; }
    .aclaraciones li { margin-bottom: 4px; color: #d4d4d4; }
    .aclaraciones li:last-child { margin-bottom: 0; }

    /* OCULTAR ELEMENTOS NATIVOS */
    a[aria-label="Link to heading"] { display: none !important; }
    [data-testid="stHeader"] { display: none !important; }
    [data-testid="stSpinnerIcon"] { display: none !important; }

    button[title="View fullscreen"],
    button[title="Fullscreen"],
    button[aria-label="View fullscreen"],
    button[aria-label="Fullscreen"] {
        display: none !important;
    }

    </style>""", unsafe_allow_html=True)