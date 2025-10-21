# Arquitectura Técnica - ApareText

**Versión:** 1.0.0  
**Última actualización:** Octubre 21, 2025

---

## Tabla de Contenidos


1. [Visión General](#visión-general)
2. [Estructura del Proyecto](#estructura-del-proyecto)

3. [Módulos Principales](#módulos-principales)
4. [Flujos de Datos](#flujos-de-datos)

5. [Base de Datos](#base-de-datos)
6. [APIs y Comunicación](#apis-y-comunicación)

7. [Consideraciones Multiplataforma](#consideraciones-multiplataforma)
8. [Decisiones de Diseño](#decisiones-de-diseño)

---

## Visión General

ApareText es una aplicación multiplataforma dividida en 3 módulos principales:


- **Core:** Motor de snippets, persistencia y lógica de negocio
- **Server:** API REST + WebSocket para comunicación con extensión

- **Desktop:** Aplicación de escritorio con paleta global e inserción

### Stack Tecnológico

```	ext
Backend:
  - Python 3.10+
  - SQLAlchemy (ORM)
  - Pydantic (Validación)
  - FastAPI (API REST)
  - Uvicorn (ASGI Server)
  - PySide6 / Qt (UI Desktop)

OS Integration:
  - keyboard (Windows/Linux hotkeys)
  - pynput (macOS hotkeys)
  - pywin32 (Windows APIs)
  - pyobjc (macOS APIs)
  - python-xlib (Linux X11)

Frontend (Extensión):
  - TypeScript
  - Manifest V3
  - WebSocket API
```	ext

---

## Estructura del Proyecto

```	ext
ApareText/
├── core/                    # Motor de snippets (biblioteca compartida)

│   ├── __init__.py
│   ├── models.py           # Modelos Pydantic + SQLAlchemy

│   ├── database.py         # Gestión de SQLite

│   ├── template_parser.py  # Parser de plantillas

│   └── snippet_manager.py  # CRUD de snippets

│
├── server/                  # API REST + WebSocket

│   ├── __init__.py
│   ├── api.py              # Endpoints FastAPI

│   ├── websocket.py        # Manager de WebSocket

│   └── main.py             # Punto de entrada

│
├── desktop/                 # Aplicación de escritorio

│   ├── __init__.py
│   ├── app.py              # Aplicación principal Qt

│   ├── hotkeys.py          # Gestor de hotkeys globales

│   ├── palette.py          # Command palette flotante

│   ├── inserter.py         # Inserción de texto

│   ├── tray.py             # System tray icon

│   ├── settings_window.py  # Ventana de configuración

│   └── main.py             # Punto de entrada

│
├── extension/               # Extensión de navegador

│   ├── manifest.json
│   ├── background/         # Service worker

│   ├── content/            # Content scripts

│   └── popup/              # Popup UI

│
├── tests/                   # Tests unitarios e integración

│   ├── core/
│   ├── server/
│   └── desktop/
│
├── docs/                    # Documentación

│   ├── SPEC.md
│   ├── ARCHITECTURE.md
│   ├── API.md
│   └── DEVELOPMENT.md
│
├── pyproject.toml          # Configuración del proyecto

├── README.md
└── .gitignore
```	ext

---

## Módulos Principales

### 1. Core Module

## Responsabilidades:

- Modelado de datos (Snippets, Variables, Settings)
- Persistencia en SQLite

- Parsing de plantillas con variables y funciones
- CRUD de snippets

- Export/Import JSON
- Logs de uso

## Componentes Clave:

#### `models.py`	ext

```python

# Modelos principales

- Snippet (Pydantic)
- SnippetVariable (Pydantic)

- Settings (Pydantic)

# Modelos de base de datos

- SnippetDB (SQLAlchemy)
- SnippetVariableDB (SQLAlchemy)

- SettingsDB (SQLAlchemy)
- UsageLogDB (SQLAlchemy)
```	ext

#### `database.py`	ext

```python
class Database:
    - __init__(db_path)
    - get_session() -> Session
    - backup(backup_path)
    - restore(backup_path)
    - export_to_json(output_path)
    - import_from_json(input_path, replace=False)
```	ext

#### `template_parser.py`	ext

```python
class TemplateParser:
    - extract_variables(template) -> list[str]
    - parse(template, variables) -> str
    - parse_with_cursor_position() -> (str, int)
    - validate_template() -> (bool, error?)
    

# Soporta:

# - Variables: {{nombre}}, {{email}}

# - Cursor: {{|}}

# - Funciones: {{date:%Y-%m-%d}}, {{clipboard}}

# - Escapes: \{{

```	ext

#### `snippet_manager.py`	ext

```python
class SnippetManager:
    - create_snippet(snippet) -> Snippet
    - get_snippet(id) -> Snippet?
    - get_all_snippets(enabled_only=False) -> list[Snippet]
    - update_snippet(id, snippet) -> Snippet?
    - delete_snippet(id) -> bool
    - search_snippets(query, tags?, scope_type?) -> list[Snippet]
    - get_snippet_by_abbreviation(abbr) -> Snippet?
    - log_usage(snippet_id, source?, target_app?, target_domain?)
    - get_usage_stats(snippet_id?) -> dict
```	ext

---

### 2. Server Module

## Responsabilidades:

- API REST para CRUD de snippets
- WebSocket para comunicación en tiempo real con extensión

- Dashboard web (futuro)
- Servir en `http://localhost:46321`	ext

## Componentes Clave:

#### `api.py` - REST API

```python

# Endpoints principales

GET    /                          # Health check

GET    /health                    # Health detallado

GET    /api/snippets              # Listar snippets

GET    /api/snippets/{id}         # Obtener snippet

POST   /api/snippets              # Crear snippet

PUT    /api/snippets/{id}         # Actualizar snippet

DELETE /api/snippets/{id}         # Eliminar snippet

GET    /api/snippets/search/{q}   # Buscar snippets

GET    /api/abbreviations/{abbr}  # Buscar por abreviatura

POST   /api/snippets/expand       # Expandir con variables

GET    /api/stats                 # Estadísticas de uso

GET    /api/export                # Exportar JSON

POST   /api/import                # Importar JSON

POST   /api/validate-template     # Validar sintaxis

```	ext

#### `websocket.py` - WebSocket Manager

```python
class WebSocketManager:
    - connect(websocket)
    - disconnect(websocket)
    - send_personal_message(message, websocket)
    - broadcast(message)
    - handle_message(websocket, data) -> response?

# Tipos de mensajes

- ping/pong
- search -> search_results

- expand -> expand_result
- get_snippet -> snippet_data

- error
```	ext

#### `main.py` - Servidor

```python

# Endpoint WebSocket

@app.websocket("/ws")
async def websocket_endpoint(websocket)

def main():
    # Uvicorn en localhost:46321

    uvicorn.run("server.main:app", host="127.0.0.1", port=46321)
```	ext

---

### 3. Desktop Module

## Responsabilidades:

- Paleta global con hotkey
- Inserción de texto en apps activas

- Detector de abreviaturas (futuro)
- System tray icon

- Ventana de configuración

## Componentes Clave:

#### `app.py` - Aplicación Principal

```python
class DesktopApp:
    - __init__()
    - setup_hotkeys()
    - show_palette()
    - show_settings()
    - toggle_pause()
    - quit_app()
    - run() -> exit_code
```	ext

#### `hotkeys.py` - Hotkeys Globales

```python
class HotkeyManager:
    - __init__()                      # Detecta plataforma

    - register(hotkey, callback)      # Registrar hotkey

    - unregister(hotkey)              # Desregistrar

    - unregister_all()
    - is_supported() -> bool

# Backends por plataforma:

# - Windows/Linux: keyboard library

# - macOS: pynput

```	ext

#### `palette.py` - Command Palette

```python
class CommandPalette(QDialog):
    - __init__(snippet_manager)
    - setup_ui()                      # Ventana frameless

    - load_snippets()
    - update_results(snippets)
    - on_search(query)                # Búsqueda incremental

    - on_item_selected(item)
    - insert_snippet(snippet)
    - show_and_focus()
    

# Features:

# - Búsqueda difusa

# - Navegación con teclado

# - Preview

# - Styled con Qt CSS

```	ext

#### `inserter.py` - Inserción de Texto

```python
class TextInserter:
    - __init__(method='auto', typing_speed=50)
    - insert_text(text) -> bool
    - _insert_by_typing(text) -> bool
    - _insert_by_clipboard(text) -> bool
    - get_available_methods() -> list[str]

# Métodos:

# - 'type': Simular tecleo (keyboard/pynput)

# - 'clipboard': Copiar + Ctrl/Cmd+V + restaurar

# - 'auto': Intentar type, fallback clipboard

```	ext

#### `tray.py` - System Tray

```python
class TrayIcon(QSystemTrayIcon):
    - __init__(app)
    - create_menu()                   # Menú contextual

    - on_tray_activated(reason)
    - update_pause_state(is_paused)

# Opciones del menú:

# - Open Palette

# - Pause/Resume

# - Settings

# - Quit

```	ext

#### `settings_window.py` - Configuración

```python
class SettingsWindow(QDialog):
    - __init__()
    - setup_ui()                      # Form con tabs

    - load_settings()                 # Desde DB

    - save_settings()                 # A DB

# Categorías:

# - Hotkeys

# - Insertion

# - UI (theme, language)

# - Behavior (auto-start, notifications)

```	ext

---

## Flujos de Datos

### Flujo 1: Insertar desde Paleta Global

```	ext
┌──────┐
│ User │ Presiona Ctrl+Space
└──┬───┘
   │
   ▼
┌────────────────┐
│ HotkeyManager  │ Detecta hotkey
└───────┬────────┘
        │ callback
        ▼
┌────────────────┐
│ DesktopApp     │ show_palette()
└───────┬────────┘
        │
        ▼
┌─────────────────┐
│ CommandPalette  │ Muestra ventana flotante
└───────┬─────────┘
        │ Usuario escribe "firma"
        │
        ▼
┌──────────────────┐
│ SnippetManager   │ search_snippets("firma")
└───────┬──────────┘
        │ [Snippet]
        ▼
┌─────────────────┐
│ CommandPalette  │ Muestra resultados
└───────┬─────────┘
        │ Usuario selecciona con Enter
        │
        ▼
┌─────────────────┐
│ TextInserter    │ insert_text(content)
└───────┬─────────┘
        │
        ├─ Método 'type' ──► keyboard.write()
        │
        └─ Método 'clipboard' ──► clipboard + Ctrl+V
```	ext

### Flujo 2: Expansión desde Extensión

```	ext
┌───────────────┐
│ Content Script│ Usuario escribe en textarea
└───────┬───────┘
        │ Usuario escribe "mor..."
        │
        ▼
┌───────────────┐
│ Extension     │ Muestra overlay flotante
└───────┬───────┘
        │ WS: {"type": "search", "query": "mor"}
        ▼
┌───────────────┐
│ WebSocket     │ ws://localhost:46321/ws
└───────┬───────┘
        │
        ▼
┌──────────────────┐
│ WebSocketManager │ handle_message()
└───────┬──────────┘
        │
        ▼
┌──────────────────┐
│ SnippetManager   │ search_snippets("mor")
└───────┬──────────┘
        │ [Snippet]
        ▼
┌──────────────────┐
│ WebSocketManager │ {"type": "search_results", "results": [...]}
└───────┬──────────┘
        │ WS response
        ▼
┌───────────────┐
│ Extension     │ Muestra snippets en overlay
└───────┬───────┘
        │ Usuario selecciona snippet
        │ WS: {"type": "expand", "snippet_id": "..."}
        ▼
┌──────────────────┐
│ TemplateParser   │ parse(template, variables)
└───────┬──────────┘
        │ content expandido
        ▼
┌───────────────┐
│ Content Script│ insertHTML() en textarea
└───────────────┘
```	ext

---

## Base de Datos

### Esquema SQLite

**Ubicación:** `~/.aparetext/aparetext.db`	ext

```sql
-- Tabla principal de snippets
CREATE TABLE snippets (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  abbreviation TEXT,
  tags TEXT,                    -- CSV: "work,email,support"
  content_text TEXT,
  content_html TEXT,
  is_rich INTEGER DEFAULT 0,
  scope_type TEXT DEFAULT 'global',
  scope_values TEXT,            -- JSON: ["slack.exe", "twitter.com"]
  caret_marker TEXT DEFAULT '{{|}}',
  usage_count INTEGER DEFAULT 0,
  enabled INTEGER DEFAULT 1,
  created_at TEXT,
  updated_at TEXT
);

CREATE INDEX idx_snippets_abbreviation ON snippets(abbreviation);
CREATE INDEX idx_snippets_enabled ON snippets(enabled);

-- Variables de snippets
CREATE TABLE snippet_variables (
  id TEXT PRIMARY KEY,
  snippet_id TEXT NOT NULL,
  key TEXT NOT NULL,
  label TEXT,
  type TEXT NOT NULL,           -- text, email, number, select, date, checkbox
  placeholder TEXT,
  default_value TEXT,
  required INTEGER DEFAULT 0,
  regex TEXT,
  options TEXT,                 -- JSON: ["10", "15", "20"]
  FOREIGN KEY (snippet_id) REFERENCES snippets(id) ON DELETE CASCADE
);

-- Configuración
CREATE TABLE settings (
  key TEXT PRIMARY KEY,
  value TEXT
);

-- Log de uso (opcional)
CREATE TABLE usage_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  snippet_id TEXT,
  timestamp TEXT,
  source TEXT,                  -- desktop, extension, web
  target_app TEXT,
  target_domain TEXT
);

CREATE INDEX idx_usage_log_snippet ON usage_log(snippet_id);
CREATE INDEX idx_usage_log_timestamp ON usage_log(timestamp);
```	ext

### Migraciones

**Sistema:** Alembic (futuro)

**Versión inicial:** 1.0.0

- Tablas base
- Índices

- Settings por defecto

---

## APIs y Comunicación

### REST API

**Base URL:** `http://localhost:46321`	ext

**Autenticación:** Ninguna (localhost only)

**CORS:** Permitido solo desde localhost y extensiones

**Formato:** JSON

## Ejemplo de Request/Response:

```bash

# Crear snippet

POST /api/snippets
Content-Type: application/json

{
  "name": "Firma Email",
  "abbreviation": ";firma",
  "tags": ["work", "email"],
  "content_text": "Saludos,\nJuan Pérez",
  "is_rich": false,
  "scope_type": "global"
}

# Response 201 Created

{
  "id": "abc123...",
  "name": "Firma Email",
  "abbreviation": ";firma",
  "tags": ["work", "email"],
  "content_text": "Saludos,\nJuan Pérez",
  "is_rich": false,
  "scope_type": "global",
  "scope_values": [],
  "variables": [],
  "usage_count": 0,
  "enabled": true,
  "created_at": "2025-10-07T10:30:00",
  "updated_at": "2025-10-07T10:30:00"
}
```	ext

### WebSocket Protocol

**URL:** `ws://localhost:46321/ws`	ext

**Formato:** JSON messages

## Mensajes soportados:

```javascript
// Ping
→ { "type": "ping", "timestamp": 1633600000 }
← { "type": "pong", "timestamp": 1633600000 }

// Búsqueda
→ { "type": "search", "query": "firma" }
← { 
    "type": "search_results", 
    "results": [
      { "id": "...", "name": "...", "abbreviation": "...", "tags": [...] }
    ]
  }

// Expandir snippet
→ { 
    "type": "expand", 
    "snippet_id": "abc123",
    "variables": { "nombre": "Juan" },
    "domain": "twitter.com"
  }
← { 
    "type": "expand_result",
    "content": "Buenos días Juan...",
    "cursor_position": 42,
    "is_rich": false
  }

// Error
← { "type": "error", "error": "Snippet not found" }
```	ext

---

## Consideraciones Multiplataforma

### Windows

## Ventajas:

- Excelente soporte para hotkeys globales
- Inserción por `SendInput` muy confiable

- Sin necesidad de permisos especiales

## Desafíos:

- SmartScreen puede bloquear ejecutable sin firma
- Antivirus pueden detectar listeners de teclado

## Soluciones:

- Firmar ejecutable con certificado de código
- Añadir información de versión y manifiesto

- Documentar claramente el propósito

### macOS

## Ventajas:

- API Quartz robusta para eventos
- Integración nativa con Accessibility

## Desafíos:

- Requiere permisos explícitos del usuario
- App Store tiene restricciones adicionales

- Notarización obligatoria para evitar warnings

## Soluciones:

- UI de onboarding clara para solicitar permisos
- Notarizar app con certificado de desarrollador

- Proveer instrucciones en System Preferences

### Linux

## Ventajas:

- Código abierto, sin restricciones
- Usuarios técnicos, familiarizados con permisos

## Desafíos:

- Wayland no soporta injection de eventos
- Distribuciones muy variadas

- Puede requerir permisos root

## Soluciones:

- Detectar X11 vs Wayland
- Fallback a clipboard en Wayland

- Documentar permisos necesarios
- Proveer script de instalación

---

## Decisiones de Diseño

### ¿Por qué Python?

✅ **Pros:**

- Cross-platform
- Excelentes bibliotecas (Qt, SQLAlchemy)

- Rápido desarrollo
- Fácil distribución con PyInstaller

❌ **Contras:**

- Ejecutable grande (~50-100MB)
- Arranque más lento que nativo

**Decisión:** Python es óptimo para MVP, consideraremos Rust/Go para v2.0

### ¿Por qué SQLite?

✅ **Pros:**

- Sin servidor, sin configuración
- Archivo único portable

- Rápido para < 10k snippets
- Transacciones ACID

❌ **Contras:**

- No adecuado para multi-usuario
- Sin sincronización built-in

**Decisión:** SQLite perfecto para app local, sincronización opcional en v1.0

### ¿Por qué FastAPI?

✅ **Pros:**

- Moderno, rápido, async
- Validación automática con Pydantic

- OpenAPI docs auto-generados
- WebSocket support

❌ **Contras:**

- Requiere servidor corriendo

**Decisión:** FastAPI ideal para API + WebSocket, mínimo overhead

### ¿Por qué PySide6 (Qt)?

✅ **Pros:**

- Maduro, estable, cross-platform
- Widgets nativos

- Excelente para ventanas personalizadas
- Licencia LGPL

❌ **Contras:**

- Curva de aprendizaje
- Tamaño del ejecutable

## Alternativas consideradas:

- Electron: Demasiado pesado (200+ MB)
- Tkinter: Aspecto anticuado

- wxPython: Menos documentación

**Decisión:** Qt es el estándar de facto para apps Python desktop

### Arquitectura Cliente-Servidor

**Pregunta:** ¿Por qué separar server y desktop?

## Respuesta:

1. **Modularidad:** Extensión puede conectarse a API
2. **Testing:** Testear API independientemente

3. **Futuro:** Dashboard web sin cambios
4. **IPC:** Canal limpio entre procesos

---

## Performance

### Targets


- **Arranque app:** < 400ms
- **Apertura paleta:** < 80ms

- **Búsqueda incremental:** < 50ms por keystroke
- **Inserción texto:** < 100ms

- **Memoria idle:** < 60 MB
- **CPU idle:** < 2%

### Optimizaciones


1. **Lazy loading:** Cargar snippets solo cuando se necesitan
2. **Índices DB:** En abbreviation, enabled, tags

3. **Cache:** Snippets frecuentes en memoria
4. **Throttling:** Búsqueda con debounce 100ms

5. **Connection pooling:** Reusar sesiones de DB

---

## Seguridad

### Amenazas y Mitigaciones

| Amenaza | Mitigación |
|---------|-----------|
| Injection en campos password | Lista negra de campos por atributo |
| Exposición de API | CORS estricto, solo localhost |
| Man-in-the-middle | WebSocket solo en localhost |
| Pérdida de datos | Backups automáticos configurables |
| Snippets sensibles | Cifrado opcional (v1.0) |

### Principios


1. **Local-first:** Sin cloud por defecto
2. **Opt-in:** Telemetría y sincronización opcionales

3. **Transparencia:** Código abierto
4. **Minimización:** Permisos mínimos necesarios

---

## Conclusión

Esta arquitectura proporciona:

✅ Modularidad y separación de responsabilidades  
✅ Escalabilidad para futuras features  
✅ Testabilidad con componentes desacoplados  
✅ Mantenibilidad con estructura clara  
✅ Cross-platform con abstracciones apropiadas

## Próximos pasos:

- Implementar detector de abreviaturas
- Crear extensión de navegador

- Añadir scopes por app/dominio
- Implementar variables en formulario

- Tests E2E en apps reales

---

## Build y Deployment

### Estrategia de Build

**Reglas críticas implementadas (Octubre 2025):**

1. **Build Location:** Siempre en `~/Desktop/ApareText-Build`
   - Evita acumulación de artifacts en repositorio
   - Mantiene repo limpio para desarrollo

2. **Database Preservation:**
   - `aparetext.db` se preserva entre builds
   - Asegura continuidad de datos de usuario
   - Backup automático durante rebuild

3. **Cleanup Automático:**
   - Eliminación de directorios antiguos (`build/`, `dist/`, `output/`)
   - Prevención de crecimiento indefinido del build
   - Solo archivos finales se mantienen

### Proceso de Build

```bash
# Script automatizado: scripts/build.ps1
1. Copiar repo → Desktop/ApareText-Build
2. Preservar DB si existe
3. Limpiar artifacts antiguos
4. Compilar backend (PyInstaller)
5. Compilar frontend (Electron)
6. Limpiar archivos temporales
7. Generar instalador .exe
```

### Estructura Post-Build

```text
Desktop/ApareText-Build/
├── aparetext.db              # ← PRESERVED
├── ApareText-Setup-*.exe    # ← INSTALLER
├── ApareText/               # ← PORTABLE VERSION
└── [source code]            # ← FOR DEBUGGING ONLY
```

### Problema Resuelto

**Antes:** Build size crecía indefinidamente (~500MB+ por build)
**Después:** Build size consistente (~50-100MB), repo limpio

**Causa:** Directorios `output/`, `dist/`, `build/` se acumulaban
**Solución:** Build en desktop + cleanup automático
