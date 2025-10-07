"""
Script para crear snippets de ejemplo en ApareText.
Ejecutar una vez para popular la base de datos con snippets de demostración.
"""

import sys
from datetime import datetime

from core.database import get_db
from core.models import Snippet, SnippetVariable, ScopeType, VariableType
from core.snippet_manager import SnippetManager

print("=" * 60)
print("📝 ApareText - Crear Snippets de Ejemplo")
print("=" * 60)
print()

# Inicializar
db = get_db()
manager = SnippetManager(db)

# Verificar cuántos snippets existen
existing = manager.get_all_snippets()
print(f"Snippets existentes: {len(existing)}")

if len(existing) > 0:
    response = input("¿Deseas agregar más snippets de ejemplo? (s/n): ")
    if response.lower() != 's':
        print("Cancelado.")
        sys.exit(0)

print()
print("Creando snippets de ejemplo...")
print()

# 1. Firma de Email Simple
snippet1 = Snippet(
    name="Firma Email Profesional",
    abbreviation=";firma",
    tags=["email", "trabajo", "firma"],
    content_text="""Saludos cordiales,

Juan Pérez
CEO, MiEmpresa
juan.perez@miempresa.com
+34 600 123 456
www.miempresa.com""",
    is_rich=False,
    scope_type=ScopeType.GLOBAL,
)
created1 = manager.create_snippet(snippet1)
print(f"✅ {created1.name} (;firma)")

# 2. Saludo de Email con Variables
snippet2 = Snippet(
    name="Saludo Email con Nombre",
    abbreviation=";hola",
    tags=["email", "saludo"],
    content_text="""Hola {{nombre}},

Espero que te encuentres bien. {{|}}

Saludos,""",
    is_rich=False,
    scope_type=ScopeType.GLOBAL,
    variables=[
        SnippetVariable(
            key="nombre",
            label="Nombre del destinatario",
            type=VariableType.TEXT,
            placeholder="Ej: María",
            required=True,
        )
    ],
)
created2 = manager.create_snippet(snippet2)
print(f"✅ {created2.name} (;hola)")

# 3. Meeting Notes
snippet3 = Snippet(
    name="Plantilla de Notas de Reunión",
    abbreviation=";meeting",
    tags=["trabajo", "reuniones", "productividad"],
    content_text="""# Notas de Reunión - {{date:%Y-%m-%d}}

**Fecha:** {{date:%d/%m/%Y}}
**Hora:** {{time:%H:%M}}
**Participantes:** {{participantes}}

## Agenda
{{|}}

## Acuerdos Tomados


## Próximos Pasos


## Notas Adicionales

""",
    is_rich=False,
    scope_type=ScopeType.GLOBAL,
    variables=[
        SnippetVariable(
            key="participantes",
            label="Participantes de la reunión",
            type=VariableType.TEXT,
            placeholder="Ej: Juan, María, Carlos",
            required=True,
        )
    ],
)
created3 = manager.create_snippet(snippet3)
print(f"✅ {created3.name} (;meeting)")

# 4. Respuesta de Soporte
snippet4 = Snippet(
    name="Respuesta de Soporte - Recibido",
    abbreviation=";soporteok",
    tags=["soporte", "cliente", "email"],
    content_text="""Hola {{nombre}},

Hemos recibido tu solicitud de soporte (Ticket #{{ticket}}).

Nuestro equipo está revisando tu caso y te responderemos en un máximo de {{tiempo}} horas hábiles.

Si tienes alguna pregunta adicional, no dudes en responder a este email.

Gracias por tu paciencia.

Atentamente,
Equipo de Soporte""",
    is_rich=False,
    scope_type=ScopeType.GLOBAL,
    variables=[
        SnippetVariable(
            key="nombre",
            label="Nombre del cliente",
            type=VariableType.TEXT,
            required=True,
        ),
        SnippetVariable(
            key="ticket",
            label="Número de ticket",
            type=VariableType.TEXT,
            placeholder="Ej: 12345",
            required=True,
        ),
        SnippetVariable(
            key="tiempo",
            label="Tiempo de respuesta",
            type=VariableType.NUMBER,
            default_value="24",
            required=False,
        ),
    ],
)
created4 = manager.create_snippet(snippet4)
print(f"✅ {created4.name} (;soporteok)")

# 5. Tweet de Lanzamiento de Producto
snippet5 = Snippet(
    name="Tweet - Lanzamiento de Producto",
    abbreviation=";tweet",
    tags=["twitter", "social media", "marketing"],
    content_text="""🚀 ¡Lanzamos {{producto}}!

{{descripcion}}

✨ Características principales:
• {{feature1}}
• {{feature2}}
• {{feature3}}

🔗 Más info: {{url}}

#{{hashtag}} #ProductLaunch{{|}}""",
    is_rich=False,
    scope_type=ScopeType.DOMAINS,
    scope_values=["twitter.com", "x.com"],
    variables=[
        SnippetVariable(key="producto", label="Nombre del producto", type=VariableType.TEXT, required=True),
        SnippetVariable(key="descripcion", label="Descripción corta", type=VariableType.TEXT, required=True),
        SnippetVariable(key="feature1", label="Característica 1", type=VariableType.TEXT, required=True),
        SnippetVariable(key="feature2", label="Característica 2", type=VariableType.TEXT, required=True),
        SnippetVariable(key="feature3", label="Característica 3", type=VariableType.TEXT, required=True),
        SnippetVariable(key="url", label="URL del producto", type=VariableType.TEXT, required=True),
        SnippetVariable(key="hashtag", label="Hashtag principal", type=VariableType.TEXT, placeholder="Sin #", required=True),
    ],
)
created5 = manager.create_snippet(snippet5)
print(f"✅ {created5.name} (;tweet)")

