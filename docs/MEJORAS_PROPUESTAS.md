# 📋 Análisis del Proyecto y Mejoras Propuestas

**Fecha:** 7 de Octubre, 2025  
**Proyecto:** ApareText v1.0  
**Arquitectura Actual:** Electron + FastAPI + SQLite

---

## 📊 Estado Actual del Proyecto

### ✅ Completado (90%)
- ✅ Core backend (Python) con modelos, DB y parser
- ✅ API REST FastAPI funcional (15+ endpoints)
- ✅ Aplicación Electron con palette y manager
- ✅ Glassmorphism UI unificada
- ✅ WYSIWYG editor con Quill.js
- ✅ Filtrado por tags en palette
- ✅ CRUD completo de snippets
- ✅ Template parser con variables y funciones
- ✅ Export/Import JSON

### ⚠️ Incompleto o Sin Implementar
- ❌ **Formulario de variables** (snippets con {{variables}} no piden valores)
- ❌ **Tests** (carpeta `tests/` vacía)
- ❌ **Detector de abreviaturas** (no funciona ;abbr + Tab)
- ❌ **Scope filtering** (no filtra por app/dominio)
- ❌ **WebSocket real-time** (implementado pero no usado)
- ❌ **Extensión de navegador** (solo documentado)
- ❌ **Inserción real de texto** (solo clipboard)
- ❌ **Estadísticas de uso** (endpoint existe pero no UI)

---

## 🎯 Mejoras Propuestas por Prioridad

### 🔴 **PRIORIDAD CRÍTICA** (Funcionalidad Básica Rota)

#### 1. **Implementar Formulario de Variables** ⭐⭐⭐⭐⭐
**Problema:** Cuando un snippet tiene variables `{{nombre}}`, se expande sin pedir valores.

**Impacto:** Funcionalidad core no funcional.

**Solución:**
```javascript
// palette.html - Detectar variables y mostrar formulario
async function expandSnippet(snippet) {
    // 1. Extraer variables del template
    const variables = extractVariables(snippet.content_text || snippet.content_html);
    
    // 2. Si hay variables, mostrar formulario modal
    if (variables.length > 0) {
        const values = await showVariableForm(snippet, variables);
        if (!values) return; // Usuario canceló
        
        // 3. Expandir con valores
        await ipcRenderer.invoke('expand-snippet', snippet.id, values);
    } else {
        // Sin variables, expandir directo
        await ipcRenderer.invoke('expand-snippet', snippet.id, {});
    }
}

function showVariableForm(snippet, variables) {
    // Crear modal dinámico con inputs para cada variable
    // Usar snippet.variables[] para metadata (label, placeholder, required)
    // Retornar Promise<object> con valores o null si canceló
}
```

**Archivos a modificar:**
- `electron-app/palette.html` (agregar modal y lógica)
- `electron-app/manager.html` (igual para preview)

**Estimación:** 4-6 horas

---

#### 2. **Detector de Abreviaturas Global** ⭐⭐⭐⭐⭐
**Problema:** No detecta cuando escribes `;firma` + Tab para expandir automáticamente.

**Impacto:** Funcionalidad principal del text-expander no funciona.

**Solución:**
Usar `node-key-sender` (ya en dependencies) o `iohook` para capturar teclas globales:

```javascript
// main.js - Agregar listener de teclado global
const iohook = require('iohook');

let keyBuffer = [];
let snippetsMap = {}; // {";firma": snippetId}

async function startAbbreviationDetector() {
    // Cargar snippets con abreviaturas
    const snippets = await axios.get(`${API_URL}/api/snippets`);
    snippets.data.forEach(s => {
        if (s.abbreviation) {
            snippetsMap[s.abbreviation] = s.id;
        }
    });
    
    // Escuchar teclas
    iohook.on('keypress', (event) => {
        const char = String.fromCharCode(event.rawcode);
        keyBuffer.push(char);
        
        // Mantener buffer corto
        if (keyBuffer.length > 50) keyBuffer.shift();
        
        // Buscar coincidencias
        const bufferStr = keyBuffer.join('');
        for (const [abbr, snippetId] of Object.entries(snippetsMap)) {
            if (bufferStr.endsWith(abbr)) {
                // ¡Match! Expandir snippet
                expandAbbreviation(snippetId, abbr.length);
                keyBuffer = [];
                break;
            }
        }
    });
    
    iohook.start();
}

async function expandAbbreviation(snippetId, abbrLength) {
    // 1. Borrar abreviatura (simular backspaces)
    // 2. Obtener snippet y expandir
    // 3. Insertar contenido
}
```

