# 🏗️ ApareText Build Instructions

## 📋 Build Process Rules

### 1. Build Location
- **ALWAYS build on OneDrive Desktop** in the same location: `C:\Users\[USER]\OneDrive\Escritorio\ApareText-Build`
- **NEVER build inside the repository** to avoid accumulating build artifacts
- **Repository contains source code only** - build directory contains compiled artifacts

### 2. Cleanup Before Build
- **ALWAYS delete everything** in the build directory except the database file (`aparetext.db`)
- **PRESERVE the database** (`aparetext.db`) between builds for data continuity
- **OVERWRITE all other files** without mercy

### 3. Build Directory Structure
```
Desktop/
└── ApareText-Build/
    ├── aparetext.db          # ← PRESERVE THIS FILE
    ├── Installers/           # ← INSTALLERS HERE
    │   ├── ApareText-Setup-*.exe
    │   └── ApareText-*.exe
    └── ApareText/            # ← Generated app directory
        └── ...
```
```
OneDrive/Escritorio/
└── ApareText-Build/           # ← Build artifacts only
    ├── aparetext.db           # ← PRESERVE THIS FILE
    ├── ApareText-Setup-*.exe  # ← Generated installer
    └── ApareText/             # ← Generated app directory
        └── ...

Repositorio (_Repostitorios/ApareText/) # ← Source code only
├── core/                      # ← Python backend
├── electron-app/              # ← Electron frontend
├── scripts/                   # ← Build scripts
└── docs/                      # ← Documentation
```

### 4. Build Commands
```bash
# 1. Clean build directory (preserve database)
# 2. Copy only necessary source code and dependencies to build location
# 3. Run build process with aggressive cleanup
# 4. Deploy generated files
```

### 5. Build Optimizations

- **Space monitoring**: Checks available disk space before build
- **Selective copying**: Excludes `.git`, `node_modules`, `__pycache__`, logs, etc.
- **Smart copying**: Only copies source code and required dependencies
- **Aggressive cleanup**: Removes build artifacts, caches, and temp files
- **Size reporting**: Shows space saved after cleanup
- **Database preservation**: Maintains user data between builds

### 6. Repository Maintenance

- Keep repository clean - no build artifacts
- Use `.gitignore` to exclude build files
- Only commit source code and documentation

## ⚠️ Critical Reminders

- **Repository vs Build separation**: Repository contains source code only, build directory contains compiled artifacts
- **OneDrive build location**: Always build in `C:\Users\[USER]\OneDrive\Escritorio\ApareText-Build`
- **Database preservation**: `aparetext.db` is preserved between builds for user data continuity
- **Clean repository**: Never commit build artifacts - keep repository lean
- **Smart copying**: Only necessary source files are copied to build directory

---

## ✅ Estado Actual

ApareText **YA ESTÁ LISTO** para ser empaquetado como instalador Windows standalone.

### Cambios Implementados (Octubre 21, 2025)

1. ✅ **Backend empaquetado con PyInstaller**
   - Archivo: `dist/ApareText-Server.exe`
   - Tamaño: ~18.6 MB
   - Sin ventana de consola (background service)
   - Incluye todas las dependencias de Python

2. ✅ **Auto-start del backend en Electron**
   - Se inicia automáticamente en producción
   - Se detiene al cerrar la aplicación
   - En desarrollo sigue iniciándose manualmente

3. ✅ **electron-builder configurado**
   - `extraResources` para incluir el backend
   - Genera instalador NSIS y versión portable
   - Nombres de archivo personalizados

4. ✅ **Script de compilación automatizado**
   - `scripts/build.ps1` compila todo en un paso
   - Verificaciones automáticas de errores
   - Reporte detallado de archivos generados

5. ✅ **Importación de snippets desde JSON**
   - Endpoint `/api/import` implementado
   - Soporte para categorías/tags
   - Compatible con backups exportados

---

## 🚀 Compilar Instalador

### Método 1: Script Automatizado (Recomendado)

```powershell
# Ejecutar desde la raíz del proyecto
.\scripts\build.ps1
```

Este script:
1. Compila el backend con PyInstaller
2. Verifica dependencias de Electron
3. Compila la aplicación con electron-builder
4. Genera instaladores en `electron-app/dist/`

**Tiempo estimado**: 5-8 minutos

### Limpieza del Repositorio

Antes de hacer commit, ejecuta el script de limpieza:

```powershell
.\scripts\cleanup.ps1
```

Este script elimina automáticamente todos los artifacts de build que puedan haberse acumulado.

**Nota:** Si el script no puede eliminar algunos directorios (archivos bloqueados), cierra todas las instancias de ApareText y reinicia tu computadora.

```powershell
# 1. Compilar backend
C:/Users/bfern/_Repostitorios/ApareText/venv/Scripts/python.exe -m PyInstaller aparetext_server.spec --clean --noconfirm

# 2. Ir a directorio de Electron
cd electron-app

# 3. Instalar dependencias (si es necesario)
npm install

# 4. Compilar aplicación
npm run build:win

# 5. Volver a raíz
cd ..
```

---

## 📁 Archivos Generados

Después de compilar, encontrarás en `electron-app/dist/`:

