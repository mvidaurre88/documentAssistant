import anthropic
import argparse
import base64
import sys
from pathlib import Path

# Tipos de extensiones soportadas
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".png"}

# Procesa un archivo y devuelve el bloque de contenido correspondiente para la API de Claude.
def encode_file(filePath: str) -> dict:
    
    path = Path(filePath)

    if not path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {filePath}")

    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Tipo de archivo no soportado: '{ext}' ({filePath})\n"
            f"Extensiones soportadas: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    # PNG
    if ext == ".png":
        with open(path, "rb") as f:
            data = base64.standard_b64encode(f.read()).decode("utf-8")
        return {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": data,
            },
        }

    # PDF
    if ext == ".pdf":
        with open(path, "rb") as f:
            data = base64.standard_b64encode(f.read()).decode("utf-8")
        return {
            "type": "document",
            "source": {
                "type": "base64",
                "media_type": "application/pdf",
                "data": data,
            },
        }

    # DOCX
    if ext == ".docx":
        with open(path, "rb") as f:
            data = base64.standard_b64encode(f.read()).decode("utf-8")
        return {
            "type": "document",
            "source": {
                "type": "base64",
                "media_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "data": data,
            },
        }

    # TXT
    if ext == ".txt":
        text_content = path.read_text(encoding="utf-8")
        return {
            "type": "text",
            "text": f"[Contenido de {path.name}]\n{text_content}",
        }


def send_to_claude(
    prompt_path: str,
    file_paths: list,
    model: str = "claude-sonnet-4-20250514",
    max_tokens: int = 4096,
    api_key: str = None,
) -> str:
    """
    Lee el prompt desde un .txt, adjunta los archivos indicados y
    envia todo a la API de Claude.

    Parametros
    ----------
    prompt_path : str
        Ruta al archivo .txt que contiene el prompt.
    file_paths  : list[str]
        Lista de rutas a los archivos a enviar (.pdf, .docx, .txt, .png).
    model       : str
        Modelo de Claude a usar.
    max_tokens  : int
        Numero maximo de tokens en la respuesta.
    api_key     : str | None
        API key de Anthropic. Si es None se usa la variable de entorno
        ANTHROPIC_API_KEY.

    Retorna
    -------
    str
        Texto de la respuesta generada por Claude.
    """
    # Leer el prompt
    prompt_file = Path(prompt_path)
    if not prompt_file.exists():
        raise FileNotFoundError(f"Archivo de prompt no encontrado: {prompt_path}")

    prompt_text = prompt_file.read_text(encoding="utf-8").strip()
    if not prompt_text:
        raise ValueError("El archivo de prompt esta vacio.")

    # Construir el contenido del mensaje
    content = []

    # Adjuntar cada archivo
    for fp in file_paths:
        print(f"  -> Procesando: {fp}")
        block = encode_file(fp)
        content.append(block)

    # Anadir el prompt al final
    content.append({"type": "text", "text": prompt_text})

    # Llamar a la API
    client = anthropic.Anthropic(api_key=api_key)  # usa ANTHROPIC_API_KEY si api_key=None

    print(f"\nEnviando solicitud a Claude ({model})...")
    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": content}],
    )

    # Extraer texto de la respuesta
    response_text = "".join(
        block.text for block in message.content if hasattr(block, "text")
    )
    return response_text


# CLI
def main():
    parser = argparse.ArgumentParser(
        description="Envia un prompt y archivos a la API de Claude."
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
        "--model",
        default="claude-sonnet-4-20250514",
        help="Modelo de Claude (default: claude-sonnet-4-20250514).",
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
        help="API key de Anthropic (opcional; si no se pasa se usa ANTHROPIC_API_KEY).",
    )

    args = parser.parse_args()

    print("=== Claude API Client ===")
    print(f"Prompt  : {args.prompt}")
    print(f"Archivos: {args.files or '(ninguno)'}")

    try:
        respuesta = send_to_claude(
            prompt_path=args.prompt,
            file_paths=args.files,
            model=args.model,
            max_tokens=args.max_tokens,
            api_key=args.api_key,
        )
        print("\n=== Respuesta de Claude ===\n")
        print(respuesta)

    except (FileNotFoundError, ValueError) as e:
        print(f"\n[ERROR] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()