**Dependencias necesarias:**
```bash
npm install iohook
```

**Archivos a crear/modificar:**
- `electron-app/main.js` (agregar detector)
- Agregar toggle on/off en tray menu

**Estimación:** 8-12 horas (complejidad de keyboard hooks cross-platform)

---

### 🟡 **PRIORIDAD ALTA** (Mejoras Importantes)

#### 3. **Inserción Real de Texto (Robot.js)** ⭐⭐⭐⭐
**Problema:** Actualmente solo copia al clipboard. El usuario debe hacer Ctrl+V manualmente.

**Solución:**
```bash
npm install robotjs
```

```javascript
// main.js
const robot = require('robotjs');

async function insertText(text) {
    // Esperar 100ms para cambiar de ventana
    await new Promise(r => setTimeout(r, 100));
    
    // Simular Ctrl+V automáticamente
    robot.keyTap('v', 'control');
    
    // O escribir carácter por carácter (más lento pero más confiable)
    // robot.typeString(text);
}
```

**Ventajas:**
- Expansión automática sin intervención del usuario
- Experiencia similar a Alfred/TextExpander

**Archivos a modificar:**
- `electron-app/main.js` (función insertText)

**Estimación:** 2-3 horas

---

#### 4. **Tests Unitarios y de Integración** ⭐⭐⭐⭐
**Problema:** Carpeta `tests/` vacía. No hay cobertura de tests.

**Solución:**
```bash
# Instalar pytest
pip install pytest pytest-asyncio httpx
```

**Estructura propuesta:**
```
tests/
├── core/
│   ├── test_database.py
│   ├── test_models.py
│   ├── test_snippet_manager.py
│   └── test_template_parser.py
├── server/
│   ├── test_api.py
│   └── test_websocket.py
└── integration/
    └── test_full_flow.py
```

**Ejemplo de test:**
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
    result = parser.parse("Hola {{nombre}}", {"nombre": "Juan"})
    assert result == "Hola Juan"

def test_cursor_position():
    parser = TemplateParser()
    result, cursor = parser.parse_with_cursor_position(
        "Hola {{nombre}}{{|}}", {"nombre": "Juan"}
    )
    assert result == "Hola Juan"
    assert cursor == len("Hola Juan")
```

**Archivos a crear:**
- 10+ archivos de test (ver estructura)
- `pytest.ini` (configuración)
- `.github/workflows/tests.yml` (CI/CD)

**Estimación:** 12-16 horas

---

#### 5. **Filtrado por Scope (Apps/Dominios)** ⭐⭐⭐⭐
**Problema:** Los snippets con `scope_type=apps` o `domains` no se filtran según la app activa.

**Solución:**
```javascript
// main.js - Detectar app activa (Windows)
const activeWin = require('active-win');

async function getActiveContext() {
    const win = await activeWin();
    return {
        app: win?.owner?.name,  // "chrome.exe"
        title: win?.title,      // "Twitter - Google Chrome"
        domain: extractDomain(win?.title)
    };
}

function extractDomain(title) {
    // Extraer dominio del título de navegador
    const match = title?.match(/(?:https?:\/\/)?(?:www\.)?([^\s/]+)/);
    return match ? match[1] : null;
}

// Al expandir, filtrar snippets por scope
ipcMain.handle('get-snippets', async () => {
    const context = await getActiveContext();
    const allSnippets = await axios.get(`${API_URL}/api/snippets`);
    
    return allSnippets.data.filter(s => {
        if (s.scope_type === 'global') return true;
        if (s.scope_type === 'apps') {
            return s.scope_values.some(app => 
                context.app?.toLowerCase().includes(app.toLowerCase())
            );
        }
        if (s.scope_type === 'domains') {
            return s.scope_values.some(domain => 
                context.domain?.includes(domain)
            );
        }
        return true;
    });
});
```

**Dependencias:**
```bash
npm install active-win
```

**Archivos a modificar:**
- `electron-app/main.js` (lógica de filtrado)
- `server/api.py` (agregar filtros a endpoints)

**Estimación:** 6-8 horas

---

### 🟢 **PRIORIDAD MEDIA** (Mejoras de UX)

#### 6. **Estadísticas de Uso en UI** ⭐⭐⭐
**Problema:** El endpoint `/api/stats` existe pero no hay UI.

**Solución:**
Agregar pestaña "📊 Stats" en el manager:

```html
<!-- manager.html -->
<div class="stats-section" id="statsSection" style="display: none;">
    <h2>Estadísticas de Uso</h2>
    <div class="stat-card">
        <div class="stat-value" id="totalUses">0</div>
        <div class="stat-label">Expansiones Totales</div>
    </div>
    <div class="stat-card">
        <div class="stat-value" id="topSnippet">-</div>
        <div class="stat-label">Snippet Más Usado</div>
    </div>
    <canvas id="usageChart"></canvas>