- `ApareText-Setup-1.0.0.exe` - **Instalador NSIS** (~200 MB)
  - Instala en `C:\Program Files\ApareText\`
  - Crea accesos directos
  - Agrega al menú inicio

- `ApareText-1.0.0-portable.exe` - **Versión portable** (~200 MB)
  - No requiere instalación
  - Ejecuta directamente
  - Ideal para USB o pruebas

---

## 🎨 Iconos (Opcional)

Por ahora, la aplicación usa el ícono por defecto de Electron. Para personalizar:

1. **Crear** ícono 512x512px en formato PNG
2. **Convertir a .ico** (Windows):
   - Online: https://convertio.co/es/png-ico/
   - O ImageMagick: `convert icon.png -resize 256x256 icon.ico`
3. **Guardar** en `electron-app/assets/icon.ico`
4. **Recompilar**: `.\scripts\build.ps1`

---

## ✅ Verificación

### 1. Probar backend standalone

```powershell
# El backend debe funcionar sin Python instalado
.\dist\ApareText-Server.exe
```

Debería iniciar sin ventana de consola. Verificar en:
- Administrador de tareas → "ApareText-Server.exe" corriendo
- Navegador: http://127.0.0.1:46321/ → {"status":"ok"}

### 2. Probar desarrollo

```powershell
# Terminal 1: Backend manual (desarrollo)
python -m uvicorn server.api:app --port 46321

# Terminal 2: Electron
cd electron-app
npm start
```

### 3. Probar instalador

1. **Ejecutar** `ApareText-Setup-1.0.0.exe` en máquina de prueba
2. **Instalar** siguiendo el wizard
3. **Iniciar** desde el menú inicio
4. **Verificar**:
   - Backend inicia automáticamente (sin ventana)
   - Paleta funciona con `Ctrl+Space`
   - Manager se abre correctamente
   - Snippets se expanden

---

## 🐛 Solución de Problemas

### Error: "Backend executable not found"

**Causa**: electron-builder no incluyó el backend

**Solución**:
```powershell
# Verificar que existe
ls dist\ApareText-Server.exe

# Recompilar
.\scripts\build.ps1
```

### Error: "PyInstaller not found"

**Causa**: PyInstaller no está instalado en el venv

**Solución**:
```powershell
C:/Users/bfern/_Repostitorios/ApareText/venv/Scripts/python.exe -m pip install pyinstaller
```

### Error: "npm ERR! Missing script: build:win"

**Causa**: package.json no tiene el script

**Solución**:
```powershell
cd electron-app
npm install electron-builder --save-dev
```

### Backend no inicia en instalador

**Diagnóstico**:
1. Abrir Administrador de Tareas
2. Buscar "ApareText-Server.exe"
3. Si no aparece, revisar:
   - `C:\Program Files\ApareText\resources\ApareText-Server.exe` existe
   - Permisos de ejecución

---

## 📊 Especificaciones Técnicas

### Backend Standalone
- **Motor**: PyInstaller 6.16.0
- **Python**: 3.13.7 (embebido)
- **Tamaño**: ~18.6 MB
- **Dependencias incluidas**:
  - FastAPI 0.118.0
  - Uvicorn 0.37.0
  - SQLAlchemy 2.0.43
  - Pydantic 2.11.10

### Aplicación Electron
- **Electron**: 28.0.0
- **Node**: Embebido
- **Tamaño**: ~200 MB (con backend)
- **Plataforma**: Windows x64

### Instalador
- **Tipo**: NSIS (Nullsoft Scriptable Install System)
- **Opciones**: Full install / Portable
- **Compresión**: Alta (reduce ~30%)

---

## 📝 Notas de Desarrollo

### Modo Desarrollo vs Producción

```javascript
// En main.js
const isDev = !app.isPackaged;

if (isDev) {
    // Backend manual, espera que esté corriendo
    console.log('[ApareText] Development mode');
} else {
    // Backend auto-start desde resources
    const backendPath = path.join(process.resourcesPath, 'ApareText-Server.exe');
    backendProcess = spawn(backendPath);
}
```

### Estructura del Instalador

```
C:\Program Files\ApareText\
├── ApareText.exe           ← Aplicación Electron
├── resources\
│   ├── app.asar            ← Código de la app
│   └── ApareText-Server.exe ← Backend (auto-start)
├── locales\
├── *.dll
└── Uninstall.exe
```

---

## 🎯 Próximas Mejoras (Futuro)

- [ ] Auto-updater (electron-updater)
- [ ] Firma digital del código (Code Signing)
- [ ] Instalador para macOS (.dmg)
- [ ] AppImage para Linux
- [ ] Icono personalizado profesional
- [ ] Splash screen durante carga
- [ ] Notificaciones de sistema

---

## 📞 Soporte

Si encuentras problemas:

1. **Revisar logs**:
   - Electron DevTools: `Ctrl+Shift+I`
   - Backend logs: (silenciado por defecto)

2. **Limpiar y recompilar**:
   ```powershell
   Remove-Item dist -Recurse -Force
   Remove-Item build -Recurse -Force
   Remove-Item electron-app\dist -Recurse -Force
   .\scripts\build.ps1
   ```

3. **Crear issue en GitHub** con:
   - Versión de Windows
   - Logs de error
   - Pasos para reproducir

---

**Última actualización**: Octubre 8, 2025  
**Versión**: 0.2.0  
**Estado**: ✅ Listo para producción
