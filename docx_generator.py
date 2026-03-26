from docxtpl import DocxTemplate
from docx import Document
from docx.oxml import OxmlElement
from docx.shared import RGBColor
from docx.oxml.ns import qn
from close_file import close_file
from word_formatter import format_richtext, agregar_bookmark, agregar_link_interno
import json
from jinja2 import Undefined, Environment

class KeepUndefined(Undefined):
    def __str__(self):
        return f"{{{{{self._undefined_name}}}}}"
    def __repr__(self):
        return f"{{{{{self._undefined_name}}}}}"

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

def generate_docx(jsonText):
    
    # Cargo el template
    tpl = DocxTemplate(r"C:\Users\mvidaurre\Desktop\RPA\documentAssistant\templatePDD.docx")

    # Cargo el JSON obtenido
    if (jsonText is not None):
        context = json.loads(jsonText)

    # Formateo todos los campos que tengan richText
    campos_richtext = ["propositoProceso"]
    for campo in campos_richtext:
        if campo in context and isinstance(context[campo], str):
            context[campo] = format_richtext(context[campo])

    # Formateo las excepciones
    excepciones = context.get("excepciones", [])
    
    excepcionesSys = [e for e in excepciones if e["tipo"] in ("tecnica", "técnica")]
    context["excepcionesSys"] = excepcionesSys
    
    excepcionesNeg = [e for e in excepciones if e["tipo"] == "negocio"]
    context["excepcionesNeg"] = excepcionesNeg

    mapa_excepciones = {e["escenario"]: e["numero"] for e in excepciones}
    fases_data = context["fases"]
    
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

    context["fases"] = fases_data

    faltantes = [var for var in variables_template if var not in context]
    vacios     = [key for key, value in context.items() if value == "" or value is None]
    print("Campos faltantes:", faltantes)
    print("Campos vacios:", vacios)

    variables_template = tpl.get_undeclared_template_variables()
    for var in variables_template:
        val = context.get(var)
        if val is None or val == "":
            context[var] = f"{{{{{var}}}}}"

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
    generate_docx()

if __name__ == "__main__":
    main()