"""
ApareText Server Module

API REST + WebSocket para comunicación con extensión y dashboard web.
"""

import sys
import os
from pathlib import Path

# Add the parent directory (project root) to sys.path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

__version__ = "0.1.0"

from .api import app
# from .websocket import WebSocketManager

__all__ = ["app"]
