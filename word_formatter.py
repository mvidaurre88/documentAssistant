from docxtpl import RichText
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

# ------------------
# FUNCION PARA FORMATEAR TEXTO CON SALTOS DE LINEA
# ------------------
def format_richtext(text):
    rt = RichText()
    lines = text.split('\n')
    for i, line in enumerate(lines):
        rt.add(line)
        if i < len(lines) - 1:
            rt.add('\a')
    return rt

# ------------------
# FUNCION PARA CREAR VINCULOS EXTERNOS (NO SE USA)
# ------------------
def format_hyperlink(tpl, text, url):
    rt = RichText()
    rt.add(text, url_id=tpl.build_url_id(url), color="0563C1", underline=True)
    return rt

bookmark_id = [0]

def agregar_bookmark(parrafo, nombre):
    bookmark_id[0] += 1
    start = OxmlElement('w:bookmarkStart')
    start.set(qn('w:id'), str(bookmark_id[0]))
    start.set(qn('w:name'), nombre)
    end = OxmlElement('w:bookmarkEnd')
    end.set(qn('w:id'), str(bookmark_id[0]))
    parrafo._p.insert(0, start)
    parrafo._p.append(end)

def agregar_link_interno(parrafo, texto, nombre_bookmark):
    for child in list(parrafo._p):
        if child.tag != qn('w:pPr'):
            parrafo._p.remove(child)
    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.set(qn('w:anchor'), nombre_bookmark)
    run = OxmlElement('w:r')
    rpr = OxmlElement('w:rPr')
    rstyle = OxmlElement('w:rStyle')
    rstyle.set(qn('w:val'), 'Hyperlink')
    rpr.append(rstyle)
    run.append(rpr)
    t = OxmlElement('w:t')
    t.text = texto
    run.append(t)
    hyperlink.append(run)
    parrafo._p.append(hyperlink)