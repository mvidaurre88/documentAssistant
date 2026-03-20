"""
gemini_worker.py

Worker de QThread para llamar a la API de Gemini sin bloquear la UI de PyQt6.

Uso:
    from gemini_worker import GeminiWorker

    self.worker = GeminiWorker(
        prompt_path="prompt.txt",
        file_paths=["archivo.pdf", "imagen.png"],
        api_key="AIzaSy...",
    )
    self.worker.finished.connect(self.on_respuesta)
    self.worker.error.connect(self.on_error)
    self.worker.start()
"""

from PyQt6.QtCore import QThread, pyqtSignal
from AIConnectorGemini import send_to_gemini


class GeminiWorker(QThread):
    finished = pyqtSignal(str)   # emite la respuesta cuando termina
    error    = pyqtSignal(str)   # emite el mensaje de error si falla

    def __init__(self, prompt_path: str, file_paths: list, api_key: str = None, max_tokens: int = 4096):
        super().__init__()
        self.prompt_path = prompt_path
        self.file_paths  = file_paths
        self.api_key     = api_key
        self.max_tokens  = max_tokens

    def run(self):
        """Se ejecuta en segundo plano, sin bloquear la UI."""
        try:
            respuesta = send_to_gemini(
                prompt_path=self.prompt_path,
                file_paths=self.file_paths,
                api_key=self.api_key,
                max_tokens=self.max_tokens,
            )
            self.finished.emit(respuesta)
        except Exception as e:
            self.error.emit(str(e))