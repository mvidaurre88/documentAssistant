import os
import json
import re
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *


def createLayout(spacing, margins, direction):
    if direction == "vertical":
        layout = QVBoxLayout()
    else:
        layout = QHBoxLayout()
    layout.setSpacing(spacing)
    layout.setContentsMargins(*margins)
    return layout

def createButton(text, icon_path=None):
    btn = QPushButton(text)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    if icon_path:
        btn.setIcon(QIcon(icon_path))
        btn.setIconSize(QSize(22, 22))
    return btn

def createLabel(text, size, bold):
    label = QLabel(text)
    weight = QFont.Weight.Bold if bold else QFont.Weight.Normal
    label.setFont(QFont("Consolas", size, weight))
    return label

def createPixmap(path, width, height):
    icon = QLabel()
    pixmap = QPixmap(path).scaled(
        width, height, Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation
    )
    icon.setPixmap(pixmap)
    return icon

def createContainer(spacing, direction="vertical"):
    container = QWidget()
    if direction == "vertical":
        container_layout = QVBoxLayout(container)
    else:
        container_layout = QHBoxLayout(container)
    container_layout.setSpacing(spacing)
    return container, container_layout

class Stepper(QWidget):
    def __init__(self, pasos):
        super().__init__()
        self.pasos = pasos
        self.paso_actual = 0
        self.setFixedHeight(80)

    def avanzar(self, paso):
        self.paso_actual = paso
        self.update()  # redibuja

    def retroceder(self, paso):
        self.paso_actual = max(0, self.paso_actual - paso)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        total = len(self.pasos)
        w = self.width()
        h = self.height()
        paso_w = w // total
        radio = 16

        COLOR_ACTIVO    = QColor("#e68200")
        COLOR_COMPLETO  = QColor("#b36500")
        COLOR_PENDIENTE = QColor("#555555")
        COLOR_TEXTO     = QColor("#ffffff")

        for i in range(total):
            cx = paso_w * i + paso_w // 2
            cy = h // 2 - 10

            # Línea conectora
            # Línea conectora
            if i < total - 1:
                next_cx = paso_w * (i + 1) + paso_w // 2

                if i + 1 <= self.paso_actual:
                    # Línea completa rellena
                    painter.setPen(QPen(COLOR_ACTIVO, 3))
                else:
                    # Línea pendiente
                    painter.setPen(QPen(COLOR_PENDIENTE, 3))
                
                painter.drawLine(cx + radio, cy, next_cx - radio, cy)

            # Círculo
            if i < self.paso_actual:
                color = COLOR_COMPLETO
            elif i == self.paso_actual:
                color = COLOR_ACTIVO
            else:
                color = COLOR_PENDIENTE

            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(cx - radio, cy - radio, radio * 2, radio * 2)

            # Número
            painter.setPen(QPen(COLOR_TEXTO))
            painter.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
            painter.drawText(cx - radio, cy - radio, radio * 2, radio * 2,
                            Qt.AlignmentFlag.AlignCenter, str(i + 1))

            # Texto debajo
            if i == self.paso_actual:
                painter.setFont(QFont("Consolas", 8))
                painter.drawText(
                    cx - paso_w // 2, cy + radio + 4, paso_w, 40,
                    Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap,
                    self.pasos[i]
                )

class FileInput(QWidget):
    # Señal para avisar que se cargó un archivo
    archivos_cargados = pyqtSignal(list)

    # Configuro el fileInput con tipos de archivos permitidos y si acepta multiples o no
    def __init__(self, placeholder="Arrastrá archivos o hacé click para buscar\n (*.docx *.pdf *.txt *.png)", tipos=None, multiple=False):
        super().__init__()
        self.tipos = tipos
        self.rutas = []
        self.multiple = multiple
        self.setAcceptDrops(True)
        self.setFixedHeight(200)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.label = QLabel(placeholder)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)

        self.layout_archivos = QVBoxLayout()
        self.layout_archivos.addWidget(self.label)
        self.setLayout(self.layout_archivos)

        self._aplicar_estilo_normal()

    def mousePressEvent(self, event):
        filtro = ""
        if self.tipos:
            exts = " ".join(f"*.{t}" for t in self.tipos)
            filtro = f"Archivos ({exts})"

        if self.multiple:
            paths, _ = QFileDialog.getOpenFileNames(self, "Seleccionar archivos", "", filtro)
        else:
            path, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo", "", filtro)
            paths = [path] if path else []

        if paths:
            self._setArchivos(paths)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self._aplicar_estilo_hover()

    def dragLeaveEvent(self, event):
        self._aplicar_estilo_normal()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            paths = [u.toLocalFile() for u in urls]
            if not self.multiple:
                paths = paths[:1]
            self._setArchivos(paths)
        self._aplicar_estilo_normal()

    def _setArchivos(self, paths):
        
        # Agrego las nuevas rutas a las anteriores, evitando duplicados
        self.rutas.extend(paths) 
        self.rutas = list(dict.fromkeys(self.rutas))
        self.archivos_cargados.emit(self.rutas) 

    def _aplicar_estilo_normal(self):
        self.setStyleSheet("""
            QWidget { background-color: #9f9f9f; border-radius: 6px; border: 1px solid #ffffff; }
            QWidget:hover { background-color: #7e7e7e; }
        """)

