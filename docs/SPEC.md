# Especificación Funcional y Técnica - ApareText

**Versión:** 1.0.0  
**Fecha:** Octubre 2025  
**Estado:** MVP en desarrollo

---

## 1. Visión y Objetivos

### Propósito
ApareText es una herramienta de productividad que permite escribir más rápido y con consistencia mediante atajos de texto (snippets) reutilizables con variables, formateo y lógica básica.

### Modos de Uso

1. **Paleta Global**: Atajo del sistema abre un buscador flotante con tus snippets → seleccionar → insertar en la app activa
2. **Expansión por Abreviatura**: Al teclear `;firma` + `Tab` (o separador) se reemplaza por el contenido
3. **Web**: Dashboard en navegador para gestionar snippets y extensión overlay dentro de cualquier textarea/contentEditable

### Público Objetivo
- Creadores de contenido
- Atención al cliente
- Equipos de ventas
- Recursos humanos
- Social media managers
- Programadores

---

## 2. Alcance

### MVP (Sprints 1-8)

**Características principales:**
- ✅ Crear/editar/eliminar snippets (texto plano y rich text HTML)
- ✅ Variables en snippets: `{{nombre}}`, con tipo, placeholder y valor por defecto
- ✅ Paleta global (hotkey configurable), búsqueda difusa, vista previa
- ✅ Insertar en app activa: simular teclado o portapapeles (fallback)
- ⏳ Abreviaturas + disparador (`Tab`, `Space`, `Enter`)
- ⏳ Scopes: global / por app (ej., solo en Twitter, Gmail, VSCode)
- ✅ Dashboard web local (http://localhost:46321) para gestionar snippets
- ✅ Persistencia local: SQLite + export/import JSON
- ⏳ Extensión navegador (Chrome/Edge/Firefox): overlay y pegado
- ✅ Tray icon + ajustes (hotkeys, temas, copia de seguridad)
- ⏳ Permisos OS (accesibilidad macOS, auto-start, firma mínima)

### v1.0 (Post-MVP)

**Características avanzadas:**
- Sincronización opcional (carpeta Dropbox/Drive o Supabase/Postgres)
- Campos avanzados: select, date, checkbox; plantillas condicionales
- Fragmentos RTF/HTML con estilos; imágenes embebidas (limitado)
- Funciones: fecha/hora, contador, recortes del portapapeles
- Analítica local (uso por snippet), sin telemetría externa por defecto
- Multilenguaje UI; tema claro/oscuro; accesos rápidos por etiquetas

---

## 3. Historias de Usuario

### US-01: Paleta Global
**Como** usuario  
**Quiero** pulsar `Ctrl+Space` y ver una paleta con mis snippets ordenados por relevancia  
**Para** seleccionar y insertar rápidamente en cualquier aplicación

**Criterios de Aceptación:**
- CA-01: Latencia desde hotkey a paleta visible < 80ms
- CA-02: Búsqueda difusa funcional (typo tolerance)
- CA-03: Preview del snippet antes de insertar
- CA-04: Soporte para navegación con teclado

### US-02: Expansión por Abreviatura
**Como** usuario  
**Quiero** escribir `;firma` + `Tab` en cualquier campo  
**Para** que se expanda automáticamente con mi firma HTML

**Criterios de Aceptación:**
- CA-01: Detección en tiempo real sin lag
- CA-02: No perder el foco del campo activo
- CA-03: Lista de exclusiones (campos password)

### US-03: Variables Dinámicas
**Como** usuario  
**Quiero** insertar un snippet con `{{nombre}}` y `{{empresa}}`  
**Para** rellenar un formulario rápido antes de pegar

**Criterios de Aceptación:**
- CA-01: Formulario modal con todos los campos
- CA-02: Validación según tipo (email, number, etc.)
- CA-03: Valores por defecto y placeholders
- CA-04: Recordar últimos valores usados

### US-04: Scopes por Aplicación
**Como** usuario  
**Quiero** marcar un snippet con scope "twitter.com"  
**Para** que solo aparezca cuando escribo un tweet

**Criterios de Aceptación:**
- CA-01: Detección automática de app/dominio activo
- CA-02: Filtrado transparente en paleta
- CA-03: Snippets globales siempre visibles

### US-05: Export/Import
**Como** usuario  
**Quiero** exportar mis snippets a JSON  
**Para** hacer backup o compartir con mi equipo

**Criterios de Aceptación:**
- CA-01: Formato JSON legible y versionado
- CA-02: Import con opción de merge o replace
- CA-03: Validación de estructura al importar

---

## 4. Requisitos Funcionales

### RF-01: Gestión de Snippets

**Operaciones CRUD:**
- Crear, editar, eliminar, duplicar snippets
- Soporte para texto plano y HTML
- Editor WYSIWYG para rich text

**Campos del Snippet:**
```typescript
interface Snippet {
  id: string;
  name: string;
  abbreviation?: string;
  tags: string[];
  content_text?: string;
  content_html?: string;
  is_rich: boolean;
  scope_type: 'global' | 'apps' | 'domains';
  scope_values: string[];
  caret_marker: string; // default: '{{|}}'
  variables: Variable[];
  usage_count: number;
  enabled: boolean;
  created_at: DateTime;
  updated_at: DateTime;
}
```

**Variables:**
```typescript
interface Variable {
  key: string;
  label?: string;
  type: 'text' | 'email' | 'number' | 'select' | 'date' | 'checkbox';
  placeholder?: string;
  default_value?: string;
  required: boolean;
  regex?: string;
  options?: string[]; // para type='select'
}
```

### RF-02: Lenguaje de Plantillas

**Variables:**
- `{{nombre}}` - Variable simple
- `{{email}}` - Variable con tipo

**Cursor:**
- `{{|}}` - Posición final del cursor

**Funciones:**
- `{{date:%Y-%m-%d}}` - Fecha actual con formato
- `{{time:%H:%M}}` - Hora actual
- `{{clipboard}}` - Contenido del portapapeles

**Escapes:**
- `\{{` - Llaves literales

### RF-03: Paleta Global

**Comportamiento:**
1. Hotkey global (configurable, default: `Ctrl+Space`)
2. Ventana flotante frameless, always-on-top
3. Búsqueda incremental con fuzzy matching
4. Lista ordenada por relevancia + usage_count
5. Preview del contenido
6. Navegación con teclado (↑↓ Enter Esc)
7. Form modal para variables antes de insertar

### RF-04: Métodos de Inserción

**Método 1: Tecleo Simulado**
- Windows: `SendInput` via `keyboard` library
- macOS: Quartz Events via `pynput`
- Linux: `keyboard` library (requiere permisos)
- Velocidad configurable (ms entre teclas)

**Método 2: Portapapeles**
1. Guardar clipboard actual
2. Copiar snippet al clipboard
3. Simular `Ctrl/Cmd+V`
4. Restaurar clipboard original
5. Delay configurable

**Método Auto:**
- Intentar tecleo primero
- Fallback a clipboard si falla

### RF-05: Scopes

**Tipos de Scope:**
- **Global**: Disponible en todas partes
- **Apps**: Solo en aplicaciones específicas (ej: `slack.exe`, `com.apple.mail`)
- **Domains**: Solo en dominios web (ej: `twitter.com`, `gmail.com`)

**Detección:**
- Windows: `win32gui.GetWindowText` + `psutil.Process`
- macOS: `NSWorkspace.activeApplication`
- Linux: `xdotool getactivewindow`

### RF-06: API REST

**Endpoints principales:**

```
GET    /api/snippets              # Listar snippets
GET    /api/snippets/{id}         # Obtener snippet
POST   /api/snippets              # Crear snippet
PUT    /api/snippets/{id}         # Actualizar snippet
DELETE /api/snippets/{id}         # Eliminar snippet

GET    /api/snippets/search/{q}   # Buscar snippets
GET    /api/abbreviations/{abbr}  # Obtener por abreviatura
POST   /api/snippets/expand       # Expandir snippet con variables

GET    /api/stats                 # Estadísticas de uso
GET    /api/export                # Exportar a JSON
POST   /api/import                # Importar desde JSON
```

### RF-07: WebSocket

**Comunicación en tiempo real:**
```
ws://localhost:46321/ws
```

**Mensajes:**
```json
// Cliente → Servidor
{
  "type": "search",
  "query": "firma"
}

// Servidor → Cliente
{
  "type": "search_results",
  "results": [...]
}

// Cliente → Servidor
{
  "type": "expand",
  "snippet_id": "abc123",
  "variables": {"nombre": "Juan"},
  "domain": "twitter.com"
}

// Servidor → Cliente
{
  "type": "expand_result",
  "content": "...",
  "cursor_position": 42,
  "is_rich": false
}
```

---

## 5. Requisitos No Funcionales

### RNF-01: Rendimiento
- Arranque de la app < 400ms
- Consumo idle < 60 MB RAM
- Listeners con CPU < 2%
- Apertura de paleta < 80ms
- Búsqueda incremental sin lag perceptible

### RNF-02: Confiabilidad
- Recuperación del clipboard garantizada
- Watchdog para listener de teclado
- Manejo robusto de crashes (no perder snippets)
- Logs rotatorios para debugging

### RNF-03: Compatibilidad
- Windows 10+
- macOS 12+ (Monterey)
- Ubuntu 22.04+ (X11/Wayland)
- Python 3.10+

### RNF-04: Seguridad
- Todo local por defecto
- Sin telemetría externa
- Lista negra de campos seguros (no insertar en passwords)
- Cifrado opcional para snippets sensibles

### RNF-05: Usabilidad
- Onboarding claro para permisos OS
- Atajos de teclado intuitivos
- Mensajes de error claros
- Navegación 100% con teclado

### RNF-06: Mantenibilidad
- Código modular y desacoplado
- Tests unitarios >70% cobertura
- Documentación inline
- Tipos con mypy

---

## 6. Casos de Uso Extendidos

### CU-01: Insertar Snippet Simple
**Actor:** Usuario  
**Precondición:** App activa, snippets configurados  
**Flujo Principal:**
1. Usuario pulsa `Ctrl+Space`
2. Se abre la paleta de comandos
3. Usuario escribe "firma"
4. Sistema filtra snippets que coinciden
5. Usuario selecciona con Enter
6. Sistema inserta el contenido en la app activa
7. Paleta se cierra automáticamente

**Flujo Alternativo 3a:** No hay coincidencias
- Sistema muestra mensaje "No snippets found"

**Postcondición:** Texto insertado, contador de uso incrementado

### CU-02: Insertar Snippet con Variables
**Flujo Principal:**
1-5. Igual que CU-01
6. Sistema detecta variables en el snippet
7. Sistema muestra formulario modal con campos
8. Usuario rellena variables
9. Usuario presiona "Insert"
10. Sistema procesa template con valores
11. Sistema inserta contenido expandido
12. Sistema mueve cursor a posición `{{|}}`

**Postcondición:** Snippet personalizado insertado

### CU-03: Expansión por Abreviatura
**Flujo Principal:**
1. Usuario escribe `;firma` en cualquier campo
2. Listener detecta el patrón
3. Usuario presiona `Tab`
4. Sistema busca snippet con abbreviation=";firma"
5. Sistema borra los caracteres de la abreviatura
6. Sistema inserta el contenido
7. Sistema posiciona el cursor

**Flujo Alternativo 4a:** Abreviatura no existe
- Sistema no hace nada (deja el texto como está)

---

## 7. Arquitectura Técnica

### Stack Tecnológico

**Backend (Python):**
- Core: SQLAlchemy, Pydantic
- API: FastAPI, Uvicorn, WebSockets
- Desktop: PySide6 (Qt)
- OS Hooks: keyboard, pynput, pywin32, pyobjc

**Frontend (Extensión):**
- TypeScript
- Manifest V3
- WebSocket client

**Base de Datos:**
- SQLite (local)
- JSON (export/import)

### Componentes

```
┌─────────────────────────────────────────┐
│           Desktop App (Qt)              │
│  ┌──────────┐  ┌──────────┐            │
│  │  Palette │  │   Tray   │            │
│  └────┬─────┘  └────┬─────┘            │
│       │             │                   │
│  ┌────▼─────────────▼─────┐            │
│  │    Hotkey Manager      │            │
│  └────────┬────────────────┘            │
│           │                             │
│  ┌────────▼────────────────┐            │
│  │   Text Inserter         │            │
│  │  (Type / Clipboard)     │            │
│  └─────────────────────────┘            │
└───────────┬─────────────────────────────┘
            │
            │ Uses
            ▼
┌─────────────────────────────────────────┐
│         Core Module                     │
│  ┌──────────────┐  ┌─────────────┐     │
│  │   Models     │  │  Template   │     │
│  │  (Pydantic)  │  │   Parser    │     │
│  └──────────────┘  └─────────────┘     │
│  ┌──────────────┐  ┌─────────────┐     │
│  │   Database   │  │  Snippet    │     │
│  │  (SQLite)    │  │  Manager    │     │
│  └──────────────┘  └─────────────┘     │
└───────────┬─────────────────────────────┘
            │
            │ Uses
            ▼
┌─────────────────────────────────────────┐
│         Server Module                   │
│  ┌──────────────┐  ┌─────────────┐     │
│  │  REST API    │  │  WebSocket  │     │
│  │  (FastAPI)   │  │   Manager   │     │
│  └──────┬───────┘  └──────┬──────┘     │
│         │                 │             │
│         └────────┬────────┘             │
│                  │                      │
│         http://localhost:46321          │
└──────────────────┬──────────────────────┘
                   │
                   │ Connects
                   ▼
┌─────────────────────────────────────────┐
│      Browser Extension                  │
│  ┌──────────────┐  ┌─────────────┐     │
│  │Content Script│  │  Background │     │
│  │  (Overlay)   │  │   Worker    │     │
│  └──────────────┘  └─────────────┘     │
└─────────────────────────────────────────┘
```

### Base de Datos

**Esquema SQLite:**

```sql
CREATE TABLE snippets (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  abbreviation TEXT,
  tags TEXT,
  content_text TEXT,
  content_html TEXT,
  is_rich INTEGER DEFAULT 0,
  scope_type TEXT DEFAULT 'global',
  scope_values TEXT,
  caret_marker TEXT DEFAULT '{{|}}',
  usage_count INTEGER DEFAULT 0,
  enabled INTEGER DEFAULT 1,
  created_at TEXT,
  updated_at TEXT
);

CREATE TABLE snippet_variables (
  id TEXT PRIMARY KEY,
  snippet_id TEXT NOT NULL,
  key TEXT NOT NULL,
  label TEXT,
  type TEXT NOT NULL,
  placeholder TEXT,
  default_value TEXT,
  required INTEGER DEFAULT 0,
  regex TEXT,
  options TEXT,
  FOREIGN KEY (snippet_id) REFERENCES snippets(id) ON DELETE CASCADE
);

CREATE TABLE settings (
  key TEXT PRIMARY KEY,
  value TEXT
);

CREATE TABLE usage_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  snippet_id TEXT,
  timestamp TEXT,
  source TEXT,
  target_app TEXT,
  target_domain TEXT
);
```

---

## 8. Consideraciones por Sistema Operativo

### Windows
- **Hotkeys:** `keyboard` library (WH_KEYBOARD_LL)
- **Ventana activa:** `win32gui.GetForegroundWindow()`
- **Inserción:** `SendInput` (Unicode support)
- **Clipboard:** `win32clipboard`
- **Auto-start:** Registry key en `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`
- **Permisos:** Ninguno especial, pero firma recomendada para evitar SmartScreen

### macOS
- **Hotkeys:** `pynput` + `pyobjc-framework-Quartz`
- **Ventana activa:** `NSWorkspace.sharedWorkspace().activeApplication()`
- **Inserción:** Quartz `CGEventCreateKeyboardEvent`
- **Clipboard:** `AppKit.NSPasteboard`
- **Auto-start:** Launch Agent en `~/Library/LaunchAgents/`
- **Permisos:** 
  - ⚠️ **Accessibility** (System Preferences → Security)
  - ⚠️ **Input Monitoring** (para hotkeys)
  - Firma y notarización recomendadas

### Linux
- **Hotkeys:** `keyboard` library (requiere root o grupo input)
- **Ventana activa:** `xdotool` (X11) o limitaciones en Wayland
- **Inserción:** `keyboard.write()` (X11) o portapapeles (Wayland)
- **Clipboard:** `pyperclip` + `xclip`/`xsel`
- **Auto-start:** `.desktop` file en `~/.config/autostart/`
- **Permisos:** Puede requerir `sudo` o agregar usuario a grupo `input`
- **Wayland:** Funcionalidad limitada (usar portapapeles + extensión web)

---

## 9. Seguridad y Privacidad

### Principios
1. **Local-first:** Todo funciona sin conexión
2. **Sin telemetría:** No se envían datos a servidores externos
3. **Transparencia:** Código abierto y auditable
4. **Control del usuario:** Sincronización opt-in

### Medidas de Seguridad
- Lista negra de campos (detectar `type="password"`)
- Cifrado opcional de snippets sensibles (v1.0)
- Logs de uso opt-in y borrables
- CORS estricto en API (solo localhost)
- Validación de entrada en todos los endpoints

### Datos Almacenados
- **Snippets:** `~/.aparetext/aparetext.db`
- **Settings:** Incluidos en la misma DB
- **Logs:** `~/.aparetext/logs/` (rotatorios, 7 días)
- **Backups:** Configurables por usuario

---

## 10. Testing

### Estrategia de Tests

**Unitarios (>70% cobertura):**
- Parser de plantillas
- Validación de modelos
- Manager de snippets (CRUD)
- Export/Import JSON

**Integración:**
- API endpoints
- WebSocket communication
- Database migrations

**E2E (Manual):**
- Paleta global en apps reales
- Expansión por abreviatura
- Inserción en campos diversos
- Hotkeys en diferentes SO

**Rendimiento:**
- Tiempo de apertura paleta
- Latencia de búsqueda
- Consumo de memoria idle
- CPU usage de listeners

---

## 11. Roadmap de Desarrollo

### Sprint 1-2: Fundamentos
- [x] Estructura del proyecto
- [x] Modelos de datos
- [x] Database + SQLite
- [x] Template parser básico
- [x] API REST básica

### Sprint 3-4: Desktop App
- [x] Estructura PySide6
- [x] Paleta de comandos
- [x] Hotkey manager
- [x] Text inserter
- [ ] Tests unitarios

### Sprint 5: Abreviaturas
- [ ] Detector de palabras
- [ ] Expansión automática
- [ ] Scopes por app

### Sprint 6: Variables
- [ ] Form modal dinámico
- [ ] Validación por tipo
- [ ] Valores recordados

### Sprint 7: Extensión
- [ ] Manifest V3 base
- [ ] Content script + overlay
- [ ] WebSocket client
- [ ] Inserción en web

### Sprint 8: Polish
- [ ] Settings UI completo
- [ ] Onboarding
- [ ] Packaging
- [ ] Beta testing

---

## 12. Ejemplos Prácticos

### Snippet Simple
```
Nombre: "Firma Email"
Abreviatura: ";firma"
Contenido:
---
Saludos,
Juan Pérez
CEO, MiEmpresa
juan@miempresa.com
+34 600 000 000
---
```

### Snippet con Variables
```
Nombre: "Outreach Twitter"
Abreviatura: ";morning"
Scope: domains = ["twitter.com"]
Variables:
  - nombre: text, required
  - motivo: text, placeholder="Ej: vi tu post sobre..."
  - duracion: select, options=["10","15","20"], default="15"

Contenido:
---
Buenos días {{nombre}},

Te escribo porque {{motivo}}. ¿Te encaja una 
llamada de {{duracion}} minutos esta semana?

Saludos,
Juan{{|}}
---
```

### Snippet con Funciones
```
Nombre: "Meeting Notes"
Abreviatura: ";notas"
Contenido:
---
# Meeting Notes - {{date:%Y-%m-%d}}

**Hora:** {{time:%H:%M}}
**Participantes:** {{participantes}}

## Agenda
{{|}}

## Acuerdos

## Próximos pasos
---
```

---

## Anexos

### A. Glosario
- **Snippet:** Fragmento de texto reutilizable
- **Abreviatura:** Atajo corto que se expande (ej: `;firma`)
- **Scope:** Contexto donde un snippet está disponible
- **Paleta:** Ventana flotante de búsqueda rápida
- **Variable:** Campo personalizable en un snippet
- **Template:** Plantilla con marcadores reemplazables

### B. Referencias
- TextExpander: https://textexpander.com
- espanso: https://espanso.org
- Alfred Workflows: https://alfredapp.com
- FastAPI: https://fastapi.tiangolo.com
- PySide6: https://doc.qt.io/qtforpython

### C. Licencia
MIT License - Open Source
