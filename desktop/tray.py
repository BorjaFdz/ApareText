"""
System tray icon con menú.
"""

from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QMenu, QSystemTrayIcon


class TrayIcon(QSystemTrayIcon):
    """Icon del sistema tray con menú contextual."""

    def __init__(self, app):
        """
        Inicializar tray icon.

        Args:
            app: Instancia de DesktopApp
        """
        super().__init__()
        self.app = app

        # TODO: Cargar icon real
        # self.setIcon(QIcon(":/icons/aparetext.png"))
        self.setToolTip("ApareText")

        # Crear menú
        self.menu = QMenu()
        self.create_menu()
        self.setContextMenu(self.menu)

        # Conectar señales
        self.activated.connect(self.on_tray_activated)

    def create_menu(self) -> None:
        """Crear menú contextual."""
        # Open Palette
        self.action_palette = QAction("Open Palette (Ctrl+Space)", self.menu)
        self.action_palette.triggered.connect(self.app.show_palette)
        self.menu.addAction(self.action_palette)

        self.menu.addSeparator()

        # Pause/Resume
        self.action_pause = QAction("Pause", self.menu)
        self.action_pause.setCheckable(True)
        self.action_pause.triggered.connect(self.app.toggle_pause)
        self.menu.addAction(self.action_pause)

        self.menu.addSeparator()

        # Settings
        action_settings = QAction("Settings", self.menu)
        action_settings.triggered.connect(self.app.show_settings)
        self.menu.addAction(action_settings)

        self.menu.addSeparator()

        # Quit
        action_quit = QAction("Quit", self.menu)
        action_quit.triggered.connect(self.app.quit_app)
        self.menu.addAction(action_quit)

    def on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """
        Manejar click en tray icon.

        Args:
            reason: Razón de activación
        """
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            # Doble click abre la paleta
            self.app.show_palette()

    def update_pause_state(self, is_paused: bool) -> None:
        """
        Actualizar estado de pausa en el menú.

        Args:
            is_paused: Si está pausado
        """
        self.action_pause.setChecked(is_paused)
        self.action_pause.setText("Resume" if is_paused else "Pause")

        # Cambiar tooltip
        status = "Paused" if is_paused else "Active"
        self.setToolTip(f"ApareText - {status}")
