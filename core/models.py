"""
Modelos de datos usando Pydantic para validación y SQLAlchemy para persistencia.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# SQLAlchemy Base
Base = declarative_base()


# Enums
class VariableType(str, Enum):
    """Tipos de variables soportadas en snippets."""

    TEXT = "text"
    EMAIL = "email"
    NUMBER = "number"
    SELECT = "select"
    DATE = "date"
    CHECKBOX = "checkbox"


class SnippetType(str, Enum):
    """Tipos de snippets."""
    
    TEXT = "text"  # Snippet de texto (puede ser plain text o HTML)
    IMAGE = "image"  # Snippet de imagen (guarda y pega imágenes)


class ScopeType(str, Enum):
    """Tipos de scope para snippets."""

    GLOBAL = "global"
    APPS = "apps"  # Aplicaciones específicas (slack.exe, com.apple.mail)
    DOMAINS = "domains"  # Dominios web (twitter.com, gmail.com)


# Modelos SQLAlchemy (Base de datos)
class SnippetDB(Base):
    """Modelo de snippet en la base de datos."""

    __tablename__ = "snippets"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False, index=True)
    abbreviation = Column(String, nullable=True, index=True)
    snippet_type = Column(String, default=SnippetType.TEXT.value, index=True)  # 'text' o 'image'
    tags = Column(String, nullable=True, index=True)  # CSV: "twitter,outreach,morning"
    category = Column(String, nullable=True, index=True)  # Categoría del snippet
    content_text = Column(Text, nullable=True)
    content_html = Column(Text, nullable=True)
    is_rich = Column(Boolean, default=False)
    image_data = Column(Text, nullable=True)  # Base64 image data para snippets tipo IMAGE
    thumbnail = Column(Text, nullable=True)  # Miniatura para snippets HTML
    scope_type = Column(String, default=ScopeType.GLOBAL.value)
    scope_values = Column(Text, nullable=True)  # JSON array
    caret_marker = Column(String, default="{{|}}")
    usage_count = Column(Integer, default=0, index=True)
    enabled = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    variables = relationship("SnippetVariableDB", back_populates="snippet", cascade="all, delete-orphan")


class SnippetVariableDB(Base):
    """Modelo de variable de snippet en la base de datos."""

    __tablename__ = "snippet_variables"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    snippet_id = Column(String, ForeignKey("snippets.id", ondelete="CASCADE"), nullable=False)
    key = Column(String, nullable=False)
    label = Column(String, nullable=True)
    type = Column(String, nullable=False, default=VariableType.TEXT.value)
    placeholder = Column(String, nullable=True)
    default_value = Column(String, nullable=True)
    required = Column(Boolean, default=False)
    regex = Column(String, nullable=True)
    options = Column(Text, nullable=True)  # JSON array para type='select'

    # Relaciones
    snippet = relationship("SnippetDB", back_populates="variables")


class SettingsDB(Base):
    """Tabla de configuración key-value."""

    __tablename__ = "settings"

    key = Column(String, primary_key=True)
    value = Column(Text, nullable=True)


class UsageLogDB(Base):
    """Log de uso de snippets."""

    __tablename__ = "usage_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    snippet_id = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    source = Column(String, nullable=True)  # 'desktop', 'extension', 'web'
    target_app = Column(String, nullable=True)  # 'slack.exe', 'chrome.exe'
    target_domain = Column(String, nullable=True)  # 'twitter.com', 'gmail.com'


class SnippetVersionDB(Base):
    """Versión histórica de un snippet para undo/redo."""

    __tablename__ = "snippet_versions"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    snippet_id = Column(String, ForeignKey("snippets.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)  # Número de versión (1, 2, 3...)
    name = Column(String, nullable=False)
    abbreviation = Column(String, nullable=True)
    snippet_type = Column(String, default=SnippetType.TEXT.value)
    tags = Column(String, nullable=True)
    category = Column(String, nullable=True)
    content_text = Column(Text, nullable=True)
    content_html = Column(Text, nullable=True)
    is_rich = Column(Boolean, default=False)
    image_data = Column(Text, nullable=True)
    thumbnail = Column(Text, nullable=True)
    scope_type = Column(String, default=ScopeType.GLOBAL.value)
    scope_values = Column(Text, nullable=True)
    caret_marker = Column(String, default="{{|}}")
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)  # Cuando se creó esta versión
    change_reason = Column(String, nullable=True)  # Razón del cambio (opcional)

    # Relaciones
    variables = relationship("SnippetVersionVariableDB", back_populates="version", cascade="all, delete-orphan")


class SnippetVersionVariableDB(Base):
    """Variables de una versión específica de snippet."""

    __tablename__ = "snippet_version_variables"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    version_id = Column(String, ForeignKey("snippet_versions.id", ondelete="CASCADE"), nullable=False)
    key = Column(String, nullable=False)
    label = Column(String, nullable=True)
    type = Column(String, nullable=False, default=VariableType.TEXT.value)
    placeholder = Column(String, nullable=True)
    default_value = Column(String, nullable=True)
    required = Column(Boolean, default=False)
    regex = Column(String, nullable=True)
    options = Column(Text, nullable=True)

    # Relaciones
    version = relationship("SnippetVersionDB", back_populates="variables")


# Modelos Pydantic (Validación y API)
class SnippetVariable(BaseModel):
    """Variable dentro de un snippet."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    snippet_id: Optional[str] = None
    key: str = Field(..., min_length=1, max_length=50)
    label: Optional[str] = None
    type: VariableType = VariableType.TEXT
    placeholder: Optional[str] = None
    default_value: Optional[str] = None
    required: bool = False
    regex: Optional[str] = None
    options: Optional[list[str]] = None  # Para type='select'

    @field_validator("key")
    @classmethod
    def validate_key(cls, v: str) -> str:
        """Validar que la key sea alfanumérica y guiones bajos."""
        if not v.replace("_", "").isalnum():
            raise ValueError("Key must be alphanumeric with underscores only")
        return v

    @field_validator("options")
    @classmethod
    def validate_options(cls, v: Optional[list[str]], info: Any) -> Optional[list[str]]:
        """Validar que options esté presente si type es SELECT."""
        if info.data.get("type") == VariableType.SELECT and not v:
            raise ValueError("options is required when type is 'select'")
        return v

    @field_validator("regex")
    @classmethod
    def validate_regex(cls, v: Optional[str]) -> Optional[str]:
        """Validar que el patrón regex sea válido."""
        if v:
            try:
                import re
                re.compile(v)
            except re.error:
                raise ValueError(f"Invalid regex pattern: {v}")
        return v

    class Config:
        from_attributes = True


