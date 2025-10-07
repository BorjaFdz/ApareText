"""
Detector de abreviaturas en tiempo real.
Escucha el teclado y expande snippets cuando detecta una abreviatura + trigger.
"""

import platform
import time
from typing import Callable, Optional

from core.database import get_db
from core.snippet_manager import SnippetManager
from core.template_parser import TemplateParser

SYSTEM = platform.system()


class AbbreviationDetector:
    """
    Detector de abreviaturas que escucha el teclado y expande snippets.
    
    Detecta patrones como:
    - ;firma + Tab
    - ;hola + Space
    - ;meeting + Enter
    """

    def __init__(
        self,
        snippet_manager: SnippetManager,
        trigger_key: str = "tab",
        max_abbr_length: int = 20,
        on_expand: Optional[Callable] = None,
    ):
        """
        Inicializar detector.

        Args:
            snippet_manager: Manager de snippets
            trigger_key: Tecla disparadora ('tab', 'space', 'enter')
            max_abbr_length: Longitud máxima de abreviatura a detectar
            on_expand: Callback cuando se expande un snippet
        """
        self.snippet_manager = snippet_manager
        self.parser = TemplateParser()
        self.trigger_key = trigger_key.lower()
        self.max_abbr_length = max_abbr_length
        self.on_expand = on_expand

        # Buffer de teclas recientes
        self.key_buffer: list[str] = []
        self.last_key_time = time.time()
        self.buffer_timeout = 2.0  # segundos

        # Estado
        self.is_listening = False
        self.keyboard_lib = None

        # Inicializar backend
        self._init_keyboard()

    def _init_keyboard(self) -> None:
        """Inicializar biblioteca de teclado según plataforma."""
        if SYSTEM in ["Windows", "Linux"]:
            try:
                import keyboard

                self.keyboard_lib = keyboard
                self.backend = "keyboard"
                print("✅ Abbreviation detector: keyboard backend")
            except ImportError:
                print("⚠️ keyboard library not found")
                self.backend = None
        elif SYSTEM == "Darwin":
            try:
                from pynput import keyboard

                self.keyboard_lib = keyboard
                self.backend = "pynput"
                print("✅ Abbreviation detector: pynput backend")
            except ImportError:
                print("⚠️ pynput library not found")
                self.backend = None
        else:
            print(f"⚠️ Platform {SYSTEM} not supported for abbreviation detection")
            self.backend = None

    def start(self) -> bool:
        """
        Iniciar detección de abreviaturas.

        Returns:
            True si se inició correctamente
        """
        if not self.backend:
            print("❌ Cannot start: no keyboard backend")
            return False

        if self.is_listening:
            print("⚠️ Already listening")
            return True

        try:
            if self.backend == "keyboard":
                # keyboard library (Windows/Linux)
                # Usar hook en lugar de on_press para no bloquear
                self.keyboard_lib.hook(self._on_key_press_keyboard, suppress=False)
                print(f"🎧 Listening for abbreviations (trigger: {self.trigger_key})")
            elif self.backend == "pynput":
                # pynput (macOS)
                listener = self.keyboard_lib.Listener(on_press=self._on_key_press_pynput)
                listener.start()
                print(f"🎧 Listening for abbreviations (trigger: {self.trigger_key})")

            self.is_listening = True
            return True

        except Exception as e:
            print(f"❌ Failed to start listener: {e}")
            return False

    def stop(self) -> None:
        """Detener detección de abreviaturas."""
        if not self.is_listening:
            return

        try:
            if self.backend == "keyboard":
                self.keyboard_lib.unhook_all()
            # pynput se detiene automáticamente

            self.is_listening = False
            print("🔇 Stopped listening for abbreviations")

        except Exception as e:
            print(f"⚠️ Error stopping listener: {e}")

    def _on_key_press_keyboard(self, event) -> None:
        """
        Callback para biblioteca keyboard (Windows/Linux).

        Args:
            event: Evento de tecla
        """
        try:
            key_name = event.name.lower()
            self._process_key(key_name)
        except Exception as e:
            print(f"⚠️ Error processing key: {e}")

    def _on_key_press_pynput(self, key) -> None:
        """
        Callback para biblioteca pynput (macOS).

        Args:
            key: Tecla presionada
        """
        try:
            # Obtener nombre de tecla
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
        """
        Procesar tecla presionada.

        Args:
            key_name: Nombre de la tecla
        """
        current_time = time.time()

        # Limpiar buffer si ha pasado mucho tiempo
        if current_time - self.last_key_time > self.buffer_timeout:
            self.key_buffer.clear()

        self.last_key_time = current_time

        # Verificar si es la tecla disparadora
        if self._is_trigger_key(key_name):
            self._check_for_abbreviation()
            return

        # Agregar tecla al buffer
        if self._is_text_key(key_name):
            self.key_buffer.append(key_name)

            # Limitar tamaño del buffer
            if len(self.key_buffer) > self.max_abbr_length:
                self.key_buffer.pop(0)

    def _is_trigger_key(self, key_name: str) -> bool:
        """
        Verificar si la tecla es la disparadora.

        Args:
            key_name: Nombre de la tecla

        Returns:
            True si es la tecla disparadora
        """
        if self.trigger_key == "tab":
            return key_name in ["tab"]
        elif self.trigger_key == "space":
            return key_name in ["space", " "]
        elif self.trigger_key == "enter":
            return key_name in ["enter", "return"]
        return False

    def _is_text_key(self, key_name: str) -> bool:
        """
        Verificar si la tecla es de texto (alfanumérica o símbolo).

        Args:
            key_name: Nombre de la tecla

        Returns:
            True si es una tecla de texto
        """
        # Teclas especiales a ignorar
        ignore_keys = [
            "shift",
            "ctrl",
            "alt",
            "cmd",
            "command",
            "option",
            "tab",
            "enter",
            "return",
            "backspace",
            "delete",
            "escape",
            "esc",
            "up",
            "down",
            "left",
            "right",
            "home",
            "end",
            "page_up",
            "page_down",
        ]

        if key_name in ignore_keys:
            return False

        # Aceptar letras, números y algunos símbolos
        return len(key_name) == 1 or key_name.startswith(";")

    def _check_for_abbreviation(self) -> None:
        """Verificar si el buffer contiene una abreviatura válida."""
        if not self.key_buffer:
            return

        # Construir texto del buffer
        buffer_text = "".join(self.key_buffer)

        # Buscar snippet por abreviatura
        snippet = self.snippet_manager.get_snippet_by_abbreviation(buffer_text)

        if snippet:
            print(f"🎯 Detected abbreviation: {buffer_text}")
            self._expand_snippet(snippet)
        else:
            # Limpiar buffer si no hay coincidencia
            self.key_buffer.clear()

    def _expand_snippet(self, snippet) -> None:
        """
        Expandir snippet detectado.

        Args:
            snippet: Snippet a expandir
        """
        # Limpiar buffer
        abbr_length = len(snippet.abbreviation) if snippet.abbreviation else 0
        self.key_buffer.clear()

        # TODO: Si tiene variables, mostrar formulario
        if snippet.variables:
            print(f"⚠️ Snippet has variables (form not yet implemented): {snippet.name}")
            if self.on_expand:
                self.on_expand(snippet, needs_form=True)
            return

        # Obtener contenido
        content = snippet.content_text
        if snippet.is_rich and snippet.content_html:
            content = snippet.content_html

        if not content:
            print(f"⚠️ Snippet has no content: {snippet.name}")
            return

        # Parsear template
        expanded = self.parser.parse(content, {})

        # Callback
        if self.on_expand:
            self.on_expand(snippet, content=expanded, abbr_length=abbr_length)
        else:
            print(f"📝 Would expand: {snippet.name}")
            print(f"   Content: {expanded[:50]}...")

        # Log de uso
        self.snippet_manager.log_usage(snippet.id, source="abbreviation")


