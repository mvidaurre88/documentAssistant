# IMPORTS DE TERCEROS
import streamlit as st

# IMPORTS PROPIOS
from docs.base import DocumentBase

class PDD(DocumentBase):
    
    extension = "docx"
    mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    
    #TODO
    def render_form(self, data: dict) -> dict:
        return data
    
    # DEVUELVE LAS ACLARACIONES A MOSTRAR EN LA PANTALLA FINAL
    def get_aclaraciones(self) -> list[str]:
        return [
            "<b>Diagramas:</b> son generados y pueden contener imprecisiones. Utilícelos como guía y valídelos antes de su uso final.",
            "<b>Pasos:</b> son poco exhaustivos y no contienen imágenes. Se recomienda completarlos con información adicional.",
            "<b>Notificaciones:</b> se mantienen las del template. Ajustarlas según corresponda junto con los criterios de aceptación.",
            ]
        
    # DEVUELVE EL NOMBRE DEL ARCHIVO A DESCARGAR
    def get_filename(self) -> str:
        return f"PDD.{self.extension}"