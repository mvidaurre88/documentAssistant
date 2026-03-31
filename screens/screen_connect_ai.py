import streamlit as st
import os
import traceback
import base64
import time
from navigation import *
from components.top_bar import top_bar
from AIConnectorGemini import send_to_gemini

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def screen_connect_ai():
    
    # OBTENGO AMBIENTE
    env = st.secrets.get("ENV")
    
    # REINICIO LA PAGINA PARA QUE SEA UNA NUEVA
    if not st.session_state.processing:
        st.session_state.processing = True
        st.rerun()
        
    # BARRA DE NAVEGACION
    top_bar(title="Procesando con IA...", back_to="load", show_stepper=True, step=2)
    
    # GIF DE CARGA
    gif = get_gif_base64(os.path.join(BASE_DIR, "icons", "loading.gif"))
    st.markdown(f'<div style="text-align:center;"><img src="data:image/gif;base64,{gif}" width="120"></div>',unsafe_allow_html=True)

    # ACTUO SEGUN EL AMBIENTE
    if(env == "DESA"):
        time.sleep(5)
        with open(os.path.join(BASE_DIR, "ejemplo copy.json"), "r", encoding="utf-8") as f:
            response = f.read()
    elif(env == "PROD"):
        with st.spinner(""):
            response = process_with_ai(st.session_state.files)
    
    # GUARDO LA RESPUESTA DE LA API
    st.session_state.response = response
    go_to("verify")
                
def process_with_ai(files):
    try:
        api_key = st.secrets["API_KEY"]
        os.makedirs("temp", exist_ok=True)

        file_paths = []
        for f in files:
            path = os.path.join("temp", f.name)
            with open(path, "wb") as tmp:
                tmp.write(f.getbuffer())
            file_paths.append(path)

        # DEFINO QUE PROMPT USAR
        type = st.session_state.doc_type
        mode = st.session_state.mode
        prompt_path = os.path.join(BASE_DIR, "prompts", type + "_" + mode + ".txt")
        
        response = send_to_gemini(
            prompt_path=prompt_path,
            file_paths=file_paths,
            api_key=api_key,
            max_tokens=65536,
        )
        return response

    except Exception as e:
        st.error(f"Error IA: {e}")
        st.code(traceback.format_exc())
        st.stop()
        
def get_gif_base64(path):
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    return data