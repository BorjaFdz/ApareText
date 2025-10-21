"""
Configuración centralizada para ApareText Server.
"""

# Configuración del servidor
HOST = "127.0.0.1"
PORT = 46321

# URLs
API_BASE_URL = f"http://{HOST}:{PORT}"
WEBSOCKET_URL = f"ws://{HOST}:{PORT}/ws"
DOCS_URL = f"http://{HOST}:{PORT}/docs"

# Configuración de la aplicación
APP_NAME = "ApareText"
APP_VERSION = "1.0.0"
DEBUG = True

# Configuración de base de datos
DATABASE_PATH = "~/.aparetext/aparetext.db"

# Configuración de CORS
CORS_ORIGINS = [
    "http://localhost:3000",  # Desarrollo React
    "http://localhost:5173",  # Desarrollo Vite
    f"http://{HOST}:{PORT}",  # API local
    "app://.",  # Electron app
    "file://",  # Desarrollo local con archivos
]


def validate_config():
    """Validar configuración básica."""
    assert isinstance(PORT, int) and 1000 <= PORT <= 65535, f"Puerto inválido: {PORT}"
    assert HOST in ['localhost', '127.0.0.1', '0.0.0.0'], f"Host inválido: {HOST}"
    return True