# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

## [0.2.0] - 2025-10-07

### ✨ Nuevas características


- **Snippets de IMAGEN**: Soporte completo para copiar/pegar imágenes
  - Almacenamiento en Base64 en la base de datos
  - Preview en el manager
  - Copy directo al clipboard usando Electron `nativeImage`	ext
  - Diferenciación visual en la paleta (🖼️ vs 📝)

- **Miniaturas para HTML**: Los snippets TEXT con HTML pueden tener preview thumbnails
- **Mensajes mejorados**: Clarificación de cuándo usar cada tipo de snippet

### 🔧 Mejoras técnicas


- Migración de base de datos: agregado `snippet_type` e `image_data`	ext
- Refactorización del handler `expand-snippet` para detectar tipo

- Logging mejorado para debugging
- Script de mantenimiento de base de datos (`scripts/db_maintenance.py`)

### 🧹 Limpieza


- Eliminados endpoints de sincronización móvil (sin uso)
- Consolidada documentación (5 docs principales vs 25 anteriores)

- Eliminados scripts de migración temporales
- README completamente reescrito y actualizado

- Estructura de proyecto más clara

### 🐛 Fixes


- Eliminación automática de snippets vacíos que causaban Error 400
- Corrección de detección de tipo en expansión

- Mejorada gestión de procesos de Electron

## [0.1.0] - 2025-01-XX

### ✨ Release inicial


- Paleta global con `Ctrl+Space`	ext
- Expansión por abreviatura (`;abrev` + Enter)

- Editor WYSIWYG con Quill.js
- Variables dinámicas en templates

- Export/Import de snippets
- API REST con FastAPI

- Aplicación Electron multiplataforma
- Base de datos SQLite local

- Sistema de tags y búsqueda

---

**Formato**: [Major.Minor.Patch]

- **Major**: Cambios incompatibles en la API
- **Minor**: Nuevas funcionalidades compatibles

- **Patch**: Corrección de bugs
