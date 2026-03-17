import sys
import os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from narwhals import col
from builder import *
from docx_generator import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class mainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Nombre de la ventana, icono y tamaño
        self.setWindowTitle("IA Documentation Assistant")
        self.setWindowIcon(QIcon(os.path.join(BASE_DIR,"icons", "icon.ico")))
        self.setMinimumSize(750, 600)
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

        agregar_elementos(layout, (icono, 20), (titulo, 20), (btn_comenzar, Qt.AlignmentFlag.AlignCenter, 20))

    # Paso 1: elegir tipo de documento
    def selectDocumentType(self):
        # Config inicial
        layout = self.initial_config(previous_screen = self.initWindow)

        # Titulo
        titulo = createLabel("Seleccione el tipo de documento a generar", size=18, bold=True)
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

        agregar_elementos(layout, (titulo, 20), (container, Qt.AlignmentFlag.AlignCenter, 20))
        layout.addStretch()

    # Paso 2: cargar archivos con datos
    def loadFiles(self):
        # Config inicial
        layout = self.initial_config(previous_screen=self.selectDocumentType)

        # Avanzo la barra de pasos
        self.stepper.avanzar(1)

        # Titulo y subtitulo
        title = createLabel("Ingrese los archivos para procesar", size=18, bold=True)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle = createLabel("Puede ingresar screenshots, transcripciones de reuniones, o cualquier otro documento ", size=10, bold=False)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #cccccc;")

        self.archivos_container = QWidget()
        self.archivos_grid = QGridLayout(self.archivos_container)
        self.archivos_grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        for col in range(4):
            self.archivos_grid.setColumnStretch(col, 1)

        self.scroll_archivos = QScrollArea()
        self.scroll_archivos.setWidget(self.archivos_container)
        self.scroll_archivos.setWidgetResizable(True)
        self.scroll_archivos.setFixedHeight(140)
        self.scroll_archivos.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.scroll_archivos.setVisible(False)

        self.file_input = FileInput(tipos=["docx", "pdf", "txt", "png"], multiple=True)
        self.file_input.setFixedHeight(120)  # ← altura fija
        self.file_input.archivos_cargados.connect(self._actualizarListaArchivos)

        btn = createButton("Avanzar paso", 140, 32)
        btn.clicked.connect(self._validarYAvanzar)

        QTimer.singleShot(500, lambda: print(
        f"file_input width: {self.file_input.width()}",
        f"scroll width: {self.scroll_archivos.width()}",
        f"archivos_container width: {self.archivos_container.width()}"
        ))

        agregar_elementos(layout, (title, 20), (subtitle, 10), (self.file_input, 20), (self.scroll_archivos, 10),"stretch", (btn, Qt.AlignmentFlag.AlignCenter, 0))

    def _validarYAvanzar(self):
        if not self.file_input.rutas:
            QMessageBox.warning(self, "Atención", "Cargá al menos un archivo antes de continuar.")
            return
        self.connectToAI()

    def _actualizarListaArchivos(self, rutas):
        # Limpiar grilla
        while self.archivos_grid.count():
            item = self.archivos_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.scroll_archivos.setVisible(len(rutas) > 0)

        COLUMNAS = 4

        for i, ruta in enumerate(rutas):
            fila = i // COLUMNAS
            col  = i % COLUMNAS

            card = QWidget()
            card.setFixedSize(160, 60)
            card.setStyleSheet("QWidget { background-color: #2d2d2d; border-radius: 6px; }")

            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(8, 6, 6, 6)
            card_layout.setSpacing(20)

            icono = QLabel("📄")
            icono.setFixedWidth(20)

            nombre = QLabel(os.path.basename(ruta))
            nombre.setStyleSheet("color: #ffffff; font-size: 10px;")
            nombre.setWordWrap(True)

            btn_x = QPushButton("✕")
            btn_x.setFixedSize(20, 20)
            btn_x.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_x.setStyleSheet("""
                QPushButton { background: transparent; border: none; color: #aaa; font-size: 12px; padding: 0px; }
                QPushButton:hover { color: #e68200; }
            """)
            btn_x.clicked.connect(lambda _, r=ruta: self._eliminarArchivo(r))

            card_layout.addWidget(icono)
            card_layout.addWidget(nombre)
            card_layout.addStretch()
            card_layout.addWidget(btn_x)

            self.archivos_grid.addWidget(card, fila, col)

    def _eliminarArchivo(self, ruta):
        self.file_input.rutas.remove(ruta)
        self._actualizarListaArchivos(self.file_input.rutas)

    # Paso 3: Conectar con la IA para procesar datos
    def connectToAI(self):
        # Config inicial
        layout = self.initial_config(previous_screen = self.loadFiles)

        # Avanzo la barra de pasos
        self.stepper.avanzar(2)

        # Muestro archivos cargados (simulando que se envían a la IA)
        print("Archivos cargados para procesamiento con IA:")
        for ruta in self.file_input.rutas:
            print(ruta)

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
        layout = createLayout(spacing=0, margins=(30, 20, 30, 20), direction="vertical")
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