# 6. Code Review Comment
snippet6 = Snippet(
    name="Code Review - Looks Good",
    abbreviation=";lgtm",
    tags=["code", "review", "github"],
    content_text="""✅ LGTM (Looks Good To Me)

Revisé los cambios y todo se ve bien. El código es claro y sigue nuestras convenciones.

{{comentario}}

Aprobado para merge. 🚀""",
    is_rich=False,
    scope_type=ScopeType.DOMAINS,
    scope_values=["github.com", "gitlab.com", "bitbucket.org"],
    variables=[
        SnippetVariable(
            key="comentario",
            label="Comentario adicional (opcional)",
            type=VariableType.TEXT,
            placeholder="Ej: Excelente trabajo en el refactor",
            required=False,
        )
    ],
)
created6 = manager.create_snippet(snippet6)
print(f"✅ {created6.name} (;lgtm)")

# 7. Fecha y Hora Actual
snippet7 = Snippet(
    name="Fecha y Hora Actual",
    abbreviation=";fecha",
    tags=["fecha", "utilidad"],
    content_text="""{{date:%d/%m/%Y}} - {{time:%H:%M}}{{|}}""",
    is_rich=False,
    scope_type=ScopeType.GLOBAL,
)
created7 = manager.create_snippet(snippet7)
print(f"✅ {created7.name} (;fecha)")

# 8. Lorem Ipsum
snippet8 = Snippet(
    name="Lorem Ipsum - Párrafo",
    abbreviation=";lorem",
    tags=["placeholder", "texto", "diseño"],
    content_text="""Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.{{|}}""",
    is_rich=False,
    scope_type=ScopeType.GLOBAL,
)
created8 = manager.create_snippet(snippet8)
print(f"✅ {created8.name} (;lorem)")

# 9. Respuesta Rápida - Gracias
snippet9 = Snippet(
    name="Respuesta Rápida - Gracias",
    abbreviation=";gracias",
    tags=["respuesta", "email", "cortesía"],
    content_text="""¡Muchas gracias por tu mensaje!

Lo revisaré y te responderé pronto.

Saludos,{{|}}""",
    is_rich=False,
    scope_type=ScopeType.GLOBAL,
)
created9 = manager.create_snippet(snippet9)
print(f"✅ {created9.name} (;gracias)")

# 10. HTML Email Template
snippet10 = Snippet(
    name="HTML Email - Plantilla Básica",
    abbreviation=";htmlemail",
    tags=["html", "email", "template"],
    content_html="""<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <h2 style="color: #333;">{{titulo}}</h2>
    
    <p>Hola {{nombre}},</p>
    
    <p>{{mensaje}}</p>
    
    <div style="background: #f5f5f5; padding: 15px; margin: 20px 0; border-left: 4px solid #4a9eff;">
        <strong>{{destacado}}</strong>
    </div>
    
    <p>Saludos cordiales,<br>
    <strong>{{firma}}</strong></p>
</div>{{|}}""",
    is_rich=True,
    scope_type=ScopeType.GLOBAL,
    variables=[
        SnippetVariable(key="titulo", label="Título del email", type=VariableType.TEXT, required=True),
        SnippetVariable(key="nombre", label="Nombre del destinatario", type=VariableType.TEXT, required=True),
        SnippetVariable(key="mensaje", label="Mensaje principal", type=VariableType.TEXT, required=True),
        SnippetVariable(key="destacado", label="Texto destacado", type=VariableType.TEXT, required=False),
        SnippetVariable(key="firma", label="Firma", type=VariableType.TEXT, default_value="El Equipo", required=False),
    ],
)
created10 = manager.create_snippet(snippet10)
print(f"✅ {created10.name} (;htmlemail)")

print()
print("=" * 60)
print(f"✅ ¡{10} snippets de ejemplo creados exitosamente!")
print("=" * 60)
print()

# Mostrar resumen
all_snippets = manager.get_all_snippets()
print(f"Total de snippets en la base de datos: {len(all_snippets)}")
print()
print("Snippets disponibles:")
for snippet in all_snippets:
    abbr = f"({snippet.abbreviation})" if snippet.abbreviation else ""
    scope_indicator = ""
    if snippet.scope_type == ScopeType.DOMAINS:
        scope_indicator = f" [🌐 {', '.join(snippet.scope_values[:2])}]"
    elif snippet.scope_type == ScopeType.APPS:
        scope_indicator = f" [📱 {', '.join(snippet.scope_values[:2])}]"
    
    print(f"  • {snippet.name} {abbr}{scope_indicator}")

print()
print("🎉 ¡Listo! Prueba los snippets:")
print("  1. Ejecuta el servidor: python -m server.main")
print("  2. Ve a: http://localhost:46321/docs")
print("  3. Prueba GET /api/snippets para ver todos")
print()
