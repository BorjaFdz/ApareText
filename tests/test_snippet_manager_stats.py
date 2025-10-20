"""
Tests para las funciones de estadísticas del SnippetManager.
"""

import pytest
from datetime import datetime, timedelta, UTC
from unittest.mock import Mock

from core.database import Database
from core.models import UsageLogDB, SnippetDB
from core.snippet_manager import SnippetManager


class TestSnippetManagerStats:
    """Tests para las funciones de estadísticas."""

    @pytest.fixture
    def db(self):
        """Fixture para base de datos en memoria."""
        db = Database(":memory:")
        # Inicializar la base de datos llamando get_session()
        with db.get_session() as session:
            pass  # Solo para inicializar
        return db

    @pytest.fixture
    def manager(self, db):
        """Fixture para SnippetManager."""
        return SnippetManager(db)

    def test_get_usage_stats_empty(self, manager):
        """Test estadísticas con base de datos que tiene snippets por defecto."""
        stats = manager.get_usage_stats()

        assert stats["total_uses"] == 0  # No hay usos aún
        assert stats["total_snippets"] >= 0  # Puede tener snippets por defecto
        assert stats["enabled_snippets"] >= 0
        assert stats["by_source"] == {}
        assert stats["by_app"] == {}
        assert stats["by_domain"] == {}
        assert stats["by_hour"] == {}
        assert stats["by_day"] == {}
        assert stats["by_month"] == {}
        # Time series arrays are always populated with date ranges
        assert len(stats["daily_usage"]) == 30  # Last 30 days
        assert len(stats["weekly_usage"]) == 12  # Last 12 weeks
        assert len(stats["monthly_usage"]) == 12  # Last 12 months
        # All counts should be 0 since there are no logs
        assert all(item["count"] == 0 for item in stats["daily_usage"])
        assert all(item["count"] == 0 for item in stats["weekly_usage"])
        assert all(item["count"] == 0 for item in stats["monthly_usage"])
        assert stats["recent_activity"] == 0
        assert isinstance(stats["top_snippets"], list)
        assert isinstance(stats["category_stats"], dict)
        assert "version_stats" in stats
        assert "productivity_metrics" in stats

    def test_get_usage_stats_with_data(self, manager, db):
        """Test estadísticas con datos de uso."""
        with db.get_session() as session:
            # Crear snippets de prueba
            snippet1 = SnippetDB(
                name="Test Snippet 1",
                abbreviation="ts1",
                category="Test",
                enabled=True
            )
            snippet2 = SnippetDB(
                name="Test Snippet 2",
                abbreviation="ts2",
                category="Work",
                enabled=True
            )
            session.add(snippet1)
            session.add(snippet2)
            session.commit()

            # Crear logs de uso
            now = datetime.now(UTC)
            logs = [
                UsageLogDB(
                    snippet_id=snippet1.id,
                    timestamp=now,
                    source="desktop",
                    target_app="chrome.exe",
                    target_domain="google.com"
                ),
                UsageLogDB(
                    snippet_id=snippet1.id,
                    timestamp=now - timedelta(hours=1),
                    source="desktop",
                    target_app="vscode.exe",
                    target_domain="github.com"
                ),
                UsageLogDB(
                    snippet_id=snippet2.id,
                    timestamp=now - timedelta(days=1),
                    source="extension",
                    target_app="firefox.exe",
                    target_domain="stackoverflow.com"
                ),
            ]
            for log in logs:
                session.add(log)
            session.commit()

        stats = manager.get_usage_stats()

        # Verificar estadísticas básicas
        assert stats["total_uses"] == 3
        assert stats["total_snippets"] == 8  # 6 default + 2 test snippets
        assert stats["enabled_snippets"] == 8

        # Verificar agrupaciones
        assert stats["by_source"]["desktop"] == 2
        assert stats["by_source"]["extension"] == 1
        assert stats["by_app"]["chrome.exe"] == 1
        assert stats["by_app"]["vscode.exe"] == 1
        assert stats["by_app"]["firefox.exe"] == 1

        # Verificar top snippets
        assert len(stats["top_snippets"]) == 2
        assert stats["top_snippets"][0]["usage_count"] == 2  # snippet1
        assert stats["top_snippets"][1]["usage_count"] == 1  # snippet2

        # Verificar categorías
        assert stats["category_stats"]["Test"] == 1
        assert stats["category_stats"]["Work"] == 1

    def test_get_usage_stats_time_series(self, manager, db):
        """Test series temporales de uso."""
        with db.get_session() as session:
            # Crear snippet
            snippet = SnippetDB(name="Test", abbreviation="t", enabled=True)
            session.add(snippet)
            session.commit()

            # Crear logs en diferentes días
            base_date = datetime.now(UTC).replace(hour=12, minute=0, second=0, microsecond=0)
            logs = []
            for i in range(10):
                log_date = base_date - timedelta(days=i)
                log = UsageLogDB(
                    snippet_id=snippet.id,
                    timestamp=log_date,
                    source="desktop"
                )
                logs.append(log)
                session.add(log)
            session.commit()

        stats = manager.get_usage_stats()

        # Verificar que hay datos en las series temporales
        assert len(stats["daily_usage"]) > 0
        assert len(stats["weekly_usage"]) > 0
        assert len(stats["monthly_usage"]) > 0

        # Verificar que los datos están ordenados
        daily_dates = [item["date"] for item in stats["daily_usage"]]
        assert daily_dates == sorted(daily_dates)

        weekly_weeks = [item["week"] for item in stats["weekly_usage"]]
        assert weekly_weeks == sorted(weekly_weeks)

        monthly_months = [item["month"] for item in stats["monthly_usage"]]
        assert monthly_months == sorted(monthly_months)

    def test_get_usage_stats_specific_snippet(self, manager, db):
        """Test estadísticas para un snippet específico."""
        with db.get_session() as session:
            # Crear dos snippets
            snippet1 = SnippetDB(name="Snippet 1", abbreviation="s1", enabled=True)
            snippet2 = SnippetDB(name="Snippet 2", abbreviation="s2", enabled=True)
            session.add(snippet1)
            session.add(snippet2)
            session.commit()

            snippet1_id = snippet1.id  # Store ID before session closes

            # Crear logs para ambos snippets
            now = datetime.now(UTC)
            logs = [
                UsageLogDB(snippet_id=snippet1.id, timestamp=now, source="desktop"),
                UsageLogDB(snippet_id=snippet1.id, timestamp=now - timedelta(hours=1), source="desktop"),
                UsageLogDB(snippet_id=snippet2.id, timestamp=now, source="extension"),
            ]
            for log in logs:
                session.add(log)
            session.commit()

        # Obtener stats para snippet1 específico
        stats = manager.get_usage_stats(snippet_id=snippet1_id)

        assert stats["total_uses"] == 2
        assert stats["by_source"]["desktop"] == 2
        assert "extension" not in stats["by_source"]

        # Top snippets no debería estar presente para stats de snippet específico
        assert stats["top_snippets"] == []

    def test_get_usage_stats_productivity_metrics(self, manager, db):
        """Test métricas de productividad."""
        with db.get_session() as session:
            snippet = SnippetDB(name="Test", abbreviation="t", enabled=True)
            session.add(snippet)
            session.commit()

            # Crear logs en diferentes horas y días
            base_date = datetime.now(UTC).replace(hour=9, minute=0, second=0, microsecond=0)
            logs = []

            # Lunes: 3 usos
            monday = base_date - timedelta(days=base_date.weekday())
            for i in range(3):
                log = UsageLogDB(
                    snippet_id=snippet.id,
                    timestamp=monday + timedelta(hours=i),
                    source="desktop"
                )
                logs.append(log)

            # Martes: 2 usos
            tuesday = monday + timedelta(days=1)
            for i in range(2):
                log = UsageLogDB(
                    snippet_id=snippet.id,
                    timestamp=tuesday + timedelta(hours=i),
                    source="desktop"
                )
                logs.append(log)

            for log in logs:
                session.add(log)
            session.commit()

        stats = manager.get_usage_stats()

        # Verificar métricas de productividad
        assert "productivity_metrics" in stats
        metrics = stats["productivity_metrics"]

        assert "avg_daily_uses" in metrics
        assert "most_active_hour" in metrics
        assert "most_active_day" in metrics

        # Verificar que los valores son razonables
        assert isinstance(metrics["avg_daily_uses"], (int, float))
        assert metrics["avg_daily_uses"] > 0

    def test_get_usage_stats_hourly_distribution(self, manager, db):
        """Test distribución por horas del día."""
        with db.get_session() as session:
            snippet = SnippetDB(name="Test", abbreviation="t", enabled=True)
            session.add(snippet)
            session.commit()

            # Crear logs en diferentes horas
            base_date = datetime.now(UTC).replace(minute=0, second=0, microsecond=0)
            hours_to_test = [9, 14, 9, 10, 14, 14]  # Más usos en hora 14

            for hour in hours_to_test:
                log_time = base_date.replace(hour=hour)
                log = UsageLogDB(
                    snippet_id=snippet.id,
                    timestamp=log_time,
                    source="desktop"
                )
                session.add(log)
            session.commit()

        stats = manager.get_usage_stats()

        # Verificar distribución por horas
        assert stats["by_hour"][9] == 2  # 2 usos a las 9
        assert stats["by_hour"][10] == 1  # 1 uso a las 10
        assert stats["by_hour"][14] == 3  # 3 usos a las 14

        # Verificar que la hora más activa es 14
        assert stats["productivity_metrics"]["most_active_hour"] == 14

    def test_get_usage_stats_weekly_distribution(self, manager, db):
        """Test distribución por días de la semana."""
        with db.get_session() as session:
            snippet = SnippetDB(name="Test", abbreviation="t", enabled=True)
            session.add(snippet)
            session.commit()

            # Crear logs en diferentes días de la semana
            base_date = datetime.now(UTC).replace(hour=12, minute=0, second=0, microsecond=0)

            # Encontrar el lunes de esta semana
            monday = base_date - timedelta(days=base_date.weekday())

            days_data = [
                (0, 2),  # Lunes: 2 usos
                (1, 1),  # Martes: 1 uso
                (2, 4),  # Miércoles: 4 usos
                (3, 1),  # Jueves: 1 uso
            ]

            for day_offset, count in days_data:
                log_date = monday + timedelta(days=day_offset)
                for i in range(count):
                    log = UsageLogDB(
                        snippet_id=snippet.id,
                        timestamp=log_date + timedelta(hours=i),
                        source="desktop"
                    )
                    session.add(log)
            session.commit()

        stats = manager.get_usage_stats()

        # Verificar distribución por días
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday"]
        expected_counts = [2, 1, 4, 1]

        for i, (day_name, expected_count) in enumerate(zip(day_names, expected_counts)):
            assert stats["by_day"][day_name] == expected_count

        # Verificar que el día más activo es Wednesday
        assert stats["productivity_metrics"]["most_active_day"] == "Wednesday"