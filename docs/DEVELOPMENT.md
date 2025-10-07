# Guía de Desarrollo - ApareText

**Última actualización:** Octubre 2025

---

## Tabla de Contenidos

1. [Configuración del Entorno](#configuración-del-entorno)
2. [Instalación](#instalación)
3. [Ejecución](#ejecución)
4. [Testing](#testing)
5. [Estilo de Código](#estilo-de-código)
6. [Estructura de Commits](#estructura-de-commits)
7. [Flujo de Trabajo](#flujo-de-trabajo)
8. [Debugging](#debugging)
9. [Build y Distribución](#build-y-distribución)

---

## Configuración del Entorno

### Requisitos

- **Python:** 3.10 o superior
- **Node.js:** 18+ (solo para extensión)
- **Git:** Última versión
- **OS:** Windows 10+, macOS 12+, o Linux (Ubuntu 22.04+)

### Herramientas Recomendadas

- **IDE:** VS Code con Python extension
- **Terminal:** PowerShell (Windows), Terminal (macOS), Bash (Linux)
- **DB Browser:** DB Browser for SQLite (opcional)

---

## Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/BorjaFdz/ApareText.git
cd ApareText
```

### 2. Crear Entorno Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

#### Opción A: Instalar todo (recomendado para desarrollo)

```bash
pip install -e ".[all]"
```

#### Opción B: Instalar módulos específicos

```bash
# Solo core
pip install -e ".[core]"

# Core + Server
pip install -e ".[core,server]"

# Core + Desktop
pip install -e ".[core,desktop]"

# Core + Server + Desktop
pip install -e ".[core,server,desktop]"

# Herramientas de desarrollo
pip install -e ".[dev]"
```

### 4. Verificar Instalación

```bash
# Verificar Python
python --version  # Debe ser 3.10+

# Verificar paquetes instalados
pip list | grep -i aparetext

# Verificar imports
python -c "from core import Database; print('✅ Core OK')"
python -c "from server import app; print('✅ Server OK')"
python -c "from desktop import DesktopApp; print('✅ Desktop OK')"
```

---

## Ejecución

### Servidor API

```bash
# Desarrollo (con hot reload)
python -m server.main

# O con uvicorn directamente
uvicorn server.main:app --reload --host 127.0.0.1 --port 46321
```

**Acceder a:**
- API: http://localhost:46321
- Docs: http://localhost:46321/docs
- WebSocket: ws://localhost:46321/ws

### Aplicación Desktop

```bash
# Ejecutar app de escritorio
python -m desktop.main
```

**Acciones disponibles:**
- `Ctrl+Space`: Abrir paleta de comandos
- System Tray: Click derecho para opciones
- Double-click tray: Abrir paleta

### Tests

```bash
# Todos los tests
pytest

# Tests de un módulo específico
pytest tests/core/
pytest tests/server/
pytest tests/desktop/

# Con cobertura
pytest --cov=core --cov=server --cov=desktop

# Con reporte HTML
pytest --cov --cov-report=html
# Abrir: htmlcov/index.html
```

---

## Testing

### Estructura de Tests

```
tests/
├── core/
│   ├── test_models.py
│   ├── test_database.py
│   ├── test_template_parser.py
│   └── test_snippet_manager.py
├── server/
│   ├── test_api.py
│   └── test_websocket.py
└── desktop/
    ├── test_hotkeys.py
    ├── test_inserter.py
    └── test_palette.py
```

### Escribir Tests

```python
# tests/core/test_template_parser.py
import pytest
from core.template_parser import TemplateParser


def test_extract_variables():
    parser = TemplateParser()
    template = "Hola {{nombre}}, tu email es {{email}}"
    
    variables = parser.extract_variables(template)
    
    assert variables == ["nombre", "email"]


def test_parse_with_variables():
    parser = TemplateParser()
    template = "Hola {{nombre}}"
    
    result = parser.parse(template, {"nombre": "Juan"})
    
    assert result == "Hola Juan"


def test_cursor_marker():
    parser = TemplateParser()
    template = "Hola {{nombre}}{{|}}"
    
    result, cursor_pos = parser.parse_with_cursor_position(
        template, {"nombre": "Juan"}
    )
    
    assert result == "Hola Juan"
    assert cursor_pos == 10
```

### Ejecutar Tests Específicos

```bash
# Un archivo
pytest tests/core/test_template_parser.py

# Una función
pytest tests/core/test_template_parser.py::test_extract_variables

# Con verbose
pytest -v

# Con print statements
pytest -s

# Parar en primer fallo
pytest -x
```

---

## Estilo de Código

### Formateo con Black

```bash
# Formatear todo el código
black core/ server/ desktop/

# Verificar sin modificar
black --check core/ server/ desktop/

# Formatear un archivo específico
black core/models.py
```

### Linting con Ruff

```bash
# Linter completo
ruff check core/ server/ desktop/

# Auto-fix problemas
ruff check --fix core/ server/ desktop/

# Ignorar un error específico
ruff check --ignore E501 core/
```

### Type Checking con mypy

```bash
# Type checking
mypy core/ server/ desktop/

# Con más strictness
mypy --strict core/

# Ignorar imports externos
mypy --ignore-missing-imports core/
```

### Configuración en pyproject.toml

```toml
[tool.black]
line-length = 100

[tool.ruff]
line-length = 100
select = ["E", "W", "F", "I", "B", "C4"]

[tool.mypy]
python_version = "3.10"
warn_return_any = true
```

---

## Estructura de Commits

### Convención de Commits

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Tipos:**
- `feat`: Nueva característica
- `fix`: Corrección de bug
- `docs`: Documentación
- `style`: Formato (no afecta código)
- `refactor`: Refactorización
- `test`: Tests
- `chore`: Tareas de mantenimiento

**Scopes:**
- `core`: Módulo core
- `server`: Módulo server
- `desktop`: Módulo desktop
- `extension`: Extensión de navegador
- `docs`: Documentación

**Ejemplos:**

```bash
# Feature
git commit -m "feat(core): add template parser with cursor support"

# Fix
git commit -m "fix(desktop): resolve hotkey conflict on macOS"

# Docs
git commit -m "docs: update installation instructions"

# Refactor
git commit -m "refactor(server): simplify WebSocket message handling"

# Breaking change
git commit -m "feat(core)!: change snippet model structure

BREAKING CHANGE: snippet.content is now snippet.content_text"
```

---

## Flujo de Trabajo

### Branching Strategy

```
main                    # Producción estable
  ├── develop          # Desarrollo activo
  │   ├── feature/xxx  # Features
  │   ├── fix/yyy      # Fixes
  │   └── refactor/zzz # Refactors
  └── release/v1.0.0   # Preparación de release
```

### Workflow

1. **Crear rama desde develop**
```bash
git checkout develop
git pull origin develop
git checkout -b feature/mi-feature
```

2. **Desarrollar y commit**
```bash
# Hacer cambios
git add .
git commit -m "feat(core): add new feature"
```

3. **Push y Pull Request**
```bash
git push origin feature/mi-feature
# Crear PR en GitHub hacia develop
```

4. **Code Review y Merge**
- Revisar código
- Pasar CI checks
- Merge a develop

5. **Release**
```bash
# Desde develop
git checkout -b release/v1.0.0
# Actualizar versión en pyproject.toml
git commit -m "chore: bump version to 1.0.0"
git checkout main
git merge release/v1.0.0
git tag v1.0.0
git push origin main --tags
```

---

## Debugging

### Debug del Servidor

```python
# server/main.py
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "server.main:app",
        host="127.0.0.1",
        port=46321,
        reload=True,
        log_level="debug"  # ← Habilitar logs debug
    )
```

### Debug de la Desktop App

```python
# desktop/main.py
import sys
import logging

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    try:
        app = DesktopApp()
        sys.exit(app.run())
    except Exception as e:
        logging.exception("Fatal error")
        sys.exit(1)
```

### VS Code Launch Configuration

`.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Server",
      "type": "python",
      "request": "launch",
      "module": "server.main",
      "console": "integratedTerminal"
    },
    {
      "name": "Desktop",
      "type": "python",
      "request": "launch",
      "module": "desktop.main",
      "console": "integratedTerminal"
    },
    {
      "name": "Tests",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["-v"],
      "console": "integratedTerminal"
    }
  ]
}
```

### Inspeccionar Base de Datos

```bash
# Abrir con sqlite3
sqlite3 ~/.aparetext/aparetext.db

# Comandos útiles
.tables
.schema snippets
SELECT * FROM snippets;
SELECT * FROM snippet_variables;
```

### Logs de la Aplicación

```bash
# Windows
%USERPROFILE%\.aparetext\logs\

# macOS/Linux
~/.aparetext/logs/
```

---

## Build y Distribución

### Build con PyInstaller

```bash
# Instalar PyInstaller
pip install pyinstaller

# Build desktop app (Windows)
pyinstaller --onefile --windowed --name ApareText desktop/main.py

# Build con icon
pyinstaller --onefile --windowed --icon=icon.ico --name ApareText desktop/main.py

# Output en: dist/ApareText.exe
```

### Build con Nuitka (más rápido)

```bash
# Instalar Nuitka
pip install nuitka

# Build
python -m nuitka --standalone --onefile --windows-disable-console desktop/main.py

# Output en: desktop.dist/main.exe
```

### Crear Instalador

#### Windows (Inno Setup)

```iss
; script.iss
[Setup]
AppName=ApareText
AppVersion=1.0.0
DefaultDirName={pf}\ApareText
DefaultGroupName=ApareText
OutputBaseFilename=ApareText_Setup

[Files]
Source: "dist\ApareText.exe"; DestDir: "{app}"

[Icons]
Name: "{group}\ApareText"; Filename: "{app}\ApareText.exe"
Name: "{userstartup}\ApareText"; Filename: "{app}\ApareText.exe"
```

```bash
# Compilar con Inno Setup
iscc script.iss
```

#### macOS (DMG)

```bash
# Crear app bundle
python setup.py py2app

# Crear DMG
hdiutil create -volname ApareText -srcfolder dist/ApareText.app -ov ApareText.dmg
```

#### Linux (DEB)

```bash
# Estructura
aparetext_1.0.0/
├── DEBIAN/
│   └── control
└── usr/
    └── local/
        └── bin/
            └── aparetext

# control file
Package: aparetext
Version: 1.0.0
Section: utils
Priority: optional
Architecture: amd64
Depends: python3
Maintainer: Your Name <email@example.com>
Description: Text expander with global palette

# Build
dpkg-deb --build aparetext_1.0.0
```

---

## Pre-commit Hooks

### Instalar

```bash
pip install pre-commit
pre-commit install
```

### Configuración (.pre-commit-config.yaml)

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.10.0
    hooks:
      - id: black
        language_version: python3.10

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
```

### Ejecutar

```bash
# Manual
pre-commit run --all-files

# Automático en cada commit
git commit  # Los hooks se ejecutan automáticamente
```

---

## Troubleshooting

### Problema: ModuleNotFoundError

```bash
# Solución: Reinstalar en modo editable
pip install -e .
```

### Problema: Hotkeys no funcionan

```bash
# Windows: Ejecutar como administrador
# macOS: Verificar permisos en System Preferences → Security → Accessibility
# Linux: Añadir usuario al grupo input
sudo usermod -a -G input $USER
```

### Problema: Base de datos bloqueada

```python
# Cerrar todas las sesiones
from core.database import close_db
close_db()
```

### Problema: Puerto 46321 ocupado

```bash
# Windows
netstat -ano | findstr :46321
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:46321 | xargs kill -9
```

---

## Recursos Adicionales

- **Documentación Python:** https://docs.python.org/3/
- **FastAPI:** https://fastapi.tiangolo.com/
- **PySide6:** https://doc.qt.io/qtforpython/
- **SQLAlchemy:** https://docs.sqlalchemy.org/
- **Pytest:** https://docs.pytest.org/

---

## Contacto y Soporte

- **Issues:** https://github.com/BorjaFdz/ApareText/issues
- **Discussions:** https://github.com/BorjaFdz/ApareText/discussions
- **Wiki:** https://github.com/BorjaFdz/ApareText/wiki
