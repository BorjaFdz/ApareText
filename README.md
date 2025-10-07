# ApareText 🚀# ApareText 🚀



**Text expander ultrarrápido con paleta global y snippets de imágenes****Text expander ultrarrápido con paleta global y snippets de imágenes**



ApareText es una herramienta de productividad que te permite escribir más rápido mediante snippets reutilizables con variables, formateo rico y copiar imágenes al instante.ApareText es una herramienta de productividad que te permite escribir más rápido mediante snippets reutilizables con variables, formateo rico y copiar imágenes al instante.



## 🎯 Características principales## 🎯 Características principales



- ⚡ **Paleta Global**: `Ctrl+Space` para acceder a tus snippets desde cualquier aplicación- ⚡ **Paleta Global**: `Ctrl+Space` para acceder a tus snippets desde cualquier aplicación

- 🔤 **Expansión inteligente**: Escribe `;firma` y presiona Enter para expandir automáticamente- 🔤 **Expansión inteligente**: Escribe `;firma` y presiona Enter para expandir automáticamente

- 🖼️ **Snippets de imágenes**: Guarda y pega imágenes completas con un solo atajo- 🖼️ **Snippets de imágenes**: Guarda y pega imágenes completas con un solo atajo

- 📝 **Variables dinámicas**: Snippets con campos personalizables (`{{nombre}}`, `{{fecha}}`)- 📝 **Variables dinámicas**: Snippets con campos personalizables (`{{nombre}}`, `{{fecha}}`)

- 🎨 **Rich text**: Soporte completo para HTML y formato enriquecido con miniaturas- 🎨 **Rich text**: Soporte completo para HTML y formato enriquecido con miniaturas

- 💾 **100% Local**: Sin telemetría, sin cloud, tus datos nunca salen de tu equipo- 💾 **100% Local**: Sin telemetría, sin cloud, tus datos nunca salen de tu equipo

- 🔄 **Export/Import**: Respaldo y sincronización de tus snippets en JSON- 🔄 **Export/Import**: Respaldo y sincronización de tus snippets en JSON

- 🎯 **Búsqueda instantánea**: Encuentra snippets por nombre, abreviatura o contenido- � **Búsqueda instantánea**: Encuentra snippets por nombre, abreviatura o contenido



## 🏗️ Arquitectura## 🏗️ Arquitectura del proyecto



```text```

ApareText/ApareText/

├── core/           # Motor de snippets, parser de plantillas, base de datos SQLite├── core/           # Motor de snippets, parser de plantillas, base de datos SQLite

├── electron-app/   # Aplicación de escritorio (Electron 27+)├── electron-app/   # Aplicación de escritorio (Electron 27+)

├── server/         # API REST (FastAPI + Uvicorn)├── server/         # API REST (FastAPI + Uvicorn)

├── scripts/        # Utilidades de mantenimiento├── scripts/        # Utilidades de mantenimiento

├── docs/           # Documentación técnica y guías├── docs/           # Documentación técnica y guías

└── tests/          # Tests del proyecto└── tests/          # Tests del proyecto

``````



## 🚀 Instalación y uso## 🚀 Quick Start



### Requisitos### Requisitos previos



- **Python 3.10+** para el backend- Python 3.10 o superior

- **Node.js 18+** para Electron- Node.js 18+ (para la extensión)

- **Windows 10/11** (soporte para otros OS en desarrollo)- Git



### Instalación rápida### Instalación de desarrollo



1. **Clonar el repositorio**1. **Clonar el repositorio**

```bash

   ```bashgit clone https://github.com/BorjaFdz/ApareText.git

   git clone https://github.com/BorjaFdz/ApareText.gitcd ApareText

   cd ApareText```

   ```

2. **Crear y activar entorno virtual**

2. **Configurar entorno Python**```bash

python -m venv venv

   ```bash

   python -m venv venv# Windows

   venv\Scripts\activate  # Windowsvenv\Scripts\activate

   pip install -e .

   ```# macOS/Linux

source venv/bin/activate

3. **Instalar dependencias de Electron**```



   ```bash3. **Instalar dependencias**

   cd electron-app```bash

   npm install# Todas las dependencias de desarrollo

   cd ..pip install -e ".[all]"

   ```

# O solo las que necesites:

4. **Iniciar la aplicación**pip install -e ".[core]"      # Motor básico

pip install -e ".[server]"    # API web

   ```bashpip install -e ".[desktop]"   # App de escritorio

   # Terminal 1: Iniciar API backendpip install -e ".[dev]"       # Herramientas de desarrollo

   python -m uvicorn server.api:app --host 127.0.0.1 --port 46321```



   # Terminal 2: Iniciar aplicación Electron4. **Ejecutar la aplicación**

   cd electron-app```bash

   npm start# Dashboard web (http://localhost:46321)

   ```python -m server.main



### Uso básico# Aplicación de escritorio

python -m desktop.main

1. **Crear un snippet TEXT**:```

   - La ventana del Manager se abre automáticamente

   - Haz clic en "+ Nuevo Snippet"## 📖 Documentación

   - Selecciona tipo **📝 TEXTO**

   - Escribe el nombre y abreviatura (ej: "Firma Email", `;firma`)- [Especificación funcional completa](docs/SPEC.md)

   - Escribe o pega tu contenido- [Guía de desarrollo](docs/DEVELOPMENT.md)

   - Haz clic en "💾 Guardar Snippet"- [Arquitectura técnica](docs/ARCHITECTURE.md)

- [API Reference](docs/API.md)

