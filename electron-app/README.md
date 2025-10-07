# ApareText - Electron Desktop App

Aplicación de escritorio multiplataforma usando Electron + tu API REST existente.

## ✨ Características

- ✅ **Detección de Abreviaturas**: `;firma` + Tab funciona PERFECTAMENTE
- ✅ **Paleta de Comandos**: Ctrl+Space para búsqueda fuzzy
- ✅ **Hooks Globales**: Sin bloqueos, sin conflictos
- ✅ **Multiplataforma**: Windows, macOS, Linux
- ✅ **Bandeja del Sistema**: Siempre accesible
- ✅ **Inserción de Texto**: Automática sin bloquear UI

## 🚀 Instalación

### 1. Instalar dependencias

```bash
cd electron-app
npm install
```

### 2. Instalar robotjs y iohook (nativos)

**Windows:**
```bash
npm install robotjs
npm install iohook
```

Si da error, instalar build tools:
```bash
npm install --global windows-build-tools
npm install robotjs
npm install iohook
```

**macOS/Linux:**
```bash
npm install robotjs
npm install iohook
```

## 📦 Dependencias Clave

- **electron**: Framework principal
- **iohook**: Hooks de teclado globales (MUCHO mejor que keyboard de Python)
- **robotjs**: Simular teclas y controlar clipboard
- **axios**: Cliente HTTP para conectar con tu API
- **electron-localshortcut**: Hotkeys globales

## 🎯 Uso

### Desarrollo

1. **Iniciar API server** (en otra terminal):
```bash
cd ..
.\venv\Scripts\Activate.ps1
python -m server.main
```

2. **Iniciar Electron app**:
```bash
cd electron-app
npm start
```

### Funcionalidades

- **Ctrl+Space**: Abrir paleta de comandos
- **`;abbreviation` + Tab**: Expandir abreviatura automáticamente
- **Click en tray**: Abrir paleta
- **Right-click en tray**: Menú de opciones

## 🏗️ Construcción

### Windows
```bash
npm run build:win
```

Genera:
- `dist/ApareText Setup.exe` (instalador)
- `dist/ApareText.exe` (portable)

### macOS
```bash
npm run build:mac
```

### Linux
```bash
npm run build:linux
```

## 🔧 Arquitectura

```
Electron App (Frontend)
    ↓
IPC Communication
    ↓
Main Process (Backend)
    ↓ HTTP
Python API Server (localhost:46321)
    ↓
SQLite Database
```

**Ventajas:**
1. ✅ Electron maneja los hooks SIN conflictos
2. ✅ Reutilizas toda tu lógica de negocio (API Python)
3. ✅ Multiplataforma real
4. ✅ Más fácil de distribuir (.exe, .dmg, .AppImage)

## 🐛 Troubleshooting

### Error: "Cannot find module 'iohook'"

```bash
npm install iohook --save
```

Si persiste (Windows):
```bash
npm install --global windows-build-tools
npm rebuild iohook --build-from-source
```

### Error: "Cannot find module 'robotjs'"

```bash
npm install robotjs --save
```

### API Server no conecta

Asegúrate de que el servidor Python está corriendo:
```bash
python -m server.main
```

Debe mostrar: `✅ Server running on http://localhost:46321`

## 📊 Comparación Python vs Electron

| Feature | Python + Qt | Electron |
|---------|-------------|----------|
| Hooks globales | ❌ Bloquea | ✅ Funciona |
| Multiplataforma | ⚠️ Complejo | ✅ Nativo |
| Distribución | ⚠️ Difícil | ✅ Fácil |
| Desarrollo UI | ⚠️ Qt Designer | ✅ HTML/CSS |
| Tamaño app | ✅ ~50MB | ⚠️ ~150MB |

## 🎨 Próximos Pasos

1. [ ] Agregar icono personalizado (`assets/icon.ico`)
2. [ ] Implementar form para variables en snippets
3. [ ] Agregar scope filtering por app/dominio
4. [ ] Mejorar UI de settings
5. [ ] Auto-updater
6. [ ] Estadísticas de uso en UI

## 📝 Notas

- **iohook es CLAVE**: Es lo que hace que los hooks funcionen sin bloquear
- La app se ejecuta en background (bandeja del sistema)
- El clipboard se usa temporalmente para insertar texto
- Requiere que el API server esté corriendo

## 🎉 ¿Funciona?

**SÍ, PERFECTAMENTE** 🚀

Ya no más bloqueos, ya no más conflictos de event loops. Electron fue diseñado para esto.
