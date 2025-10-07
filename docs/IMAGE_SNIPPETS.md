# 🖼️ Guía Completa de Snippets de Tipo IMAGEN

## Introducción

ApareText ahora soporta **dos tipos fundamentales de snippets**:

1. **📝 TEXT (Texto)**: Expande texto (puede ser plain text o HTML)
2. **🖼️ IMAGE (Imagen)**: Guarda imágenes y las copia al portapapeles al escribir la abreviación

Esta guía explica cómo usar los snippets de tipo IMAGEN.

---

## 🎯 ¿Qué es un Snippet de Tipo IMAGEN?

Un snippet de tipo IMAGEN es completamente diferente a un snippet de texto:

- **NO expande texto** - expande una imagen
- **Guarda una imagen** como contenido principal
- **Al escribir la abreviación**, copia la imagen al portapapeles
- **Puedes pegar la imagen** donde necesites (Word, Slack, Discord, etc.)

### Ejemplo de Uso

```
Caso de uso: Firma visual
1. Creas un snippet tipo IMAGEN con abreviación "firma"
2. Subes/pegas tu firma escaneada o diseñada
3. En cualquier app, escribes ;firma
4. La imagen se copia al portapapeles
5. Haces Ctrl+V para pegar tu firma
```

---

## 🚀 Crear un Snippet de Tipo IMAGEN

### Paso 1: Nuevo Snippet

1. Abre el Snippet Manager
2. Haz clic en **"+ Nuevo Snippet"**

### Paso 2: Seleccionar Tipo IMAGEN

En la sección **"Tipo de Snippet"**, selecciona:

```
🖼️ Imagen
Copia imagen al portapapeles
```

Al seleccionar IMAGEN:
- ✅ Se muestra el área de carga de imagen
- ❌ Se oculta el editor de texto

### Paso 3: Configurar el Snippet

**Nombre**: Describe la imagen
```
Ejemplo: "Firma Personal" o "Logo Empresa"
```

**Abreviatura** (opcional pero recomendada):
```
Ejemplo: firma, logo, captura
```
Se mostrará como `;firma` en la paleta

**Tags**: Categoriza tus imágenes
```
Ejemplo: personal, trabajo, diseño
```

### Paso 4: Agregar la Imagen

Tienes **3 opciones** para agregar la imagen:

#### Opción A: Pegar desde Portapapeles

1. Copia una imagen (Ctrl+C sobre cualquier imagen)
2. Haz clic en **"📋 Pegar desde Portapapeles"**
3. La imagen aparecerá en el preview (200x200px)

```
✅ Mejor para: Screenshots, imágenes de internet
```

#### Opción B: Seleccionar Archivo

1. Haz clic en **"📁 Seleccionar Archivo"**
2. Navega a tu archivo de imagen
3. Selecciona PNG, JPG o GIF
4. La imagen se cargará automáticamente

```
✅ Mejor para: Archivos guardados, logos, firmas
```

#### Opción C: Capturar Screenshot (solo para snippets HTML)

```
⚠️ NOTA: Esta opción solo funciona para snippets tipo TEXT con HTML
No está disponible para snippets tipo IMAGEN
```

### Paso 5: Guardar

1. Haz clic en **"💾 Guardar Snippet"**
2. ¡Listo! Tu snippet de imagen está creado

---

## 🎨 Formatos de Imagen Soportados

| Formato | Extensión | Uso Recomendado |
|---------|-----------|-----------------|
| **PNG** | `.png` | Screenshots, transparencias, calidad |
| **JPG** | `.jpg`, `.jpeg` | Fotos, imágenes complejas |
| **GIF** | `.gif` | Animaciones, imágenes simples |

### Recomendaciones de Formato

```
📸 Screenshots → PNG (mejor calidad)
📷 Fotos → JPG (menor tamaño)
🎬 Animaciones → GIF (único formato animado)
✍️ Firmas → PNG (soporta transparencia)
🎨 Logos → PNG (soporta transparencia)
```

---

## 🔄 Usar un Snippet de Tipo IMAGEN

### Método 1: Paleta de Snippets (Recomendado)

