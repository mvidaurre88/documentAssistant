from builder import *

# Paso 2: cargar archivos con datos
class loadFiles:
    def __init__(self, main_window):
        self.main = main_window
        
    def render(self, BASE_DIR):
        # Config inicial
        layout = self.main.initial_config(previous_screen=self.main.selectDocumentType)

        # Avanzo la barra de pasos
        self.main.stepper.avanzar(1)

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

        self.file_input = FileInput(tipos=["docx", "pdf", "txt", "png", "jpg"], multiple=True)
        self.file_input.setFixedHeight(120)  # ← altura fija
        self.file_input.archivos_cargados.connect(self._actualizarListaArchivos)

        btn = createButton("Avanzar paso")
        btn.setFixedSize(140, 32)
        btn.clicked.connect(self._validarYAvanzar)

        agregar_elementos(layout, (title, 20), (subtitle, 10), (self.file_input, 20), (self.scroll_archivos, 10),"stretch", (btn, Qt.AlignmentFlag.AlignCenter, 0))

    def _validarYAvanzar(self):
        if not self.file_input.rutas:
            QMessageBox.warning(self.main, "Atención", "Cargá al menos un archivo antes de continuar.")
            return
        self.main.connectToAI()

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
