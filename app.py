import sys
import os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from narwhals import col
from builder import *
from docx_generator import *
from AIConnector import *

from pages.initWindow import initWindow
from pages.selectDocumentType import selectDocumentType
from pages.loadFiles import loadFiles as loadFilesPage
from pages.connectToAI import connectToAI as connectToAIPage
from pages.verifyResponse import verifyResponse as verifyResponsePage

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class mainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._worker = None

        # Nombre de la ventana, icono y tamaño
        self.setWindowTitle("IA Documentation Assistant")
        self.setWindowIcon(QIcon(os.path.join(BASE_DIR,"icons", "icon.ico")))
        self.setMinimumSize(750, 600)
        self.initWindow()
        self.stepper = Stepper(["Inicio", "Cargar datos", "Generar archivo", "Verificar datos", "Fin"])

    def initWindow(self):
        initWindow(self).render(BASE_DIR)

    # Paso 1: Elegir tipo de documento -----------------------------------------
    def selectDocumentType(self):
        selectDocumentType(self).render(BASE_DIR)

    # Paso 2: Cargar archivos con datos ----------------------------------------
    def loadFiles(self):
        self._loadFilesPage = loadFilesPage(self)
        self._loadFilesPage.render(BASE_DIR)

    # Paso 3: Conectar con la IA para procesar datos ---------------------------
    def connectToAI(self):
        self._connectToAIPage = connectToAIPage(self)
        self._connectToAIPage.render(BASE_DIR)

    # Paso 4: Verificar respuesta de la IA y editar datos si es necesario ------
    def verificarRespuesta(self, response=None):
        self._verifyResponsePage = verifyResponsePage(self)  # ← guardás la instancia
        self._verifyResponsePage.render(response)

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
        layout = createLayout(spacing=0, margins=(30, 20, 30, 20), direction="vertical")
        if stretch:
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        central.setLayout(layout)

        if previous_screen:
            # Botón para volver al paso anterior
            backButton = createButton("← Volver")
            backButton.setFixedWidth(90)
            backButton.setFixedHeight(28)
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
    import traceback

    def handle_exception(exc_type, exc_value, exc_tb):
        print("CRASH NO CAPTURADO:")
        traceback.print_exception(exc_type, exc_value, exc_tb)

    sys.excepthook = handle_exception

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