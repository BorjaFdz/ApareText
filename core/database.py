"""
Gestión de base de datos SQLite con SQLAlchemy.
"""

import json
import os
from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from core.models import Base, SettingsDB, SnippetDB, SnippetVariableDB, UsageLogDB


class Database:
    """Gestor de base de datos SQLite."""

    def __init__(self, db_path: Optional[str] = None):
        """
        Inicializar conexión a base de datos.

        Args:
            db_path: Ruta al archivo SQLite. Si es None, usa ~/.aparetext/aparetext.db
        """
        if db_path is None:
            # Directorio por defecto
            home = Path.home()
            aparetext_dir = home / ".aparetext"
            aparetext_dir.mkdir(exist_ok=True)
            db_path = str(aparetext_dir / "aparetext.db")

        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        # Defer heavy DB initialization (create_all / default inserts) until first session is requested.
        # This reduces startup/import cost when the application is packaged.
        self._initialized = False

    def _init_db(self) -> None:
        """Crear tablas en la base de datos."""
        Base.metadata.create_all(bind=self.engine)

        # Insertar configuración por defecto si no existe
        with self.SessionLocal() as session:
            if session.query(SettingsDB).count() == 0:
                self._insert_default_settings(session)
                session.commit()

    def _insert_default_settings(self, session: Session) -> None:
        """Insertar configuración por defecto."""
        default_settings = {
            "global_hotkey": "ctrl+space",
            "abbreviation_trigger": "tab",
            "insertion_method": "auto",
            "restore_clipboard": "true",
            "typing_speed": "50",
            "theme": "dark",
            "language": "es",
            "fuzzy_search": "true",
            "auto_start": "false",
            "show_notifications": "true",
            "log_usage": "false",
            "backup_enabled": "false",
            "backup_frequency": "7",
        }

        for key, value in default_settings.items():
            setting = SettingsDB(key=key, value=value)
            session.add(setting)

    def get_session(self) -> Session:
        """Obtener nueva sesión de base de datos."""
        # Ensure DB schema and defaults are created on first real use.
        if not getattr(self, "_initialized", False):
            try:
                self._init_db()
            finally:
                # Even if _init_db raises, avoid retry storms; mark initialized to allow subsequent errors to surface normally
                self._initialized = True
        return self.SessionLocal()

    def close(self) -> None:
        """Cerrar conexión a base de datos."""
        self.engine.dispose()
        self._initialized = False

    def backup(self, backup_path: str) -> None:
        """
        Crear backup de la base de datos.

        Args:
            backup_path: Ruta donde guardar el backup
        """
        import shutil

        backup_dir = Path(backup_path).parent
        backup_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(self.db_path, backup_path)

    def restore(self, backup_path: str) -> None:
        """
        Restaurar base de datos desde backup.

        Args:
            backup_path: Ruta del backup
        """
        import shutil

        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup file not found: {backup_path}")

        # Cerrar conexión actual
        self.close()

        # Restaurar archivo
        shutil.copy2(backup_path, self.db_path)

        # Reconectar
        self.engine = create_engine(f"sqlite:///{self.db_path}", echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        # Reset initialized flag so schema/defaults will be ensured on next use
        self._initialized = False

    def export_to_json(self, output_path: str) -> None:
        """
        Exportar snippets a JSON.

        Args:
            output_path: Ruta del archivo JSON de salida
        """
        from datetime import datetime

        with self.get_session() as session:
            snippets_db = session.query(SnippetDB).all()

            export_data = {
                "version": "1.0.0",
                "exported_at": datetime.utcnow().isoformat(),
                "snippets": [],
            }

            for snippet_db in snippets_db:
                snippet_data = {
                    "id": snippet_db.id,
                    "name": snippet_db.name,
                    "abbreviation": snippet_db.abbreviation,
                    "tags": snippet_db.tags.split(",") if snippet_db.tags else [],
                    "content_text": snippet_db.content_text,
                    "content_html": snippet_db.content_html,
                    "is_rich": snippet_db.is_rich,
                    "scope_type": snippet_db.scope_type,
                    "scope_values": (
                        json.loads(snippet_db.scope_values)
                        if snippet_db.scope_values
                        else []
                    ),
                    "caret_marker": snippet_db.caret_marker,
                    "usage_count": snippet_db.usage_count,
                    "enabled": snippet_db.enabled,
                    "created_at": snippet_db.created_at.isoformat(),
                    "updated_at": snippet_db.updated_at.isoformat(),
                    "variables": [],
                }

                for var_db in snippet_db.variables:
                    var_data = {
                        "id": var_db.id,
                        "key": var_db.key,
                        "label": var_db.label,
                        "type": var_db.type,
                        "placeholder": var_db.placeholder,
                        "default_value": var_db.default_value,
                        "required": var_db.required,
                        "regex": var_db.regex,
                        "options": json.loads(var_db.options) if var_db.options else None,
                    }
                    snippet_data["variables"].append(var_data)

                export_data["snippets"].append(snippet_data)

        # Escribir JSON
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

    def import_from_json(self, input_path: str, replace: bool = False) -> dict:
        """
        Importar snippets desde JSON.

        Args:
            input_path: Ruta del archivo JSON
            replace: Si True, elimina todos los snippets existentes antes de importar

        Returns:
            Dict con 'imported' y 'skipped' counts
        """
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "version" not in data or "snippets" not in data:
            raise ValueError("Invalid export file format")

        with self.get_session() as session:
            if replace:
                session.query(SnippetDB).delete()
                session.commit()

            imported = 0
            skipped = 0
            for snippet_data in data["snippets"]:
                # Verificar si existe por ID
                existing = session.query(SnippetDB).filter_by(id=snippet_data["id"]).first()
                if existing:
                    skipped += 1
                    continue  # Skip duplicados

                # Crear snippet
                snippet_db = SnippetDB(
                    id=snippet_data["id"],
                    name=snippet_data["name"],
                    abbreviation=snippet_data.get("abbreviation"),
                    tags=",".join(snippet_data.get("tags", [])),
                    content_text=snippet_data.get("content_text"),
                    content_html=snippet_data.get("content_html"),
                    is_rich=snippet_data.get("is_rich", False),
                    scope_type=snippet_data.get("scope_type", "global"),
                    scope_values=json.dumps(snippet_data.get("scope_values", [])),
                    caret_marker=snippet_data.get("caret_marker", "{{|}}"),
                    usage_count=snippet_data.get("usage_count", 0),
                    enabled=snippet_data.get("enabled", True),
                )

                session.add(snippet_db)
                session.flush()  # Para obtener el ID

                # Crear variables
                for var_data in snippet_data.get("variables", []):
                    var_db = SnippetVariableDB(
                        id=var_data.get("id"),
                        snippet_id=snippet_db.id,
                        key=var_data["key"],
                        label=var_data.get("label"),
                        type=var_data.get("type", "text"),
                        placeholder=var_data.get("placeholder"),
                        default_value=var_data.get("default_value"),
                        required=var_data.get("required", False),
                        regex=var_data.get("regex"),
                        options=json.dumps(var_data.get("options")) if var_data.get("options") else None,
                    )
                    session.add(var_db)

                imported += 1

            session.commit()

        return {"imported": imported, "skipped": skipped}


# Singleton para acceso global
_db_instance: Optional[Database] = None


def get_db(db_path: Optional[str] = None) -> Database:
    """
    Obtener instancia singleton de base de datos.

    Args:
        db_path: Ruta opcional al archivo de base de datos

    Returns:
        Instancia de Database
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = Database(db_path)
    return _db_instance


def close_db() -> None:
    """Cerrar instancia global de base de datos."""
    global _db_instance
    if _db_instance:
        _db_instance.close()
        _db_instance = None
