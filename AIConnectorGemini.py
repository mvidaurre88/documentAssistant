"""
gemini_api_client.py

Conecta a la API de Gemini, lee un prompt desde un .txt y envia
una lista de archivos como parametro.

Tipos de archivo soportados: .pdf, .docx, .txt, .png

Uso:
    python gemini_api_client.py \
        --prompt prompt.txt \
        --files archivo.pdf imagen.png documento.docx notas.txt

Requisitos:
    pip install requests python-docx
"""

import argparse
import base64
import json
import sys
import requests
from docx import Document
from pathlib import Path


# Endpoint y modelo
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent"

# Extensiones soportadas
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".png"}


def encode_file(file_path: str) -> dict:
    """
    Procesa un archivo y devuelve la parte correspondiente
    para la API de Gemini.

    Soporta:
      - .png  -> inline_data image/png        (base64)
      - .pdf  -> inline_data application/pdf  (base64)
      - .docx -> texto extraido con python-docx (Gemini no soporta .docx nativo)
      - .txt  -> text plano
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Tipo de archivo no soportado: '{ext}' ({file_path})\n"
            f"Extensiones soportadas: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    # PNG
    if ext == ".png":
        with open(path, "rb") as f:
            data = base64.standard_b64encode(f.read()).decode("utf-8")
        return {
            "inline_data": {
                "mime_type": "image/png",
                "data": data,
            }
        }

    # PDF
    if ext == ".pdf":
        with open(path, "rb") as f:
            data = base64.standard_b64encode(f.read()).decode("utf-8")
        return {
            "inline_data": {
                "mime_type": "application/pdf",
                "data": data,
            }
        }

    # DOCX
    if ext == ".docx":
        doc = Document(path)
        text_content = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        return {
            "text": f"[Contenido de {path.name}]\n{text_content}"
        }

    # TXT
    if ext == ".txt":
        text_content = path.read_text(encoding="utf-8")
        return {
            "text": f"[Contenido de {path.name}]\n{text_content}"
        }


def send_to_gemini(
    prompt_path: str,
    file_paths: list,
    api_key: str = None,
    max_tokens: int = 4096,
) -> str:
    """
    Lee el prompt desde un .txt, adjunta los archivos indicados y
    envia todo a la API de Gemini.

    Parametros
    ----------
    prompt_path : str
        Ruta al archivo .txt que contiene el prompt.
    file_paths  : list[str]
        Lista de rutas a los archivos a enviar (.pdf, .docx, .txt, .png).
    api_key     : str | None
        API key de Google. Si es None se usa la variable de entorno
        GEMINI_API_KEY.
    max_tokens  : int
        Numero maximo de tokens en la respuesta.

    Retorna
    -------
    str
        Texto de la respuesta generada por Gemini.
    """
    import os

    # Resolver API key
    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise ValueError(
            "No se encontro la API key. Pasa --api-key o define la variable de entorno GEMINI_API_KEY."
        )

    # Leer el prompt
    prompt_file = Path(prompt_path)
    if not prompt_file.exists():
        raise FileNotFoundError(f"Archivo de prompt no encontrado: {prompt_path}")

    prompt_text = prompt_file.read_text(encoding="utf-8").strip()
    if not prompt_text:
        raise ValueError("El archivo de prompt esta vacio.")

    # Construir las partes del mensaje
    parts = []

    # Adjuntar cada archivo
    for fp in file_paths:
        print(f"  -> Procesando: {fp}")
        part = encode_file(fp)
        parts.append(part)

    # Anadir el prompt al final
    parts.append({"text": prompt_text})

    # Armar el payload
    payload = {
        "contents": [
            {
                "parts": parts
            }
        ],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
        }
    }

    # Llamar a la API
    url = f"{API_URL}?key={key}"
    print(f"\nEnviando solicitud a Gemini...")

    response = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload),
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Error en la API de Gemini ({response.status_code}): {response.text}"
        )

    result = response.json()

    # Extraer texto de la respuesta
    try:
        response_text = result["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"Respuesta inesperada de la API: {result}") from e

    return response_text


# CLI
def main():
    parser = argparse.ArgumentParser(
        description="Envia un prompt y archivos a la API de Gemini."
    )
    parser.add_argument(
        "--prompt",
        required=True,
        help="Ruta al archivo .txt con el prompt.",
    )
    parser.add_argument(
        "--files",
        nargs="+",
        default=[],
        help="Rutas de los archivos a enviar (.pdf, .docx, .txt, .png).",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=4096,
        help="Maximo de tokens en la respuesta (default: 4096).",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="API key de Google (opcional; si no se pasa se usa GEMINI_API_KEY).",
    )

    args = parser.parse_args()

    print("=== Gemini API Client ===")
    print(f"Prompt  : {args.prompt}")
    print(f"Archivos: {args.files or '(ninguno)'}")

    try:
        respuesta = send_to_gemini(
            prompt_path=args.prompt,
            file_paths=args.files,
            api_key=args.api_key,
            max_tokens=args.max_tokens,
        )
        print("\n=== Respuesta de Gemini ===\n")
        print(respuesta)

    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(f"\n[ERROR] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()