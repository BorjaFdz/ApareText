"""
Inserción de texto en aplicaciones (tecleo o portapapeles).
"""

import platform
import time
from typing import Optional

# Detectar plataforma
SYSTEM = platform.system()


class TextInserter:
    """
    Insertar texto en aplicaciones activas.

    Soporta dos métodos:
    1. Tecleo simulado (type) - Más natural pero más lento
    2. Portapapeles (clipboard) - Más rápido pero modifica clipboard
    """

    def __init__(self, method: str = "auto", typing_speed: int = 50):
        """
        Inicializar inserter.

        Args:
            method: 'type', 'clipboard', o 'auto' (intenta type, fallback a clipboard)
            typing_speed: Milisegundos entre teclas para método 'type'
        """
        self.method = method
        self.typing_speed = typing_speed / 1000.0  # Convertir a segundos
        self.system = SYSTEM

        # Inicializar backends
        self._init_backends()

    def _init_backends(self) -> None:
        """Inicializar backends según plataforma."""
        self.keyboard_available = False
        self.clipboard_available = False

        # Keyboard backend
        if self.system in ["Windows", "Linux"]:
            try:
                import keyboard

                self.keyboard_lib = keyboard
                self.keyboard_available = True
                print("✅ Keyboard backend available")
            except ImportError:
                print("⚠️ keyboard library not found")

        elif self.system == "Darwin":
            try:
                from pynput import keyboard

                self.keyboard_lib = keyboard
                self.keyboard_available = True
                print("✅ pynput backend available (macOS)")
            except ImportError:
                print("⚠️ pynput library not found")

        # Clipboard backend
        try:
            import pyperclip

            self.pyperclip = pyperclip
            self.clipboard_available = True
            print("✅ Clipboard backend available")
        except ImportError:
            print("⚠️ pyperclip library not found")

    def insert_text(self, text: str) -> bool:
        """
        Insertar texto en aplicación activa.

        Args:
            text: Texto a insertar

        Returns:
            True si se insertó exitosamente
        """
        if self.method == "type":
            return self._insert_by_typing(text)

        elif self.method == "clipboard":
            return self._insert_by_clipboard(text)

        elif self.method == "auto":
            # Intentar tecleo primero
            if self.keyboard_available:
                success = self._insert_by_typing(text)
                if success:
                    return True

            # Fallback a clipboard
            if self.clipboard_available:
                return self._insert_by_clipboard(text)

        return False

    def _insert_by_typing(self, text: str) -> bool:
        """
        Insertar texto simulando tecleo.

        Args:
            text: Texto a insertar

        Returns:
            True si exitoso
        """
        if not self.keyboard_available:
            print("⚠️ Keyboard backend not available")
            return False

        try:
            # Pequeño delay antes de empezar
            time.sleep(0.1)

            if self.system in ["Windows", "Linux"]:
                # keyboard library
                self.keyboard_lib.write(text, delay=self.typing_speed)

            elif self.system == "Darwin":
                # pynput (macOS)
                controller = self.keyboard_lib.Controller()
                for char in text:
                    controller.type(char)
                    time.sleep(self.typing_speed)

            return True

        except Exception as e:
            print(f"❌ Failed to insert by typing: {e}")
            return False

    def _insert_by_clipboard(self, text: str) -> bool:
        """
        Insertar texto usando portapapeles + Ctrl/Cmd+V.

        Args:
            text: Texto a insertar

        Returns:
            True si exitoso
        """
        if not self.clipboard_available:
            print("⚠️ Clipboard backend not available")
            return False

        try:
            # Guardar contenido actual del portapapeles
            original_clipboard = None
            try:
                original_clipboard = self.pyperclip.paste()
            except Exception:
                pass

            # Copiar texto al portapapeles
            self.pyperclip.copy(text)

            # Pequeño delay
            time.sleep(0.05)

            # Simular Ctrl+V (o Cmd+V en macOS)
            if self.system in ["Windows", "Linux"]:
                if self.keyboard_available:
                    self.keyboard_lib.send("ctrl+v")
                else:
                    print("⚠️ Cannot paste: keyboard library not available")
                    return False

            elif self.system == "Darwin":
                if self.keyboard_available:
                    controller = self.keyboard_lib.Controller()
                    with controller.pressed(self.keyboard_lib.Key.cmd):
                        controller.press("v")
                        controller.release("v")
                else:
                    print("⚠️ Cannot paste: pynput not available")
                    return False

            # Delay antes de restaurar
            time.sleep(0.1)

            # Restaurar clipboard original
            if original_clipboard is not None:
                try:
                    self.pyperclip.copy(original_clipboard)
                except Exception:
                    pass

            return True

        except Exception as e:
            print(f"❌ Failed to insert by clipboard: {e}")
            return False

    def _delete_chars(self, count: int) -> bool:
        """
        Borrar caracteres simulando tecla Backspace.

        Args:
            count: Número de caracteres a borrar

        Returns:
            True si exitoso
        """
        if not self.keyboard_available:
            print("⚠️ Keyboard backend not available for deletion")
            return False

        try:
            time.sleep(0.05)

            if self.system in ["Windows", "Linux"]:
                # keyboard library
                for _ in range(count):
                    self.keyboard_lib.press_and_release("backspace")
                    time.sleep(0.01)

            elif self.system == "Darwin":
                # pynput (macOS)
                controller = self.keyboard_lib.Controller()
                for _ in range(count):
                    controller.press(self.keyboard_lib.Key.backspace)
                    controller.release(self.keyboard_lib.Key.backspace)
                    time.sleep(0.01)

            return True

        except Exception as e:
            print(f"❌ Failed to delete characters: {e}")
            return False

    def get_available_methods(self) -> list[str]:
        """
        Obtener métodos de inserción disponibles.

        Returns:
            Lista de métodos disponibles
        """
        methods = []

        if self.keyboard_available:
            methods.append("type")

        if self.clipboard_available:
            methods.append("clipboard")

        if methods:
            methods.append("auto")

        return methods
