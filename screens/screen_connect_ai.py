import os, re, traceback, base64, requests, json5, streamlit as st
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
        response = None
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
    try:
        file_content = response
        file_content_clean = file_content.replace("```json", "").replace("```", "").strip()
        file_content_clean = fix_encoding(file_content_clean)
        data = json5.loads(file_content_clean)
    except Exception as e:
        error_msg = str(e)
        print(f"[ERROR] Fallo al parsear JSON: {error_msg}")

        match  = re.search(r'line (\d+) column (\d+) \(char (\d+)\)', error_msg)
        match2 = re.search(r'<string>:(\d+).*?at column (\d+)', error_msg)

        lines    = file_content_clean.splitlines() if 'file_content_clean' in locals() else []
        line_num = None
        col_num  = None

        if match:
            line_num = int(match.group(1))
            col_num  = int(match.group(2))
            char_pos = int(match.group(3))
            print(f"[ERROR] Posición: línea {line_num}, columna {col_num} (char {char_pos})")
        elif match2:
            line_num = int(match2.group(1))
            col_num  = int(match2.group(2))
            print(f"[ERROR] Posición: línea {line_num}, columna {col_num}")

        if line_num is not None and lines:
            context_start = max(0, line_num - 3)
            context_end   = min(len(lines), line_num + 2)

            print(f"[ERROR] Contexto alrededor del error:")
            for i, l in enumerate(lines[context_start:context_end], start=context_start + 1):
                marker = " >>> " if i == line_num else "     "
                print(f"{marker}línea {i:4d}: {l}")

            if 0 < line_num <= len(lines):
                broken_line = lines[line_num - 1]
                snippet     = broken_line[max(0, col_num - 40):col_num + 40]
                arrow       = " " * min(40, col_num - 1) + "^"
                print(f"[ERROR] Fragmento (~80 chars alrededor de col {col_num}):")
                print(f"        {snippet}")
                print(f"        {arrow}")
        elif lines:
            print(f"[ERROR] No se pudo determinar posición. Primeras 15 líneas del JSON:")
            for i, l in enumerate(lines[:15], start=1):
                print(f"  línea {i:4d}: {l}")

        st.error(f"Error al procesar la respuesta de la IA. Revisá los logs para más detalle.\n\n`{error_msg}`")
        st.stop()

    st.session_state.response = file_content_clean
    if st.session_state.doc_type == "PDD":
        with st.spinner("Generando diagramas..."):
            st.session_state.diagramaAltoNivel = generate_mermaid_img(data.get("diagramaAltoNivel", ""))
        with st.spinner("Generando diagramas..."):
            st.session_state.diagramaBajoNivel = generate_mermaid_img(data.get("diagramaBajoNivel", ""))
            print(f"[DEBUG] diagramaBajoNivel: {type(st.session_state.diagramaBajoNivel)}, len: {len(st.session_state.diagramaBajoNivel) if st.session_state.diagramaBajoNivel else 'None'}")
    elif st.session_state.doc_type == "SDD":
        with st.spinner("Generando diagramas..."):
            st.session_state.diagrama_pasos = generate_mermaid_img(data.get("diagrama_pasos", ""))
        with st.spinner("Generando diagramas..."):
            st.session_state.diagrama_detalle = generate_mermaid_img(data.get("diagrama_detalle", ""))
    go_to("verify")

# FUNCION PARA LLAMADA A LA API                
def process_with_ai(files):
    try:
        os.makedirs("temp", exist_ok=True)

        file_paths = []
        for f in files:
            path = os.path.join("temp", f.name)
            with open(path, "wb") as tmp:
                tmp.write(f.getbuffer())
            file_paths.append(path)

        # DEFINO QUE PROMPT USAR
        type = st.session_state.doc_type
        prompt_path = os.path.join(BASE_DIR, "prompts", type + ".txt")
        
        response = send_to_gemini(promptPath=prompt_path, filePaths=file_paths, maxTokens=65536)
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
def generate_mermaid_img(diagram: str):
    if not diagram:
        return None
    
    diagram = diagram.replace("\\n", "\n")
    
    try:
        response = requests.post(
            "https://kroki.io/mermaid/png",
            headers={"Content-Type": "text/plain"},
            data=diagram.encode("utf-8"),
            timeout=15
        )
        response.raise_for_status()
        return response.content

    except Exception as e:
        st.error(f"Error generando imagen: {e}")
        print(f"[DEBUG] Status code: {response.status_code if 'response' in locals() else 'N/A'}")
        print(f"[DEBUG] Response body: {response.text[:200] if 'response' in locals() else 'N/A'}")
        return None
    
def fix_encoding(text: str) -> str:
    try:
        return text.encode('latin1').decode('utf-8')
    except (UnicodeDecodeError, UnicodeEncodeError):
        return text