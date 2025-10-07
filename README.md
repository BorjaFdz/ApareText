# ApareText 🚀

**Text expander con paleta global, expansión por abreviatura e integración con navegador**

ApareText es una herramienta de productividad que te permite escribir más rápido mediante snippets reutilizables con variables, formateo y lógica básica.

## 🎯 Características principales

- ⚡ **Paleta Global**: Atajo de teclado para acceder a tus snippets desde cualquier aplicación
- 🔤 **Expansión por abreviatura**: Escribe `;firma` + Tab y se expande automáticamente
- 🌐 **Integración web**: Dashboard y extensión de navegador para usar en cualquier textarea
- 📝 **Variables dinámicas**: Snippets con campos personalizables (`{{nombre}}`, `{{fecha}}`)
- 🎨 **Rich text**: Soporte para HTML y formato enriquecido
- 🎯 **Scopes**: Snippets específicos por aplicación o dominio web
- 💾 **Todo local**: Sin telemetría, tus datos se quedan en tu equipo
- 🔄 **Export/Import**: Respaldo y sincronización de tus snippets en JSON

## 🏗️ Arquitectura del proyecto

Este es un monorepo con los siguientes módulos:

```
ApareText/
├── core/           # Motor de snippets, parser de plantillas, base de datos
├── desktop/        # Aplicación de escritorio (PySide6)
├── server/         # API REST + WebSocket (FastAPI)
├── extension/      # Extensión de navegador (Chrome/Edge/Firefox)
├── docs/           # Documentación
└── tests/          # Tests del proyecto
```

## 🚀 Quick Start

### Requisitos previos

- Python 3.10 o superior
- Node.js 18+ (para la extensión)
- Git

### Instalación de desarrollo

1. **Clonar el repositorio**
```bash
git clone https://github.com/BorjaFdz/ApareText.git
cd ApareText
```

2. **Crear y activar entorno virtual**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
# Todas las dependencias de desarrollo
pip install -e ".[all]"

# O solo las que necesites:
pip install -e ".[core]"      # Motor básico
pip install -e ".[server]"    # API web
pip install -e ".[desktop]"   # App de escritorio
pip install -e ".[dev]"       # Herramientas de desarrollo
```

4. **Ejecutar la aplicación**
```bash
# Dashboard web (http://localhost:46321)
python -m server.main

# Aplicación de escritorio
python -m desktop.main
```

## 📖 Documentación

- [Especificación funcional completa](docs/SPEC.md)
- [Guía de desarrollo](docs/DEVELOPMENT.md)
- [Arquitectura técnica](docs/ARCHITECTURE.md)
- [API Reference](docs/API.md)

## 🛠️ Desarrollo

### Estructura de módulos

#### `core/` - Motor central
- Gestión de snippets y variables
- Parser de plantillas
- Base de datos SQLite
- Export/Import JSON

#### `desktop/` - Aplicación de escritorio
- Paleta global con hotkey
- Detector de abreviaturas
- Inserción de texto (tecleo/clipboard)
- System tray icon
- UI con PySide6

#### `server/` - API y dashboard web
- REST API con FastAPI
- WebSocket para comunicación en tiempo real
- Dashboard web con React/HTMX
- CRUD de snippets

#### `extension/` - Extensión de navegador
- Manifest V3 (Chrome/Edge/Firefox)
- Overlay en páginas web
- Comunicación con servidor local
- Inserción en textarea/contentEditable

### Comandos útiles

```bash
# Formatear código
black core/ server/ desktop/

# Linter
ruff check core/ server/ desktop/

# Type checking
mypy core/ server/ desktop/

# Tests
pytest

# Tests con cobertura
pytest --cov=core --cov=server --cov=desktop --cov-report=html
```

### Pre-commit hooks

```bash
# Instalar pre-commit
pip install pre-commit

# Configurar hooks
pre-commit install

# Ejecutar manualmente
pre-commit run --all-files
```

## 🎯 Roadmap

### MVP (Sprint 1-8)
- [x] Estructura base del proyecto
- [ ] Core: Motor de snippets + SQLite
- [ ] Server: API REST básica
- [ ] Desktop: Paleta global + inserción
- [ ] Desktop: Detector de abreviaturas
- [ ] Core: Variables y formularios
- [ ] Extension: Overlay web + comunicación
- [ ] Desktop: Scopes por app/dominio

### v1.0 (Post-MVP)
- [ ] Sincronización opcional (Dropbox/Drive)
- [ ] Campos avanzados (select, date, checkbox)
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
