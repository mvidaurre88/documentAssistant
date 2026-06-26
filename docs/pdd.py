# IMPORTS DE TERCEROS
import streamlit as st

# IMPORTS PROPIOS
from docs.base import DocumentBase
from components.form import field_row
from utils.verify_components import render_section_list, render_input_list, render_common_fields, show_img_overlay

class PDD(DocumentBase):
    
    extension = "docx"
    mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    
    def render_form(self, data: dict) -> dict:
        
        # CAMPOS COMUNES
        render_common_fields(data)

        # PROPOSITO DEL BOT
        field_row("Objetivo del Bot", "propositoProceso", data, multiline=True, col_ratio=(1, 4.6), only_input=True)
        
        # SISTEMAS
        sistemas = data.setdefault("sistemasInvolucrados", [])
        if sistemas:
            with st.container(key="form_container_sistemas_pdd"):
                render_section_list("Sistemas Involucrados", sistemas, "sistemasInvolucrados", "Sistema",
                                    fields_config=[
                                        {"label": "Nombre", "key": "sistema"},
                                        {"label": "Descripción", "key": "descripcion"},
                                        {"label": "Detalle", "key": "detalle", "multiline": True}
                                    ],
                                    empty_item={"sistema": "", "descripción": "", "detalle": ""}
                )
        
        # INPUTS
        inputs = data.setdefault("entradas", [])
        if inputs:
            with st.container(key="form_container_inputs_pdd"):
                render_input_list("Archivos Input", inputs, "entradas", multiline=True)
        
        # OUTPUTS
        outputs = data.setdefault("salidas", [])
        if outputs:
            with st.container(key="form_container_outputs_pdd"):
                render_input_list("Archivos Output", outputs, "salidas", multiline=True)
        
        # CARPETAS
        field_row("Ruta Compartida", "carpetaCompartida", data, col_ratio=(1, 4.6), only_input=True)
        field_row("Ruta Output", "carpetaOutput", data, col_ratio=(1, 4.6), only_input=True)
        field_row("Ruta Input", "carpetaInput", data, col_ratio=(1, 4.6), only_input=True)
        
        # CONTACTOS
        contactos = data.setdefault("contactos", [])
        if contactos:
            with st.container(key="form_container_contacts_pdd"):
                render_input_list("Contactos", contactos, "contactos", multiline=True)

        # FORMA DE EJECUCION
        field_row("Forma de Ejecución", "ejecucion", data, multiline=True, col_ratio=(1, 4.6), only_input=True)
        
        # FASES
        fases = data.setdefault("fases", [])
        if fases:
            with st.container(key="form_container_fases_pdd"):
                render_section_list("Fases del Proceso", fases, "fases", "Fase",
                                    fields_config=[
                                        {"label": "Título de fase", "key": "tituloFase"},
                                        {"label": "Pasos", "label_singular": "Paso", "key": "pasos", "type": "list", "subfields": [
                                                                                                        {"label": "Acción", "key": "accion"},
                                                                                                        {"label": "Detalle", "key": "detalle", "multiline": True},
                                                                                                        {"label": "Excepción / Escenario", "key": "excepciones", "multiline": True}]
                                        }
                                    ],
                                    empty_item={"tituloFase": "", "pasos": []}
                )

        # EXCEPCIONES
        excepciones = data.setdefault("excepciones", [])
        if excepciones:
            with st.container(key="form_container_excepciones_pdd"):
                render_section_list("Excepciones", excepciones, "excepciones", "Excepción",
            fields_config=[
                {"label": "Escenario de excepción", "key": "escenario"},
                {"label": "Tipo de excepción", "key": "tipo"},
                {"label": "Acción a tomar", "key": "accion", "multiline": True}
            ],
            empty_item={"escenario": "", "tipo": "", "accion": ""}
        )
        
        # DIAGRAMAS
        col_1, col_2, col_3, col_4 = st.columns([3, 1, 2, 2])
        with col_1:
            st.markdown("**Diagrama de Alto Nivel**")
        with col_2:
            img_bytes = st.session_state.get("diagramaAltoNivel", None)
            if img_bytes:
                show_img_overlay(img_bytes, key="alto_nivel")
        col_1, col_2, col_3, col_4 = st.columns([3, 1, 2, 2])
        with col_1:
            st.markdown("**Diagrama de Bajo Nivel**")
        with col_2:
            img_bytes = st.session_state.get("diagramaBajoNivel", None)
            if img_bytes:
                show_img_overlay(img_bytes, key="bajo_nivel")
    
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
    
    # DEVUELVE UNA LISTA CON LOS CAMPOS
    def get_fields(self):
        return {
            "Propósito del proceso": (["propositoProceso"], True),
            "Diagrama de alto nivel": (["diagramaAltoNivel"], True),
            "Diagrama de bajo nivel": (["diagramaBajoNivel"], True),
            "Archivos de entrada": (["entradas"], True),
            "Archivos de salida": (["salidas"], True),
            "Carpetas (input, output, compartida)": (["carpetaInput", "carpetaOutput", "carpetaCompartida"], True),
            "Contactos": (["contactos"], True),
            "Forma de ejecución": (["ejecucion"], True),
            "Sistemas involucrados": (["sistemasInvolucrados"], True),
            "Fases del proceso": (["fases"], True),
            "Excepciones": (["excepciones"], True),
        }
        
    # GENERA LOS CAMPOS PERSONALIZABLES
    @st.fragment
    def get_personalization(self) -> None:
        fields = self.get_fields()
        
        # Inicializar toggles usando el valor default de cada campo
        if "field_toggles" not in st.session_state:
            st.session_state.field_toggles = {
                label: default_enabled
                for label, (_keys, default_enabled) in fields.items()
            }
        
        for label, (_keys, default_enabled) in fields.items():
            col_label, col_toggle = st.columns([8, 1])
            with col_label:
                st.markdown(f"<p class='field-label'>{label}</p>", unsafe_allow_html=True)
            with col_toggle:
                st.session_state.field_toggles[label] = st.toggle(
                    label=label,
                    value=st.session_state.field_toggles.get(label, default_enabled),
                    key=f"toggle_{label}",
                    label_visibility="collapsed",
                )