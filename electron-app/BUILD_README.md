# Build Instructions - ApareText

## Problemas comunes y soluciones

### ❌ "output file is locked for writing (maybe by virus scanner)"

Este error ocurre cuando Windows Defender o el antivirus bloquean los archivos durante el build.

#### Soluciones automáticas implementadas:

1. **Script de limpieza agresiva**: Mata todos los procesos relacionados antes del build
2. **Desactivación temporal de Windows Defender**: Se desactiva durante el build y se reactiva después
3. **Múltiples métodos de limpieza**: Usa PowerShell, CMD y robocopy para asegurar limpieza completa
4. **Configuración optimizada**: Electron-builder configurado para no esperar por archivos bloqueados

#### Si aún tienes problemas:

1. **Cierra todas las aplicaciones** relacionadas con ApareText
2. **Desactiva temporalmente el antivirus** manualmente
3. **Ejecuta como administrador**:
   ```powershell
   # En PowerShell como administrador
   cd C:\Users\[tu_usuario]\_Repostitorios\ApareText\electron-app
   npm run build:win
   ```

4. **Limpieza manual** si es necesario:
   ```powershell
   # Detener procesos
   taskkill /F /IM "ApareText*.exe" /T
   taskkill /F /IM "electron.exe" /T

   # Limpiar directorios
   Remove-Item -Path "dist" -Recurse -Force -ErrorAction SilentlyContinue
   Remove-Item -Path "build" -Recurse -Force -ErrorAction SilentlyContinue
   ```

## Comando de build

```bash
npm run build:win
```

Este comando ejecuta automáticamente:
- `npm run prebuild` - Limpieza inicial
- `scripts/before-build.js` - Limpieza con Node.js
- `scripts/before-build.ps1` - Limpieza agresiva con PowerShell
- `electron-builder --win` - Build principal
- `scripts/after-build.ps1` - Verificación y limpieza final

## Archivos generados

- `dist/ApareText-Setup-X.X.X.exe` - Instalador NSIS
- `dist/ApareText-X.X.X-portable.exe` - Versión portable
- `dist/build-info.json` - Información del build

## Troubleshooting

### Build se queda colgado
- Presiona `Ctrl+C` para cancelar
- Ejecuta la limpieza manual
- Reinicia la computadora si es necesario

### Archivos corruptos
- Borra manualmente las carpetas `dist` y `build`
- Ejecuta `npm run clean`
- Vuelve a intentar el build

### Error de permisos
- Ejecuta PowerShell como administrador
- Asegúrate de que no hay archivos abiertos en las carpetas del proyecto