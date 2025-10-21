"""
Punto de entrada del servidor FastAPI.
"""

# Configure sys.path to ensure imports work regardless of execution directory
import sys
import os
from pathlib import Path

# Add the parent directory (project root) to sys.path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Add the server directory to sys.path for local imports
server_dir = Path(__file__).parent
if str(server_dir) not in sys.path:
    sys.path.insert(0, str(server_dir))

import uvicorn

from server.api import app
from server.config import HOST, PORT, API_BASE_URL, DOCS_URL

import time
import json
from pathlib import Path
import threading
import socket





def main():
    """Iniciar servidor."""
    import sys
    import os
    import time
    import json
    from pathlib import Path
    
    # Detectar si estamos en PyInstaller
    is_frozen = getattr(sys, 'frozen', False)
    
    if is_frozen:
        # En PyInstaller: Deshabilitar COMPLETAMENTE el logging de uvicorn
        import logging
        logging.disable(logging.CRITICAL)  # Deshabilitar TODOS los logs
        os.environ["UVICORN_LOG_CONFIG"] = ""  # Variable de entorno vacía
    
    if not is_frozen:
        print(f"🚀 Starting ApareText Server...")
        print(f"📡 API: {API_BASE_URL}")
        print(f" Docs: {DOCS_URL}")
        print("\nPress CTRL+C to stop\n")

    # If a pre-generated OpenAPI JSON exists, use it to avoid expensive runtime generation.
    # This helps reduce startup time (FastAPI builds the OpenAPI schema on first access).
    def _load_prebuilt_openapi():
        # When bundled by PyInstaller, data files are extracted to sys._MEIPASS
        base = getattr(sys, '_MEIPASS', None) or os.path.dirname(__file__)

        # Build a list of candidate paths where openapi.json might be placed by PyInstaller
        candidates = [
            Path(base) / 'openapi.json',
            Path(base) / 'server' / 'openapi.json',
            Path(os.path.dirname(__file__)) / 'openapi.json',
            Path(os.path.dirname(__file__)) / 'server' / 'openapi.json',
            Path(base) / '_internal' / 'server' / 'openapi.json',
            Path(os.path.dirname(__file__)) / '_internal' / 'server' / 'openapi.json',
        ]

        # Also try importlib.resources (package data) as a fallback
        tried = []
        for candidate in candidates:
            try:
                tried.append(str(candidate))
                if candidate.exists():
                    with candidate.open('r', encoding='utf-8') as f:
                        spec = json.load(f)
                    # Set both the callable and the cached schema so FastAPI will use it
                    app.openapi = lambda: spec
                    try:
                        app.openapi_schema = spec
                    except Exception:
                        # Some versions may not allow assignment; ignore if so
                        pass
                    if not is_frozen:
                        print(f"[startup] Loaded prebuilt OpenAPI from: {candidate}")
                    return True
            except Exception as e:
                if not is_frozen:
                    print(f"[startup] Error reading {candidate}: {e}")

        try:
            # Try loading from package resources (server package)
            import importlib.resources as pkg_resources
            if pkg_resources.is_resource('server', 'openapi.json'):
                with pkg_resources.open_text('server', 'openapi.json', encoding='utf-8') as f:
                    spec = json.load(f)
                app.openapi = lambda: spec
                if not is_frozen:
                    print("[startup] Loaded prebuilt OpenAPI from package resources (server.openapi.json)")
                return True
        except Exception as e:
            if not is_frozen:
                print(f"[startup] importlib.resources fallback failed: {e}")

        if not is_frozen:
            print(f"[startup] Did not find openapi.json in candidates: {tried}")
        return False

    # Emit timestamps to help debug startup time in frozen builds.
    t_start = time.time()
    print(f"[startup] main() start: {t_start}", file=sys.stderr)
    loaded = _load_prebuilt_openapi()
    t_after_openapi = time.time()
    print(f"[startup] after _load_prebuilt_openapi: {t_after_openapi} (loaded={loaded})", file=sys.stderr)

    # Register a FastAPI startup event to measure when the ASGI app runs its startup handlers
    # Now handled by lifespan in api.py
    
    # Start uvicorn. When frozen, use the Server API and explicit lifecycle steps so we
    # can print timestamps for: config creation, server creation, startup (binding sockets)
    # and when the app's startup event runs. In dev (not frozen) keep uvicorn.run for
    # convenience.
    t_before_uvicorn = time.time()
    print(f"[startup] before uvicorn: {t_before_uvicorn}", file=sys.stderr)

    if not is_frozen:
        # Developer workflow: keep the concise API
        try:
            uvicorn.run(
                "server.api:app",
                app_dir=".",
                host=HOST,
                port=PORT,
                reload=False,
                log_level="info",
                access_log=True,
                log_config=None,
            )
        except Exception as e:
            print(f"Error in uvicorn.run: {e}")
            import traceback
            traceback.print_exc()
    else:
        # Frozen (PyInstaller) — use a thread to run server.run() and poll for readiness.

        t_cfg_start = time.time()
        print(f"[uvicorn-instr] creating Config: {t_cfg_start}", file=sys.stderr)

        config = uvicorn.Config(
            app,
            host=HOST,
            port=PORT,
            reload=False,
            log_level="critical",
            access_log=False,
            log_config=None,
        )

        t_cfg_done = time.time()
        print(f"[uvicorn-instr] Config created: {t_cfg_done}", file=sys.stderr)

        server = uvicorn.Server(config)
        t_server_created = time.time()
        print(f"[uvicorn-instr] Server object created: {t_server_created}", file=sys.stderr)

        # Run server.run() in a daemon thread so main can poll for socket readiness
        def _run_server():
            try:
                server.run()
            except Exception as e:
                print(f"[uvicorn-instr] server.run exception: {e}", file=sys.stderr)

        thread = threading.Thread(target=_run_server, daemon=True)
        t_thread_start = time.time()
        thread.start()
        print(f"[uvicorn-instr] server thread started: {t_thread_start}", file=sys.stderr)

        # Poll until the socket is accepting connections (or timeout after 30s)
        t_poll_start = time.time()
        timeout = 30.0
        addr = (HOST, PORT)
        ready = False
        while time.time() - t_poll_start < timeout:
            try:
                with socket.create_connection(addr, timeout=0.5):
                    ready = True
                    break
            except Exception:
                time.sleep(0.05)

        t_poll_end = time.time()
        print(f"[uvicorn-instr] socket ready={ready} at: {t_poll_end} (poll start: {t_poll_start})", file=sys.stderr)

        # Block forever (server thread is daemon); keep main thread alive until killed.
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("[uvicorn-instr] KeyboardInterrupt received, exiting")


if __name__ == "__main__":
    main()
