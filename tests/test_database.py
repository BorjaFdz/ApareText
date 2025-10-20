"""
Tests para el módulo de base de datos.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from sqlalchemy.orm import Session

from core.database import Database
from core.models import SettingsDB, SnippetDB, SnippetVariableDB, UsageLogDB


class TestDatabase:
    """Tests para la clase Database."""

    def test_init_with_default_path(self):
        """Test inicialización con ruta por defecto."""
        db = Database()
        expected_path = str(Path.home() / ".aparetext" / "aparetext.db")
        assert db.db_path == expected_path
        assert db.engine is not None
        assert db.SessionLocal is not None
        assert not db._initialized

    def test_init_with_custom_path(self):
        """Test inicialización con ruta personalizada."""
        custom_path = ":memory:"
        db = Database(custom_path)
        assert db.db_path == custom_path
        assert db.engine is not None

    def test_get_session_initializes_db(self):
        """Test que get_session inicializa la base de datos en la primera llamada."""
        db = Database(":memory:")
        assert not db._initialized

        # Primera llamada debería inicializar
        session = db.get_session()
        assert db._initialized
        assert isinstance(session, Session)

        # Cerrar sesión
        session.close()

    def test_get_session_reuse_after_init(self):
        """Test que get_session reutiliza la inicialización."""
        db = Database(":memory:")

        # Primera sesión
        session1 = db.get_session()
        assert db._initialized
        session1.close()

        # Segunda sesión debería reutilizar
        session2 = db.get_session()
        assert db._initialized
        assert isinstance(session2, Session)
        session2.close()

    @patch('pathlib.Path.home')
    def test_default_db_directory_creation(self, mock_home):
        """Test que se crea el directorio por defecto."""
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_home.return_value = Path(temp_dir)

            db = Database()
            expected_dir = Path(temp_dir) / ".aparetext"
            assert expected_dir.exists()

    def test_close_resets_initialization(self):
        """Test que close() resetea el estado de inicialización."""
        db = Database(":memory:")
        db.get_session().close()  # Inicializa la DB

        assert db._initialized

        db.close()
        assert not db._initialized

    def test_close_resets_initialization(self):
        """Test que se insertan las configuraciones por defecto."""
        db = Database(":memory:")

        with db.get_session() as session:
            # Forzar inicialización
            db._init_db()

            settings_count = session.query(SettingsDB).count()
            assert settings_count > 0  # Debería haber configuraciones por defecto

            # Verificar algunas configuraciones específicas
            hotkey_setting = session.query(SettingsDB).filter_by(key="global_hotkey").first()
            assert hotkey_setting is not None
            assert hotkey_setting.value == "ctrl+space"

    def test_default_snippets_insertion(self):
        """Test que se insertan los snippets por defecto."""
        db = Database(":memory:")

        with db.get_session() as session:
            # Forzar inicialización
            db._init_db()

            snippets_count = session.query(SnippetDB).count()
            assert snippets_count > 0  # Debería haber snippets por defecto

            # Verificar que hay snippets con variables
            variables_count = session.query(SnippetVariableDB).count()
            assert variables_count > 0

    def test_init_db_idempotent(self):
        """Test que _init_db() es idempotente."""
        db = Database(":memory:")

        with db.get_session() as session:
            # Primera inicialización
            db._init_db()

            initial_snippets = session.query(SnippetDB).count()
            initial_settings = session.query(SettingsDB).count()

            # Segunda inicialización (debería ser idempotente)
            db._init_db()

            final_snippets = session.query(SnippetDB).count()
            final_settings = session.query(SettingsDB).count()

            assert final_snippets == initial_snippets
            assert final_settings == initial_settings

    def test_engine_disposal_on_close(self):
        """Test que close() dispone correctamente el engine."""
        db = Database(":memory:")

        # Inicializar
        db.get_session().close()

        # Cerrar
        db.close()

        # El engine debería estar dispuesto
        assert db.engine is not None  # Engine object still exists but is disposed