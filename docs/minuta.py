import streamlit as st
from pathlib import Path
from docs.base import DocumentBase
from components.form import field_row

TIPOS_REUNION = ["Interna", "Cliente"]

BASE_DIR = Path("templates/minuta")
CLIENTES_FILE = BASE_DIR / "clientes.txt"
LOGOS_DIR = BASE_DIR / "logos"

TEMPLATE_INTERNA = BASE_DIR / "T-OP-Minuta de reunion INTERNA-v0.docx"
TEMPLATE_CLIENTE = BASE_DIR / "T-OP-Minuta de reunion CLIENTE-v0.docx"


class Minuta(DocumentBase):

    extension = "docx"
    mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    needs_personalization = True
    personalization_title = "Datos de la reunión"

    # ------------------------------------------------------------
    # PASO 1: DATOS DE LA REUNIÓN (tipo, título, cliente, logo)
    # ------------------------------------------------------------
    @st.fragment
    def get_personalization(self) -> None:
        data = st.session_state.setdefault("minuta_data", {})

        data["tipo_reunion"] = st.radio("Tipo de reunión", TIPOS_REUNION, key="minuta_tipo")
        data["titulo_breve"] = st.text_input("Título breve de la reunión", key="minuta_titulo")

        if data["tipo_reunion"] == "Cliente":
            clientes = self._get_clientes()
            nombres = [c["nombre"] for c in clientes] + ["Otro"]
            seleccion = st.selectbox("Cliente", nombres, key="minuta_cliente_select")

            if seleccion == "Otro":
                cliente = {"nombre": "", "proyecto": "", "logo_path": None}
                es_nuevo = True
            else:
                cliente = next(c for c in clientes if c["nombre"] == seleccion)
                es_nuevo = False

            if es_nuevo:
                data["cliente_nombre"] = st.text_input(
                    "Nombre del cliente", key="minuta_cliente_nuevo_nombre"
                )
            else:
                data["cliente_nombre"] = cliente["nombre"]

            data["cliente_proyecto"] = st.text_input(
                "Número y nombre del proyecto",
                value=cliente["proyecto"],
                key=f"minuta_proyecto_{seleccion}",
                placeholder="ej. 02852 - Grupo Assa - Implementación Payroll",
            )

            logo_en_disco = cliente["logo_path"] and cliente["logo_path"].exists()
            if logo_en_disco:
                data["logo_path"] = cliente["logo_path"]
                data["logo_bytes"] = None
                st.image(str(cliente["logo_path"]), width=150, caption=cliente["logo_path"].name)
            else:
                logo_file = st.file_uploader(
                    "Logo del cliente (fondo transparente)",
                    type=["png", "jpg", "jpeg"],
                    key=f"minuta_logo_{seleccion}",
                )
                data["logo_bytes"] = logo_file.getvalue() if logo_file else None
                data["logo_path"] = None

                if data["logo_bytes"]:
                    st.image(data["logo_bytes"], width=150, caption="Vista previa")

            data["cliente_es_nuevo"] = es_nuevo
        else:
            for k in ("cliente_nombre", "cliente_proyecto", "logo_bytes",
                      "logo_path", "cliente_es_nuevo"):
                data.pop(k, None)

    def is_personalization_valid(self) -> bool:
        data = st.session_state.get("minuta_data", {})
        if not data.get("titulo_breve", "").strip():
            return False
        if data.get("tipo_reunion") == "Cliente":
            if not data.get("cliente_nombre") or not data.get("cliente_proyecto"):
                return False
            if not data.get("logo_path") and not data.get("logo_bytes"):
                return False
        return True

    @staticmethod
    def _get_clientes() -> list[dict]:
        if not CLIENTES_FILE.exists():
            return []
        clientes = []
        for linea in CLIENTES_FILE.read_text(encoding="utf-8").splitlines():
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue
            nombre, proyecto, logo_nombre = linea.split("|")
            clientes.append({
                "nombre": nombre.strip(),
                "proyecto": proyecto.strip(),
                "logo_path": (LOGOS_DIR / logo_nombre.strip()) if logo_nombre.strip() else None,
            })
        return clientes

    # ------------------------------------------------------------
    # PASO 2: REVISIÓN/EDICIÓN DE LO EXTRAÍDO DEL TRANSCRIPT
    # ------------------------------------------------------------
    def render_form(self, data: dict) -> None:
        field_row("Participantes", "participantes", data, multiline=True, col_ratio=(1, 4.6), only_input=True)
        field_row("Agenda", "agenda", data, multiline=True, col_ratio=(1, 4.6), only_input=True)
        field_row("Desarrollo", "desarrollo", data, multiline=True, col_ratio=(1, 4.6), only_input=True)
        field_row("Próxima reunión", "proximaReunion", data, multiline=True, col_ratio=(1, 4.6), only_input=True)

    def get_aclaraciones(self) -> list[str]:
        return [
            "<b>Agenda y Desarrollo:</b> generados a partir del transcript. Revíselos antes de enviar la minuta.",
            "<b>Próxima reunión:</b> se completa solo si el transcript la menciona explícitamente.",
            "<b>Índice:</b> al abrir el archivo en Word, actualícelo manualmente (clic derecho → Actualizar campos → Actualizar toda la tabla).",
        ]

    def get_filename(self) -> str:
        data = st.session_state.get("minuta_data", {})
        titulo = data.get("titulo_breve", "").strip()
        if data.get("tipo_reunion") == "Cliente":
            cliente = data.get("cliente_nombre", "").strip()
            return f"D-OP-{cliente}-Minuta de reunión-{titulo}-v0.{self.extension}"
        return f"D-OP-Minuta de reunión-{titulo}-v0.{self.extension}"

    def get_fields(self):
        return {
            "Participantes": (["participantes"], True),
            "Agenda": (["agenda"], True),
            "Desarrollo": (["desarrollo"], True),
            "Próxima reunión": (["proximaReunion"], True),
        }