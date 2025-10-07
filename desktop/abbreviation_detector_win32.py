"""
Detector de abreviaturas usando Win32 API (sin bloquear UI).
Usa SetWindowsHookEx para capturar teclas de forma asíncrona.
"""

import platform
import time
from typing import Callable, Optional
from ctypes import windll, WINFUNCTYPE, c_int, c_void_p, byref
from ctypes.wintypes import DWORD, WPARAM, LPARAM

from core.snippet_manager import SnippetManager
from core.template_parser import TemplateParser

SYSTEM = platform.system()

# Constantes Win32
WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
WM_SYSKEYDOWN = 0x0104


class Win32AbbreviationDetector:
    """
    Detector de abreviaturas usando Win32 API.
    No bloquea el thread principal de Qt.
    """

    def __init__(
        self,
        snippet_manager: SnippetManager,
        trigger_key: int = 0x09,  # VK_TAB
        max_abbr_length: int = 20,
        on_expand: Optional[Callable] = None,
    ):
        """
        Inicializar detector.

        Args:
            snippet_manager: Manager de snippets
            trigger_key: Virtual key code del trigger (0x09 = Tab)
            max_abbr_length: Longitud máxima de abreviatura
            on_expand: Callback cuando se expande un snippet
        """
        self.snippet_manager = snippet_manager
        self.parser = TemplateParser()
        self.trigger_key = trigger_key
        self.max_abbr_length = max_abbr_length
        self.on_expand = on_expand

        # Buffer de teclas
        self.key_buffer: list[str] = []
        self.last_key_time = time.time()
        self.buffer_timeout = 2.0

        # Estado
        self.is_listening = False
        self.hook = None
        
        # Solo en Windows
        if SYSTEM != "Windows":
            print(f"⚠️ Win32 detector only works on Windows (current: {SYSTEM})")

    def start(self) -> bool:
        """
        Iniciar detección de abreviaturas.

        Returns:
            True si se inició correctamente
        """
        if SYSTEM != "Windows":
            return False

        if self.is_listening:
            return True

        try:
            # Crear función de callback para el hook
            self.keyboard_callback = WINFUNCTYPE(c_int, c_int, WPARAM, LPARAM)(
                self._keyboard_hook_callback
            )

            # Instalar hook de teclado de bajo nivel
            user32 = windll.user32
            kernel32 = windll.kernel32
            
            hook_id = user32.SetWindowsHookExW(
                WH_KEYBOARD_LL,
                self.keyboard_callback,
                kernel32.GetModuleHandleW(None),
                0
            )

            if not hook_id:
                print("❌ Failed to install keyboard hook")
                return False

            self.hook = hook_id
            self.is_listening = True
            print("✅ Win32 keyboard hook installed (non-blocking)")
            print(f"🎧 Listening for abbreviations (trigger: Tab)")
            return True

        except Exception as e:
            print(f"❌ Failed to start Win32 detector: {e}")
            return False

    def stop(self) -> None:
        """Detener detección."""
        if not self.is_listening or not self.hook:
            return

        try:
            windll.user32.UnhookWindowsHookEx(self.hook)
            self.hook = None
            self.is_listening = False
            print("🔇 Win32 keyboard hook removed")
        except Exception as e:
            print(f"⚠️ Error stopping Win32 detector: {e}")

    def _keyboard_hook_callback(self, nCode: int, wParam: WPARAM, lParam: LPARAM) -> int:
        """
        Callback del hook de teclado Win32.
        
        Args:
            nCode: Hook code
            wParam: Message identifier
            lParam: Pointer to keyboard struct
            
        Returns:
            Result to pass to next hook
        """
        try:
            if nCode >= 0 and wParam in (WM_KEYDOWN, WM_SYSKEYDOWN):
                # Obtener virtual key code
                import ctypes
                vk_code = ctypes.cast(lParam, ctypes.POINTER(ctypes.c_ulong)).contents.value & 0xFFFFFFFF
                vk_code = (vk_code >> 0) & 0xFF  # Extraer byte bajo

                self._process_key(vk_code)

        except Exception as e:
            print(f"⚠️ Error in keyboard hook: {e}")

        # Llamar al siguiente hook en la cadena
        return windll.user32.CallNextHookEx(None, nCode, wParam, lParam)

    def _process_key(self, vk_code: int) -> None:
        """
        Procesar tecla presionada.

        Args:
            vk_code: Virtual key code
        """
        current_time = time.time()

        # Limpiar buffer si ha pasado mucho tiempo
        if current_time - self.last_key_time > self.buffer_timeout:
            self.key_buffer.clear()

        self.last_key_time = current_time

        # Verificar si es la tecla disparadora
        if vk_code == self.trigger_key:
            self._check_for_abbreviation()
            return

        # Convertir VK a carácter
        char = self._vk_to_char(vk_code)
        if char and self._is_text_key(char):
            self.key_buffer.append(char)

            # Limitar tamaño del buffer
            if len(self.key_buffer) > self.max_abbr_length:
                self.key_buffer.pop(0)

    def _vk_to_char(self, vk_code: int) -> Optional[str]:
        """
        Convertir virtual key code a carácter.

        Args:
            vk_code: Virtual key code

        Returns:
            Carácter o None
        """
        # Letras A-Z (0x41-0x5A)
        if 0x41 <= vk_code <= 0x5A:
            return chr(vk_code).lower()

        # Números 0-9 (0x30-0x39)
        if 0x30 <= vk_code <= 0x39:
            return chr(vk_code)

        # Símbolos comunes
        symbol_map = {
            0xBA: ";",  # VK_OEM_1 (;:)
            0xBD: "-",  # VK_OEM_MINUS
            0xBB: "=",  # VK_OEM_PLUS
            0xDB: "[",  # VK_OEM_4
            0xDD: "]",  # VK_OEM_6
            0xDC: "\\", # VK_OEM_5
            0xBC: ",",  # VK_OEM_COMMA
            0xBE: ".",  # VK_OEM_PERIOD
            0xBF: "/",  # VK_OEM_2
        }

        return symbol_map.get(vk_code)

    def _is_text_key(self, char: str) -> bool:
        """
        Verificar si es un carácter válido.

        Args:
            char: Carácter

        Returns:
            True si es válido
        """
        return len(char) == 1 and (char.isalnum() or char in ";-_.,/")

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

        # Log de uso
        self.snippet_manager.log_usage(snippet.id, source="abbreviation")
