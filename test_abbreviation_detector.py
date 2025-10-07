"""
Prueba del detector de abreviaturas.
Escucha abreviaturas y simula expansión (sin insertar texto).
"""

import sys
import time
import os

# Agregar directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.database import get_db
from core.snippet_manager import SnippetManager

# Importar solo el módulo necesario (sin PySide6)
import platform
from typing import Callable, Optional

from core.template_parser import TemplateParser


SYSTEM = platform.system()


class SimpleAbbreviationDetector:
    """Detector simplificado sin dependencias de desktop."""

    def __init__(
        self,
        snippet_manager: SnippetManager,
        trigger_key: str = "tab",
        on_expand: Optional[Callable] = None,
    ):
        self.snippet_manager = snippet_manager
        self.parser = TemplateParser()
        self.trigger_key = trigger_key.lower()
        self.on_expand = on_expand

        # Buffer de teclas
        self.key_buffer: list[str] = []
        self.last_key_time = time.time()
        self.buffer_timeout = 2.0

        # Estado
        self.is_listening = False
        self.keyboard_lib = None

        # Inicializar backend
        self._init_keyboard()

    def _init_keyboard(self) -> None:
        """Inicializar biblioteca de teclado."""
        if SYSTEM in ["Windows", "Linux"]:
            try:
                import keyboard
                self.keyboard_lib = keyboard
                self.backend = "keyboard"
            except ImportError:
                print("⚠️ keyboard library not found")
                print("   Install: pip install keyboard")
                self.backend = None
        elif SYSTEM == "Darwin":
            try:
                from pynput import keyboard
                self.keyboard_lib = keyboard
                self.backend = "pynput"
            except ImportError:
                print("⚠️ pynput library not found")
                print("   Install: pip install pynput")
                self.backend = None
        else:
            print(f"⚠️ Platform {SYSTEM} not supported")
            self.backend = None

    def start(self) -> bool:
        """Iniciar detección."""
        if not self.backend:
            return False

        if self.is_listening:
            return True

        try:
            if self.backend == "keyboard":
                self.keyboard_lib.on_press(self._on_key_press_keyboard)
            elif self.backend == "pynput":
                listener = self.keyboard_lib.Listener(on_press=self._on_key_press_pynput)
                listener.start()

            self.is_listening = True
            return True

        except Exception as e:
            print(f"❌ Failed to start listener: {e}")
            return False

    def stop(self) -> None:
        """Detener detección."""
        if not self.is_listening:
            return

        try:
            if self.backend == "keyboard":
                self.keyboard_lib.unhook_all()
            self.is_listening = False
        except Exception as e:
            print(f"⚠️ Error stopping listener: {e}")

    def _on_key_press_keyboard(self, event) -> None:
        """Callback para keyboard (Windows/Linux)."""
        try:
            key_name = event.name.lower()
            self._process_key(key_name)
        except Exception as e:
            print(f"⚠️ Error processing key: {e}")

    def _on_key_press_pynput(self, key) -> None:
        """Callback para pynput (macOS)."""
        try:
            if hasattr(key, "char") and key.char:
                key_name = key.char.lower()
            elif hasattr(key, "name"):
                key_name = key.name.lower()
            else:
                key_name = str(key).lower()
            self._process_key(key_name)
        except Exception as e:
            print(f"⚠️ Error processing key: {e}")

    def _process_key(self, key_name: str) -> None:
        """Procesar tecla."""
        current_time = time.time()

        # Limpiar buffer si timeout
        if current_time - self.last_key_time > self.buffer_timeout:
            self.key_buffer.clear()

        self.last_key_time = current_time

        # Verificar trigger
        if self._is_trigger_key(key_name):
            self._check_for_abbreviation()
            return

        # Agregar al buffer
        if self._is_text_key(key_name):
            self.key_buffer.append(key_name)
            if len(self.key_buffer) > 20:
                self.key_buffer.pop(0)

    def _is_trigger_key(self, key_name: str) -> bool:
        """Verificar si es tecla trigger."""
        if self.trigger_key == "tab":
            return key_name in ["tab"]
        elif self.trigger_key == "space":
            return key_name in ["space", " "]
        elif self.trigger_key == "enter":
            return key_name in ["enter", "return"]
        return False

    def _is_text_key(self, key_name: str) -> bool:
        """Verificar si es tecla de texto."""
        ignore_keys = [
            "shift", "ctrl", "alt", "cmd", "command", "option",
            "tab", "enter", "return", "backspace", "delete",
            "escape", "esc", "up", "down", "left", "right",
            "home", "end", "page_up", "page_down",
        ]
        if key_name in ignore_keys:
            return False
        return len(key_name) == 1 or key_name.startswith(";")

    def _check_for_abbreviation(self) -> None:
        """Verificar si hay abreviatura en buffer."""
        if not self.key_buffer:
            return

        buffer_text = "".join(self.key_buffer)
        snippet = self.snippet_manager.get_snippet_by_abbreviation(buffer_text)

        if snippet:
            self._expand_snippet(snippet)
        else:
            self.key_buffer.clear()

    def _expand_snippet(self, snippet) -> None:
        """Expandir snippet."""
        abbr_length = len(snippet.abbreviation) if snippet.abbreviation else 0
        self.key_buffer.clear()

        # Si tiene variables
        if snippet.variables:
            if self.on_expand:
                self.on_expand(snippet, needs_form=True)
            return

        # Obtener contenido
        content = snippet.content_text
        if snippet.is_rich and snippet.content_html:
            content = snippet.content_html

        if not content:
            return

        # Parsear
        expanded = self.parser.parse(content, {})

        # Callback
        if self.on_expand:
            self.on_expand(snippet, content=expanded, abbr_length=abbr_length)

        # Log
        self.snippet_manager.log_usage(snippet.id, source="abbreviation")


