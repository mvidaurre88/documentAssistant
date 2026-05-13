from openpyxl.utils import get_column_letter
from xlsxtpl.writerx import BookWriter
from PIL import ImageFont
from io import BytesIO
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import PatternFill
import os
from copy import copy

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATHS = [ ("/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf", 1.0), ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 0.85)]
FONT_WIDTH_MULTIPLIER = {
    "times new roman": 1.20,
    "verdana": 1.05,
}

VERDE    = PatternFill(start_color="92D050", end_color="92D050", fill_type="solid")
AMARILLO = PatternFill(start_color="FFFF66", end_color="FFFF66", fill_type="solid")
ROJO     = PatternFill(start_color="C00000", end_color="C00000", fill_type="solid")
BLANCO   = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")

# Multiplicador de altura adicional para fuentes serif (interlineado mayor)
FONT_HEIGHT_MULTIPLIER = {
    "times new roman": 1.15,
    "times": 1.15,
    "cambria": 1.10,
    "georgia": 1.12,
    "garamond": 1.05,
}


def _get_font_and_correction(size):
    """Devuelve (font, correction_factor). Carlito = 1.0, DejaVu = 0.85."""
    for path, correction in FONT_PATHS:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, int(size)), correction
            except OSError:
                continue
    return ImageFont.load_default(), 0.85


def generate(context):
    
    context = expandir_tdd(context)
    
    # CARGO EL TEMPLATE -----------------------------------------------------------------------------
    template_path = os.path.join(BASE_DIR, "templates", "TDD.xlsx")
    writer = BookWriter(template_path)
    
    # ARMO LOS PAYLOADS DE LAS 3 HOJAS FIJAS --------------------------------------------------------
    payloads = [
        {
            "tpl_idx": 0,
            "sheet_name": "Cover",
            "nombreBot": context.get("nombreBot", ""),
            "codigoBot": context.get("codigoBot", ""),
            "descripcionBot": context.get("descripcionBot", ""),
            "version": context.get("version", ""),
        },
        {
            "tpl_idx": 1,
            "sheet_name": "Doc Info",
            "cliente": context.get("cliente", ""),
            "nombreProyecto": context.get("nombreProyecto", ""),
            "codigoBot": context.get("codigoBot", ""),
            "descripcionBot": context.get("descripcionBot", ""),
            "modificaciones": context.get("modificaciones", []),
        },
        {
            "tpl_idx": 2,
            "sheet_name": "Descripción del proceso",
            "inputsProceso": context.get("inputsProceso", []),
            "pasosProceso": context.get("pasosProceso", []),
        }
    ]
    
    # AGREGO UN PAYLOAD POR CADA ESCENARIO ----------------------------------------------------------
    # Si el escenario tiene 1 caso uso Escenario_Single (tpl_idx=3),
    # si tiene varios casos uso Escenario_Complejo (tpl_idx=4)
    titulos_por_hoja = {}
    for esc in context.get("escenarios", []):
        is_single = len(esc.get("casos", [])) <= 1
        tpl_idx = 3 if is_single else 4
        sheet_name = f"Escenario {esc.get('numero', '')}"
        
        if len(esc.get("casos", [])) > 1:  # solo escenarios complejos
            sheet_name = f"Escenario {esc.get('numero', '')}"
            titulos_por_hoja[sheet_name] = [c.get("titulo", "") for c in esc["casos"]]
        
        payload = {
            "tpl_idx": tpl_idx,
            "sheet_name": sheet_name,
            "numero": esc.get("numero", ""),
            "titulo": esc.get("titulo", ""),
            "casos": esc.get("casos", []),
            "fecha": context.get("fecha", ""),
        }
        # Para Escenario_Single, además expongo el primer (y único) caso como "caso"
        if is_single and esc.get("casos"):
            primer_caso = esc["casos"][0]
            payload["caso"] = primer_caso
            payload["fecha"] = context.get("fecha", "")
            payload["desarrollador"] = context.get("desarrollador", "")
        payloads.append(payload)
    
    writer.render_book(payloads=payloads)
    
    # HAGO VISIBLES TODAS LAS HOJAS, OCULTO GRIDLINES Y AJUSTO ALTURAS ------------------------------
    for ws in writer.workbook._sheets:
        ws.sheet_state = "visible"
        ws.sheet_view.showGridLines = False
        if ws.title in titulos_por_hoja:
            distribuir_titulos(ws, titulos_por_hoja[ws.title])
        autofit_wrapped_rows(ws)
        aplicar_formato_condicional_resultados(ws)
    writer.workbook.active = 0
    writer.custom_doc_props = ()

    # GUARDO EN BUFFER ------------------------------------------------------------------------------
    buffer = BytesIO()
    writer.workbook.save(buffer)
    buffer.seek(0)
    
    return buffer


