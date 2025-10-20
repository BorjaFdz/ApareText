"""
Tests para el módulo SnippetManager.
"""

import pytest
from unittest.mock import Mock
from datetime import datetime, UTC

from core.database import Database
from core.snippet_manager import SnippetManager
from core.models import Snippet, SnippetVariable, ScopeType, SnippetDB, SnippetVariableDB


class TestSnippetManager:
    """Tests para la clase SnippetManager."""

    @pytest.fixture
    def db(self, tmp_path):
        """Fixture para base de datos en memoria."""
        db_path = str(tmp_path / "test.db")
        db = Database(db_path)
        # Clear default snippets for testing
        with db.get_session() as session:
            session.query(SnippetDB).delete()
            session.query(SnippetVariableDB).delete()
            session.commit()
        return db

    @pytest.fixture
    def manager(self, db):
        """Fixture para SnippetManager."""
        return SnippetManager(db)

    def test_init(self, db):
        """Test inicialización del manager."""
        manager = SnippetManager(db)
        assert manager.db == db

    def test_tags_to_string(self):
        """Test conversión de lista de tags a string."""
        # Lista vacía
        assert SnippetManager._tags_to_string([]) is None

        # Lista con tags
        tags = ["tag1", "tag2", "tag3"]
        result = SnippetManager._tags_to_string(tags)
        assert result == "tag1,tag2,tag3"

    def test_string_to_tags(self):
        """Test conversión de string de tags a lista."""
        # String vacío/None
        assert SnippetManager._string_to_tags(None) == []
        assert SnippetManager._string_to_tags("") == []

        # String con tags
        tag_string = "tag1,tag2,tag3"
        result = SnippetManager._string_to_tags(tag_string)
        assert result == ["tag1", "tag2", "tag3"]

        # Con espacios
        tag_string_with_spaces = " tag1 , tag2 , tag3 "
        result = SnippetManager._string_to_tags(tag_string_with_spaces)
        assert result == ["tag1", "tag2", "tag3"]

    def test_create_snippet_basic(self, manager):
        """Test creación básica de snippet."""
        snippet = Snippet(
            name="Test Snippet",
            abbreviation="test",
            content_text="Test content",
            tags=["test", "basic"]
        )

        created = manager.create_snippet(snippet)

        assert created.id is not None
        assert created.name == "Test Snippet"
        assert created.abbreviation == "test"
        assert created.content_text == "Test content"
        assert created.tags == ["test", "basic"]
        assert created.enabled is True  # Default value

    def test_create_snippet_with_variables(self, manager):
        """Test creación de snippet con variables."""
        variables = [
            SnippetVariable(
                key="name",
                label="Nombre",
                type="text",
                placeholder="Juan Pérez",
                required=True
            ),
            SnippetVariable(
                key="email",
                label="Email",
                type="email",
                placeholder="juan@email.com",
                required=False
            )
        ]

        snippet = Snippet(
            name="Email Template",
            abbreviation="email",
            content_text="Hola {{name}}, tu email es {{email}}",
            variables=variables
        )

        created = manager.create_snippet(snippet)

        assert created.id is not None
        assert len(created.variables) == 2
        assert created.variables[0].key == "name"
        assert created.variables[0].required is True
        assert created.variables[1].key == "email"
        assert created.variables[1].required is False

    def test_get_snippet_existing(self, manager):
        """Test obtener snippet existente."""
        # Crear snippet
        snippet = Snippet(
            name="Test Snippet",
            abbreviation="test",
            content_text="Test content"
        )
        created = manager.create_snippet(snippet)

        # Obtener snippet
        retrieved = manager.get_snippet(created.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == "Test Snippet"
        assert retrieved.abbreviation == "test"

    def test_get_snippet_nonexistent(self, manager):
        """Test obtener snippet inexistente."""
        result = manager.get_snippet("nonexistent-id")
        assert result is None

    def test_get_all_snippets_empty(self, manager):
        """Test obtener todos los snippets cuando no hay ninguno."""
        snippets = manager.get_all_snippets()
        assert snippets == []

    def test_get_all_snippets(self, manager):
        """Test obtener todos los snippets."""
        # Crear varios snippets
        snippet1 = manager.create_snippet(Snippet(
            name="Snippet 1",
            abbreviation="s1",
            content_text="Content 1"
        ))

        snippet2 = manager.create_snippet(Snippet(
            name="Snippet 2",
            abbreviation="s2",
            content_text="Content 2",
            enabled=False
        ))

        # Obtener todos
        all_snippets = manager.get_all_snippets()
        assert len(all_snippets) == 2

        # Obtener solo habilitados
        enabled_snippets = manager.get_all_snippets(enabled_only=True)
        assert len(enabled_snippets) == 1
        assert enabled_snippets[0].id == snippet1.id

    def test_update_snippet(self, manager):
        """Test actualizar snippet."""
        # Crear snippet
        snippet = Snippet(
            name="Original Name",
            abbreviation="orig",
            content_text="Original content",
            tags=["old"]
        )
        created = manager.create_snippet(snippet)

        # Actualizar
        updated_data = Snippet(
            name="Updated Name",
            abbreviation="updated",
            content_text="Updated content",
            tags=["new", "updated"]
        )

        updated = manager.update_snippet(created.id, updated_data)

        assert updated is not None
        assert updated.id == created.id
        assert updated.name == "Updated Name"
        assert updated.abbreviation == "updated"
        assert updated.content_text == "Updated content"
        assert updated.tags == ["new", "updated"]

    def test_update_snippet_nonexistent(self, manager):
        """Test actualizar snippet inexistente."""
        snippet = Snippet(
            name="Test",
            abbreviation="test",
            content_text="Test content"
        )

        result = manager.update_snippet("nonexistent-id", snippet)
        assert result is None

    def test_delete_snippet_existing(self, manager):
        """Test eliminar snippet existente."""
        # Crear snippet
        snippet = Snippet(
            name="Test Snippet",
            abbreviation="test",
            content_text="Test content"
        )
        created = manager.create_snippet(snippet)

        # Verificar que existe
        assert manager.get_snippet(created.id) is not None

        # Eliminar
        result = manager.delete_snippet(created.id)
        assert result is True

        # Verificar que ya no existe
        assert manager.get_snippet(created.id) is None

    def test_delete_snippet_nonexistent(self, manager):
        """Test eliminar snippet inexistente."""
        result = manager.delete_snippet("nonexistent-id")
        assert result is False

    def test_get_snippet_by_abbreviation(self, manager):
        """Test obtener snippet por abreviatura."""
        # Crear snippet
        snippet = Snippet(
            name="Test Snippet",
            abbreviation="testabbr",
            content_text="Test content"
        )
        created = manager.create_snippet(snippet)

        # Obtener por abreviatura
        retrieved = manager.get_snippet_by_abbreviation("testabbr")

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.abbreviation == "testabbr"

    def test_get_snippet_by_abbreviation_nonexistent(self, manager):
        """Test obtener snippet por abreviatura inexistente."""
        result = manager.get_snippet_by_abbreviation("nonexistent")
        assert result is None

    def test_increment_usage(self, manager):
        """Test incrementar contador de uso."""
        # Crear snippet
        snippet = Snippet(
            name="Test Snippet",
            abbreviation="test",
            content_text="Test content",
            usage_count=0
        )
        created = manager.create_snippet(snippet)

        # Verificar contador inicial
        retrieved = manager.get_snippet(created.id)
        assert retrieved.usage_count == 0

        # Incrementar uso
        manager.increment_usage(created.id)

        # Verificar contador incrementado
        retrieved = manager.get_snippet(created.id)
        assert retrieved.usage_count == 1

    def test_log_usage(self, manager):
        """Test registrar uso de snippet."""
        # Crear snippet
        snippet = Snippet(
            name="Test Snippet",
            abbreviation="test",
            content_text="Test content"
        )
        created = manager.create_snippet(snippet)

        # Registrar uso
        manager.log_usage(
            snippet_id=created.id,
            source="desktop",
            target_app="chrome.exe",
            target_domain="example.com"
        )

        # Verificar estadísticas incluyen el uso
        stats = manager.get_usage_stats()
        assert stats["total_uses"] >= 1

    def test_search_snippets_by_name(self, manager):
        """Test búsqueda de snippets por nombre."""
        # Crear snippets
        manager.create_snippet(Snippet(
            name="Python Script",
            abbreviation="py",
            content_text="print('hello')"
        ))

        manager.create_snippet(Snippet(
            name="JavaScript Function",
            abbreviation="js",
            content_text="console.log('hello')"
        ))

        manager.create_snippet(Snippet(
            name="Email Template",
            abbreviation="email",
            content_text="Dear customer..."
        ))

        # Buscar por "python"
        results = manager.search_snippets("python")
        assert len(results) == 1
        assert "Python Script" in results[0].name

        # Buscar por "javascript"
        results = manager.search_snippets("javascript")
        assert len(results) == 1
        assert "JavaScript Function" in results[0].name

        # Buscar por "email"
        results = manager.search_snippets("email")
        assert len(results) == 1
        assert "Email Template" in results[0].name

    def test_search_snippets_by_tags(self, manager):
        """Test búsqueda de snippets por tags."""
        # Crear snippets con tags
        manager.create_snippet(Snippet(
            name="Python Snippet",
            abbreviation="py",
            content_text="print('hello')",
            tags=["python", "code"]
        ))

        manager.create_snippet(Snippet(
            name="JavaScript Snippet",
            abbreviation="js",
            content_text="console.log('hello')",
            tags=["javascript", "code"]
        ))

        # Buscar por tag "python"
        results = manager.search_snippets("python")
        assert len(results) == 1
        assert results[0].tags == ["python", "code"]

        # Buscar por tag "code"
        results = manager.search_snippets("code")
        assert len(results) == 2

    def test_search_snippets_empty_query(self, manager):
        """Test búsqueda con query vacío."""
        # Crear algunos snippets
        manager.create_snippet(Snippet(name="Test 1", abbreviation="t1", content_text="Content 1"))
        manager.create_snippet(Snippet(name="Test 2", abbreviation="t2", content_text="Content 2"))

        # Búsqueda vacía debería devolver todos
        results = manager.search_snippets("")
        assert len(results) == 2

    def test_db_to_pydantic_conversion(self, manager):
        """Test conversión de modelo DB a Pydantic."""
        # Crear snippet en DB
        snippet = Snippet(
            name="Test Snippet",
            abbreviation="test",
            content_text="Test content",
            tags=["tag1", "tag2"],
            category="test_category"
        )
        created = manager.create_snippet(snippet)

        # Obtener el objeto DB
        with manager.db.get_session() as session:
            snippet_db = session.query(SnippetDB).filter_by(id=created.id).first()

            # Convertir usando el método interno
            converted = manager._db_to_pydantic(snippet_db)

            assert converted.id == created.id
            assert converted.name == "Test Snippet"
            assert converted.abbreviation == "test"
            assert converted.tags == ["tag1", "tag2"]
            assert converted.category == "test_category"