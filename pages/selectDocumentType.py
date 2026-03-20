from builder import *
from pages import initWindow

#Paso 1: elegir tipo de documento
class selectDocumentType:
    def __init__(self, main_window):
        self.main = main_window
        
    def render(self, BASE_DIR):
        # Config inicial
        layout = self.main.initial_config(previous_screen = self.main.initWindow)

        # Titulo
        titulo = createLabel("Seleccione el tipo de documento a generar", size=18, bold=True)
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Botones para tipos de documento
        container, container_layout = createContainer(15, direction="horizontal")
        
        btn1 = createButton("Crear PDD", os.path.join(BASE_DIR,"icons", "icon2.ico"))
        btn1.clicked.connect(self.main.loadFiles)
            
        btn2 = createButton("Crear SDD", os.path.join(BASE_DIR,"icons", "icon2.ico"))
        btn2.clicked.connect(self.main.loadFiles)
            
        btn3 = createButton("Crear OH", os.path.join(BASE_DIR,"icons", "icon2.ico"))
        btn3.clicked.connect(self.main.loadFiles)
        
        for btn in [btn1, btn2, btn3]:
            btn.setMinimumHeight(120)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            container_layout.addWidget(btn)

        agregar_elementos(layout, (titulo, 20), (container, 20))
        layout.addStretch()