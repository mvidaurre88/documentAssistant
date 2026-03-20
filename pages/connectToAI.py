from builder import *
from ai_strategy import AIWorker
from ai_config_loader import loadStrategy
from datetime import date

# Paso 3: Conectar con la IA para procesar datos
class connectToAI():
    def __init__(self, main_window):
        self.main = main_window
    
    def render(self, BASE_DIR):
        layout = self.main.initial_config(previous_screen=self.main.loadFiles)
        self.main.stepper.avanzar(2)

        print("Archivos cargados para procesamiento con IA:")
        for ruta in self.main._loadFilesPage.file_input.rutas:
            print(ruta)

        # Animación de carga
        self.loading_label = QLabel()
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.movie = QMovie(os.path.join(BASE_DIR, "icons", "loading.gif"))
        self.movie.setScaledSize(QSize(120, 120))
        self.loading_label.setMovie(self.movie)
        self.movie.start()

        texto = createLabel("Procesando con IA...", size=11, bold=False)
        texto.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.loading_label)
        layout.addWidget(texto)

        # Solo lanzar el worker si no hay uno corriendo ya
        if self.main._worker is not None and self.main._worker.isRunning():
            return

        self.main._worker = AIWorker(
            strategy=loadStrategy(),
            prompt_path=os.path.join(BASE_DIR, "prompt v1.txt"),
            file_paths=self.main._loadFilesPage.file_input.rutas,
        )
        self.main._worker.finished.connect(self.on_respuesta)
        self.main._worker.error.connect(self.on_error)
        self.main._worker.start()

    def on_respuesta(self, texto: str):
        try:
            self.movie.stop()
            self.loading_label.hide()

            # Parsear el JSON y corregir fechas
            texto_limpio = re.sub(r"```json|```", "", texto).strip()
            data = json.loads(texto_limpio)
            data = fix_fechas(data)

            # Convertir de vuelta a string para pasarle al JsonEditor
            texto_corregido = json.dumps(data, ensure_ascii=False, indent=4)

            self.main.respuesta_ia = texto_corregido
            self.main.verificarRespuesta(texto_corregido)
        except Exception as e:
            import traceback
            print("ERROR en on_respuesta:", traceback.format_exc())

    def on_error(self, mensaje: str):
        try:
            self.movie.stop()
            self.loading_label.hide()
            QMessageBox.critical(self.main, "Error", f"Error al conectarse con la IA: {mensaje}")
        except Exception as e:
            import traceback
            print("ERROR en on_error:", traceback.format_exc())

def fix_fechas(data: dict) -> dict:
        hoy = date.today().strftime("%d/%m/%Y")

        def _recorrer(obj):
            if isinstance(obj, dict):
                for key in obj:
                    if "fecha" in key.lower():
                        obj[key] = hoy
                    else:
                        _recorrer(obj[key])
            elif isinstance(obj, list):
                for item in obj:
                    _recorrer(item)

        _recorrer(data)
        return data