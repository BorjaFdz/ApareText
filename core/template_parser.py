"""
Parser de plantillas para snippets con variables y funciones.
"""

import re
from datetime import datetime
from typing import Any, Optional


class TemplateParser:
    """
    Parser de plantillas de snippets.

    Soporta:
    - Variables: {{nombre}}, {{email}}
    - Cursor: {{|}}
    - Funciones: {{date:%Y-%m-%d}}, {{clipboard}}
    - Escapes: \\{{ para llaves literales
    """

    # Patrones regex
    VARIABLE_PATTERN = re.compile(r"\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}")
    CURSOR_PATTERN = re.compile(r"\{\{\|\}\}")
    FUNCTION_PATTERN = re.compile(r"\{\{(date|clipboard|time)(:[^}]+)?\}\}")
    ESCAPE_PATTERN = re.compile(r"\\(\{\{)")

    def __init__(self):
        """Inicializar parser."""
        self._clipboard_value: Optional[str] = None

    def set_clipboard(self, value: str) -> None:
        """
        Establecer valor del portapapeles para función {{clipboard}}.

        Args:
            value: Contenido del portapapeles
        """
        self._clipboard_value = value

    def extract_variables(self, template: str) -> list[str]:
        """
        Extraer lista de variables únicas del template.

        Args:
            template: Template string

        Returns:
            Lista de nombres de variables (sin duplicados)
        """
        matches = self.VARIABLE_PATTERN.findall(template)
        # Excluir funciones reservadas
        reserved = {"date", "clipboard", "time"}
        variables = [m for m in matches if m not in reserved]
        return list(dict.fromkeys(variables))  # Eliminar duplicados manteniendo orden

    def has_cursor_marker(self, template: str) -> bool:
        """
        Verificar si el template tiene marcador de cursor.

        Args:
            template: Template string

        Returns:
            True si contiene {{|}}
        """
        return bool(self.CURSOR_PATTERN.search(template))

    def parse(
        self,
        template: str,
        variables: Optional[dict[str, Any]] = None,
        remove_cursor: bool = False,
    ) -> str:
        """
        Parsear template reemplazando variables y funciones.

        Args:
            template: Template string
            variables: Diccionario con valores de variables
            remove_cursor: Si True, elimina el marcador {{|}}

        Returns:
            Template procesado
        """
        if variables is None:
            variables = {}

        result = template

        # 1. Procesar funciones
        result = self._process_functions(result)

        # 2. Reemplazar variables
        result = self._replace_variables(result, variables)

        # 3. Procesar cursor
        if remove_cursor:
            result = self.CURSOR_PATTERN.sub("", result)

        # 4. Procesar escapes
        result = self._unescape(result)

        return result

    def parse_with_cursor_position(
        self, template: str, variables: Optional[dict[str, Any]] = None
    ) -> tuple[str, int]:
        """
        Parsear template y devolver posición del cursor.

        Args:
            template: Template string
            variables: Diccionario con valores de variables

        Returns:
            Tupla (texto_procesado, posición_cursor)
            Si no hay marcador, posición es -1 (final del texto)
        """
        # Reemplazar marcador con placeholder único
        cursor_placeholder = "<<<CURSOR_HERE>>>"
        temp = self.CURSOR_PATTERN.sub(cursor_placeholder, template)

        # Parsear template
        result = self.parse(temp, variables, remove_cursor=False)

        # Encontrar posición del cursor
        cursor_pos = result.find(cursor_placeholder)
        if cursor_pos >= 0:
            result = result.replace(cursor_placeholder, "")
        else:
            cursor_pos = -1  # Final del texto

        return result, cursor_pos

    def _process_functions(self, template: str) -> str:
        """Procesar funciones del template."""

        def replace_function(match: re.Match) -> str:
            func_name = match.group(1)
            func_arg = match.group(2)

            if func_name == "date":
                return self._process_date_function(func_arg)
            elif func_name == "time":
                return self._process_time_function(func_arg)
            elif func_name == "clipboard":
                return self._process_clipboard_function()

            return match.group(0)  # No reemplazar si no se reconoce

        return self.FUNCTION_PATTERN.sub(replace_function, template)

    def _process_datetime_function(self, func_name: str, format_arg: Optional[str], default_format: str) -> str:
        """Procesar funciones de fecha/hora {{date:format}} o {{time:format}}."""
        if format_arg:
            dt_format = format_arg.lstrip(":")
        else:
            dt_format = default_format

        try:
            return datetime.now().strftime(dt_format)
        except ValueError:
            return f"{{{{{func_name}{format_arg or ''}}}}}"  # Formato inválido, devolver original

    def _process_date_function(self, format_arg: Optional[str]) -> str:
        """Procesar función {{date:format}}."""
        return self._process_datetime_function("date", format_arg, "%Y-%m-%d")

    def _process_time_function(self, format_arg: Optional[str]) -> str:
        """Procesar función {{time:format}}."""
        return self._process_datetime_function("time", format_arg, "%H:%M:%S")

    def _process_clipboard_function(self) -> str:
        """Procesar función {{clipboard}}."""
        if self._clipboard_value is not None:
            return self._clipboard_value
        return "{{clipboard}}"  # No disponible

    def _replace_variables(self, template: str, variables: dict[str, Any]) -> str:
        """Reemplazar variables del template."""

        def replace_var(match: re.Match) -> str:
            var_name = match.group(1)

            # Ignorar funciones reservadas
            if var_name in {"date", "clipboard", "time"}:
                return match.group(0)

            # Reemplazar si existe
            if var_name in variables:
                value = variables[var_name]
                return str(value) if value is not None else ""

            # Si no existe, dejar como está
            return match.group(0)

        return self.VARIABLE_PATTERN.sub(replace_var, template)

    def _unescape(self, template: str) -> str:
        """Procesar escapes \\{{ -> {{."""
        return self.ESCAPE_PATTERN.sub(r"\1", template)

    def validate_template(self, template: str) -> tuple[bool, Optional[str]]:
        """
        Validar sintaxis del template.

        Args:
            template: Template string

        Returns:
            Tupla (es_válido, mensaje_error)
        """
        # Verificar llaves balanceadas
        open_braces = template.count("{{")
        close_braces = template.count("}}")

        if open_braces != close_braces:
            return False, f"Unbalanced braces: {open_braces} opening, {close_braces} closing"

        # Encontrar todos los patrones {{...}}
        all_patterns = re.findall(r'\{\{([^}]+)\}\}', template)
        
        for pattern in all_patterns:
            # Verificar si es función conocida
            func_name = pattern.split(':', 1)[0] if ':' in pattern else pattern
            if func_name in {"date", "clipboard", "time"}:
                # Es una función válida
                continue
            elif pattern == "|":
                # Cursor marker es válido
                continue
            else:
                # Debe ser variable válida
                if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", pattern):
                    return False, f"Invalid variable name: {pattern}"

        return True, None

    def get_template_info(self, template: str) -> dict[str, Any]:
        """
        Obtener información del template.

        Args:
            template: Template string

        Returns:
            Diccionario con información del template
        """
        return {
            "variables": self.extract_variables(template),
            "has_cursor": self.has_cursor_marker(template),
            "functions_used": self._extract_functions(template),
            "is_valid": self.validate_template(template)[0],
        }

    def _extract_functions(self, template: str) -> list[str]:
        """Extraer funciones usadas en el template."""
        matches = self.FUNCTION_PATTERN.findall(template)
        return list(dict.fromkeys([m[0] for m in matches]))  # Eliminar duplicados