class Snippet(BaseModel):
    """Snippet completo con validación."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(..., min_length=1, max_length=200)
    abbreviation: Optional[str] = Field(None, max_length=50)
    snippet_type: SnippetType = SnippetType.TEXT
    tags: list[str] = Field(default_factory=list)
    category: Optional[str] = None
    content_text: Optional[str] = None
    content_html: Optional[str] = None
    is_rich: bool = False
    image_data: Optional[str] = None  # Base64 image data para snippets tipo IMAGE
    thumbnail: Optional[str] = None  # Miniatura para snippets HTML
    scope_type: ScopeType = ScopeType.GLOBAL
    scope_values: list[str] = Field(default_factory=list)
    caret_marker: str = "{{|}}"
    variables: list[SnippetVariable] = Field(default_factory=list)
    usage_count: int = 0
    enabled: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("abbreviation")
    @classmethod
    def validate_abbreviation(cls, v: Optional[str]) -> Optional[str]:
        """Validar formato de abreviatura."""
        if v and " " in v:
            raise ValueError("Abbreviation cannot contain spaces")
        return v

    @field_validator("tags", mode="before")
    @classmethod
    def parse_tags(cls, v: Any) -> list[str]:
        """Parsear tags desde CSV o lista."""
        if isinstance(v, str):
            return [tag.strip() for tag in v.split(",") if tag.strip()]
        return v or []

    @field_validator("image_data")
    @classmethod
    def validate_image_data(cls, v: Optional[str], info: Any) -> Optional[str]:
        """Validar datos de imagen base64."""
        if v and info.data.get("snippet_type") == SnippetType.IMAGE:
            if not v.startswith("data:image/"):
                raise ValueError("Image data must be valid base64 data URL")
        return v

    @field_validator("content_text", "content_html")
    @classmethod
    def validate_content(cls, v: Optional[str], info: Any) -> Optional[str]:
        """Validar que haya contenido cuando sea requerido."""
        if info.data.get("snippet_type") == SnippetType.TEXT and not v:
            # Para snippets de texto, al menos uno de content_text o content_html debe existir
            other_content = info.data.get("content_html" if info.field_name == "content_text" else "content_text")
            if not other_content:
                raise ValueError("Text snippets must have either content_text or content_html")
        return v

    @field_validator("scope_values")
    @classmethod
    def validate_scope_values(cls, v: list[str], info: Any) -> list[str]:
        """Validar valores de scope según el tipo."""
        scope_type = info.data.get("scope_type")
        if scope_type == ScopeType.APPS:
            # Validar que sean nombres de aplicaciones válidos
            for app in v:
                if not app or len(app.strip()) == 0:
                    raise ValueError("App names cannot be empty")
        elif scope_type == ScopeType.DOMAINS:
            # Validar formato de dominio básico
            import re
            domain_pattern = re.compile(r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$')
            for domain in v:
                if not domain_pattern.match(domain):
                    raise ValueError(f"Invalid domain format: {domain}")
        return v

    class Config:
        from_attributes = True

    def __str__(self):
        return f"Snippet(id={self.id}, name='{self.name}', abbr='{self.abbreviation}')"


class SnippetVersion(BaseModel):
    """Versión histórica de un snippet."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    snippet_id: str
    version_number: int
    name: str = Field(..., min_length=1, max_length=200)
    abbreviation: Optional[str] = Field(None, max_length=50)
    snippet_type: SnippetType = SnippetType.TEXT
    tags: list[str] = Field(default_factory=list)
    category: Optional[str] = None
    content_text: Optional[str] = None
    content_html: Optional[str] = None
    is_rich: bool = False
    image_data: Optional[str] = None
    thumbnail: Optional[str] = None
    scope_type: ScopeType = ScopeType.GLOBAL
    scope_values: list[str] = Field(default_factory=list)
    caret_marker: str = "{{|}}"
    enabled: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    change_reason: Optional[str] = None
    variables: list[SnippetVariable] = Field(default_factory=list)

    class Config:
        from_attributes = True

    def __str__(self):
        return f"SnippetVersion(id={self.id}, snippet_id={self.snippet_id}, version={self.version_number})"


