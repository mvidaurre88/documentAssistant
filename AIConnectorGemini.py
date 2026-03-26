import os
import base64
from pathlib import Path
from docx import Document
from google import genai
from google.genai import types

# Extensiones soportadas
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".png"}


def encode_file(file_path: str):
    """
    Procesa un archivo y devuelve la parte correspondiente para la API de Gemini.
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
        return types.Part.from_bytes(data=base64.b64decode(data), mime_type="image/png")

    # PDF
    if ext == ".pdf":
        with open(path, "rb") as f:
            raw = f.read()
        return types.Part.from_bytes(data=raw, mime_type="application/pdf")

    # DOCX
    if ext == ".docx":
        doc = Document(path)
        text_content = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        return types.Part.from_text(text=f"[Contenido de {path.name}]\n{text_content}")

    # TXT
    if ext == ".txt":
        text_content = path.read_text(encoding="utf-8")
        return types.Part.from_text(text=f"[Contenido de {path.name}]\n{text_content}")


def send_to_gemini(
    prompt_path: str,
    file_paths: list,
    api_key: str = None,
    max_tokens: int = 4096,
) -> str:
    # Resolver API key
    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise ValueError("No se encontró la API key.")

    # Leer el prompt
    prompt_file = Path(prompt_path)
    if not prompt_file.exists():
        raise FileNotFoundError(f"Archivo de prompt no encontrado: {prompt_path}")

    prompt_text = prompt_file.read_text(encoding="utf-8").strip()
    if not prompt_text:
        raise ValueError("El archivo de prompt está vacío.")

    # Construir las partes
    parts = []

    for fp in file_paths:
        print(f"  -> Procesando: {fp}")
        parts.append(encode_file(fp))

    # Prompt al final
    parts.append(types.Part.from_text(text=prompt_text))

    # Cliente y configuración
    client = genai.Client(api_key=key)

    contents = [
        types.Content(
            role="user",
            parts=parts,
        )
    ]

    generate_content_config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=-1),
        max_output_tokens=max_tokens,
    )

    print("Enviando solicitud a Gemini 2.5 Flash...")

    # Llamada con streaming, acumulamos la respuesta
    full_response = ""
    for chunk in client.models.generate_content_stream(
        model="gemini-2.5-flash",
        contents=contents,
        config=generate_content_config,
    ):
        if chunk.text:
            full_response += chunk.text

    return full_response