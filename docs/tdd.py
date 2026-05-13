import streamlit as st

# IMPORTS PROPIOS
from docs.base import DocumentBase

class TDD(DocumentBase):
    
    extension = "xlsx"
    mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    #TODO
    def render_form(self, data: dict) -> dict:
        return data
    
    # DEVUELVE LAS ACLARACIONES A MOSTRAR EN LA PANTALLA FINAL
    def get_aclaraciones(self) -> list[str]:
        return []
        
    # DEVUELVE EL NOMBRE DEL ARCHIVO A DESCARGAR
    def get_filename(self) -> str:
        return f"TDD.{self.extension}"