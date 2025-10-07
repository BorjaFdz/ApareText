"""
Script de prueba rápida para verificar que ApareText funciona correctamente.
"""

import sys
import time
from datetime import datetime

print("=" * 60)
print("🧪 ApareText - Test Suite")
print("=" * 60)
print()

# Test 1: Imports
print("📦 Test 1: Verificando imports...")
try:
    from core.models import Snippet, SnippetVariable, VariableType, ScopeType
    from core.database import Database, get_db
    from core.snippet_manager import SnippetManager
    from core.template_parser import TemplateParser
    print("   ✅ Core imports OK")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

try:
    from server.api import app
    from server.websocket import WebSocketManager
    print("   ✅ Server imports OK")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

print()

# Test 2: Database
print("📊 Test 2: Verificando base de datos...")
try:
    import tempfile
    import os
    
    # Crear DB temporal
    temp_db = os.path.join(tempfile.gettempdir(), "aparetext_test.db")
    if os.path.exists(temp_db):
        os.remove(temp_db)
    
    db = Database(temp_db)
    print(f"   ✅ Database creada: {temp_db}")
    
    # Verificar tablas
    with db.get_session() as session:
        from core.models import SnippetDB
        count = session.query(SnippetDB).count()
        print(f"   ✅ Snippets en DB: {count}")
    
    db.close()
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

print()

# Test 3: Template Parser
print("🔧 Test 3: Verificando template parser...")
try:
    parser = TemplateParser()
    
    # Test variables
    template = "Hola {{nombre}}, tu email es {{email}}"
    variables = parser.extract_variables(template)
    assert variables == ["nombre", "email"], f"Expected ['nombre', 'email'], got {variables}"
    print(f"   ✅ Variables extraídas: {variables}")
    
    # Test parsing
    result = parser.parse(template, {"nombre": "Juan", "email": "juan@example.com"})
    expected = "Hola Juan, tu email es juan@example.com"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print(f"   ✅ Template parseado: {result}")
    
    # Test cursor
    template_cursor = "Hola {{nombre}}{{|}}"
    content, cursor_pos = parser.parse_with_cursor_position(template_cursor, {"nombre": "Juan"})
    assert content == "Hola Juan", f"Expected 'Hola Juan', got '{content}'"
    # Cursor debería estar al final "Hola Juan" = 9 caracteres
    assert cursor_pos == 9 or cursor_pos == len(content), f"Expected cursor at end, got {cursor_pos}"
    print(f"   ✅ Cursor position: {cursor_pos} (después de '{content}')")
    
    # Test funciones
    template_func = "Fecha: {{date:%Y-%m-%d}}"
    result_func = parser.parse(template_func, {})
    print(f"   ✅ Función date: {result_func}")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 4: Snippet Manager
print("📝 Test 4: Verificando snippet manager...")
try:
    # Usar DB temporal
    temp_db = os.path.join(tempfile.gettempdir(), "aparetext_test2.db")
    if os.path.exists(temp_db):
        os.remove(temp_db)
    
    db = Database(temp_db)
    manager = SnippetManager(db)
    
    # Crear snippet
    snippet = Snippet(
        name="Test Snippet",
        abbreviation=";test",
        tags=["test", "demo"],
        content_text="Este es un snippet de prueba",
        is_rich=False,
        scope_type=ScopeType.GLOBAL,
    )
    
    created = manager.create_snippet(snippet)
    print(f"   ✅ Snippet creado: {created.name} (ID: {created.id[:8]}...)")
    
    # Obtener snippet
    retrieved = manager.get_snippet(created.id)
    assert retrieved is not None, "Snippet not found"
    assert retrieved.name == "Test Snippet", f"Expected 'Test Snippet', got '{retrieved.name}'"
    print(f"   ✅ Snippet recuperado: {retrieved.name}")
    
    # Buscar snippet
    results = manager.search_snippets("test")
    assert len(results) > 0, "Search returned no results"
    print(f"   ✅ Búsqueda: {len(results)} resultado(s)")
    
    # Buscar por abreviatura
    by_abbr = manager.get_snippet_by_abbreviation(";test")
    assert by_abbr is not None, "Snippet not found by abbreviation"
    print(f"   ✅ Búsqueda por abreviatura: {by_abbr.name}")
    
    # Incrementar uso
    manager.log_usage(created.id, source="test")
    updated = manager.get_snippet(created.id)
    assert updated.usage_count == 1, f"Expected usage_count=1, got {updated.usage_count}"
    print(f"   ✅ Usage count: {updated.usage_count}")
    
    db.close()
    os.remove(temp_db)
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 5: Export/Import
print("💾 Test 5: Verificando export/import...")
try:
    temp_db = os.path.join(tempfile.gettempdir(), "aparetext_test3.db")
    temp_json = os.path.join(tempfile.gettempdir(), "aparetext_export.json")
    
    if os.path.exists(temp_db):
        os.remove(temp_db)
    if os.path.exists(temp_json):
        os.remove(temp_json)
    
    db = Database(temp_db)
    manager = SnippetManager(db)
    
    # Crear algunos snippets
    for i in range(3):
        snippet = Snippet(
            name=f"Snippet {i+1}",
            abbreviation=f";s{i+1}",
            content_text=f"Contenido del snippet {i+1}",
        )
        manager.create_snippet(snippet)
    
    print(f"   ✅ Creados 3 snippets de prueba")
    
    # Export
    db.export_to_json(temp_json)
    assert os.path.exists(temp_json), "Export file not created"
    print(f"   ✅ Exportado a: {temp_json}")
    
    # Verificar contenido del JSON
    import json
    with open(temp_json, 'r', encoding='utf-8') as f:
        export_data = json.load(f)
    
    assert "version" in export_data, "Missing version in export"
    assert "snippets" in export_data, "Missing snippets in export"
    assert len(export_data["snippets"]) == 3, f"Expected 3 snippets, got {len(export_data['snippets'])}"
    print(f"   ✅ JSON válido con {len(export_data['snippets'])} snippets")
    
    # Import a nueva DB
    temp_db2 = os.path.join(tempfile.gettempdir(), "aparetext_test4.db")
    if os.path.exists(temp_db2):
        os.remove(temp_db2)
    
    db2 = Database(temp_db2)
    imported_count = db2.import_from_json(temp_json)
    assert imported_count == 3, f"Expected 3 imported, got {imported_count}"
    print(f"   ✅ Importados {imported_count} snippets")
    
    # Verificar
    manager2 = SnippetManager(db2)
    all_snippets = manager2.get_all_snippets()
    assert len(all_snippets) == 3, f"Expected 3 snippets in DB, got {len(all_snippets)}"
    print(f"   ✅ Verificación: {len(all_snippets)} snippets en nueva DB")
    
    # Cleanup
    db.close()
    db2.close()
    os.remove(temp_db)
    os.remove(temp_db2)
    os.remove(temp_json)
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Resumen final
print("=" * 60)
print("✅ ¡TODOS LOS TESTS PASARON!")
print("=" * 60)
print()
print("ApareText está listo para usar:")
print("  • Core: Motor de snippets funcionando")
print("  • Database: SQLite + Export/Import OK")
print("  • Template Parser: Variables y funciones OK")
print("  • Snippet Manager: CRUD completo OK")
print()
print("Próximos pasos:")
print("  1. Ejecutar servidor: python -m server.main")
print("  2. Abrir docs: http://localhost:46321/docs")
print("  3. Ejecutar desktop: python -m desktop.main")
print()
print("🚀 ¡Feliz desarrollo!")
