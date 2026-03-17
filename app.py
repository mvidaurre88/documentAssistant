import sys
import os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from builder import *
from docx_generator import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class mainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Nombre de la ventana, icono y tamaño
        self.setWindowTitle("IA Documentation Assistant")
        self.setWindowIcon(QIcon(os.path.join(BASE_DIR,"icons", "icon.ico")))
        self.setMinimumSize(750, 500)
        self.initWindow()

    def initWindow(self):
        # Config inicial
        layout = self.initial_config(previous_screen = None, stretch=True)

        # Icono
        icono = createPixmap(os.path.join(BASE_DIR,"icons", "icon.ico"), 96, 96)
        icono.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Título
        titulo = createLabel("IA Documentation Assistant", size=22, bold=True)
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Botón para comenzar
        btn_comenzar = createButton("Comenzar", 160, 38)
        btn_comenzar.clicked.connect(self.selectDocumentType)

        # Stepper para proximas etapas
        self.stepper = Stepper(["Inicio", "Cargar datos", "Generar archivo", "Verificar datos", "Fin"])

        layout.addWidget(icono)
        layout.addWidget(titulo)
        layout.addWidget(btn_comenzar, alignment=Qt.AlignmentFlag.AlignCenter)

    # Paso 1: elegir tipo de documento
    def selectDocumentType(self):
        # Config inicial
        layout = self.initial_config(previous_screen = self.initWindow)

        # Titulo
        titulo = createLabel("Selecciona el tipo de documento a generar", size=18, bold=True)
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Botones para tipos de documento
        btn1 = createButton("Crear PDD", 250, 32, os.path.join(BASE_DIR,"icons", "icon2.ico"))
        btn1.clicked.connect(self.loadFiles)
        
        btn2 = createButton("Crear SDD", 250, 32, os.path.join(BASE_DIR,"icons", "icon2.ico"))
        btn2.clicked.connect(self.loadFiles)
        
        btn3 = createButton("Crear OH", 250, 32, os.path.join(BASE_DIR,"icons", "icon2.ico"))
        btn3.clicked.connect(self.loadFiles)

        container, container_layout = createContainer(35)

        container_layout.addWidget(btn1)
        container_layout.addWidget(btn2)
        container_layout.addWidget(btn3)

        layout.addWidget(self.stepper)
        layout.addWidget(titulo)
        layout.addWidget(container)

    # Paso 2: cargar archivos con datos
    def loadFiles(self):
        # Config inicial
        layout = self.initial_config(previous_screen = self.selectDocumentType)

        # Avanzo la barra de pasos
        self.stepper.avanzar(1)

        # FileInput que soporta multiples archivos y tipos específicos
        self.file_input = FileInput(tipos=["docx", "pdf", "txt"], multiple=True)
        self.file_input.archivos_cargados.connect(lambda rutas: print(rutas))

        btn = createButton("Avanzar paso", 140, 32)
        btn.clicked.connect(self.connectToAI)

        layout.addWidget(self.stepper)
        layout.addWidget(self.file_input)
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def onArchivoSeleccionado(self, ruta):
        print(f"Archivo cargado: {ruta}")
        self.ruta_archivo = ruta

    # Paso 3: Conectar con la IA para procesar datos
    def connectToAI(self):
        # Config inicial
        layout = self.initial_config(previous_screen = self.loadFiles)

        # Avanzo la barra de pasos
        self.stepper.avanzar(2)

        # Animación de carga
        loading_label = QLabel()
        loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        movie = QMovie(os.path.join(BASE_DIR, "icons", "loading.gif"))
        movie.setScaledSize(QSize(120, 120))
        loading_label.setMovie(movie)
        movie.start()

        # Texto debajo del gif
        texto = createLabel("Procesando con IA...", size=11, bold=False)
        texto.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.stepper)
        layout.addWidget(loading_label)
        layout.addWidget(texto)

        # Para simular que me conecto a la IA
        QTimer.singleShot(10000, self.verificarRespuesta)
        
    # Paso 4: Verificar respuesta de la IA
    def verificarRespuesta(self):
        # Config inicial
        layout = self.initial_config(previous_screen = self.connectToAI)

        # Avanzo la barra de pasos
        self.stepper.avanzar(3)

        ruta_json = os.path.join(BASE_DIR, "ejemplo.json")

        if not os.path.exists(ruta_json):
            QMessageBox.critical(self, "Error", f"No se encontró el archivo ejemplo.json en {BASE_DIR}")
            return

        editor = JsonEditor(ruta_json)
        scroll = QScrollArea()
        scroll.setWidget(editor)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        btn = createButton("Generar documento", 160, 32)
        btn.clicked.connect(self.generarDocumento)

        layout.addWidget(self.stepper)
        layout.addWidget(scroll)
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def generarDocumento(self):
        # Config inicial
        layout = self.initial_config(previous_screen = self.verificarRespuesta)

        # Avanzo la barra de pasos
        self.stepper.avanzar(4)

        generate_docx()

    def initial_config(self, previous_screen, stretch=False):

        central = QWidget()
        self.setCentralWidget(central)

        # Layout
        layout = createLayout(spacing=20, margins=(30, 20, 30, 20), direction="vertical")
        if stretch:
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        central.setLayout(layout)

        if previous_screen:
            # Botón para volver al paso anterior
            backButton = createButton("← Volver", 90, 28)
            backButton.clicked.connect(lambda: self.volver(previous_screen))
            backButton.setStyleSheet("""
                QPushButton {background: transparent; border: none; color: #aaa; font-size: 13px;}
                QPushButton:hover {color: #e68200;}
            """)
            layout.addWidget(backButton, alignment=Qt.AlignmentFlag.AlignLeft)
            layout.addWidget(self.stepper)

        return layout

    def volver(self, previous_screen):
        self.stepper.retroceder(1) 
        previous_screen()

if __name__ == "__main__":
   app = QApplication(sys.argv)
   
   # Configuro estilo para todos los elementos de la aplicación
   app.setStyleSheet("""
        QMainWindow, QWidget {background-color: #3c3c3c; font-family: Consolas;}
                     
        QPushButton {background-color: #e68200; color: #ffffff; font-weight: bold; font-size: 15px; padding: 6px 12px; border-radius: 3px;}
                     
        QPushButton:hover {background-color: #ff9500;}
        
        QPushButton:pressed {background-color: #b36500;}
        
        QLineEdit, QTextEdit {background-color: #2d2d2d; color: #d4d4d4; border: 1px solid #555; padding: 4px;}
        
        QLabel {color: #ffffff;} 
    """)
   
   window = mainWindow()
   window.show()
   sys.exit(app.exec())