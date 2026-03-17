from datetime import date
from docxtpl import DocxTemplate
from docx import Document
from docx.oxml import OxmlElement
from docx.shared import RGBColor
from docx.oxml.ns import qn
from close_file import close_file
from word_formatter import format_richtext, agregar_bookmark, agregar_link_interno
import json

def crear_subdoc_fase(tpl, fase):
    """Crea un subdocumento con título + tabla para una fase."""
    sd = tpl.new_subdoc()
    sd.add_paragraph(fase["tituloFase"], style="Heading 2")
    tabla = sd.add_table(rows=1, cols=4)
    tabla.style = 'Table Grid'
    headers = ["N°", "Acción", "Detalle", "Excepción"]
    for i, h in enumerate(headers):
        tabla.rows[0].cells[i].text = h
    for paso in fase["pasos"]:
        row = tabla.add_row()
        #row.cells[0].text = paso["numero"]
        row.cells[1].text = paso["accion"]
        row.cells[2].text = paso["detalle"]
        #row.cells[3].text = paso.get("excepcion_numero", "")
    return sd

def generate_docx():

    tpl = DocxTemplate(r"C:\Users\mvidaurre\Desktop\RPA\templatePDD.docx")  # <-- adentro
    fecha = date.today().strftime("%d/%m/%Y")

    excepcionesSys_raw = [
        {"escenario": "Error de conexión a SharePoint", "accion": "Reintentar conexión 3 veces. Si persiste, enviar alerta a soporte técnico."},
        {"escenario": "Archivo Excel no accesible",     "accion": "Verificar que el archivo esté disponible."},
    ]
    excepcionesNeg_raw = [
        {"escenario": "Archivo faltante",    "accion": "Se registra en el reporte final."},
        {"escenario": "Nombre incorrecto",   "accion": "Se registra el error de nomenclatura en el reporte final."},
    ]

    excepcionesSys = [{"numero": f"4.2.{i+1}", **e} for i, e in enumerate(excepcionesSys_raw)]
    offset = len(excepcionesSys)
    excepcionesNeg = [{"numero": f"4.2.{i+1+offset}", **e} for i, e in enumerate(excepcionesNeg_raw)]
    mapa_excepciones = {e["escenario"]: e["numero"] for e in excepcionesSys + excepcionesNeg}

    fases_data = [
        {
            "tituloFase": "Tomar datos divisas",
            "pasos": [
                {"accion": "Abrir Excel",       "detalle": "Abrimos el archivo...", "excepcion_escenario": "Error de conexión a SharePoint"},
                {"accion": "Ingresar DolarHoy", "detalle": "Abrimos navegador...",  "excepcion_escenario": "Archivo Excel no accesible"},
            ]
        },
        {
            "tituloFase": "Cargar datos en formulario",
            "pasos": [
                {"accion": "Ingresar formulario", "detalle": "Ingresamos al link...", "excepcion_escenario": "Archivo faltante"},
            ]
        },
    ]

    # Enumerar pasos y agregar número de excepción desde el mapa
    paso_counter = [1]
    for fase in fases_data:
        for paso in fase["pasos"]:
            paso["numero"] = f"3.1.{paso_counter[0]}"
            paso["excepcion_numero"] = mapa_excepciones.get(paso["excepcion_escenario"], "")
            paso_counter[0] += 1

    # Generar subdocs DESPUÉS de crear tpl
    fases_subdocs = [crear_subdoc_fase(tpl, f) for f in fases_data]

    variables_template = tpl.get_undeclared_template_variables()

    # Usar ruta absoluta para asegurarse
    ruta = r"C:\Users\mvidaurre\Desktop\RPA\ejemplo.json"

    with open(ruta, "r", encoding="utf-8") as f:
        context = json.load(f)

    fases_data = context["fases"]

    todas_excepciones = context.get("excepciones", [])
    excepcionesSys = [e for e in todas_excepciones if e["tipo"] == "tecnica"]
    excepcionesNeg = [e for e in todas_excepciones if e["tipo"] == "negocio"]

    mapa_excepciones = {e["escenario"]: e["numero"] for e in todas_excepciones}

    # Enumerar pasos y agregar número de excepción
    paso_counter = [1]
    for fase in fases_data:
        for paso in fase["pasos"]:
            paso["numero"] = f"3.1.{paso_counter[0]}"
            paso["excepcion_numero"] = mapa_excepciones.get(paso.get("excepcion_escenario", ""), "")
            paso_counter[0] += 1

    context["excepcionesSys"] = excepcionesSys
    context["excepcionesNeg"] = excepcionesNeg
    context["fases"] = fases_data

    faltantes = [var for var in variables_template if var not in context]
    vacios     = [key for key, value in context.items() if value == "" or value is None]
    print("Campos faltantes:", faltantes)
    print("Campos vacios:", vacios)

    tpl.render(context)
    tpl.save(r"C:\Users\mvidaurre\Desktop\RPA\output.docx")

    doc = Document(r"C:\Users\mvidaurre\Desktop\RPA\output.docx")

    # Insertar tabla después de cada título de fase
    for fase in fases_data:
        for i, para in enumerate(doc.paragraphs):
            if para.text.strip() == fase["tituloFase"]:
                tabla = doc.add_table(rows=1, cols=4)
                tabla.style = 'Table Grid'
                headers = ["N°", "Acción", "Detalle", "Excepción"]
                for j, h in enumerate(headers):
                    cell = tabla.rows[0].cells[j]
                    cell.text = h
                    # Fondo naranja
                    tcPr = cell._tc.get_or_add_tcPr()
                    shd = OxmlElement('w:shd')
                    shd.set(qn('w:fill'), 'ED7D31')
                    shd.set(qn('w:val'), 'clear')
                    shd.set(qn('w:color'), 'auto')
                    tcPr.append(shd)
                    # Texto blanco y negrita
                    run = cell.paragraphs[0].runs[0]
                    run.bold = True
                    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                for paso in fase["pasos"]:
                    row = tabla.add_row()
                    row.cells[0].text = paso["numero"]
                    row.cells[1].text = paso["accion"]
                    row.cells[2].text = paso["detalle"]
                    row.cells[3].text = paso.get("excepcion_numero", "")
                para._p.addnext(tabla._tbl)
                break
    doc.save(r"C:\Users\mvidaurre\Desktop\RPA\output.docx")
    print("Listo!")

def main():
    close_file("output.docx")
    generate_docx()

if __name__ == "__main__":
    main()