1. Presiona `Ctrl+Espacio` (o tu atajo configurado)
2. Escribe `;` seguido de tu abreviación
```
Ejemplo: ;firma
```
3. **La imagen se copia automáticamente al portapapeles**
4. Ve a donde quieras pegar (Word, Slack, Discord, etc.)
5. Presiona `Ctrl+V` para pegar la imagen

### Método 2: Expansión Directa

1. En cualquier aplicación, escribe tu abreviación
```
Ejemplo: ;logo
```
2. **La imagen se copia al portapapeles automáticamente**
3. El texto de la abreviación desaparece
4. Presiona `Ctrl+V` para pegar la imagen

### Comportamiento Importante

```
⚠️ DIFERENCIA CLAVE con snippets de texto:

Snippet TEXT:
;firma → Expande texto en el cursor

Snippet IMAGE:
;firma → Copia imagen al portapapeles
          (necesitas hacer Ctrl+V después)
```

---

## 💡 Casos de Uso Comunes

### 1. Firmas Digitales
```
Abreviación: ;firma
Imagen: Tu firma escaneada o diseñada
Uso: Emails, documentos, contratos
```

### 2. Logos Empresariales
```
Abreviación: ;logo, ;logoempresa
Imagen: Logo en alta resolución con transparencia
Uso: Presentaciones, documentos, emails
```

### 3. Diagramas Frecuentes
```
Abreviación: ;arquitectura, ;flujo
Imagen: Diagramas técnicos que usas seguido
Uso: Documentación, wikis, Confluence
```

### 4. Capturas de Pantalla Recurrentes
```
Abreviación: ;dashboard, ;error404
Imagen: Screenshots que compartes frecuentemente
Uso: Reportes, soporte técnico, documentación
```

### 5. Memes o Imágenes de Respuesta
```
Abreviación: ;ok, ;thumbsup, ;facepalm
Imagen: Reacciones visuales rápidas
Uso: Slack, Discord, Teams
```

### 6. Códigos QR
```
Abreviación: ;qrwifi, ;qrcontacto
Imagen: Códigos QR que compartes
Uso: Presentaciones, emails, documentos
```

---

## 📊 Gestión de Snippets de Imagen

### Ver Snippets de Imagen

En la lista de snippets, los de tipo IMAGEN se identifican por:

- **Icono**: 🖼️ (en lugar de 📝)
- **Borde azul púrpura** en el thumbnail
- **Preview de la imagen** en el thumbnail

### Editar un Snippet de Imagen

1. Haz clic en el snippet en la lista
2. El editor se abrirá en modo IMAGEN
3. Puedes:
   - Cambiar nombre, abreviación, tags
   - Reemplazar la imagen (pegar o seleccionar nueva)
   - Eliminar la imagen
   - Habilitar/deshabilitar

### Duplicar Snippets de Imagen

```
⚠️ NOTA: La función duplicar copiará TODA la imagen
Esto puede resultar en snippets grandes si la imagen es pesada
```

### Eliminar la Imagen

Dentro del editor:
1. Haz clic en **"🗑️ Eliminar Imagen"**
2. La imagen se borra del preview
3. Al guardar, **debes agregar una nueva imagen**

---

## ⚡ Diferencias: TEXT vs IMAGE

| Característica | Snippet TEXT | Snippet IMAGE |
|----------------|--------------|---------------|
| **Contenido** | Texto (plain o HTML) | Imagen (PNG/JPG/GIF) |
| **Expansión** | Inserta texto en cursor | Copia imagen al portapapeles |
| **Editor** | Quill WYSIWYG o textarea | Área de carga de imagen |
| **Thumbnail** | Opcional (solo para HTML) | La imagen ES el contenido |
| **Variables** | ✅ Soportadas | ❌ No soportadas |
| **Preview** | Vista previa del HTML renderizado | Preview de la imagen |
| **Habilitar/Deshabilitar** | ✅ Sí | ✅ Sí |
| **Tags** | ✅ Sí | ✅ Sí |
| **Búsqueda** | ✅ Sí | ✅ Sí |

---

## 🔧 Solución de Problemas

### ❌ "No hay imagen en el portapapeles"

**Problema**: Al intentar pegar desde portapapeles, aparece este error.

**Solución**:
1. Asegúrate de haber copiado una IMAGEN (no texto)
2. Copia la imagen directamente (clic derecho → Copiar imagen)
3. No copies el enlace o ruta, copia la imagen misma
4. Intenta de nuevo con **"📋 Pegar desde Portapapeles"**

