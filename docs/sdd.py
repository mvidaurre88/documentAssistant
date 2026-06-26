import streamlit as st

# IMPORTS PROPIOS
from docs.base import DocumentBase
from utils.verify_components import render_common_fields, render_section_list, render_input_list, show_img_overlay
from components.form import field_row

class SDD(DocumentBase):
    
    extension = "docx"
    mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    
    # DEVUELVE LAS ACLARACIONES A MOSTRAR EN LA PANTALLA FINAL
    def get_aclaraciones(self) -> list[str]:
        return [
            "<b>Diagramas:</b> son generados y pueden contener imprecisiones. Utilícelos como guía y valídelos antes de su uso final.",
        ]
        
    # DEVUELVE EL NOMBRE DEL ARCHIVO A DESCARGAR
    def get_filename(self) -> str:
        return f"SDD.{self.extension}"

    # DEVUELVE UNA LISTA CON LOS CAMPOS
    def get_fields(self):
        return {
            "Propósito del proceso": (["procesoNegocioAltoNivel"], True),
            "Diagrama de tasks": (["diagrama_pasos"], True),
            "Diagrama a detalle": (["diagrama_detalle"], True),
            "Solución técnica de alto nivel": (["solucionTecnicaAltoNivel"], True),
            "Solución técnica detallada": (["solucionTecnicaDetallada"], True),
            "Excepciones": (["excepciones"], True),
            "Aplicaciones": (["aplicaciones"], True),
            "Archivos": (["archivos"], True),
            "Pre-requisitos técnicos": (["requisitos"], True),
            "Forma de ejecución": (["ejecucion"], True),
            "Forma de re-ejecución": (["reejecucion"], True),
            "Renovación de credenciales": (["renovacionCredenciales"], True),
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
    
    def render_form(self, data: dict) -> dict:
        
        # CAMPOS COMUNES
        render_common_fields(data)
        
        # PROPOSITO DEL BOT
        field_row("Objetivo del Bot", "procesoNegocioAltoNivel", data, multiline=True, col_ratio=(1, 4.6))
        
        # SOLUCION TECNICA ALTO NIVEL
        empty_alto_nivel = {"nombreTarea": "", "descripcionTarea": ""}
        solucion_alto_nivel = data.get("solucionTecnicaAltoNivel") or []
        data["solucionTecnicaAltoNivel"] = solucion_alto_nivel
        if not solucion_alto_nivel:
            solucion_alto_nivel.append(dict(empty_alto_nivel))
        with st.container(key="form_container_solucion_alto_nivel_sdd"):
            render_section_list( "Solucion Técnica de Alto Nivel", solucion_alto_nivel, "solucionTecnicaAltoNivel", "Tarea",
                                    fields_config=[ {"label": "Nombre de tarea", "key": "nombreTarea"},
                                                    {"label": "Descripción de tarea", "key": "descripcionTarea", "multiline": True}
                                    ],
                                    empty_item=empty_alto_nivel
            )
        
        # SOLUCION TECNICA DETALLADA
        empty_detallada = {"nombreTarea": "", "descripcionExacta": "", "excepciones": []}
        solucion_tecnica_detallada = data.get("solucionTecnicaDetallada") or []
        data["solucionTecnicaDetallada"] = solucion_tecnica_detallada
        if not solucion_tecnica_detallada:
            solucion_tecnica_detallada.append(dict(empty_detallada))
        with st.container(key="form_container_solucion_tecnica_detallada_sdd"):
            render_section_list("Solución Técnica Detallada", solucion_tecnica_detallada, "solucionTecnicaDetallada", "Tarea",
                                    fields_config=[ {"label": "Nombre de tarea", "key": "nombreTarea"},
                                                    {"label": "Descripción exacta de tarea", "key": "descripcionExacta", "multiline": True},
                                                    {"label": "Excepciones", "label_singular": "Excepción", "key": "excepciones", "type": "list",
                                                    "subfields": [
                                                        {"label": "Evento de Excepción", "key": "evento"}
                                                    ]
                                            }
                                    ],
                                    empty_item=empty_detallada)
        
        # EXCEPCIONES
        empty_excepcion = {"evento": "", "detalle": "", "accion": "", "responsable": ""}
        excepciones = data.get("excepciones") or []
        data["excepciones"] = excepciones
        if not excepciones:
            excepciones.append(dict(empty_excepcion))
        with st.container(key="form_container_excepciones_sdd"):
            render_section_list("Excepciones", excepciones, "excepciones", "Excepción",
                                    fields_config=[ {"label": "Evento", "key": "evento"},
                                                    {"label": "Detalle", "key": "detalle", "multiline": True},
                                                    {"label": "Acción", "key": "accion", "multiline": True},
                                                    {"label": "Responsable", "key": "responsable"}
                                    ],
                empty_item=empty_excepcion
            )
        
        # APLICACIONES
        empty_aplicacion = {"nombre": "", "version": "", "comentarios": ""}
        aplicaciones = data.get("aplicaciones") or []
        data["aplicaciones"] = aplicaciones
        if not aplicaciones:
            aplicaciones.append(dict(empty_aplicacion))
        with st.container(key="form_container_aplicaciones_sdd"):
            render_section_list("Aplicaciones", aplicaciones, "aplicaciones", "Aplicación",
                fields_config=[
                    {"label": "Nombre", "key": "nombre"},
                    {"label": "Version", "key": "version"},
                    {"label": "Comentarios", "key": "comentarios", "multiline": True}
                ],
                empty_item=empty_aplicacion
        )

        # ARCHIVOS
        empty_archivo = {"nombre": "", "comentarios": "", "nomenclatura": ""}
        archivos = data.get("archivos") or []
        data["archivos"] = archivos
        if not archivos:
            archivos.append(dict(empty_archivo))
        with st.container(key="form_container_archivos_sdd"):
            render_section_list("Archivos", archivos, "archivos", "Archivo",
                fields_config=[
                    {"label": "Nombre", "key": "nombre"},
                    {"label": "Comentarios", "key": "comentarios", "multiline": True},
                    {"label": "Nomenclatura", "key": "nomenclatura"}
                ],
                empty_item=empty_archivo
        )

        # PREREQUISITOS TECNICOS
        requisitos = data.get("requisitos") or []
        data["requisitos"] = requisitos
        if not requisitos:
            requisitos.append("")
        with st.container(key="form_container_requisitos_sdd"):
            render_input_list("Pre-requisitos Técnicos", requisitos, "requisitos", multiline=True)
        
        # EJECUCION Y REEJECUCION
        field_row("Forma de Ejecución", "ejecucion", data, multiline=True, col_ratio=(1, 6.5))
        field_row("Forma de Re-ejecución", "reejecucion", data, multiline=True, col_ratio=(1, 6.5))
        
        # MACROS EXCEL
        
        # CODIGO PYTHON
        
        # DIAGRAMAS
        col_1, col_2, col_3, col_4 = st.columns([3, 1, 2, 2])
        with col_1:
            st.markdown("**Diagrama de tasks**")
        with col_2:
            img_bytes = st.session_state.get("diagrama_pasos", None)
            if img_bytes:
                show_img_overlay(img_bytes, key="pasos")
        col_1, col_2, col_3, col_4 = st.columns([3, 1, 2, 2])
        with col_1:
            st.markdown("**Diagrama a detalle**")
        with col_2:
            img_bytes = st.session_state.get("diagrama_detalle", None)
            if img_bytes:
                show_img_overlay(img_bytes, key="detalle")