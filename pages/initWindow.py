from builder import *

class initWindow:
    def __init__(self, main_window):
        self.main = main_window
        
    def render(self, BASE_DIR):
        # Config inicial
        layout = self.main.initial_config(previous_screen = None, stretch=True)

        # Icono
        icono = createPixmap(os.path.join(BASE_DIR,"icons", "icon.ico"), 96, 96)
        icono.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Título
        titulo = createLabel("IA Documentation Assistant", size=22, bold=True)
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Botón para comenzar
        btn_comenzar = createButton("Comenzar")
        btn_comenzar.setFixedWidth(160)
        btn_comenzar.setFixedHeight(38)
        btn_comenzar.clicked.connect(self.main.selectDocumentType)

        agregar_elementos(layout, (icono, 20), (titulo, 20), (btn_comenzar, Qt.AlignmentFlag.AlignCenter, 20))
