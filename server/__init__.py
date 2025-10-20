"""
ApareText Server Module

API REST + WebSocket para comunicación con extensión y dashboard web.
"""

__version__ = "0.1.0"

from server.api import app
from server.websocket import WebSocketManager

__all__ = ["app", "WebSocketManager"]