2. **Crear un snippet IMAGE**:

   - Haz clic en "+ Nuevo Snippet"## 🛠️ Desarrollo

   - Selecciona tipo **🖼️ IMAGEN**

   - Copia una imagen (Ctrl+C en cualquier lugar)### Estructura de módulos

   - Haz clic en "📋 Pegar desde Portapapeles"

   - Verás la preview de la imagen#### `core/` - Motor central

   - Haz clic en "💾 Guardar Snippet"- Gestión de snippets y variables

- Parser de plantillas

3. **Usar snippets**:- Base de datos SQLite

   - Presiona `Ctrl+Space` en cualquier aplicación- Export/Import JSON

   - Escribe `;` seguido de la abreviatura (ej: `;firma`)

   - Presiona Enter#### `desktop/` - Aplicación de escritorio

   - **TEXT**: Se copia al clipboard y se inserta en el cursor- Paleta global con hotkey

   - **IMAGE**: Se copia la imagen al clipboard (pega con Ctrl+V)- Detector de abreviaturas

- Inserción de texto (tecleo/clipboard)

## 🛠️ Mantenimiento- System tray icon

- UI con PySide6

### Verificar integridad de la base de datos

#### `server/` - API y dashboard web

```bash- REST API con FastAPI

python scripts/db_maintenance.py --check- WebSocket para comunicación en tiempo real

```- Dashboard web con React/HTMX

- CRUD de snippets

### Limpiar snippets vacíos

#### `extension/` - Extensión de navegador

```bash- Manifest V3 (Chrome/Edge/Firefox)

python scripts/db_maintenance.py --clean-empty- Overlay en páginas web

```- Comunicación con servidor local

- Inserción en textarea/contentEditable

### Ver estadísticas

### Comandos útiles

```bash

python scripts/db_maintenance.py --stats```bash

```# Formatear código

black core/ server/ desktop/

## 📚 Documentación

# Linter

- **[User Guide](docs/USER_GUIDE.md)**: Guía completa de usuarioruff check core/ server/ desktop/

- **[Image Snippets](docs/IMAGE_SNIPPETS.md)**: Guía de snippets de imágenes

- **[Development](docs/DEVELOPMENT.md)**: Guía para desarrolladores# Type checking

- **[Architecture](docs/ARCHITECTURE.md)**: Arquitectura técnica del sistemamypy core/ server/ desktop/



## 🔧 Tecnologías# Tests

pytest

- **Backend**: Python 3.10, FastAPI, SQLAlchemy, SQLite

- **Frontend**: Electron 27, Quill.js (editor), axios# Tests con cobertura

- **Desktop**: Node.js, IPC, Global Shortcuts, Clipboard APIpytest --cov=core --cov=server --cov=desktop --cov-report=html

```

## 🤝 Contribuir

### Pre-commit hooks

Las contribuciones son bienvenidas. Por favor:

```bash

1. Fork el proyecto# Instalar pre-commit

2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)pip install pre-commit

3. Commit tus cambios (`git commit -m 'Add: AmazingFeature'`)

4. Push a la rama (`git push origin feature/AmazingFeature`)# Configurar hooks

5. Abre un Pull Requestpre-commit install



## 📝 Licencia# Ejecutar manualmente

pre-commit run --all-files

Este proyecto está bajo la licencia MIT. Ver `LICENSE` para más detalles.```



## 👤 Autor## 🎯 Roadmap



**Borja Fernández**### MVP (Sprint 1-8)

- [x] Estructura base del proyecto

- GitHub: [@BorjaFdz](https://github.com/BorjaFdz)- [ ] Core: Motor de snippets + SQLite

- [ ] Server: API REST básica

## 🙏 Agradecimientos- [ ] Desktop: Paleta global + inserción

- [ ] Desktop: Detector de abreviaturas

- Quill.js por el excelente editor WYSIWYG- [ ] Core: Variables y formularios

- FastAPI por el framework ultra rápido- [ ] Extension: Overlay web + comunicación

- Electron por hacer posible las apps de escritorio multiplataforma- [ ] Desktop: Scopes por app/dominio



---### v1.0 (Post-MVP)

- [ ] Sincronización opcional (Dropbox/Drive)

**ApareText** - Escribe más rápido, trabaja más inteligente ⚡- [ ] Campos avanzados (select, date, checkbox)

- [ ] Plantillas condicionales
- [ ] Funciones avanzadas (contador, clipboard history)
- [ ] Analítica local de uso
- [ ] Multilenguaje (ES/EN)
- [ ] Tema claro/oscuro

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Tests de un módulo específico
pytest tests/core/
pytest tests/server/
pytest tests/desktop/

# Con cobertura
pytest --cov --cov-report=html
```

## 📦 Build y distribución

```bash
# Build con PyInstaller
pyinstaller --onefile --windowed desktop/main.py

# Build con Nuitka (más rápido)
python -m nuitka --standalone --onefile desktop/main.py
```

## 🤝 Contribuir

Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

MIT License - ver [LICENSE](LICENSE) para más detalles

## 🔒 Privacidad y seguridad

- ✅ Todo funciona localmente por defecto
- ✅ Sin telemetría ni conexiones externas
- ✅ Tus snippets nunca salen de tu equipo
- ✅ Sincronización opcional y bajo tu control
- ✅ Código abierto y auditable

## 💬 Soporte

- 📧 Email: [Crear issue en GitHub](https://github.com/BorjaFdz/ApareText/issues)
- 📚 Documentación: [Wiki del proyecto](https://github.com/BorjaFdz/ApareText/wiki)

## 🙏 Agradecimientos

Inspirado por herramientas como TextExpander, espanso, y Alfred.

---

**Hecho con ❤️ para aumentar tu productividad**
