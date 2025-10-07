"""
Ventana de configuración.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from core.database import get_db


class SettingsWindow(QDialog):
    """Ventana de configuración de ApareText."""

    def __init__(self, parent=None):
        """
        Inicializar ventana de configuración.

        Args:
            parent: Widget padre
        """
        super().__init__(parent)
        self.db = get_db()

        self.setup_ui()
        self.load_settings()

    def setup_ui(self) -> None:
        """Configurar interfaz."""
        self.setWindowTitle("ApareText Settings")
        self.setMinimumWidth(600)

        layout = QVBoxLayout()

        # Hotkeys
        group_hotkeys = QGroupBox("Hotkeys")
        form_hotkeys = QFormLayout()

        self.input_global_hotkey = QLineEdit()
        self.input_global_hotkey.setPlaceholderText("ctrl+space")
        form_hotkeys.addRow("Global Palette:", self.input_global_hotkey)

        self.combo_trigger = QComboBox()
        self.combo_trigger.addItems(["tab", "space", "enter"])
        form_hotkeys.addRow("Abbreviation Trigger:", self.combo_trigger)

        group_hotkeys.setLayout(form_hotkeys)
        layout.addWidget(group_hotkeys)

        # Insertion
        group_insertion = QGroupBox("Text Insertion")
        form_insertion = QFormLayout()

        self.combo_method = QComboBox()
        self.combo_method.addItems(["auto", "type", "clipboard"])
        form_insertion.addRow("Method:", self.combo_method)

        self.check_restore_clipboard = QCheckBox("Restore clipboard after paste")
        form_insertion.addRow("", self.check_restore_clipboard)

        self.spin_typing_speed = QSpinBox()
        self.spin_typing_speed.setRange(10, 200)
        self.spin_typing_speed.setSuffix(" ms")
        form_insertion.addRow("Typing Speed:", self.spin_typing_speed)

        group_insertion.setLayout(form_insertion)
        layout.addWidget(group_insertion)

        # UI
        group_ui = QGroupBox("User Interface")
        form_ui = QFormLayout()

        self.combo_theme = QComboBox()
        self.combo_theme.addItems(["dark", "light"])
        form_ui.addRow("Theme:", self.combo_theme)

        self.combo_language = QComboBox()
        self.combo_language.addItems(["es", "en"])
        form_ui.addRow("Language:", self.combo_language)

        self.check_fuzzy_search = QCheckBox("Enable fuzzy search")
        form_ui.addRow("", self.check_fuzzy_search)

        group_ui.setLayout(form_ui)
        layout.addWidget(group_ui)

        # Behavior
        group_behavior = QGroupBox("Behavior")
        form_behavior = QFormLayout()

        self.check_auto_start = QCheckBox("Start with system")
        form_behavior.addRow("", self.check_auto_start)

        self.check_notifications = QCheckBox("Show notifications")
        form_behavior.addRow("", self.check_notifications)

        self.check_log_usage = QCheckBox("Log snippet usage")
        form_behavior.addRow("", self.check_log_usage)

        group_behavior.setLayout(form_behavior)
        layout.addWidget(group_behavior)

        # Buttons
        buttons_layout = QHBoxLayout()

        btn_save = QPushButton("Save")
        btn_save.clicked.connect(self.save_settings)

        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)

        buttons_layout.addStretch()
        buttons_layout.addWidget(btn_save)
        buttons_layout.addWidget(btn_cancel)

        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def load_settings(self) -> None:
        """Cargar configuración desde la base de datos."""
        with self.db.get_session() as session:
            from core.models import SettingsDB

            settings = session.query(SettingsDB).all()
            settings_dict = {s.key: s.value for s in settings}

            # Cargar valores
            self.input_global_hotkey.setText(settings_dict.get("global_hotkey", "ctrl+space"))
            self.combo_trigger.setCurrentText(settings_dict.get("abbreviation_trigger", "tab"))
            self.combo_method.setCurrentText(settings_dict.get("insertion_method", "auto"))
            self.check_restore_clipboard.setChecked(
                settings_dict.get("restore_clipboard", "true") == "true"
            )
            self.spin_typing_speed.setValue(int(settings_dict.get("typing_speed", "50")))
            self.combo_theme.setCurrentText(settings_dict.get("theme", "dark"))
            self.combo_language.setCurrentText(settings_dict.get("language", "es"))
            self.check_fuzzy_search.setChecked(
                settings_dict.get("fuzzy_search", "true") == "true"
            )
            self.check_auto_start.setChecked(settings_dict.get("auto_start", "false") == "true")
            self.check_notifications.setChecked(
                settings_dict.get("show_notifications", "true") == "true"
            )
            self.check_log_usage.setChecked(settings_dict.get("log_usage", "false") == "true")

    def save_settings(self) -> None:
        """Guardar configuración en la base de datos."""
        with self.db.get_session() as session:
            from core.models import SettingsDB

            settings = {
                "global_hotkey": self.input_global_hotkey.text(),
                "abbreviation_trigger": self.combo_trigger.currentText(),
                "insertion_method": self.combo_method.currentText(),
                "restore_clipboard": str(self.check_restore_clipboard.isChecked()).lower(),
                "typing_speed": str(self.spin_typing_speed.value()),
                "theme": self.combo_theme.currentText(),
                "language": self.combo_language.currentText(),
                "fuzzy_search": str(self.check_fuzzy_search.isChecked()).lower(),
                "auto_start": str(self.check_auto_start.isChecked()).lower(),
                "show_notifications": str(self.check_notifications.isChecked()).lower(),
                "log_usage": str(self.check_log_usage.isChecked()).lower(),
            }

            # Actualizar cada setting
            for key, value in settings.items():
                setting = session.query(SettingsDB).filter_by(key=key).first()
                if setting:
                    setting.value = value
                else:
                    setting = SettingsDB(key=key, value=value)
                    session.add(setting)

            session.commit()

        print("✅ Settings saved")
        self.accept()
