"""
Paleta de comandos flotante (overlay).
"""

from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
)

from core.models import Snippet
from core.snippet_manager import SnippetManager
from desktop.inserter import TextInserter


class CommandPalette(QDialog):
    """
    Paleta de comandos flotante para buscar y seleccionar snippets.
    """

    snippet_selected = Signal(Snippet)

    def __init__(self, snippet_manager: SnippetManager, parent=None):
        """
        Inicializar paleta.

        Args:
            snippet_manager: Gestor de snippets
            parent: Widget padre
        """
        super().__init__(parent)
        self.snippet_manager = snippet_manager
        self.inserter = TextInserter()
        self.snippets: list[Snippet] = []

        self.setup_ui()
        self.load_snippets()

    def setup_ui(self) -> None:
        """Configurar interfaz."""
        # Ventana sin marco, siempre encima
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(600, 400)

        # Layout principal
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Campo de búsqueda
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search snippets...")
        self.search_input.textChanged.connect(self.on_search)
        self.search_input.setStyleSheet(
            """
            QLineEdit {
                background: #2d2d2d;
                color: #ffffff;
                border: none;
                border-bottom: 2px solid #4a9eff;
                padding: 12px;
                font-size: 16px;
            }
            """
        )

        # Lista de resultados
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self.on_item_selected)
        self.results_list.setStyleSheet(
            """
            QListWidget {
                background: #1e1e1e;
                color: #ffffff;
                border: none;
                outline: none;
                padding: 8px;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #2d2d2d;
            }
            QListWidget::item:hover {
                background: #2d2d2d;
            }
            QListWidget::item:selected {
                background: #4a9eff;
                color: #ffffff;
            }
            """
        )

        # Info label
        self.info_label = QLabel("Press Enter to insert, Esc to cancel")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet(
            """
            QLabel {
                background: #2d2d2d;
                color: #888888;
                padding: 8px;
                font-size: 12px;
            }
            """
        )

        # Agregar widgets
        layout.addWidget(self.search_input)
        layout.addWidget(self.results_list)
        layout.addWidget(self.info_label)

        self.setLayout(layout)

        # Estilo del contenedor
        self.setStyleSheet(
            """
            QDialog {
                background: #1e1e1e;
                border: 2px solid #4a9eff;
                border-radius: 8px;
            }
            """
        )

    def load_snippets(self) -> None:
        """Cargar todos los snippets habilitados."""
        self.snippets = self.snippet_manager.get_all_snippets(enabled_only=True)
        self.update_results(self.snippets)

    def update_results(self, snippets: list[Snippet]) -> None:
        """
        Actualizar lista de resultados.

        Args:
            snippets: Lista de snippets a mostrar
        """
        self.results_list.clear()

        for snippet in snippets[:20]:  # Limitar a 20 resultados
            item = QListWidgetItem()

            # Texto del item
            text = snippet.name
            if snippet.abbreviation:
                text += f"  ({snippet.abbreviation})"
            if snippet.tags:
                text += f"  [{', '.join(snippet.tags[:3])}]"

            item.setText(text)
            item.setData(Qt.ItemDataRole.UserRole, snippet)

            self.results_list.addItem(item)

        # Seleccionar primer item
        if self.results_list.count() > 0:
            self.results_list.setCurrentRow(0)

    def on_search(self, query: str) -> None:
        """
        Manejar cambio en búsqueda.

        Args:
            query: Texto de búsqueda
        """
        if not query:
            self.update_results(self.snippets)
            return

        # Buscar snippets
        results = self.snippet_manager.search_snippets(query)
        self.update_results(results)

    def on_item_selected(self, item: QListWidgetItem) -> None:
        """
        Manejar selección de snippet.

        Args:
            item: Item seleccionado
        """
        snippet = item.data(Qt.ItemDataRole.UserRole)
        if snippet:
            self.insert_snippet(snippet)

    def insert_snippet(self, snippet: Snippet) -> None:
        """
        Insertar snippet seleccionado.

        Args:
            snippet: Snippet a insertar
        """
        # TODO: Si el snippet tiene variables, mostrar formulario
        if snippet.variables:
            print(f"⚠️ Snippet has variables (not yet implemented): {snippet.name}")
            # TODO: Mostrar VariableDialog
            return

        # Ocultar paleta
        self.hide()

        # Obtener contenido
        content = snippet.content_text
        if snippet.is_rich and snippet.content_html:
            # TODO: Convertir HTML a texto si es necesario
            content = snippet.content_html

        if not content:
            print(f"⚠️ Snippet has no content: {snippet.name}")
            return

        # Insertar texto
        success = self.inserter.insert_text(content)

        if success:
            # Log de uso
            self.snippet_manager.log_usage(
                snippet_id=snippet.id,
                source="desktop",
            )
            print(f"✅ Inserted snippet: {snippet.name}")
        else:
            print(f"❌ Failed to insert snippet: {snippet.name}")

    def show_and_focus(self) -> None:
        """Mostrar paleta y dar foco al campo de búsqueda."""
        # Centrar en pantalla
        from PySide6.QtWidgets import QApplication

        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 3,
        )

        # Limpiar búsqueda
        self.search_input.clear()

        # Recargar snippets
        self.load_snippets()

        # Mostrar y dar foco
        self.show()
        self.activateWindow()
        self.search_input.setFocus()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
        Manejar eventos de teclado.

        Args:
            event: Evento de teclado
        """
        if event.key() == Qt.Key.Key_Escape:
            self.hide()

        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            current_item = self.results_list.currentItem()
            if current_item:
                self.on_item_selected(current_item)

        elif event.key() == Qt.Key.Key_Down:
            # Mover selección hacia abajo
            current_row = self.results_list.currentRow()
            if current_row < self.results_list.count() - 1:
                self.results_list.setCurrentRow(current_row + 1)

        elif event.key() == Qt.Key.Key_Up:
            # Mover selección hacia arriba
            current_row = self.results_list.currentRow()
            if current_row > 0:
                self.results_list.setCurrentRow(current_row - 1)

        else:
            super().keyPressEvent(event)