class JsonEditor(QWidget):
    datos_actualizados = pyqtSignal(dict)

    def __init__(self, ruta_o_texto):
        super().__init__()
        self.ruta_txt = None
        self.campos = {}

        # Si es una ruta a un archivo existente, lo lee
        if os.path.exists(ruta_o_texto):
            self.ruta_txt = ruta_o_texto
            with open(ruta_o_texto, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            # Si es texto directo, lo parsea como JSON
            # Limpia bloques ```json ... ``` por si Gemini los incluye
            texto = ruta_o_texto.strip()
            texto = re.sub(r"```json|```", "", texto).strip()
            self.data = json.loads(texto)

        layout = QVBoxLayout()
        self.setLayout(layout)
        self._construirCampos(self.data, layout)

        btn_guardar = createButton("Guardar cambios")
        btn_guardar.setFixedSize(160, 32)
        btn_guardar.clicked.connect(self.guardar)
        layout.addWidget(btn_guardar, alignment=Qt.AlignmentFlag.AlignRight)

    def _construirCampos(self, data, layout, prefijo="", nivel=0):
        for key, value in data.items():
            path = f"{prefijo}.{key}" if prefijo else key

            if isinstance(value, dict):
                # Título de sección
                titulo = QLabel(f"{'  ' * nivel}▶ {key}")
                titulo.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
                titulo.setStyleSheet("color: #e68200;")
                layout.addWidget(titulo)

                # Recursivo
                self._construirCampos(value, layout, prefijo=path, nivel=nivel+1)

            else:
                fila = QHBoxLayout()

                label = QLabel(f"{'  ' * nivel}{key}")
                label.setFixedWidth(200)
                label.setFont(QFont("Consolas", 9))

                input_widget = self._crearInput(value)
                self.campos[path] = input_widget

                fila.addWidget(label)
                fila.addWidget(input_widget)    
                layout.addLayout(fila)

    UMBRAL_LARGO = 60  # caracteres

    def _crearInput(self, valor):
        texto = str(valor)
        if isinstance(valor, (list, dict)) or len(texto) > self.UMBRAL_LARGO:
            input_widget = QTextEdit()
            input_widget.setPlainText(texto)
            input_widget.setStyleSheet("background-color: #2d2d2d; color: white; border: 1px solid #555;")
            # Agregá .text = input_widget.toPlainText para unificar la interfaz
            input_widget.text = input_widget.toPlainText

            input_widget.document().adjustSize()
            alto = int(input_widget.document().size().height()) + 20  # +20 de padding
            input_widget.setFixedHeight(max(60, min(alto, 300)))

        else:
            input_widget = QLineEdit(texto)
            input_widget.setStyleSheet("background-color: #2d2d2d; color: white; border: 1px solid #555;")
        return input_widget

    def _setValor(self, data, keys, valor, valor_original):
        for key in keys[:-1]:
            data = data[key]
        
        ultimo = keys[-1]
        try:
            if isinstance(valor_original, int):
                data[ultimo] = int(valor)
            elif isinstance(valor_original, float):
                data[ultimo] = float(valor)
            elif isinstance(valor_original, (list, dict)):
                # Si el original era lista o dict, parsear con ast
                import ast
                data[ultimo] = ast.literal_eval(valor)
            else:
                data[ultimo] = valor
        except (ValueError, SyntaxError):
            data[ultimo] = valor

    def _getValorOriginal(self, data, keys):
        """Obtiene el valor original para saber el tipo"""
        for key in keys:
            data = data[key]
        return data

    def guardar(self):
        for path, input_widget in self.campos.items():
            keys = path.split(".")
            valor_original = self._getValorOriginal(self.data, keys)
            self._setValor(self.data, keys, input_widget.text(), valor_original)

        # Emite el dict actualizado en lugar de guardar en disco
        self.datos_actualizados.emit(self.data)
        QMessageBox.information(self, "Guardado", "Cambios guardados correctamente")

def agregar_elementos(layout, *items):
        for item in items:
            if isinstance(item, tuple):
                if len(item) == 3:
                    widget, alignment, spacing = item
                    layout.addSpacing(spacing)
                    layout.addWidget(widget, alignment=alignment)
                elif len(item) == 2:
                    # distinguir si es (widget, alignment) o (widget, spacing)
                    widget, segundo = item
                    if isinstance(segundo, int):
                        layout.addSpacing(segundo)
                        layout.addWidget(widget)
                    else:
                        layout.addWidget(widget, alignment=segundo)
            elif item == "stretch":
                layout.addStretch()
            else:
                layout.addStretch(item)