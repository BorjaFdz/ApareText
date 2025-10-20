"""
Gestor de snippets - CRUD y búsqueda.
"""

import json
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from core.database import Database
from core.models import (
    Snippet, SnippetDB, SnippetVariable, SnippetVariableDB, UsageLogDB,
    SnippetVersion, SnippetVersionDB, SnippetVersionVariableDB
)


class SnippetManager:
    """Gestor de operaciones CRUD para snippets."""

    def __init__(self, db: Database):
        """
        Inicializar gestor de snippets.

        Args:
            db: Instancia de Database
        """
        self.db = db

    @staticmethod
    def _tags_to_string(tags: list[str]) -> Optional[str]:
        """Convertir lista de tags a string separado por comas."""
        return ",".join(tags) if tags else None

    @staticmethod
    def _string_to_tags(tags_str: Optional[str]) -> list[str]:
        """Convertir string de tags separado por comas a lista."""
        return [tag.strip() for tag in tags_str.split(",")] if tags_str else []

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
                tags=self._tags_to_string(snippet.tags),
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

            # Guardar versión anterior antes de actualizar
            self._save_snippet_version(session, snippet_db, change_reason="Actualización manual")

            # Actualizar campos
            snippet_db.name = snippet.name
            snippet_db.abbreviation = snippet.abbreviation
            snippet_db.snippet_type = snippet.snippet_type.value
            snippet_db.tags = self._tags_to_string(snippet.tags)
            snippet_db.category = snippet.category
            snippet_db.content_text = snippet.content_text
            snippet_db.content_html = snippet.content_html
            snippet_db.is_rich = snippet.is_rich
            snippet_db.image_data = snippet.image_data
            snippet_db.thumbnail = snippet.thumbnail
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
        Obtener estadísticas de uso avanzadas.

        Args:
            snippet_id: ID del snippet (opcional, si None devuelve stats globales)

        Returns:
            Diccionario con estadísticas avanzadas
        """
        with self.db.get_session() as session:
            # Estadísticas básicas usando count() en lugar de cargar todos los registros
            total_snippets = session.query(SnippetDB).count()
            enabled_snippets = session.query(SnippetDB).filter_by(enabled=True).count()
            
            # Query base para logs de uso
            usage_query = session.query(UsageLogDB)
            if snippet_id:
                usage_query = usage_query.filter_by(snippet_id=snippet_id)
            
            total_uses = usage_query.count()
            
            # Solo cargar logs si necesitamos análisis detallado
            logs = []
            if total_uses > 0:
                logs = usage_query.all()

            # Estadísticas básicas
            stats = {
                "total_uses": total_uses,
                "total_snippets": total_snippets,
                "enabled_snippets": enabled_snippets,
                "by_source": {},
                "by_app": {},
                "by_domain": {},
                "by_hour": {},
                "by_day": {},
                "by_month": {},
                "daily_usage": [],
                "weekly_usage": [],
                "monthly_usage": [],
                "recent_activity": [],
                "top_snippets": [],
                "category_stats": {},
                "version_stats": {},
                "productivity_metrics": {}
            }

            # Análisis por fuente, app y dominio
            for log in logs:
                # Por source
                if log.source:
                    stats["by_source"][log.source] = stats["by_source"].get(log.source, 0) + 1

                # Por app
                if log.target_app:
                    stats["by_app"][log.target_app] = stats["by_app"].get(log.target_app, 0) + 1

                # Por dominio
                if log.target_domain:
                    stats["by_domain"][log.target_domain] = stats["by_domain"].get(log.target_domain, 0) + 1

                # Por hora del día
                if log.timestamp:
                    hour = log.timestamp.hour
                    stats["by_hour"][hour] = stats["by_hour"].get(hour, 0) + 1

                # Por día de la semana
                if log.timestamp:
                    day = log.timestamp.strftime('%A')
                    stats["by_day"][day] = stats["by_day"].get(day, 0) + 1

                # Por mes
                if log.timestamp:
                    month = log.timestamp.strftime('%Y-%m')
                    stats["by_month"][month] = stats["by_month"].get(month, 0) + 1

            # Calcular series temporales
            now = datetime.utcnow()
            
            # Uso diario (últimos 30 días)
            daily_counts = {}
            for i in range(30):
                date = (now - timedelta(days=i)).strftime('%Y-%m-%d')
                daily_counts[date] = 0
            
            # Uso semanal (últimas 12 semanas)
            weekly_counts = {}
            for i in range(12):
                week_start = now - timedelta(weeks=i)
                week_key = f"{week_start.year}-{week_start.isocalendar()[1]:02d}"
                weekly_counts[week_key] = 0
            
            # Uso mensual (últimos 12 meses)
            monthly_counts = {}
            for i in range(12):
                month_date = now - timedelta(days=i*30)
                month_key = month_date.strftime('%Y-%m')
                monthly_counts[month_key] = 0
            
            # Contar usos por período
            for log in logs:
                if log.timestamp:
                    # Diario
                    day_key = log.timestamp.strftime('%Y-%m-%d')
                    if day_key in daily_counts:
                        daily_counts[day_key] += 1
                    
                    # Semanal
                    week_key = f"{log.timestamp.year}-{log.timestamp.isocalendar()[1]:02d}"
                    if week_key in weekly_counts:
                        weekly_counts[week_key] += 1
                    
                    # Mensual
                    month_key = log.timestamp.strftime('%Y-%m')
                    if month_key in monthly_counts:
                        monthly_counts[month_key] += 1
            
            # Convertir a arrays ordenados
            stats["daily_usage"] = [
                {"date": date, "count": count}
                for date, count in sorted(daily_counts.items())
            ]
            
            stats["weekly_usage"] = [
                {"week": week, "count": count}
                for week, count in sorted(weekly_counts.items())
            ]
            
            stats["monthly_usage"] = [
                {"month": month, "count": count}
                for month, count in sorted(monthly_counts.items())
            ]

            # Top snippets por uso
            if not snippet_id:
                snippet_usage = {}
                for log in session.query(UsageLogDB).all():
                    snippet_usage[log.snippet_id] = snippet_usage.get(log.snippet_id, 0) + 1

                # Obtener detalles de los snippets más usados
                top_snippet_ids = sorted(snippet_usage.items(), key=lambda x: x[1], reverse=True)[:10]
                for top_snippet_id, usage_count in top_snippet_ids:
                    snippet = session.query(SnippetDB).filter_by(id=top_snippet_id).first()
                    if snippet:
                        stats["top_snippets"].append({
                            "id": snippet.id,
                            "name": snippet.name,
                            "abbreviation": snippet.abbreviation,
                            "usage_count": usage_count,
                            "category": snippet.category
                        })

            # Estadísticas por categoría (usando consulta SQL eficiente)
            if not snippet_id:
                from sqlalchemy import func
                category_counts = {}
                category_results = session.query(
                    SnippetDB.category,
                    func.count(SnippetDB.id)
                ).group_by(SnippetDB.category).all()
                
                for category, count in category_results:
                    category_name = category if category is not None else 'Sin categoría'
                    category_counts[category_name] = count
                stats["category_stats"] = category_counts

            # Estadísticas de versiones
            if not snippet_id:
                # Total de versiones guardadas
                total_versions = session.query(SnippetVersionDB).count()
                stats["version_stats"] = {
                    "total_versions": total_versions,
                    "avg_versions_per_snippet": total_versions / max(total_snippets, 1)
                }

            # Actividad reciente (últimos 7 días)
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_logs = session.query(UsageLogDB).filter(UsageLogDB.timestamp >= week_ago).all()
            stats["recent_activity"] = len(recent_logs)

            # Métricas de productividad
            if logs:
                # Uso promedio por día
                first_log = min(log.timestamp for log in logs if log.timestamp)
                last_log = max(log.timestamp for log in logs if log.timestamp)
                days_diff = max((last_log - first_log).days, 1)
                stats["productivity_metrics"] = {
                    "avg_daily_uses": len(logs) / days_diff,
                    "most_active_hour": max(stats["by_hour"].items(), key=lambda x: x[1], default=(0, 0))[0],
                    "most_active_day": max(stats["by_day"].items(), key=lambda x: x[1], default=("N/A", 0))[0]
                }

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
            tags=self._string_to_tags(snippet_db.tags),
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

    def _save_snippet_version(self, session: Session, snippet_db: SnippetDB, change_reason: Optional[str] = None):
        """
        Guardar una versión del snippet antes de actualizarlo.

        Args:
            session: Sesión de base de datos
            snippet_db: Snippet a versionar
            change_reason: Razón del cambio (opcional)
        """
        # Obtener el número de versión más alto para este snippet
        max_version = session.query(SnippetVersionDB.version_number)\
            .filter_by(snippet_id=snippet_db.id)\
            .order_by(SnippetVersionDB.version_number.desc())\
            .first()

        next_version = (max_version[0] + 1) if max_version else 1

        # Crear nueva versión
        version_db = SnippetVersionDB(
            snippet_id=snippet_db.id,
            version_number=next_version,
            name=snippet_db.name,
            abbreviation=snippet_db.abbreviation,
            snippet_type=snippet_db.snippet_type,
            tags=snippet_db.tags,
            category=snippet_db.category,
            content_text=snippet_db.content_text,
            content_html=snippet_db.content_html,
            is_rich=snippet_db.is_rich,
            image_data=snippet_db.image_data,
            thumbnail=snippet_db.thumbnail,
            scope_type=snippet_db.scope_type,
            scope_values=snippet_db.scope_values,
            caret_marker=snippet_db.caret_marker,
            enabled=snippet_db.enabled,
            created_at=datetime.utcnow(),
            change_reason=change_reason
        )

        session.add(version_db)
        session.flush()  # Para obtener el ID

        # Guardar variables de la versión
        for var_db in snippet_db.variables:
            version_var_db = SnippetVersionVariableDB(
                version_id=version_db.id,
                key=var_db.key,
                label=var_db.label,
                type=var_db.type,
                placeholder=var_db.placeholder,
                default_value=var_db.default_value,
                required=var_db.required,
                regex=var_db.regex,
                options=var_db.options,
            )
            session.add(version_var_db)

    def get_snippet_versions(self, snippet_id: str) -> list[SnippetVersion]:
        """
        Obtener todas las versiones de un snippet.

        Args:
            snippet_id: ID del snippet

        Returns:
            Lista de versiones ordenadas por número de versión descendente
        """
        with self.db.get_session() as session:
            version_dbs = session.query(SnippetVersionDB)\
                .filter_by(snippet_id=snippet_id)\
                .order_by(SnippetVersionDB.version_number.desc())\
                .all()

            versions = []
            for version_db in version_dbs:
                # Obtener variables de la versión
                variables = [
                    SnippetVariable(
                        id=var.id,
                        key=var.key,
                        label=var.label,
                        type=var.type,
                        placeholder=var.placeholder,
                        default_value=var.default_value,
                        required=var.required,
                        regex=var.regex,
                        options=json.loads(var.options) if var.options else None,
                    )
                    for var in version_db.variables
                ]

                version = SnippetVersion(
                    id=version_db.id,
                    snippet_id=version_db.snippet_id,
                    version_number=version_db.version_number,
                    name=version_db.name,
                    abbreviation=version_db.abbreviation,
                    snippet_type=version_db.snippet_type,
                    tags=self._string_to_tags(version_db.tags),
                    category=version_db.category,
                    content_text=version_db.content_text,
                    content_html=version_db.content_html,
                    is_rich=version_db.is_rich,
                    image_data=version_db.image_data,
                    thumbnail=version_db.thumbnail,
                    scope_type=version_db.scope_type,
                    scope_values=json.loads(version_db.scope_values) if version_db.scope_values else [],
                    caret_marker=version_db.caret_marker,
                    enabled=version_db.enabled,
                    created_at=version_db.created_at,
                    change_reason=version_db.change_reason,
                    variables=variables
                )
                versions.append(version)

            return versions

    def restore_snippet_version(self, snippet_id: str, version_id: str) -> Optional[Snippet]:
        """
        Restaurar un snippet a una versión específica.

        Args:
            snippet_id: ID del snippet actual
            version_id: ID de la versión a restaurar

        Returns:
            Snippet restaurado o None si no existe
        """
        with self.db.get_session() as session:
            # Obtener la versión
            version_db = session.query(SnippetVersionDB)\
                .filter_by(id=version_id, snippet_id=snippet_id)\
                .first()

            if not version_db:
                return None

            # Obtener el snippet actual
            snippet_db = session.query(SnippetDB).filter_by(id=snippet_id).first()
            if not snippet_db:
                return None

            # Guardar versión actual antes de restaurar
            self._save_snippet_version(session, snippet_db, change_reason=f"Restauración a versión {version_db.version_number}")

            # Restaurar datos desde la versión
            snippet_db.name = version_db.name
            snippet_db.abbreviation = version_db.abbreviation
            snippet_db.snippet_type = version_db.snippet_type
            snippet_db.tags = version_db.tags
            snippet_db.category = version_db.category
            snippet_db.content_text = version_db.content_text
            snippet_db.content_html = version_db.content_html
            snippet_db.is_rich = version_db.is_rich
            snippet_db.image_data = version_db.image_data
            snippet_db.thumbnail = version_db.thumbnail
            snippet_db.scope_type = version_db.scope_type
            snippet_db.scope_values = version_db.scope_values
            snippet_db.caret_marker = version_db.caret_marker
            snippet_db.enabled = version_db.enabled
            snippet_db.updated_at = datetime.utcnow()

            # Restaurar variables
            session.query(SnippetVariableDB).filter_by(snippet_id=snippet_id).delete()

            for version_var_db in version_db.variables:
                var_db = SnippetVariableDB(
                    snippet_id=snippet_db.id,
                    key=version_var_db.key,
                    label=version_var_db.label,
                    type=version_var_db.type,
                    placeholder=version_var_db.placeholder,
                    default_value=version_var_db.default_value,
                    required=version_var_db.required,
                    regex=version_var_db.regex,
                    options=version_var_db.options,
                )
                session.add(var_db)

            session.commit()
            session.refresh(snippet_db)

            return self._db_to_pydantic(snippet_db)
