"""
ai_strategy.py

Patron Strategy para conectarse a diferentes IAs de forma intercambiable.
Actualmente soporta: Gemini, Claude.

Uso:
    from ai_strategy import GeminiStrategy, ClaudeStrategy, AIWorker

    # Elegis la estrategia
    strategy = GeminiStrategy(api_key="AIzaSy...")
    # strategy = ClaudeStrategy(api_key="sk-ant-...")

    # El worker es siempre el mismo
    self.worker = AIWorker(strategy, prompt_path="prompt.txt", file_paths=[...])
    self.worker.finished.connect(self.on_respuesta)
    self.worker.error.connect(self.on_error)
    self.worker.start()
"""

from abc import ABC, abstractmethod
from AIConnectorGemini import send_to_gemini

# ── Interfaz base ────────────────────────────────────────────────────────────

class AIStrategy(ABC):
    @abstractmethod
    def send(self, prompt_path: str, file_paths: list) -> str:
        """Envia el prompt y los archivos a la IA y retorna la respuesta."""
        pass


# ── Estrategias concretas ────────────────────────────────────────────────────

class GeminiStrategy(AIStrategy):
    def __init__(self, api_key: str = None, max_tokens: int = 4096):
        self.api_key    = api_key
        self.max_tokens = max_tokens

    def send(self, prompt_path: str, file_paths: list) -> str:
        return send_to_gemini(
            prompt_path=prompt_path,
            file_paths=file_paths,
            api_key=self.api_key,
            max_tokens=self.max_tokens,
        )