def test_detector():
    """Función de prueba del detector."""
    from core.database import get_db

    print("=" * 60)
    print("🧪 Test: Abbreviation Detector")
    print("=" * 60)
    print()

    # Inicializar
    db = get_db()
    manager = SnippetManager(db)

    # Callback de prueba
    def on_expand(snippet, content=None, needs_form=False, abbr_length=0):
        print()
        print(f"✨ EXPAND: {snippet.name}")
        if needs_form:
            print(f"   → Needs variable form")
        elif content:
            print(f"   → Content: {content[:100]}...")
            print(f"   → Should delete {abbr_length} characters")
        print()

    # Crear detector
    detector = AbbreviationDetector(
        snippet_manager=manager, trigger_key="tab", on_expand=on_expand
    )

    # Verificar snippets
    snippets = manager.get_all_snippets()
    print(f"Snippets disponibles: {len(snippets)}")
    for s in snippets:
        if s.abbreviation:
            print(f"  • {s.abbreviation} → {s.name}")
    print()

    # Iniciar detector
    success = detector.start()
    if not success:
        print("❌ Failed to start detector")
        return

    print("🎧 Detector activo!")
    print(f"   Escribe una abreviatura + {detector.trigger_key.upper()}")
    print("   Ejemplos: ;firma + TAB, ;hola + TAB")
    print()
    print("Presiona Ctrl+C para salir")
    print()

    try:
        # Mantener vivo
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Deteniendo detector...")
        detector.stop()
        print("✅ Detector detenido")


if __name__ == "__main__":
    test_detector()
