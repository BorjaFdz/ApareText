# ApareText Icons

Por ahora, electron-builder puede funcionar sin iconos (usará el ícono por defecto de Electron).

Para crear iconos profesionales:

1. **Crear diseño 512x512px** en formato PNG
2. **Convertir a .ico** (Windows):
   - Usar herramienta online: https://convertio.co/es/png-ico/
   - O usar ImageMagick: `convert icon.png -resize 256x256 icon.ico`

3. **Convertir a .icns** (macOS):
   - Usar herramienta online: https://cloudconvert.com/png-to-icns
   - O usar iconutil en macOS

4. **Guardar archivos** en este directorio:
   - `icon.ico` para Windows
   - `icon.icns` para macOS  
   - `icon.png` (512x512) para Linux

## Nota

El empaquetado funcionará sin iconos, pero es recomendable agregarlos para una apariencia profesional.
