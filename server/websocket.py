"""
WebSocket manager para comunicación en tiempo real con extensión de navegador.
"""

import asyncio
from typing import Any, Optional

from fastapi import WebSocket
from pydantic import BaseModel, ValidationError

# Import core modules at module level to avoid performance issues
from core.database import get_db
from core.snippet_manager import SnippetManager
from core.template_parser import TemplateParser


# WebSocket Message Models
class PingMessage(BaseModel):
    type: str = "ping"
    timestamp: Optional[float] = None


class SearchMessage(BaseModel):
    type: str = "search"
    query: str = ""


class ExpandMessage(BaseModel):
    type: str = "expand"
    snippet_id: str
    variables: Optional[dict[str, Any]] = None
    domain: Optional[str] = None


class GetSnippetMessage(BaseModel):
    type: str = "get_snippet"
    snippet_id: str


class WebSocketMessage(BaseModel):
    type: str

    @classmethod
    def parse_message(cls, data: dict[str, Any]) -> Optional[BaseModel]:
        """Parse and validate WebSocket message."""
        message_type = data.get("type")
        if not message_type:
            return None

        try:
            if message_type == "ping":
                return PingMessage(**data)
            elif message_type == "search":
                return SearchMessage(**data)
            elif message_type == "expand":
                return ExpandMessage(**data)
            elif message_type == "get_snippet":
                return GetSnippetMessage(**data)
            else:
                return None
        except ValidationError:
            return None


class WebSocketManager:
    """
    Gestor de conexiones WebSocket.

    Permite comunicación bidireccional entre servidor y extensiones de navegador.
    """

    def __init__(self):
        """Inicializar gestor."""
        self.active_connections: list[WebSocket] = []
        self._lock = asyncio.Lock()  # Thread-safe access to connections list

    async def connect(self, websocket: WebSocket) -> None:
        """
        Aceptar nueva conexión WebSocket.

        Args:
            websocket: Cliente WebSocket
        """
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)
        print(f"Client connected. Total connections: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket) -> None:
        """
        Desconectar cliente.

        Args:
            websocket: Cliente a desconectar
        """
        async with self._lock:
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
            await self.disconnect(websocket)

    async def broadcast(self, message: dict[str, Any]) -> None:
        """
        Enviar mensaje a todos los clientes conectados.

        Args:
            message: Mensaje a enviar
        """
        if not self.active_connections:
            return

        disconnected = []
        for connection in self.active_connections[:]:  # Create a copy to avoid modification during iteration
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)

        # Limpiar conexiones desconectadas
        for conn in disconnected:
            await self.disconnect(conn)

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
        try:
            # Validate message
            message = WebSocketMessage.parse_message(data)
            if not message:
                return {"type": "error", "error": "Invalid message format or unknown message type"}

            message_type = message.type

            if isinstance(message, PingMessage):
                return {"type": "pong", "timestamp": message.timestamp}

            elif isinstance(message, SearchMessage):
                # Búsqueda de snippets
                try:
                    manager = SnippetManager(get_db())
                    results = manager.search_snippets(message.query)

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
                except Exception as e:
                    print(f"Error in search: {e}")
                    return {"type": "error", "error": "Search failed"}

            elif isinstance(message, ExpandMessage):
                # Expandir snippet
                try:
                    manager = SnippetManager(get_db())
                    parser = TemplateParser()

                    snippet = manager.get_snippet(message.snippet_id)
                    if not snippet:
                        return {"type": "error", "error": "Snippet not found"}

                    content = snippet.content_html if snippet.is_rich else snippet.content_text
                    if not content:
                        return {"type": "error", "error": "Snippet has no content"}

                    expanded, cursor_pos = parser.parse_with_cursor_position(content, message.variables or {})

                    # Log de uso
                    manager.log_usage(
                        snippet_id=message.snippet_id,
                        source="extension",
                        target_domain=message.domain,
                    )

                    return {
                        "type": "expand_result",
                        "content": expanded,
                        "cursor_position": cursor_pos,
                        "is_rich": snippet.is_rich,
                    }
                except Exception as e:
                    print(f"Error in expand: {e}")
                    return {"type": "error", "error": "Expansion failed"}

            elif isinstance(message, GetSnippetMessage):
                # Obtener snippet completo
                try:
                    manager = SnippetManager(get_db())
                    snippet = manager.get_snippet(message.snippet_id)
                    if not snippet:
                        return {"type": "error", "error": "Snippet not found"}

                    return {
                        "type": "snippet_data",
                        "snippet": snippet.model_dump(mode="json"),
                    }
                except Exception as e:
                    print(f"Error in get_snippet: {e}")
                    return {"type": "error", "error": "Failed to get snippet"}

            else:
                return {"type": "error", "error": f"Unknown message type: {message_type}"}

        except Exception as e:
            print(f"Unexpected error in handle_message: {e}")
            return {"type": "error", "error": "Internal server error"}


# Instancia global
ws_manager = WebSocketManager()
