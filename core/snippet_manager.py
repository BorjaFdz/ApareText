"""
Gestor de snippets - CRUD y búsqueda.
"""

import json
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from core.database import Database
from core.models import Snippet, SnippetDB, SnippetVariable, SnippetVariableDB, UsageLog, UsageLogDB


class SnippetManager:
    """Gestor de operaciones CRUD para snippets."""

    def __init__(self, db: Database):
        """
        Inicializar gestor de snippets.

        Args:
            db: Instancia de Database
        """
        self.db = db

    def create_snippet(self, snippet: Snippet) -> Snippet:
        """
        Crear nuevo snippet.

        Args:
            snippet: Datos del snippet

        Returns:
            Snippet creado con ID
        """
        with self.db.get_session() as session:
            snippet_db = SnippetDB(
                id=snippet.id,
                name=snippet.name,
                abbreviation=snippet.abbreviation,
                tags=",".join(snippet.tags) if snippet.tags else None,
                content_text=snippet.content_text,
                content_html=snippet.content_html,
                is_rich=snippet.is_rich,
                scope_type=snippet.scope_type.value,
                scope_values=json.dumps(snippet.scope_values),
                caret_marker=snippet.caret_marker,
                usage_count=snippet.usage_count,
                enabled=snippet.enabled,
            )

            session.add(snippet_db)
            session.flush()

            # Crear variables
            for var in snippet.variables:
                var_db = SnippetVariableDB(
                    id=var.id,
                    snippet_id=snippet_db.id,
                    key=var.key,
                    label=var.label,
                    type=var.type.value,
                    placeholder=var.placeholder,
                    default_value=var.default_value,
                    required=var.required,
                    regex=var.regex,
                    options=json.dumps(var.options) if var.options else None,
                )
                session.add(var_db)

            session.commit()
            session.refresh(snippet_db)

            return self._db_to_pydantic(snippet_db)

    def get_snippet(self, snippet_id: str) -> Optional[Snippet]:
        """
        Obtener snippet por ID.

        Args:
            snippet_id: ID del snippet

        Returns:
            Snippet o None si no existe
        """
        with self.db.get_session() as session:
            snippet_db = session.query(SnippetDB).filter_by(id=snippet_id).first()
            if snippet_db:
                return self._db_to_pydantic(snippet_db)
            return None

    def get_all_snippets(self, enabled_only: bool = False) -> list[Snippet]:
        """
        Obtener todos los snippets.

        Args:
            enabled_only: Si True, solo devuelve snippets habilitados

        Returns:
            Lista de snippets
        """
        with self.db.get_session() as session:
            query = session.query(SnippetDB)
            if enabled_only:
                query = query.filter_by(enabled=True)

            snippets_db = query.all()
            return [self._db_to_pydantic(s) for s in snippets_db]

    def update_snippet(self, snippet_id: str, snippet: Snippet) -> Optional[Snippet]:
        """
        Actualizar snippet existente.

        Args:
            snippet_id: ID del snippet a actualizar
            snippet: Nuevos datos del snippet

        Returns:
            Snippet actualizado o None si no existe
        """
        with self.db.get_session() as session:
            snippet_db = session.query(SnippetDB).filter_by(id=snippet_id).first()
            if not snippet_db:
                return None

            # Actualizar campos
            snippet_db.name = snippet.name
            snippet_db.abbreviation = snippet.abbreviation
            snippet_db.tags = ",".join(snippet.tags) if snippet.tags else None
            snippet_db.content_text = snippet.content_text
            snippet_db.content_html = snippet.content_html
            snippet_db.is_rich = snippet.is_rich
            snippet_db.scope_type = snippet.scope_type.value
            snippet_db.scope_values = json.dumps(snippet.scope_values)
            snippet_db.caret_marker = snippet.caret_marker
            snippet_db.enabled = snippet.enabled
            snippet_db.updated_at = datetime.utcnow()

            # Eliminar variables antiguas
            session.query(SnippetVariableDB).filter_by(snippet_id=snippet_id).delete()

            # Crear nuevas variables
            for var in snippet.variables:
                var_db = SnippetVariableDB(
                    id=var.id,
                    snippet_id=snippet_db.id,
                    key=var.key,
                    label=var.label,
                    type=var.type.value,
                    placeholder=var.placeholder,
                    default_value=var.default_value,
                    required=var.required,
                    regex=var.regex,
                    options=json.dumps(var.options) if var.options else None,
                )
                session.add(var_db)

            session.commit()
            session.refresh(snippet_db)

            return self._db_to_pydantic(snippet_db)

    def delete_snippet(self, snippet_id: str) -> bool:
        """
        Eliminar snippet.

        Args:
            snippet_id: ID del snippet

        Returns:
            True si se eliminó, False si no existía
        """
        with self.db.get_session() as session:
            snippet_db = session.query(SnippetDB).filter_by(id=snippet_id).first()
            if not snippet_db:
                return False

            session.delete(snippet_db)
            session.commit()
            return True

    def search_snippets(
        self,
        query: str,
        tags: Optional[list[str]] = None,
        scope_type: Optional[str] = None,
        enabled_only: bool = True,
    ) -> list[Snippet]:
        """
        Buscar snippets.

        Args:
            query: Texto de búsqueda (nombre o abreviatura)
            tags: Filtrar por tags
            scope_type: Filtrar por tipo de scope
            enabled_only: Solo snippets habilitados

        Returns:
            Lista de snippets que coinciden
        """
        with self.db.get_session() as session:
            db_query = session.query(SnippetDB)

            if enabled_only:
                db_query = db_query.filter_by(enabled=True)

            if scope_type:
                db_query = db_query.filter_by(scope_type=scope_type)

            snippets_db = db_query.all()

            # Filtrar por query
            results = []
            query_lower = query.lower()

            for snippet_db in snippets_db:
                # Buscar en nombre
                if query_lower in snippet_db.name.lower():
                    results.append(snippet_db)
                    continue

                # Buscar en abreviatura
                if snippet_db.abbreviation and query_lower in snippet_db.abbreviation.lower():
                    results.append(snippet_db)
                    continue

                # Buscar en tags
                if snippet_db.tags and query_lower in snippet_db.tags.lower():
                    results.append(snippet_db)
                    continue

            # Filtrar por tags adicionales
            if tags:
                results = [
                    s
                    for s in results
                    if s.tags and any(tag in s.tags.split(",") for tag in tags)
                ]

            return [self._db_to_pydantic(s) for s in results]

    def get_snippet_by_abbreviation(self, abbreviation: str) -> Optional[Snippet]:
        """
        Obtener snippet por abreviatura.

        Args:
            abbreviation: Abreviatura a buscar

        Returns:
            Snippet o None si no existe
        """
        with self.db.get_session() as session:
            snippet_db = (
                session.query(SnippetDB)
                .filter_by(abbreviation=abbreviation, enabled=True)
                .first()
            )
            if snippet_db:
                return self._db_to_pydantic(snippet_db)
            return None

    def increment_usage(self, snippet_id: str) -> None:
        """
        Incrementar contador de uso de un snippet.

        Args:
            snippet_id: ID del snippet
        """
        with self.db.get_session() as session:
            snippet_db = session.query(SnippetDB).filter_by(id=snippet_id).first()
            if snippet_db:
                snippet_db.usage_count += 1
                session.commit()

    def log_usage(
        self,
        snippet_id: str,
        source: Optional[str] = None,
        target_app: Optional[str] = None,
        target_domain: Optional[str] = None,
    ) -> None:
        """
        Registrar uso de snippet.

        Args:
            snippet_id: ID del snippet
            source: Origen ('desktop', 'extension', 'web')
            target_app: App donde se usó
            target_domain: Dominio web donde se usó
        """
        with self.db.get_session() as session:
            log = UsageLogDB(
                snippet_id=snippet_id,
                source=source,
                target_app=target_app,
                target_domain=target_domain,
            )
            session.add(log)
            session.commit()

        # Incrementar contador
        self.increment_usage(snippet_id)

    def get_usage_stats(self, snippet_id: Optional[str] = None) -> dict:
        """
        Obtener estadísticas de uso.

        Args:
            snippet_id: ID del snippet (opcional, si None devuelve stats globales)

        Returns:
            Diccionario con estadísticas
        """
        with self.db.get_session() as session:
            query = session.query(UsageLogDB)

            if snippet_id:
                query = query.filter_by(snippet_id=snippet_id)

            logs = query.all()

            stats = {
                "total_uses": len(logs),
                "by_source": {},
                "by_app": {},
                "by_domain": {},
            }

            for log in logs:
                # Por source
                if log.source:
                    stats["by_source"][log.source] = stats["by_source"].get(log.source, 0) + 1

                # Por app
                if log.target_app:
                    stats["by_app"][log.target_app] = stats["by_app"].get(log.target_app, 0) + 1

                # Por dominio
                if log.target_domain:
                    stats["by_domain"][log.target_domain] = (
                        stats["by_domain"].get(log.target_domain, 0) + 1
                    )

            return stats

    def _db_to_pydantic(self, snippet_db: SnippetDB) -> Snippet:
        """Convertir modelo SQLAlchemy a Pydantic."""
        variables = [
            SnippetVariable(
                id=var.id,
                snippet_id=var.snippet_id,
                key=var.key,
                label=var.label,
                type=var.type,
                placeholder=var.placeholder,
                default_value=var.default_value,
                required=var.required,
                regex=var.regex,
                options=json.loads(var.options) if var.options else None,
            )
            for var in snippet_db.variables
        ]

        return Snippet(
            id=snippet_db.id,
            name=snippet_db.name,
            abbreviation=snippet_db.abbreviation,
            tags=snippet_db.tags.split(",") if snippet_db.tags else [],
            content_text=snippet_db.content_text,
            content_html=snippet_db.content_html,
            is_rich=snippet_db.is_rich,
            scope_type=snippet_db.scope_type,
            scope_values=json.loads(snippet_db.scope_values) if snippet_db.scope_values else [],
            caret_marker=snippet_db.caret_marker,
            variables=variables,
            usage_count=snippet_db.usage_count,
            enabled=snippet_db.enabled,
            created_at=snippet_db.created_at,
            updated_at=snippet_db.updated_at,
        )
