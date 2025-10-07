"""
WebSocket manager para comunicación en tiempo real con extensión de navegador.
"""

import asyncio
import json
from typing import Any, Optional

from fastapi import WebSocket, WebSocketDisconnect


class WebSocketManager:
    """
    Gestor de conexiones WebSocket.

    Permite comunicación bidireccional entre servidor y extensiones de navegador.
    """

    def __init__(self):
        """Inicializar gestor."""
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """
        Aceptar nueva conexión WebSocket.

        Args:
            websocket: Cliente WebSocket
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket) -> None:
        """
        Desconectar cliente.

        Args:
            websocket: Cliente a desconectar
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: dict[str, Any], websocket: WebSocket) -> None:
        """
        Enviar mensaje a cliente específico.

        Args:
            message: Mensaje a enviar
            websocket: Cliente destinatario
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Error sending message: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: dict[str, Any]) -> None:
        """
        Enviar mensaje a todos los clientes conectados.

        Args:
            message: Mensaje a enviar
        """
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)

        # Limpiar conexiones desconectadas
        for conn in disconnected:
            self.disconnect(conn)

    async def handle_message(
        self, websocket: WebSocket, data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        """
        Procesar mensaje recibido del cliente.

        Args:
            websocket: Cliente que envió el mensaje
            data: Datos del mensaje

        Returns:
            Respuesta al cliente o None
        """
        message_type = data.get("type")

        if message_type == "ping":
            return {"type": "pong", "timestamp": data.get("timestamp")}

        elif message_type == "search":
            # Búsqueda de snippets
            from core.database import get_db
            from core.snippet_manager import SnippetManager

            manager = SnippetManager(get_db())
            query = data.get("query", "")
            results = manager.search_snippets(query)

            return {
                "type": "search_results",
                "results": [
                    {
                        "id": s.id,
                        "name": s.name,
                        "abbreviation": s.abbreviation,
                        "tags": s.tags,
                        "is_rich": s.is_rich,
                    }
                    for s in results
                ],
            }

        elif message_type == "expand":
            # Expandir snippet
            from core.database import get_db
            from core.snippet_manager import SnippetManager
            from core.template_parser import TemplateParser

            manager = SnippetManager(get_db())
            parser = TemplateParser()

            snippet_id = data.get("snippet_id")
            variables = data.get("variables", {})

            snippet = manager.get_snippet(snippet_id)
            if not snippet:
                return {"type": "error", "error": "Snippet not found"}

            content = snippet.content_html if snippet.is_rich else snippet.content_text
            if not content:
                return {"type": "error", "error": "Snippet has no content"}

            expanded, cursor_pos = parser.parse_with_cursor_position(content, variables)

            # Log de uso
            manager.log_usage(
                snippet_id=snippet_id,
                source="extension",
                target_domain=data.get("domain"),
            )

            return {
                "type": "expand_result",
                "content": expanded,
                "cursor_position": cursor_pos,
                "is_rich": snippet.is_rich,
            }

        elif message_type == "get_snippet":
            # Obtener snippet completo
            from core.database import get_db
            from core.snippet_manager import SnippetManager

            manager = SnippetManager(get_db())
            snippet_id = data.get("snippet_id")

            snippet = manager.get_snippet(snippet_id)
            if not snippet:
                return {"type": "error", "error": "Snippet not found"}

            return {
                "type": "snippet_data",
                "snippet": snippet.model_dump(mode="json"),
            }

        else:
            return {"type": "error", "error": f"Unknown message type: {message_type}"}


# Instancia global
ws_manager = WebSocketManager()
