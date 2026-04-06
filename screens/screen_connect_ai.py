import os, traceback, base64, time, tempfile, subprocess, json, streamlit as st
from utils.navigation import *
from components.top_bar import top_bar
from utils.AIConnectorGemini import send_to_gemini

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def screen_connect_ai():
    
    placeholder = st.empty()

    with placeholder.container():
        # OBTENGO AMBIENTE
        env = st.secrets.get("ENV")
        # BARRA DE NAVEGACION
        top_bar(title="Procesando con IA...", back_to="load", show_stepper=True, step=2)
        # GIF DE CARGA
        gif = get_gif_base64(os.path.join(BASE_DIR, "icons", "loading.gif"))
        st.markdown(f'<div style="text-align:center;"><img src="data:image/gif;base64,{gif}" width="120"></div>',unsafe_allow_html=True)
        # ACTUO SEGUN EL AMBIENTE Y ARCHIVO
        if(env == "DESA"):
            if(st.session_state.doc_type == "PDD"):
                with open(os.path.join(BASE_DIR, "prompts", "PDD_example.json"), "r", encoding="utf-8") as f:
                    response = f.read()
            elif(st.session_state.doc_type == "SDD"):
                with open(os.path.join(BASE_DIR, "prompts", "SDD_example.json"), "r", encoding="utf-8") as f:
                    response = f.read()
        elif(env == "PROD"):
            with st.spinner(""):
                response = process_with_ai(st.session_state.files)
    
    # GUARDO LA RESPUESTA DE LA API
    st.session_state.response = response
    data = json.loads(response)
    if(st.session_state.doc_type == "PDD"):
        st.session_state.diagramaAltoNivel = generate_mermaid_img(data.get("diagramaAltoNivel", ""))
        st.session_state.diagramaBajoNivel = generate_mermaid_img(data.get("diagramaBajoNivel", ""))
    elif(st.session_state.doc_type == "SDD"):
        st.session_state.diagrama_pasos = generate_mermaid_img(data.get("diagrama_pasos", ""))
        st.session_state.diagrama_detalle = generate_mermaid_img(data.get("diagrama_detalle", ""))
    go_to("verify")

# FUNCION PARA LLAMADA A LA API                
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
        prompt_path = os.path.join(BASE_DIR, "prompts", type + ".txt")
        
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
        
# FUNCION PARA INYECTAR GIF
def get_gif_base64(path):
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    return data

# FUNCION PARA GENERAR DIAGRAMAS -----------------------------------------------------------------------
def generate_mermaid_img(code):
    mermaidCode = code
    
    if not mermaidCode:
        return None

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            mmd_path = f"{tmpdir}/diagrama.mmd"
            png_path = f"{tmpdir}/diagrama.png"

            with open(mmd_path, "w", encoding="utf-8") as f:
                f.write(
                    '%%{init: {"theme": "neutral", "flowchart": {"curve": "stepAfter", "rankSpacing": 40}}}%%\n'
                    + mermaidCode +
                    "\nlinkStyle default stroke-width:4px;"
                )

            subprocess.run(f"mmdc -i {mmd_path} -o {png_path} -w 1200 -H 600", shell=True, check=True)

            with open(png_path, "rb") as img_file:
                return img_file.read()

    except Exception as e:
        st.warning(f"No se pudo generar el preview: {e}")
        return None