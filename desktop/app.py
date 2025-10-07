"""
Aplicación principal de escritorio.
"""

import sys
import platform
import threading
from typing import Optional

from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QSystemTrayIcon

from core.database import get_db
from core.snippet_manager import SnippetManager
from desktop.hotkeys import HotkeyManager
from desktop.inserter import TextInserter
from desktop.palette import CommandPalette
from desktop.settings_window import SettingsWindow
from desktop.tray import TrayIcon

# Importar detector según plataforma
if platform.system() == "Windows":
    from desktop.abbreviation_detector_win32 import Win32AbbreviationDetector as AbbreviationDetector
else:
    from desktop.abbreviation_detector import AbbreviationDetector


class DesktopApp:
    """Aplicación principal de escritorio."""

    def __init__(self):
        """Inicializar aplicación."""
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("ApareText")
        self.app.setOrganizationName("ApareText")

        # Base de datos
        self.db = get_db()
        self.snippet_manager = SnippetManager(self.db)

        # Ventanas
        self.palette: Optional[CommandPalette] = None
        self.settings_window: Optional[SettingsWindow] = None

        # System tray primero
        self.tray = TrayIcon(self)
        self.tray.show()

        # Estado
        self.is_paused = False

        # Text inserter
        self.text_inserter = TextInserter()

        # Inicializar hotkeys y detector en un timer
        # para no bloquear la inicialización de Qt
        QTimer.singleShot(500, self._init_background_services)

        print("✅ ApareText Desktop initialized")

    def _init_background_services(self) -> None:
        """Inicializar servicios en background (hotkeys, detector)."""
        def init_thread():
            try:
                # Hotkeys
                self.hotkey_manager = HotkeyManager()
                self.setup_hotkeys()
                
                print("✅ Hotkeys initialized")
                
                # Abbreviation detector (Win32 no bloquea)
                self.abbreviation_detector = AbbreviationDetector(
                    snippet_manager=self.snippet_manager,
                    trigger_key=0x09,  # VK_TAB
                    on_expand=self.on_abbreviation_expand,
                )
                
                # Iniciar detector
                if self.abbreviation_detector.start():
                    print("✅ Abbreviation detector initialized (Win32 hook)")
                else:
                    print("⚠️ Abbreviation detector failed to start")
                
            except Exception as e:
                print(f"⚠️ Failed to initialize services: {e}")
                import traceback
                traceback.print_exc()
        
        # Ejecutar en thread separado
        thread = threading.Thread(target=init_thread, daemon=True)
        thread.start()

    def setup_hotkeys(self) -> None:
        """Configurar hotkeys globales."""
        try:
            # Hotkey para abrir paleta (Ctrl+Space por defecto)
            self.hotkey_manager.register("ctrl+space", self.show_palette)
            print("✅ Global hotkey registered: Ctrl+Space")
        except Exception as e:
            print(f"⚠️ Failed to register hotkey: {e}")

    def show_palette(self) -> None:
        """Mostrar paleta de comandos."""
        if self.is_paused:
            return

        if self.palette is None:
            self.palette = CommandPalette(self.snippet_manager)

        self.palette.show_and_focus()

    def show_settings(self) -> None:
        """Mostrar ventana de configuración."""
        if self.settings_window is None:
            self.settings_window = SettingsWindow()

        self.settings_window.show()
        self.settings_window.activateWindow()

    def on_abbreviation_expand(
        self, snippet, content: Optional[str] = None, needs_form: bool = False, abbr_length: int = 0
    ) -> None:
        """
        Callback cuando se detecta una abreviatura.

        Args:
            snippet: Snippet a expandir
            content: Contenido expandido (si no hay variables)
            needs_form: True si necesita formulario de variables
            abbr_length: Longitud de la abreviatura a borrar
        """
        if self.is_paused:
            return

        if needs_form:
            # TODO: Mostrar formulario de variables
            print(f"⚠️ Snippet has variables (form not yet implemented): {snippet.name}")
            return

        if not content:
            return

        try:
            # Borrar abreviatura + trigger
            import time
            time.sleep(0.05)  # Pequeño delay para asegurar que el trigger se procesó

            # Borrar abreviatura (backspaces)
            delete_count = abbr_length + 1  # +1 para el trigger (Tab)
            self.text_inserter._delete_chars(delete_count)

            # Insertar contenido
            time.sleep(0.05)
            self.text_inserter.insert_text(content)

            print(f"✨ Expanded: {snippet.name}")

        except Exception as e:
            print(f"❌ Failed to expand abbreviation: {e}")

    def toggle_pause(self) -> None:
        """Pausar/reanudar la aplicación."""
        self.is_paused = not self.is_paused
        status = "paused" if self.is_paused else "active"
        print(f"ApareText {status}")

        # Actualizar tray icon
        self.tray.update_pause_state(self.is_paused)

        # Pausar/reanudar detector de abreviaturas
        if hasattr(self, 'abbreviation_detector'):
            if self.is_paused:
                self.abbreviation_detector.stop()
            else:
                self.abbreviation_detector.start()

    def quit_app(self) -> None:
        """Salir de la aplicación."""
        print("Shutting down ApareText...")

        # Cleanup
        try:
            if hasattr(self, 'abbreviation_detector'):
                self.abbreviation_detector.stop()
            if hasattr(self, 'hotkey_manager'):
                self.hotkey_manager.unregister_all()
            self.db.close()
        except Exception as e:
            print(f"⚠️ Error during cleanup: {e}")

        # Quit
        self.app.quit()

    def run(self) -> int:
        """
        Ejecutar aplicación.

        Returns:
            Código de salida
        """
        print("🚀 ApareText Desktop is running")
        print("   Press Ctrl+Space to open command palette")
        print("   Type abbreviations + Tab to expand (e.g., ;firma + Tab)")
        print("   Check system tray for options")
        print("   Services initializing in background...\n")

        return self.app.exec()