</div>
```

```javascript
async function loadStats() {
    const stats = await ipcRenderer.invoke('get-stats');
    document.getElementById('totalUses').textContent = stats.total_uses;
    // Render chart con Chart.js
    renderUsageChart(stats);
}
```

**Dependencias:**
```bash
npm install chart.js
```

**Archivos a modificar:**
- `electron-app/manager.html` (agregar pestaña)
- `electron-app/main.js` (agregar IPC handler)

**Estimación:** 4-5 horas

---

#### 7. **Backup/Restore desde UI** ⭐⭐⭐
**Problema:** Export/Import existen en API pero no hay botones en UI.

**Solución:**
```html
<!-- manager.html - Agregar toolbar buttons -->
<button class="btn-icon" onclick="exportSnippets()">
    💾 Export
</button>
<button class="btn-icon" onclick="importSnippets()">
    📥 Import
</button>
```

```javascript
async function exportSnippets() {
    const { filePath } = await electron.remote.dialog.showSaveDialog({
        defaultPath: `aparetext_backup_${new Date().toISOString()}.json`,
        filters: [{ name: 'JSON', extensions: ['json'] }]
    });
    
    if (filePath) {
        const data = await ipcRenderer.invoke('export-snippets');
        await fs.writeFile(filePath, JSON.stringify(data, null, 2));
        alert('✅ Snippets exportados correctamente');
    }
}

async function importSnippets() {
    const { filePaths } = await electron.remote.dialog.showOpenDialog({
        filters: [{ name: 'JSON', extensions: ['json'] }],
        properties: ['openFile']
    });
    
    if (filePaths[0]) {
        const content = await fs.readFile(filePaths[0], 'utf8');
        await ipcRenderer.invoke('import-snippets', JSON.parse(content));
        await loadSnippets();
        alert('✅ Snippets importados correctamente');
    }
}
```

**Archivos a modificar:**
- `electron-app/manager.html` (agregar botones)
- `electron-app/main.js` (agregar IPC handlers)

**Estimación:** 3-4 horas

---

#### 8. **Búsqueda Fuzzy Mejorada** ⭐⭐⭐
**Problema:** La búsqueda actual es simple `.includes()`. No soporta typos ni búsqueda inteligente.

**Solución:**
```bash
npm install fuse.js
```

```javascript
// palette.html
const Fuse = require('fuse.js');

const fuse = new Fuse(allSnippets, {
    keys: ['name', 'abbreviation', 'tags', 'content_text'],
    threshold: 0.3,  // Tolerancia a typos
    ignoreLocation: true
});

function searchSnippets(query) {
    if (!query) return allSnippets;
    return fuse.search(query).map(result => result.item);
}
```

**Ventajas:**
- Búsqueda tolerante a errores tipográficos
- Búsqueda por relevancia
- Búsqueda multi-campo

**Archivos a modificar:**
- `electron-app/palette.html` (reemplazar búsqueda)

**Estimación:** 2-3 horas

---

#### 9. **Preview en Tiempo Real** ⭐⭐⭐
**Problema:** Al editar un snippet, no ves cómo se verá el resultado final.

**Solución:**
```html
<!-- manager.html -->
<div class="preview-panel">
    <h3>Vista Previa</h3>
    <div id="snippetPreview" class="preview-content"></div>
</div>
```

```javascript
// Actualizar preview en tiempo real
contentInput.addEventListener('input', updatePreview);

