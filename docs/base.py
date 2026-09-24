from abc import ABC, abstractmethod

class DocumentBase(ABC):

    extension: str = "docx"
    mime: str = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    needs_personalization: bool = True
    personalization_title: str = "¿Qué información querés generar?"

    @abstractmethod
    def render_form(self, data: dict) -> dict:
        ...

    @abstractmethod
    def get_aclaraciones(self) -> list[str]:
        ...

    @abstractmethod
    def get_filename(self) -> str:
        ...

    @abstractmethod
    def get_fields(self) -> dict[str, tuple[list[str], bool]]:
        ...

    @abstractmethod
    def get_personalization(self) -> None:
        ...

    def is_personalization_valid(self) -> bool:
        """Default: sin validación extra (ej. PDD/SDD/TDD con toggles, siempre válido)."""
        return True
    