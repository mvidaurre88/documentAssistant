import streamlit as st

# IMPORTS PROPIOS
from docs.base import DocumentBase

class SDD(DocumentBase):
    
    extension = "docx"
    mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    
    #TODO
    def render_form(self, data: dict) -> dict:
        return data
    
    # DEVUELVE LAS ACLARACIONES A MOSTRAR EN LA PANTALLA FINAL
    def get_aclaraciones(self) -> list[str]:
        return [
            "<b>Diagramas:</b> son generados y pueden contener imprecisiones. Utilícelos como guía y valídelos antes de su uso final.",
        ]
        
    # DEVUELVE EL NOMBRE DEL ARCHIVO A DESCARGAR
    def get_filename(self) -> str:
        return f"SDD.{self.extension}"