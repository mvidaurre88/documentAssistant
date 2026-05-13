import io
import logging, mammoth, base64, anthropic, httpx, streamlit as st
import os
from time import time
from pathlib import Path
from openpyxl import load_workbook

logger = logging.getLogger(__name__)

# EXTENSIONES SOPORTADAS -----------------------------------------------------------------------------
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".png", ".py", ".xlsm"}

# ENCODE FILES TO SEND TO AI -------------------------------------------------------------------------
def encode_file(file_or_path):
    """Acepta un Path o un objeto tipo UploadedFile de Streamlit."""
    
    # Determinar si es Path o file-like
    if isinstance(file_or_path, Path):
        if not file_or_path.exists():
            logger.error(f"Archivo no encontrado: {file_or_path}")
            return None
        name = file_or_path.name
        ext = file_or_path.suffix.lower()
        read_bytes = lambda: file_or_path.read_bytes()
        read_text = lambda: file_or_path.read_text(encoding="utf-8")
        open_for_mammoth = lambda: open(file_or_path, "rb")
        path_for_openpyxl = file_or_path
    else:
        # UploadedFile de Streamlit u objeto similar
        name = file_or_path.name
        ext = os.path.splitext(name)[1].lower()
        read_bytes = lambda: file_or_path.getvalue()
        read_text = lambda: file_or_path.getvalue().decode("utf-8")
        open_for_mammoth = lambda: io.BytesIO(file_or_path.getvalue())
        # openpyxl puede leer desde BytesIO también
        path_for_openpyxl = io.BytesIO(file_or_path.getvalue())
    
    if ext not in SUPPORTED_EXTENSIONS:
        logger.error(f"Tipo no soportado: '{ext}'")
        return None

    block = None

    if ext == ".png":
        data = base64.standard_b64encode(read_bytes()).decode("utf-8")
        block = {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": data}}

    elif ext == ".pdf":
        data = base64.standard_b64encode(read_bytes()).decode("utf-8")
        block = {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": data}}

    elif ext == ".docx":
        with open_for_mammoth() as f:
            result = mammoth.convert_to_markdown(f, convert_image=mammoth.images.img_element(lambda image: {}))
        block = {"type": "text", "text": f"[Contenido de {name}]\n{result.value}"}

    elif ext in (".txt", ".py"):
        block = {"type": "text", "text": f"[Contenido de {name}]\n{read_text()}"}

    elif ext in (".xlsm", ".xlsx"):
        wb = load_workbook(path_for_openpyxl, read_only=True, keep_vba=True)
        try:
            lines = []
            for sheet_name in wb.sheetnames:
                ws = wb[sheet_name]
                lines.append(f"### Hoja: {sheet_name}")
                for row in ws.iter_rows(values_only=True):
                    row_text = "\t".join("" if cell is None else str(cell) for cell in row)
                    if row_text.strip():
                        lines.append(row_text)
        finally:
            wb.close()
        block = {"type": "text", "text": f"[Contenido de {name}]\n" + "\n".join(lines)}

    # Log de tokens (igual que antes)
    if block is not None:
        if block["type"] == "text":
            estimated_tokens = len(block["text"]) // 4
        elif block["type"] == "image":
            # Imágenes: estimación rough basada en tamaño base64 (no es exacto, pero da idea)
            estimated_tokens = len(block["source"]["data"]) // 4
        elif block["type"] == "document":
            # PDFs: cada página ~2000 tokens, pero como acá no sabemos cuántas páginas tiene,
            # usamos el tamaño base64 como aproximación gruesa
            estimated_tokens = len(block["source"]["data"]) // 4
        else:
            estimated_tokens = 0

        logger.info(
            f"Archivo procesado: {file_or_path.name} | "
            f"Tipo: {block['type']} | "
            f"Tokens estimados: ~{estimated_tokens:,}"
        )

    return block

def send_to_ai(promptPath: str, files: list, maxTokens: int = 4096) -> str:
    
    # GET API KEY -----------------------------------------------------------------------------
    key = st.secrets.get("API_KEY")
    if not key:
        logger.error("API_KEY no encontrada en las variables de entorno.")
        raise EnvironmentError("API_KEY no encontrada en las variables de entorno.")

    # READ PROMPT ----------------------------------------------------------------------------------
    prompt_file = Path(promptPath)
    if not prompt_file.exists():
        logger.error(f"Archivo de prompt no encontrado: {promptPath}")
        raise FileNotFoundError(f"Archivo de prompt no encontrado: {promptPath}")

    prompt_text = prompt_file.read_text(encoding="utf-8").strip()
    if not prompt_text:
        logger.error(f"Archivo de prompt está vacío: {promptPath}")
        raise ValueError("El archivo de prompt está vacío.")

    # GET FILES AND ENCODE -----------------------------------------------------------
    content_blocks = []
    for file in files:
        block = encode_file(file)
        if block:
            content_blocks.append(block)

    if not content_blocks and files:
        logger.error("No se pudieron procesar los archivos proporcionados.")
        raise ValueError("Ningún archivo pudo ser procesado.")
    
    # Prompt al final
    content_blocks.append({"type": "text", "text": prompt_text})

    # CONFIG CLIENT -----------------------------------------------------------------------------------------
    client = anthropic.Anthropic(api_key=key, timeout=900.0)

    # Retry con backoff
    max_retries = 3
    last_error = None
    
    for attempt in range(max_retries):
        try:
            full_response = ""
            with client.messages.stream(
                model="claude-sonnet-4-6",
                max_tokens=maxTokens,
                messages=[{"role": "user", "content": content_blocks}],
            ) as stream:
                for text in stream.text_stream:
                    full_response += text
            
            logger.info(f"Respuesta IA generada exitosamente (intento {attempt + 1}, {len(full_response)} chars)")
            return full_response
        
        # ERRORES TRANSITORIOS: retry tiene sentido
        except (
            anthropic.APIConnectionError,
            anthropic.APITimeoutError,
            anthropic.InternalServerError,
            anthropic.RateLimitError,
            httpx.RemoteProtocolError,    # ← cubre "peer closed connection"
            httpx.ReadTimeout,
            httpx.ConnectTimeout,
        ) as e:
            last_error = e
            logger.warning(f"Error transitorio en intento {attempt + 1}/{max_retries}: {type(e).__name__}: {e}")
            if attempt < max_retries - 1:
                wait = 2 ** attempt  # 1s, 2s, 4s
                logger.info(f"Reintentando en {wait}s...")
                time.sleep(wait)
                continue
        
        # ERRORES DE API NO RECUPERABLES: 400, 401, 403, 404, etc.
        except anthropic.APIError as e:
            logger.error(f"Error de API no recuperable: {type(e).__name__}: {e}")
            raise
        
        # CUALQUIER OTRO ERROR INESPERADO
        except Exception as e:
            logger.error(f"Error inesperado: {type(e).__name__}: {e}")
            raise
    
    # Si llegamos acá, todos los reintentos fallaron
    logger.error(f"Todos los reintentos fallaron. Último error: {last_error}")
    raise last_error if last_error else RuntimeError("Falló sin error registrado")