function updatePreview() {
    const template = contentInput.value;
    const testVars = {};
    
    // Llenar variables con placeholders
    const variables = parser.extract_variables(template);
    variables.forEach(v => {
        testVars[v] = `[${v}]`;
    });
    
    const preview = parser.parse(template, testVars);
    document.getElementById('snippetPreview').innerHTML = preview;
}
```

**Archivos a modificar:**
- `electron-app/manager.html` (agregar panel)

**Estimación:** 2-3 horas

---

### 🔵 **PRIORIDAD BAJA** (Mejoras Opcionales)

#### 10. **Hotkey Personalizable** ⭐⭐
Permitir cambiar Ctrl+Space por otro atajo.

```javascript
// Agregar en settings
function registerCustomHotkey(hotkey) {
    globalShortcut.unregisterAll();
    globalShortcut.register(hotkey, showPalette);
}
```

**Estimación:** 2 horas

---

#### 11. **Themes (Dark/Light Mode)** ⭐⭐
Agregar tema oscuro.

```css
/* palette.html */
[data-theme="dark"] {
    --bg-color: rgba(30, 30, 40, 0.95);
    --text-color: rgba(255, 255, 255, 0.9);
    --border-color: rgba(255, 255, 255, 0.1);
}
```

**Estimación:** 3-4 horas

---

#### 12. **Snippets Compartidos (Cloud Sync)** ⭐
Sincronización con Dropbox/Google Drive.

**Estimación:** 16-20 horas

---

## 🏗️ Mejoras de Arquitectura

### 1. **Separar Lógica de UI**
Actualmente todo el código JS está en los HTML. Mejor:
```
electron-app/
├── main.js
├── preload.js
├── renderer/
│   ├── palette.js
│   ├── manager.js
│   └── shared.js
├── styles/
│   ├── palette.css
│   └── manager.css
└── views/
    ├── palette.html
    └── manager.html
```

---

### 2. **Estado Global con Vuex/Redux**
Evitar pasar snippets entre ventanas manualmente.

---

### 3. **Modularizar API**
```python
server/
├── api/
│   ├── __init__.py
│   ├── snippets.py
│   ├── stats.py
│   └── export.py
├── middleware/
└── utils/
```

---

## 📈 Roadmap Sugerido

### **Sprint 1 (1-2 semanas)** - Funcionalidad Core
1. ✅ Formulario de variables
2. ✅ Detector de abreviaturas
3. ✅ Inserción real de texto
4. ✅ Tests básicos

### **Sprint 2 (1 semana)** - UX
5. ✅ Scope filtering
6. ✅ Estadísticas en UI
7. ✅ Búsqueda fuzzy
8. ✅ Backup/Restore UI

### **Sprint 3 (1 semana)** - Polish
9. ✅ Preview en tiempo real
10. ✅ Hotkey personalizable
11. ✅ Dark mode
12. ✅ Refactoring arquitectura

### **Sprint 4 (2-3 semanas)** - Extensión Browser
13. ✅ Extensión Chrome/Firefox
14. ✅ WebSocket real-time
15. ✅ Cloud sync (opcional)

---

## 🎯 Quick Wins (Bajo Esfuerzo, Alto Impacto)

1. **Preview en tiempo real** (2h, mejora experiencia)
2. **Búsqueda fuzzy** (3h, mejor UX)
3. **Backup/Restore UI** (4h, evita pérdida de datos)
4. **Estadísticas** (5h, engagement)
5. **Tests básicos** (8h, calidad)

---

## 🚨 Bugs Conocidos a Corregir

1. ❌ **Snippets con variables no se expanden correctamente**
2. ❌ **Detector de abreviaturas no funciona**
3. ⚠️ **Quill editor puede tener scroll issues** (revisar height)
4. ⚠️ **Tags con espacios no se filtran bien** (trim en split)
5. ⚠️ **WebSocket no se usa en ningún lugar**

---

## 📦 Dependencias Sugeridas

```json
{
  "dependencies": {
    "axios": "^1.6.2",
    "iohook": "^0.9.3",        // NEW: Keyboard hooks
    "robotjs": "^0.6.0",        // NEW: Inserción texto
    "active-win": "^7.7.1",     // NEW: Detectar app activa
    "fuse.js": "^7.0.0",        // NEW: Búsqueda fuzzy
    "chart.js": "^4.4.0"        // NEW: Stats charts
  },
  "devDependencies": {
    "electron": "^28.0.0",
    "electron-builder": "^24.9.1",
    "jest": "^29.7.0",          // NEW: Testing
    "eslint": "^8.55.0"         // NEW: Linting
  }
}
```

---

## 💡 Conclusión

El proyecto tiene una **base sólida** (90% completado) pero le faltan **funcionalidades críticas** para ser usable:

**Bloqueantes:**
- ❌ Formulario de variables
- ❌ Detector de abreviaturas
- ❌ Tests

**Recomendación:** Priorizar Sprint 1 (funcionalidad core) antes de agregar features nuevas.

**Tiempo estimado para MVP completo:** 3-4 semanas (1 dev full-time)

---

