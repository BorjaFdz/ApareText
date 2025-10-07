# 🎮 Guía de Uso - ApareText

## ✅ Aplicación Funcionando

La aplicación ApareText está ahora ejecutándose en segundo plano.

---

## 🎯 Cómo Usar

### 1. **Command Palette (Ctrl+Space)**

**Abrir paleta:**
1. Presiona `Ctrl+Space` en cualquier momento
2. Aparece ventana de búsqueda flotante
3. Escribe parte del nombre del snippet (ej: "firma", "lorem")
4. Usa ↑↓ para navegar
5. Presiona `Enter` para insertar

**Ejemplo:**
```
Ctrl+Space → escribe "firma" → Enter
→ Se inserta la firma completa
```

---

### 2. **Expansión de Abreviaturas (Tab)**

**Expandir snippet:**
1. Abre cualquier aplicación (Notepad, VS Code, navegador, etc.)
2. Escribe la abreviatura: `;firma`
3. Presiona `Tab`
4. La abreviatura se borra y se inserta el contenido

**Snippets disponibles:**

| Abreviatura | Descripción | Tiene Variables |
|-------------|-------------|-----------------|
| `;firma` | Firma Email Profesional | No |
| `;hola` | Saludo con Nombre | Sí (nombre) |
| `;meeting` | Notas de Reunión | Sí (participantes) |
| `;soporteok` | Respuesta de Soporte | Sí (nombre, ticket, tiempo) |
| `;tweet` | Tweet Producto | Sí (7 variables) |
| `;lgtm` | Code Review LGTM | Sí (comentario) |
| `;fecha` | Fecha y Hora Actual | No |
| `;lorem` | Lorem Ipsum | No |
| `;gracias` | Respuesta Rápida | No |
| `;htmlemail` | Email HTML | Sí (5 variables) |

**Prueba rápida:**
1. Abre Notepad (Win+R → `notepad` → Enter)
2. Escribe: `;fecha`
3. Presiona `Tab`
4. ¡Verás la fecha y hora actual!

---

### 3. **System Tray Icon**

**Menú de opciones:**
1. Busca el icono de ApareText en la bandeja del sistema (abajo a la derecha)
2. Click derecho para ver el menú:
   - **Settings:** Configuración (en desarrollo)
   - **Pause/Resume:** Pausar temporalmente la app
   - **Quit:** Salir de ApareText

**Pausar la app:**
- Útil si quieres desactivar temporalmente los hotkeys
- Click derecho en tray → Pause
- Para reactivar: Click derecho → Resume

---

## 🔧 Snippets con Variables

Algunos snippets tienen variables (`;hola`, `;meeting`, etc.).

**Estado actual:**
- ✅ Se detectan correctamente
- ⚠️ Formulario de variables pendiente
- Actualmente muestra mensaje: "Snippet has variables (form not yet implemented)"

**Snippets sin variables funcionan perfectamente:**
- `;firma`
- `;fecha`
- `;lorem`
- `;gracias`

---

## 🎨 Funciones en Templates

Algunos snippets usan funciones dinámicas:

### `;fecha` - Fecha y Hora Actual
```
Fecha: {{date:%Y-%m-%d}}
Hora: {{time:%H:%M:%S}}
```

**Resultado:**
```
Fecha: 2025-10-07
Hora: 14:23:45
```

---

## 🌐 Snippets con Scope (Contexto)

Algunos snippets están limitados a ciertos sitios web:

- **`;tweet`** → Solo en twitter.com, x.com
- **`;lgtm`** → Solo en github.com, gitlab.com, bitbucket.org

**Nota:** Filtrado por scope aún no implementado, todos los snippets están disponibles en todas partes.

---

## 🐛 Problemas Conocidos

### ⚠️ 1. System Tray Sin Icono Visual
**Síntoma:** Warning "No Icon set"
**Impacto:** El tray funciona pero sin icono
**Solución:** Pendiente crear archivo icon.ico

### ⚠️ 2. Formulario de Variables
**Síntoma:** Snippets con variables no se expanden
**Impacto:** No puedes usar `;hola`, `;meeting`, etc.
**Solución:** Pendiente implementar formulario Qt

### ⚠️ 3. Cursor puede quedar en Reloj
**Síntoma:** Cursor se congela brevemente al iniciar
**Causa:** Inicialización de hotkeys/detector
**Solución:** ✅ SOLUCIONADO - Ahora se inicializa en background

---

## 💡 Tips de Uso

### **1. Prueba Primero los Snippets Simples**
- `;firma` ✅
- `;fecha` ✅
- `;lorem` ✅
- `;gracias` ✅

### **2. Usa Ctrl+Space para Descubrir**
- Presiona Ctrl+Space
- Escribe palabras clave: "email", "fecha", "code"
- Explora los snippets disponibles

### **3. Tab es la Tecla Mágica**
- Escribe abreviatura
- Presiona Tab (no Space ni Enter)
- Disfruta la expansión automática

### **4. Prueba en Diferentes Apps**
- Notepad ✅
- VS Code ✅
- Navegador ✅
- Word ✅
- Cualquier input de texto

---

## 🚀 Comandos Útiles

### **Reiniciar Aplicación**
Si algo falla, reinicia:
1. Click derecho en tray → Quit
2. Ejecuta de nuevo:
```bash
python -m desktop.main
```

### **Ver Logs**
Los mensajes se muestran en la terminal donde ejecutaste la app.

### **Detener Aplicación**
- Opción 1: Click derecho en tray → Quit
- Opción 2: `Ctrl+C` en la terminal

---

## 📊 Estado Actual

### ✅ Funcional
- Command Palette (Ctrl+Space)
- Expansión simple (sin variables)
- Detección de abreviaturas
- System tray
- 10 snippets de ejemplo
- Funciones en templates ({{date}}, {{time}})

### 🔜 Pendiente
- Formulario de variables
- Icono de system tray
- Filtrado por scope (app/domain)
- Settings window completa

---

## 🎉 ¡Disfruta ApareText!

La aplicación está lista para usar. Prueba expandir algunos snippets y aumenta tu productividad.

**¿Dudas o problemas?**
- Revisa la terminal para ver mensajes de debug
- Los snippets se guardan en: `~/.aparetext/aparetext.db`
- La configuración se carga automáticamente

**¡Feliz expansión de texto!** 🚀