### ❌ "Formato no soportado"

**Problema**: Al seleccionar archivo, aparece este error.

**Solución**:
1. Verifica que el archivo sea PNG, JPG o GIF
2. Formatos NO soportados: BMP, TIFF, SVG, WEBP
3. Convierte la imagen a PNG o JPG usando Paint o similar
4. Intenta cargar de nuevo

### ❌ "Por favor, agrega una imagen para el snippet"

**Problema**: Al guardar, aparece este error.

**Solución**:
1. Un snippet tipo IMAGEN **requiere** una imagen
2. Agrega una imagen usando alguno de los 3 métodos:
   - Pegar desde portapapeles
   - Seleccionar archivo
3. Verifica que el preview muestre la imagen
4. Guarda de nuevo

### ❌ La imagen no se pega donde quiero

**Problema**: Después de usar el snippet, la imagen no aparece.

**Solución**:
1. Recuerda: los snippets IMAGE **copian al portapapeles**
2. Después de escribir `;firma`, debes hacer **Ctrl+V**
3. Verifica que la aplicación de destino soporte imágenes
   - ✅ Word, Slack, Discord, Notion, etc.
   - ❌ Notepad, editores de texto plano
4. Si no funciona, verifica que el snippet esté **habilitado** (✓)

### ⚠️ La imagen se ve borrosa

**Problema**: La imagen pegada se ve con mala calidad.

**Solución**:
1. Usa imágenes de mayor resolución
2. Prefiere PNG sobre JPG para capturas de pantalla
3. Evita redimensionar imágenes pequeñas a grande
4. Usa imágenes originales sin compresión

---

## 📈 Estadísticas y Analíticas

Los snippets de tipo IMAGEN también se rastrean en las estadísticas:

- ✅ Contador de uso
- ✅ Tiempo ahorrado estimado
- ✅ Racha de días de uso
- ✅ Insights de productividad

---

## 🎓 Mejores Prácticas

### 1. Nombres Descriptivos

```
✅ BUENO:
- "Logo Empresa Transparente"
- "Firma Digital John Doe"
- "Diagrama Arquitectura V2"

❌ MALO:
- "Imagen 1"
- "Sin título"
- "Screenshot"
```

### 2. Abreviaturas Memorables

```
✅ BUENO:
- ;firma
- ;logo
- ;qrwifi

❌ MALO:
- ;img1
- ;x
- ;asdfgh
```

### 3. Organización con Tags

```
Usa tags consistentes:
- trabajo, personal
- diseño, capturas, logos
- documentación, presentaciones
```

### 4. Habilitar/Deshabilitar según contexto

```
Snippet: "Logo Cliente X"
- Habilitar: Cuando trabajas en proyecto del cliente
- Deshabilitar: Cuando cambias a otro cliente
```

### 5. Optimiza el Tamaño de Imagen

```
📏 Tamaños recomendados:
- Logos: 512x512px o menos
- Firmas: 300x100px aprox
- Screenshots: 1920x1080px máximo
- QR Codes: 256x256px o 512x512px
```

---

## 🔮 Próximas Características (Roadmap)

Funcionalidades planeadas para snippets IMAGE:

- [ ] Soporte para múltiples imágenes por snippet
- [ ] Editor de imagen integrado (recortar, rotar)
- [ ] Optimización automática de tamaño
- [ ] Conversión de formato automática
- [ ] Sincronización de imágenes entre dispositivos
- [ ] Galería de imágenes prediseñadas

---

## 📞 Soporte

¿Problemas con snippets de imagen?

1. Revisa esta guía completa
2. Verifica la sección "Solución de Problemas"
3. Consulta los logs de la aplicación
4. Reporta bugs en el repositorio

---

## 🎉 Conclusión

Los snippets de tipo IMAGEN son una herramienta poderosa para:

✅ **Ahorrar tiempo** compartiendo imágenes frecuentes
✅ **Mantener consistencia** con logos, firmas, etc.
✅ **Agilizar comunicación** con respuestas visuales rápidas
✅ **Centralizar recursos visuales** en un solo lugar

**¡Empieza a crear tus snippets de imagen hoy!** 🚀
