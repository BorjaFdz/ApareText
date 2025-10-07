"""
Punto de entrada de la aplicación de escritorio.
"""

import sys

from desktop.app import DesktopApp


def main():
    """Iniciar aplicación de escritorio."""
    try:
        app = DesktopApp()
        sys.exit(app.run())
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
