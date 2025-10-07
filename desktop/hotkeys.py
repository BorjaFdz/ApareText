"""
Gestor de hotkeys globales (multiplataforma).
"""

import platform
from typing import Callable, Optional

# Intentar importar bibliotecas según plataforma
SYSTEM = platform.system()


class HotkeyManager:
    """
    Gestor de hotkeys globales multiplataforma.

    Soporta Windows, macOS y Linux (X11).
    """

    def __init__(self):
        """Inicializar gestor de hotkeys."""
        self.callbacks: dict[str, Callable] = {}
        self.system = SYSTEM

        # Backend específico de plataforma
        if self.system == "Windows":
            self._init_windows()
        elif self.system == "Darwin":
            self._init_macos()
        elif self.system == "Linux":
            self._init_linux()
        else:
            print(f"⚠️ Platform {self.system} not fully supported for hotkeys")

    def _init_windows(self) -> None:
        """Inicializar backend para Windows."""
        try:
            import keyboard

            self.backend = "keyboard"
            self.keyboard = keyboard
            print("✅ Windows hotkey backend: keyboard")
        except ImportError:
            print("⚠️ keyboard library not found. Install: pip install keyboard")
            self.backend = None

    def _init_macos(self) -> None:
        """Inicializar backend para macOS."""
        try:
            from pynput import keyboard

            self.backend = "pynput"
            self.keyboard = keyboard
            print("✅ macOS hotkey backend: pynput")
            print("⚠️ Remember to grant Accessibility permissions!")
        except ImportError:
            print("⚠️ pynput library not found. Install: pip install pynput")
            self.backend = None

    def _init_linux(self) -> None:
        """Inicializar backend para Linux."""
        try:
            import keyboard

            self.backend = "keyboard"
            self.keyboard = keyboard
            print("✅ Linux hotkey backend: keyboard")
            print("⚠️ May require root or xhost permissions")
        except ImportError:
            print("⚠️ keyboard library not found. Install: pip install keyboard")
            self.backend = None

    def register(self, hotkey: str, callback: Callable) -> bool:
        """
        Registrar hotkey global.

        Args:
            hotkey: Combinación de teclas (ej: "ctrl+space", "alt+j")
            callback: Función a ejecutar

        Returns:
            True si se registró exitosamente
        """
        if not self.backend:
            print(f"⚠️ Cannot register hotkey {hotkey}: no backend available")
            return False

        try:
            self.callbacks[hotkey] = callback

            if self.backend == "keyboard":
                # keyboard library (Windows/Linux)
                self.keyboard.add_hotkey(hotkey, callback, suppress=False)
                print(f"✅ Registered hotkey: {hotkey}")
                return True

            elif self.backend == "pynput":
                # pynput (macOS)
                # TODO: Implementar con pynput.keyboard.GlobalHotKeys
                print(f"⚠️ pynput hotkey registration not yet implemented")
                return False

        except Exception as e:
            print(f"❌ Failed to register hotkey {hotkey}: {e}")
            return False

        return False

    def unregister(self, hotkey: str) -> bool:
        """
        Desregistrar hotkey.

        Args:
            hotkey: Combinación de teclas

        Returns:
            True si se desregistró
        """
        if not self.backend or hotkey not in self.callbacks:
            return False

        try:
            if self.backend == "keyboard":
                self.keyboard.remove_hotkey(hotkey)

            del self.callbacks[hotkey]
            print(f"✅ Unregistered hotkey: {hotkey}")
            return True

        except Exception as e:
            print(f"❌ Failed to unregister hotkey {hotkey}: {e}")
            return False

    def unregister_all(self) -> None:
        """Desregistrar todos los hotkeys."""
        hotkeys = list(self.callbacks.keys())
        for hotkey in hotkeys:
            self.unregister(hotkey)

    def is_supported(self) -> bool:
        """Verificar si hotkeys están soportados en esta plataforma."""
        return self.backend is not None