def main():
    """Función principal de prueba."""
    print("=" * 60)
    print("🧪 Test: Abbreviation Detector")
    print("=" * 60)
    print()

    # Inicializar
    db = get_db()
    manager = SnippetManager(db)

    # Listar snippets disponibles
    snippets = manager.get_all_snippets()
    print(f"📚 Snippets disponibles: {len(snippets)}")
    print()

    abbr_snippets = [s for s in snippets if s.abbreviation]
    if not abbr_snippets:
        print("⚠️ No hay snippets con abreviaturas.")
        print("   Ejecuta create_example_snippets.py primero")
        return 1

    print("Abreviaturas registradas:")
    for s in abbr_snippets:
        scope_info = ""
        if s.scope_type != "global" and s.scope_values:
            if s.scope_type == "domains":
                scope_info = f" [🌐 {', '.join(s.scope_values)}]"
            elif s.scope_type == "apps":
                scope_info = f" [💻 {', '.join(s.scope_values)}]"
        
        var_info = ""
        if s.variables:
            var_keys = [v.key for v in s.variables]
            var_info = f" [vars: {', '.join(var_keys)}]"
        
        print(f"  • {s.abbreviation:<12} → {s.name}{scope_info}{var_info}")
    print()

    # Callback de prueba
    def on_expand(snippet, content=None, needs_form=False, abbr_length=0):
        print()
        print("=" * 60)
        print(f"✨ DETECTED: {snippet.abbreviation}")
        print(f"   Snippet: {snippet.name}")
        
        if needs_form:
            print(f"   ⚠️ Needs variable form")
            if snippet.variables:
                print(f"   Variables: {[v.key for v in snippet.variables]}")
        elif content:
            preview = content[:80] + "..." if len(content) > 80 else content
            print(f"   Content: {preview}")
            print(f"   Would delete: {abbr_length + 1} chars (abbr + trigger)")
        
        print("=" * 60)
        print()

    # Crear detector
    print("🎧 Inicializando detector de abreviaturas...")
    detector = SimpleAbbreviationDetector(
        snippet_manager=manager, 
        trigger_key="tab",
        on_expand=on_expand
    )

    # Iniciar detector
    success = detector.start()
    if not success:
        print("❌ No se pudo iniciar el detector")
        print("   Verifica que las bibliotecas keyboard/pynput estén instaladas")
        return 1

    print()
    print("✅ Detector activo!")
    print()
    print("=" * 60)
    print("Instrucciones:")
    print("  1. Abre cualquier aplicación (Notepad, VS Code, etc.)")
    print("  2. Escribe una abreviatura: ;firma, ;hola, ;fecha, etc.")
    print("  3. Presiona TAB")
    print("  4. Verás la detección en esta consola")
    print()
    print("Presiona Ctrl+C para salir")
    print("=" * 60)
    print()

    try:
        # Mantener vivo
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Deteniendo detector...")
        detector.stop()
        print("✅ Detector detenido")
        return 0


if __name__ == "__main__":
    sys.exit(main())
