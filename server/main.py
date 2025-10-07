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
    print("🚀 Starting ApareText Server...")
    print("📡 API: http://localhost:46321")
    print("🔌 WebSocket: ws://localhost:46321/ws")
    print("📚 Docs: http://localhost:46321/docs")
    print("\nPress CTRL+C to stop\n")

    uvicorn.run(
        "server.main:app",
        host="127.0.0.1",
        port=46321,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    main()