def _build_merge_map(ws):
    """
    Devuelve dos dicts:
    - merge_widths: {(row, col): ancho_total_en_unidades_excel} para celdas anchor de merges.
    - merged_skip: set de (row, col) que son parte de un merge pero NO el anchor.
    """
    merge_widths = {}
    merged_skip = set()
    
    for merged_range in ws.merged_cells.ranges:
        min_col, min_row, max_col, max_row = (
            merged_range.min_col, merged_range.min_row,
            merged_range.max_col, merged_range.max_row
        )
        
        # Sumar anchos de todas las columnas del merge
        ancho_total = 0
        for col in range(min_col, max_col + 1):
            col_letter = get_column_letter(col)
            dim = ws.column_dimensions.get(col_letter)
            ancho_total += (dim.width if dim and dim.width else 8.43)
        
        # La anchor es la celda top-left
        merge_widths[(min_row, min_col)] = ancho_total
        
        # Marcar las otras celdas del merge para no procesarlas
        for r in range(min_row, max_row + 1):
            for c in range(min_col, max_col + 1):
                if (r, c) != (min_row, min_col):
                    merged_skip.add((r, c))
    
    return merge_widths, merged_skip


def autofit_wrapped_rows(ws, default_font_size=11, line_height_factor=1.4, min_height=18):
    PX_POR_UNIDAD = 4.5   # mucho más conservador
    PADDING_CELDA = 10    # NUEVO: padding interno de Excel (px)
    
    merge_widths, merged_skip = _build_merge_map(ws)
    
    anchos_col = {}
    for col_letter, dim in ws.column_dimensions.items():
        anchos_col[col_letter] = dim.width or 8.43
    
    for row in ws.iter_rows():
        max_lineas = 1
        max_font = default_font_size
        max_font_name = "calibri"
        
        for cell in row:
            if cell.value is None:
                continue
            if not (cell.alignment and cell.alignment.wrap_text):
                continue
            if (cell.row, cell.column) in merged_skip:
                continue
            
            if (cell.row, cell.column) in merge_widths:
                ancho_unidades = merge_widths[(cell.row, cell.column)]
            else:
                ancho_unidades = anchos_col.get(cell.column_letter, 8.43)
            
            # CAMBIO: restar padding del ancho disponible
            ancho_px = max(20, ancho_unidades * PX_POR_UNIDAD - PADDING_CELDA)
            
            font_size = default_font_size
            font_name = "calibri"
            if cell.font:
                if cell.font.size:
                    font_size = int(cell.font.size)
                if cell.font.name:
                    font_name = cell.font.name.lower().strip()
            
            font_width_mult = FONT_WIDTH_MULTIPLIER.get(font_name, 1.0)
            
            font, correction = _get_font_and_correction(font_size)
            effective_correction = correction * font_width_mult
            
            texto = str(cell.value).replace("\r\n", "\n").replace("\r", "\n")
            
            total_lineas = 0
            for parrafo in texto.split("\n"):
                if not parrafo:
                    total_lineas += 1
                    continue
                
                palabras = parrafo.split(" ")
                linea_actual = ""
                lineas_parrafo = 0
                
                for palabra in palabras:
                    test = (linea_actual + " " + palabra).strip() if linea_actual else palabra
                    try:
                        ancho_test = font.getlength(test) * effective_correction
                    except AttributeError:
                        ancho_test = font.getsize(test)[0] * effective_correction
                    
                    if ancho_test <= ancho_px:
                        linea_actual = test
                    else:
                        if linea_actual:
                            lineas_parrafo += 1
                        linea_actual = palabra
                
                if linea_actual:
                    lineas_parrafo += 1
                
                total_lineas += max(1, lineas_parrafo)
            
            if total_lineas > max_lineas:
                max_lineas = total_lineas
                max_font = max(max_font, font_size)
                max_font_name = font_name
        
        if max_lineas > 1:
            height_mult = FONT_HEIGHT_MULTIPLIER.get(max_font_name, 1.0)
            lineas_con_margen = max_lineas + 1  # mantener margen
            alto = max(min_height, lineas_con_margen * max_font * line_height_factor * height_mult)
            ws.row_dimensions[row[0].row].height = alto


"""
Expansor de TDD compacto.

El nuevo prompt devuelve los casos en formato compacto: solo declara
qué excepción se dispara, en qué paso falla, y qué pasos finales se
ejecutan a pesar de la falla. Este módulo reconstruye la lista completa
de pasos con sus comentarios, manteniendo la estructura que el template
TDD.xlsx espera.

Uso típico:

    from tdd_expander import expandir_tdd
    
    context = json.loads(respuesta_llm)
    context = expandir_tdd(context)
    buffer = generate(context)
"""

COMENTARIO_OK = "El paso se concretó como lo esperado."
COMENTARIO_FALLA = "El paso no pudo concretarse; por lo que el resultado de la prueba es correcto."
COMENTARIO_OMITIDO = "Se omitió el paso"

# Campos auxiliares que el LLM devuelve en formato compacto y que NO
# queremos que lleguen al template (para no ensuciar el render).
CAMPOS_AUXILIARES = ("excepcion", "pasoFalla", "pasosFinalesEjecutados", "datosPrueba")


