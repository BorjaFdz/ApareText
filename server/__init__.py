"""
ApareText Server Module

API REST + WebSocket para comunicación con extensión y dashboard web.
"""

__version__ = "0.1.0"

from api import app
from websocket import WebSocketManager

__all__ = ["app", "WebSocketManager"]
