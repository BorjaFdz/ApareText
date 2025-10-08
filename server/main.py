"""
Punto de entrada del servidor FastAPI.
"""

import uvicorn
from fastapi import WebSocket, WebSocketDisconnect

from server.api import app
from server.websocket import ws_manager


# Endpoint WebSocket
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Endpoint WebSocket para comunicación con extensión.
    """
    await ws_manager.connect(websocket)

    try:
        while True:
            # Recibir mensaje
            data = await websocket.receive_json()

            # Procesar mensaje
            response = await ws_manager.handle_message(websocket, data)

            # Enviar respuesta si existe
            if response:
                await ws_manager.send_personal_message(response, websocket)

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)


def main():
    """Iniciar servidor."""
    import sys
    import os
    
    # Detectar si estamos en PyInstaller
    is_frozen = getattr(sys, 'frozen', False)
    
    if is_frozen:
        # En PyInstaller: Deshabilitar COMPLETAMENTE el logging de uvicorn
        import logging
        logging.disable(logging.CRITICAL)  # Deshabilitar TODOS los logs
        os.environ["UVICORN_LOG_CONFIG"] = ""  # Variable de entorno vacía
    
    if not is_frozen:
        print("🚀 Starting ApareText Server...")
        print("📡 API: http://localhost:46321")
        print("🔌 WebSocket: ws://localhost:46321/ws")
        print("📚 Docs: http://localhost:46321/docs")
        print("\nPress CTRL+C to stop\n")
    
    # Usar uvicorn.run() pero con logging deshabilitado
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=46321,
        reload=False,
        log_level="critical" if is_frozen else "info",
        access_log=False if is_frozen else True,
        log_config=None,  # CRÍTICO: No cargar archivo de config
    )


if __name__ == "__main__":
    main()