def expandir_caso(caso, pasos_proceso):
    """
    Convierte un caso compacto en la lista completa de pasos detallados
    con resultado, comentario, datosPrueba y captura.

    Reglas:
    - Happy Path (pasoFalla = None) -> todos los pasos OK.
    - Pasos previos al pasoFalla    -> OK.
    - Paso == pasoFalla             -> FALLA.
    - Pasos posteriores listados en
      pasosFinalesEjecutados        -> OK (notificación se manda igual).
    - Resto de pasos posteriores    -> OMITIDO.
    """
    paso_falla = caso.get("pasoFalla")
    paso_falla = int(paso_falla) if paso_falla not in (None, "", "null") else None
    finales = {int(x) for x in (caso.get("pasosFinalesEjecutados") or []) if str(x).strip()}
    datos = caso.get("datosPrueba", {}) or {}

    pasos_expandidos = []
    for paso in pasos_proceso:
        n = int(paso.get("numero"))

        if paso_falla is None or n < paso_falla:
            comentario = COMENTARIO_OK
        elif n == paso_falla:
            comentario = COMENTARIO_FALLA
        elif n in finales:
            comentario = COMENTARIO_OK
        else:
            comentario = COMENTARIO_OMITIDO

        # datosPrueba puede venir con clave string o int desde el JSON
        dato = datos.get(str(n)) or datos.get(n) or "N/A"

        pasos_expandidos.append({
            "numero": n,
            "descripcion": paso.get("descripcion", ""),
            "datosPrueba": dato,
            "resultado": "Correcto",
            "comentario": comentario,
            "captura": "N/A",
        })

    return pasos_expandidos


def expandir_tdd(context):
    """
    Expande in-place todos los casos de todos los escenarios del context.
    Devuelve el mismo dict modificado, listo para pasar a generate().
    """
    pasos_proceso = context.get("pasosProceso", [])

    for escenario in context.get("escenarios", []):
        for caso in escenario.get("casos", []):
            # Si ya viene expandido (tiene "pasos"), no lo toco.
            if "pasos" in caso and caso["pasos"]:
                continue

            caso["pasos"] = expandir_caso(caso, pasos_proceso)

            # Limpio los campos auxiliares para no ensuciar el template
            for campo in CAMPOS_AUXILIARES:
                caso.pop(campo, None)

    return context

def aplicar_formato_condicional_resultados(ws):
    """
    Aplica formato condicional en la columna D desde la fila 8 en adelante.
    Verde = Correcto, Amarillo = Con observaciones, Rojo = Defecto, Blanco = N/A.
    """
    rango = "D8:D200"  # 200 filas debería sobrar para cualquier caso
    
    ws.conditional_formatting.add(
        rango,
        CellIsRule(operator="equal", formula=['"Correcto"'], fill=VERDE)
    )
    ws.conditional_formatting.add(
        rango,
        CellIsRule(operator="equal", formula=['"Con observaciones"'], fill=AMARILLO)
    )
    ws.conditional_formatting.add(
        rango,
        CellIsRule(operator="equal", formula=['"Defecto"'], fill=ROJO)
    )
    ws.conditional_formatting.add(
        rango,
        CellIsRule(operator="equal", formula=['"N/A"'], fill=BLANCO)
    )
    
def distribuir_titulos(ws, titulos, fila_titulos=2, filas_a_replicar=(3, 4), col_inicial=2):
    """
    Distribuye los títulos en columnas horizontales (B2, C2, D2...) 
    y replica el contenido y formato de las filas indicadas en filas_a_replicar
    a las nuevas columnas.
    
    Args:
        titulos: lista de títulos a distribuir.
        fila_titulos: fila donde van los títulos (por default fila 2).
        filas_a_replicar: tupla con filas cuyo contenido se replica en las nuevas columnas.
        col_inicial: columna donde arranca todo (2 = B).
    """
    if not titulos:
        return
    
    # 1. Distribuir los títulos en la fila de títulos
    cell_titulo_base = ws.cell(row=fila_titulos, column=col_inicial)
    
    for i, titulo in enumerate(titulos):
        col_idx = col_inicial + i
        cell = ws.cell(row=fila_titulos, column=col_idx)
        cell.value = titulo
        
        # Replicar formato de la celda base de títulos
        if i > 0 and cell_titulo_base.has_style:
            cell.font = copy(cell_titulo_base.font)
            cell.fill = copy(cell_titulo_base.fill)
            cell.border = copy(cell_titulo_base.border)
            cell.alignment = copy(cell_titulo_base.alignment)
            cell.number_format = cell_titulo_base.number_format
    
    # 2. Replicar las filas adicionales (3, 4, etc.) a las columnas nuevas
    for fila in filas_a_replicar:
        cell_base = ws.cell(row=fila, column=col_inicial)
        valor_base = cell_base.value
        
        # Si la celda base está vacía, no hay nada que copiar
        if valor_base is None:
            continue
        
        for i in range(1, len(titulos)):  # arrancar en 1 porque la columna 0 ya tiene su valor
            col_idx = col_inicial + i
            cell = ws.cell(row=fila, column=col_idx)
            cell.value = valor_base
            
            if cell_base.has_style:
                cell.font = copy(cell_base.font)
                cell.fill = copy(cell_base.fill)
                cell.border = copy(cell_base.border)
                cell.alignment = copy(cell_base.alignment)
                cell.number_format = cell_base.number_format