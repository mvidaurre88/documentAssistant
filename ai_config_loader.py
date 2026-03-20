"""
ai_config_loader.py

Lee config.config y devuelve la estrategia de IA configurada lista para usar.

Formato esperado del .config (clave = valor, sin secciones):

    strategy        = gemini
    gemini_api_key  = AIzaSy...
    gemini_max_tokens = 4096
    claude_api_key  = sk-ant-...
    claude_max_tokens = 4096

Uso:
    from ai_config_loader import loadStrategy

    strategy = loadStrategy()

    self.worker = AIWorker(
        strategy=strategy,
        prompt_path="prompt.txt",
        file_paths=[...],
    )
"""

import os
from ai_strategy import GeminiStrategy, ClaudeStrategy, AIStrategy

# Ruta al .config (misma carpeta que este archivo)
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.config")

STRATEGIES = {
    "gemini": GeminiStrategy,
    "claude": ClaudeStrategy,
}


def _read_config(config_path: str) -> dict:
    """Lee un archivo clave=valor (sin secciones) y retorna un dict."""
    result = {}
    with open(config_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Ignorar comentarios y lineas vacias
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                result[key.strip()] = value.strip()
    return result


def loadStrategy(config_path: str = CONFIG_PATH) -> AIStrategy:
    """
    Lee el archivo .config y retorna la estrategia configurada.

    Lanza ValueError si la estrategia no es valida.
    Lanza FileNotFoundError si no encuentra el archivo .config.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"No se encontro el archivo de configuracion: {config_path}"
        )

    config = _read_config(config_path)

    strategy_name = config.get("ai_strategy", "").strip().lower()

    if strategy_name not in STRATEGIES:
        raise ValueError(
            f"Estrategia '{strategy_name}' no valida. "
            f"Opciones disponibles: {', '.join(STRATEGIES.keys())}"
        )

    api_key    = config.get(f"{strategy_name}_api_key", None)
    max_tokens = int(config.get(f"{strategy_name}_max_tokens", 4096))

    return STRATEGIES[strategy_name](api_key=api_key, max_tokens=max_tokens)