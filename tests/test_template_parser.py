"""
Tests para el módulo TemplateParser.
"""

import pytest
from unittest.mock import patch
from datetime import datetime

from core.template_parser import TemplateParser


class TestTemplateParser:
    """Tests para la clase TemplateParser."""

    @pytest.fixture
    def parser(self):
        """Fixture para TemplateParser."""
        return TemplateParser()

    def test_init(self):
        """Test inicialización del parser."""
        parser = TemplateParser()
        assert parser._clipboard_value is None

    def test_set_clipboard(self, parser):
        """Test establecer valor del portapapeles."""
        parser.set_clipboard("test content")
        assert parser._clipboard_value == "test content"

    def test_extract_variables_simple(self, parser):
        """Test extracción de variables simples."""
        template = "Hola {{nombre}}, tu email es {{email}}"
        variables = parser.extract_variables(template)
        assert variables == ["nombre", "email"]

    def test_extract_variables_duplicates(self, parser):
        """Test extracción de variables con duplicados."""
        template = "Hola {{nombre}}, {{nombre}} es tu nombre"
        variables = parser.extract_variables(template)
        assert variables == ["nombre"]

    def test_extract_variables_reserved_words(self, parser):
        """Test que las funciones reservadas no se incluyan como variables."""
        template = "Fecha: {{date}}, Clipboard: {{clipboard}}, Hora: {{time}}"
        variables = parser.extract_variables(template)
        assert variables == []

    def test_extract_variables_mixed(self, parser):
        """Test extracción de variables mixtas con funciones."""
        template = "Hola {{nombre}}, fecha: {{date}}, email: {{email}}"
        variables = parser.extract_variables(template)
        assert variables == ["nombre", "email"]

    def test_extract_variables_empty_template(self, parser):
        """Test extracción de variables en template vacío."""
        variables = parser.extract_variables("")
        assert variables == []

    def test_extract_variables_no_variables(self, parser):
        """Test extracción cuando no hay variables."""
        template = "Este es un texto sin variables"
        variables = parser.extract_variables(template)
        assert variables == []

    def test_has_cursor_marker_true(self, parser):
        """Test detección de marcador de cursor presente."""
        template = "Hola {{nombre}}, {{|}} aquí va el cursor"
        assert parser.has_cursor_marker(template) is True

    def test_has_cursor_marker_false(self, parser):
        """Test detección de marcador de cursor ausente."""
        template = "Hola {{nombre}}, sin cursor aquí"
        assert parser.has_cursor_marker(template) is False

    def test_has_cursor_marker_empty(self, parser):
        """Test detección de marcador en template vacío."""
        assert parser.has_cursor_marker("") is False

    def test_parse_simple_variables(self, parser):
        """Test parseo de variables simples."""
        template = "Hola {{nombre}}, tienes {{edad}} años"
        variables = {"nombre": "Juan", "edad": 25}
        result = parser.parse(template, variables)
        assert result == "Hola Juan, tienes 25 años"

    def test_parse_missing_variables(self, parser):
        """Test parseo con variables faltantes."""
        template = "Hola {{nombre}}, tienes {{edad}} años"
        variables = {"nombre": "Juan"}
        result = parser.parse(template, variables)
        assert result == "Hola Juan, tienes {{edad}} años"

    def test_parse_none_variables(self, parser):
        """Test parseo con variables None."""
        template = "Hola {{nombre}}, {{apellido}}"
        variables = {"nombre": "Juan", "apellido": None}
        result = parser.parse(template, variables)
        assert result == "Hola Juan, "

    def test_parse_date_function_default(self, parser):
        """Test función date con formato por defecto."""
        template = "Fecha: {{date}}"
        result = parser.parse(template)
        # Verificar que contiene una fecha en formato YYYY-MM-DD
        assert "Fecha: 2025-" in result or "Fecha: 2024-" in result

    def test_parse_date_function_custom_format(self, parser):
        """Test función date con formato personalizado."""
        template = "Fecha: {{date:%d/%m/%Y}}"
        result = parser.parse(template)
        # Verificar formato DD/MM/YYYY
        assert "Fecha: " in result
        date_part = result.split(": ")[1]
        assert len(date_part.split("/")) == 3

    def test_parse_time_function_default(self, parser):
        """Test función time con formato por defecto."""
        template = "Hora: {{time}}"
        result = parser.parse(template)
        # Verificar que contiene una hora en formato HH:MM:SS
        assert "Hora: " in result
        time_part = result.split(": ")[1]
        assert ":" in time_part

    def test_parse_time_function_custom_format(self, parser):
        """Test función time con formato personalizado."""
        template = "Hora: {{time:%H:%M}}"
        result = parser.parse(template)
        # Verificar formato HH:MM
        assert "Hora: " in result
        time_part = result.split(": ")[1]
        parts = time_part.split(":")
        assert len(parts) == 2

    def test_parse_clipboard_function_with_value(self, parser):
        """Test función clipboard con valor establecido."""
        parser.set_clipboard("copied text")
        template = "Pegar: {{clipboard}}"
        result = parser.parse(template)
        assert result == "Pegar: copied text"

    def test_parse_clipboard_function_without_value(self, parser):
        """Test función clipboard sin valor establecido."""
        template = "Pegar: {{clipboard}}"
        result = parser.parse(template)
        assert result == "Pegar: {{clipboard}}"

    def test_parse_mixed_functions_and_variables(self, parser):
        """Test parseo mixto de funciones y variables."""
        parser.set_clipboard("test")
        template = "Hola {{nombre}}, fecha {{date:%d/%m}}, clipboard: {{clipboard}}"
        variables = {"nombre": "Juan"}
        result = parser.parse(template, variables)
        assert "Hola Juan, fecha " in result
        assert "clipboard: test" in result
        assert "{{date:" not in result

    def test_parse_cursor_removal_true(self, parser):
        """Test eliminación del marcador de cursor."""
        template = "Hola {{nombre}}, {{|}} aquí"
        variables = {"nombre": "Juan"}
        result = parser.parse(template, variables, remove_cursor=True)
        assert result == "Hola Juan,  aquí"

    def test_parse_cursor_removal_false(self, parser):
        """Test mantener marcador de cursor."""
        template = "Hola {{nombre}}, {{|}} aquí"
        variables = {"nombre": "Juan"}
        result = parser.parse(template, variables, remove_cursor=False)
        assert result == "Hola Juan, {{|}} aquí"

    def test_parse_escapes(self, parser):
        """Test procesamiento de escapes."""
        template = "Mostrar llaves: \\{{literal}} y variable {{nombre}}"
        variables = {"nombre": "Juan"}
        result = parser.parse(template, variables)
        assert result == "Mostrar llaves: {{literal}} y variable Juan"

    def test_parse_with_cursor_position_with_marker(self, parser):
        """Test parseo con posición del cursor cuando hay marcador."""
        template = "Hola {{nombre}}, {{|}} bienvenido"
        variables = {"nombre": "Juan"}
        result, cursor_pos = parser.parse_with_cursor_position(template, variables)
        assert result == "Hola Juan,  bienvenido"
        assert cursor_pos == 11  # Posición después de "Hola Juan, "

    def test_parse_with_cursor_position_no_marker(self, parser):
        """Test parseo con posición del cursor cuando no hay marcador."""
        template = "Hola {{nombre}}, bienvenido"
        variables = {"nombre": "Juan"}
        result, cursor_pos = parser.parse_with_cursor_position(template, variables)
        assert result == "Hola Juan, bienvenido"
        assert cursor_pos == -1

    def test_parse_with_cursor_position_at_start(self, parser):
        """Test parseo con cursor al inicio."""
        template = "{{|}}Hola {{nombre}}"
        variables = {"nombre": "Juan"}
        result, cursor_pos = parser.parse_with_cursor_position(template, variables)
        assert result == "Hola Juan"
        assert cursor_pos == 0

    def test_parse_with_cursor_position_at_end(self, parser):
        """Test parseo con cursor al final."""
        template = "Hola {{nombre}}{{|}}"
        variables = {"nombre": "Juan"}
        result, cursor_pos = parser.parse_with_cursor_position(template, variables)
        assert result == "Hola Juan"
        assert cursor_pos == 9

    def test_validate_template_valid(self, parser):
        """Test validación de template válido."""
        template = "Hola {{nombre}}, fecha {{date:%d/%m}}"
        valid, error = parser.validate_template(template)
        assert valid is True
        assert error is None

    def test_validate_template_unbalanced_braces(self, parser):
        """Test validación con llaves desbalanceadas."""
        template = "Hola {{nombre, fecha {{date}}"
        valid, error = parser.validate_template(template)
        assert valid is False
        assert "Unbalanced braces" in error

    def test_validate_template_unknown_function(self, parser):
        """Test validación con función desconocida."""
        template = "Hola {{unknown_func:%Y-%m-%d}}"
        valid, error = parser.validate_template(template)
        assert valid is False
        assert "Unknown function: unknown_func" in error

    def test_validate_template_invalid_variable_name(self, parser):
        """Test validación con nombre de variable inválido."""
        template = "Hola {{123invalid}}"
        valid, error = parser.validate_template(template)
        assert valid is False
        assert "Invalid variable name: 123invalid" in error

    def test_validate_template_valid_variable_names(self, parser):
        """Test validación con nombres de variables válidos."""
        template = "Hola {{nombre}}, {{_var}}, {{var123}}, {{VAR_NAME}}"
        valid, error = parser.validate_template(template)
        assert valid is True
        assert error is None

    def test_get_template_info(self, parser):
        """Test obtener información del template."""
        parser.set_clipboard("test")
        template = "Hola {{nombre}}, fecha {{date}}, {{|}} cursor aquí"
        variables = {"nombre": "Juan"}

        info = parser.get_template_info(template)

        assert info["variables"] == ["nombre"]
        assert info["has_cursor"] is True
        assert "date" in info["functions_used"]
        assert info["is_valid"] is True

    def test_get_template_info_invalid(self, parser):
        """Test información de template inválido."""
        template = "Hola {{123invalid}}"
        info = parser.get_template_info(template)
        assert info["is_valid"] is False

    def test_process_datetime_function_invalid_format(self, parser):
        """Test función datetime con formato inválido."""
        template = "Fecha: {{date:%INVALID}}"
        result = parser.parse(template)
        # strftime processes invalid codes partially, so we get partial result
        assert "Fecha: " in result and "INVALID" in result

    @patch('core.template_parser.datetime')
    def test_parse_date_function_mocked(self, mock_datetime, parser):
        """Test función date con datetime mockeado."""
        mock_datetime.now.return_value = datetime(2023, 10, 20, 15, 30, 45)
        template = "Fecha: {{date:%Y-%m-%d}}"
        result = parser.parse(template)
        assert result == "Fecha: 2023-10-20"

    @patch('core.template_parser.datetime')
    def test_parse_time_function_mocked(self, mock_datetime, parser):
        """Test función time con datetime mockeado."""
        mock_datetime.now.return_value = datetime(2023, 10, 20, 15, 30, 45)
        template = "Hora: {{time:%H:%M:%S}}"
        result = parser.parse(template)
        assert result == "Hora: 15:30:45"

    def test_extract_functions_unique(self, parser):
        """Test extracción de funciones únicas."""
        template = "Fecha {{date}}, otra {{date}}, hora {{time}}"
        functions = parser._extract_functions(template)
        assert set(functions) == {"date", "time"}

    def test_extract_functions_empty(self, parser):
        """Test extracción de funciones en template sin funciones."""
        template = "Hola {{nombre}}"
        functions = parser._extract_functions(template)
        assert functions == []

    def test_complex_template(self, parser):
        """Test template complejo con múltiples características."""
        parser.set_clipboard("pasted content")
        template = """Asunto: {{asunto}}

Estimado {{cliente}},

Le escribo para {{motivo}}.

Fecha: {{date:%d/%m/%Y}}
Hora: {{time:%H:%M}}

Contenido pegado: {{clipboard}}

{{|}}
Atentamente,
{{firma}}"""

        variables = {
            "asunto": "Consulta importante",
            "cliente": "Sr. García",
            "motivo": "informarle sobre el proyecto",
            "firma": "Juan Pérez"
        }

        result, cursor_pos = parser.parse_with_cursor_position(template, variables)

        # Verificar que las variables se reemplazaron
        assert "Asunto: Consulta importante" in result
        assert "Estimado Sr. García" in result
        assert "informarle sobre el proyecto" in result
        assert "Atentamente," in result
        assert "Juan Pérez" in result

        # Verificar funciones
        assert "Fecha: " in result
        assert "Hora: " in result
        assert "Contenido pegado: pasted content" in result

        # Verificar cursor al final
        assert cursor_pos > 0
        assert result[cursor_pos:].strip() == "Atentamente,\nJuan Pérez"