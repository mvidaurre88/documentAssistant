from builder import *

class verifyResponse:
    def __init__(self, main_window):
        self.main = main_window

    def render(self, response=None):
        layout = self.main.initial_config(previous_screen=self.main.loadFiles)
        self.main.stepper.avanzar(3)

        if response is None:
            QMessageBox.critical(self.main, "Error", "No se recibió respuesta de la IA.")
            return

        self.editor = JsonEditor(response)
        self.editor.datos_actualizados.connect(self._onDatosActualizados)

        scroll = QScrollArea()
        scroll.setWidget(self.editor)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        btn = createButton("Generar documento")
        btn.setFixedSize(160, 32)
        btn.clicked.connect(self.main.generarDocumento)

        layout.addWidget(scroll)
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def _onDatosActualizados(self, data: dict):
        self.main.respuesta_ia = data