class Settings(BaseModel):
    """Configuración de la aplicación."""

    # Hotkeys
    global_hotkey: str = "ctrl+space"
    abbreviation_trigger: str = "tab"  # tab, space, enter

    # Inserción
    insertion_method: str = "type"  # type, clipboard, auto
    restore_clipboard: bool = True
    typing_speed: int = 50  # ms entre teclas

    # UI
    theme: str = "dark"  # dark, light
    language: str = "es"  # es, en
    fuzzy_search: bool = True

    # Comportamiento
    auto_start: bool = False
    show_notifications: bool = True
    log_usage: bool = False

    # Backup
    backup_enabled: bool = False
    backup_path: Optional[str] = None
    backup_frequency: int = 7  # días

    class Config:
        from_attributes = True


class SnippetExport(BaseModel):
    """Formato de exportación de snippets."""

    version: str = "1.0.0"
    exported_at: datetime = Field(default_factory=datetime.utcnow)
    snippets: list[Snippet]

    class Config:
        from_attributes = True


class UsageLog(BaseModel):
    """Log de uso de snippet."""

    id: Optional[int] = None
    snippet_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: Optional[str] = None  # 'desktop', 'extension', 'web'
    target_app: Optional[str] = None
    target_domain: Optional[str] = None

    class Config:
        from_attributes = True
