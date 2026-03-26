import streamlit as st
import os
from navigation import *
from components.top_bar import top_bar
from AIConnectorGemini import send_to_gemini

def screen_connect_ai():
    
    top_bar(title="Seleccione el tipo de documento", back_to="Procesando con IA...", show_stepper=True, step=0)

    if st.session_state.response is None:
        with st.spinner("Procesando..."):
            response = process_with_ai(st.session_state.files)
            if response:
                st.session_state.response = response
                go_to("verify")
                
def process_with_ai(files):
    import traceback
    try:
        api_key = st.secrets["API_KEY"]
        os.makedirs("temp", exist_ok=True)

        file_paths = []
        for f in files:
            path = os.path.join("temp", f.name)
            with open(path, "wb") as tmp:
                tmp.write(f.getbuffer())
            file_paths.append(path)

        response = send_to_gemini(
            prompt_path="prompt v1.txt",
            file_paths=file_paths,
            api_key=api_key,
            max_tokens=65536,
        )
        return response

    except Exception as e:
        st.error(f"Error IA: {e}")
        st.code(traceback.format_exc())
        st.stop()