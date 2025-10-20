"""
API REST con FastAPI.
"""

from datetime import datetime
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from server.config import CORS_ORIGINS

# NOTE: avoid importing heavy core modules (SQLAlchemy, Pydantic models) at module import time.
# Import them lazily in handlers to reduce startup/import overhead of the frozen binary.


# Lightweight API Pydantic models (used for request/response typing in handlers)
class APISnippetVariable(BaseModel):
    id: str | None = None
    snippet_id: str | None = None
    key: str
    label: str | None = None
    type: str = "text"
    placeholder: str | None = None
    default_value: str | None = None
    required: bool = False
    regex: str | None = None
    options: list[str] | None = None


class APISnippet(BaseModel):
    id: str | None = None
    name: str
    abbreviation: str | None = None
    snippet_type: str = "text"
    tags: list[str] = []
    content_text: str | None = None
    content_html: str | None = None
    is_rich: bool = False
    image_data: str | None = None
    scope_type: str = "global"
    scope_values: list[str] = []
    caret_marker: str = "{{|}}"
    variables: list[APISnippetVariable] = []
    usage_count: int = 0
    enabled: bool = True
    created_at: str | None = None
    updated_at: str | None = None


class APISnippetVersion(BaseModel):
    id: str | None = None
    snippet_id: str
    version_number: int
    name: str
    abbreviation: str | None = None
    snippet_type: str = "text"
    tags: list[str] = []
    category: str | None = None
    content_text: str | None = None
    content_html: str | None = None
    is_rich: bool = False
    image_data: str | None = None
    thumbnail: str | None = None
    scope_type: str = "global"
    scope_values: list[str] = []
    caret_marker: str = "{{|}}"
    enabled: bool = True
    created_at: str | None = None
    change_reason: str | None = None
    variables: list[APISnippetVariable] = []


def get_snippet_manager():
    """Lazy import of SnippetManager and Database to avoid import-time DB initialization."""
    from core.database import get_db
    from core.snippet_manager import SnippetManager

    db = get_db()
    return SnippetManager(db)


def get_parser():
    """Lazy import of TemplateParser."""
    from core.template_parser import TemplateParser

    return TemplateParser()

# Crear app
app = FastAPI(
    title="ApareText API",
    description="API REST para gestión de snippets",
    version="0.1.0",
)

# CORS - permitir solo localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS + [
        "chrome-extension://*",
        "moz-extension://*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependencias
# Use the lazy helpers defined earlier (`get_snippet_manager` and `get_parser`) to avoid
# importing heavy modules at import time. The lightweight variants are defined above.


# Modelos de request/response
class SnippetCreate(BaseModel):
    """Request para crear snippet."""

    name: str
    abbreviation: Optional[str] = None
    snippet_type: str = "text"  # 'text' o 'image'
    tags: list[str] = []
    content_text: Optional[str] = None
    content_html: Optional[str] = None
    is_rich: bool = False
    image_data: Optional[str] = None  # Base64 image data para snippets tipo IMAGE
    scope_type: str = "global"
    scope_values: list[str] = []
    variables: list[APISnippetVariable] = []


class SnippetUpdate(BaseModel):
    """Request para actualizar snippet."""

    name: Optional[str] = None
    abbreviation: Optional[str] = None
    snippet_type: Optional[str] = None  # 'text' o 'image'
    tags: Optional[list[str]] = None
    content_text: Optional[str] = None
    content_html: Optional[str] = None
    is_rich: Optional[bool] = None
    image_data: Optional[str] = None  # Base64 image data para snippets tipo IMAGE
    scope_type: Optional[str] = None
    scope_values: Optional[list[str]] = None
    variables: Optional[list[APISnippetVariable]] = None
    enabled: Optional[bool] = None


class SnippetExpand(BaseModel):
    """Request para expandir snippet."""

    snippet_id: str
    variables: dict[str, Any] = {}
    source: Optional[str] = None
    target_app: Optional[str] = None
    target_domain: Optional[str] = None


class SnippetExpandResponse(BaseModel):
    """Response de expansión."""

    content: str
    cursor_position: int
    is_rich: bool


# Health check
@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "ApareText API", "version": "0.1.0"}


@app.get("/health")
async def health():
    """Health check detallado."""
    # Lazy: avoid importing core modules at import-time
    manager = get_snippet_manager()
    snippets = manager.get_all_snippets()

    return {
        "status": "healthy",
        "database": "connected",
        "snippets_count": len(snippets),
    }


# CRUD Snippets
@app.get("/api/snippets", response_model=list[APISnippet])
async def list_snippets(
    enabled_only: bool = Query(False, description="Filtrar solo snippets habilitados"),
    tags: Optional[str] = Query(None, description="Filtrar por tags (CSV)"),
):
    """Listar todos los snippets."""
    manager = get_snippet_manager()
    snippets = manager.get_all_snippets(enabled_only=enabled_only)

    # Filtrar por tags si se especifica
    if tags:
        tag_list = [t.strip() for t in tags.split(",")]
        snippets = [s for s in snippets if any(tag in s.tags for tag in tag_list)]

    return snippets


@app.get("/api/snippets/{snippet_id}", response_model=APISnippet)
async def get_snippet(snippet_id: str):
    """Obtener snippet por ID."""
    manager = get_snippet_manager()
    snippet = manager.get_snippet(snippet_id)

    if not snippet:
        raise HTTPException(status_code=404, detail="Snippet not found")

    return snippet


@app.post("/api/snippets", response_model=APISnippet, status_code=201)
async def create_snippet(snippet_data: SnippetCreate):
    """Crear nuevo snippet."""
    manager = get_snippet_manager()

    # Lazily import core Pydantic Snippet model and convert
    from core.models import Snippet as CoreSnippet, SnippetVariable as CoreSnippetVariable

    # Convert variables
    core_vars = []
    for v in (snippet_data.variables or []):
        if isinstance(v, dict):
            core_vars.append(CoreSnippetVariable(**v))
        else:
            # APISnippetVariable is a BaseModel; convert via dict
            core_vars.append(CoreSnippetVariable(**v.model_dump()))

    core_snippet = CoreSnippet(
        name=snippet_data.name,
        abbreviation=snippet_data.abbreviation,
        snippet_type=snippet_data.snippet_type,
        tags=snippet_data.tags,
        content_text=snippet_data.content_text,
        content_html=snippet_data.content_html,
        is_rich=snippet_data.is_rich,
        image_data=snippet_data.image_data,
        scope_type=snippet_data.scope_type,
        scope_values=snippet_data.scope_values,
        variables=core_vars,
    )

    created = manager.create_snippet(core_snippet)
    # Return as APISnippet for consistent API schema
    return APISnippet(**created.model_dump())


@app.put("/api/snippets/{snippet_id}", response_model=APISnippet)
async def update_snippet(snippet_id: str, snippet_data: SnippetUpdate):
    """Actualizar snippet existente."""
    manager = get_snippet_manager()

    # Obtener snippet actual
    existing = manager.get_snippet(snippet_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Snippet not found")

    # Actualizar solo campos proporcionados
    update_dict = snippet_data.model_dump(exclude_unset=True)
    
    # Convertir enums y otros tipos especiales
    for key, value in update_dict.items():
        if value is not None:
            # Si es scope_type y viene como string, convertir a ScopeType
            if key == "scope_type" and isinstance(value, str):
                from core.models import ScopeType
                value = ScopeType(value)
            # Si es variables, asegurarse de que sean SnippetVariable objects
            elif key == "variables" and isinstance(value, list):
                from core.models import SnippetVariable
                value = [SnippetVariable(**v) if isinstance(v, dict) else SnippetVariable(**v.model_dump()) for v in value]
            
            setattr(existing, key, value)

    # Actualizar timestamp
    existing.updated_at = datetime.utcnow()
    
    updated = manager.update_snippet(snippet_id, existing)
    return APISnippet(**updated.model_dump())


@app.delete("/api/snippets/{snippet_id}", status_code=204)
async def delete_snippet(snippet_id: str):
    """Eliminar snippet."""
    manager = get_snippet_manager()
    success = manager.delete_snippet(snippet_id)

    if not success:
        raise HTTPException(status_code=404, detail="Snippet not found")

    return None


# Versiones de snippets
@app.get("/api/snippets/{snippet_id}/versions", response_model=list[APISnippetVersion])
async def get_snippet_versions(snippet_id: str):
    """Obtener todas las versiones de un snippet."""
    manager = get_snippet_manager()

    # Verificar que el snippet existe
    snippet = manager.get_snippet(snippet_id)
    if not snippet:
        raise HTTPException(status_code=404, detail="Snippet not found")

    versions = manager.get_snippet_versions(snippet_id)

    # Convertir a formato API
    api_versions = []
    for version in versions:
        api_version = APISnippetVersion(
            id=version.id,
            snippet_id=version.snippet_id,
            version_number=version.version_number,
            name=version.name,
            abbreviation=version.abbreviation,
            snippet_type=version.snippet_type,
            tags=version.tags,
            category=version.category,
            content_text=version.content_text,
            content_html=version.content_html,
            is_rich=version.is_rich,
            image_data=version.image_data,
            thumbnail=version.thumbnail,
            scope_type=version.scope_type,
            scope_values=version.scope_values,
            caret_marker=version.caret_marker,
            enabled=version.enabled,
            created_at=version.created_at.isoformat() if version.created_at else None,
            change_reason=version.change_reason,
            variables=[
                APISnippetVariable(
                    id=var.id,
                    key=var.key,
                    label=var.label,
                    type=var.type,
                    placeholder=var.placeholder,
                    default_value=var.default_value,
                    required=var.required,
                    regex=var.regex,
                    options=var.options,
                )
                for var in version.variables
            ]
        )
        api_versions.append(api_version)

    return api_versions


@app.post("/api/snippets/{snippet_id}/versions/{version_id}/restore", response_model=APISnippet)
async def restore_snippet_version(snippet_id: str, version_id: str):
    """Restaurar un snippet a una versión específica."""
    manager = get_snippet_manager()

    # Verificar que el snippet existe
    snippet = manager.get_snippet(snippet_id)
    if not snippet:
        raise HTTPException(status_code=404, detail="Snippet not found")

    restored_snippet = manager.restore_snippet_version(snippet_id, version_id)
    if not restored_snippet:
        raise HTTPException(status_code=404, detail="Version not found")

    # Convertir a formato API
    return APISnippet(
        id=restored_snippet.id,
        name=restored_snippet.name,
        abbreviation=restored_snippet.abbreviation,
        snippet_type=restored_snippet.snippet_type,
        tags=restored_snippet.tags,
        content_text=restored_snippet.content_text,
        content_html=restored_snippet.content_html,
        is_rich=restored_snippet.is_rich,
        image_data=restored_snippet.image_data,
        scope_type=restored_snippet.scope_type,
        scope_values=restored_snippet.scope_values,
        caret_marker=restored_snippet.caret_marker,
        variables=[
            APISnippetVariable(
                id=var.id,
                key=var.key,
                label=var.label,
                type=var.type,
                placeholder=var.placeholder,
                default_value=var.default_value,
                required=var.required,
                regex=var.regex,
                options=var.options,
            )
            for var in restored_snippet.variables
        ],
        usage_count=restored_snippet.usage_count,
        enabled=restored_snippet.enabled,
        created_at=restored_snippet.created_at.isoformat() if restored_snippet.created_at else None,
        updated_at=restored_snippet.updated_at.isoformat() if restored_snippet.updated_at else None,
    )


# Búsqueda
@app.get("/api/snippets/search/{query}", response_model=list[APISnippet])
async def search_snippets(
    query: str,
    tags: Optional[str] = Query(None, description="Filtrar por tags (CSV)"),
    scope_type: Optional[str] = Query(None, description="Filtrar por scope"),
):
    """Buscar snippets."""
    manager = get_snippet_manager()

    tag_list = None
    if tags:
        tag_list = [t.strip() for t in tags.split(",")]

    results = manager.search_snippets(
        query=query,
        tags=tag_list,
        scope_type=scope_type,
    )

    return results


# Expansión
@app.post("/api/snippets/expand", response_model=SnippetExpandResponse)
async def expand_snippet(expand_data: SnippetExpand):
    """Expandir snippet con variables."""
    manager = get_snippet_manager()
    parser = get_parser()

    # Obtener snippet
    snippet = manager.get_snippet(expand_data.snippet_id)
    if not snippet:
        raise HTTPException(status_code=404, detail="Snippet not found")

    # Usar contenido apropiado
    content = snippet.content_html if snippet.is_rich else snippet.content_text
    if not content:
        raise HTTPException(status_code=400, detail="Snippet has no content")

    # Parsear template con posición de cursor
    expanded, cursor_pos = parser.parse_with_cursor_position(content, expand_data.variables)

    # Log de uso
    manager.log_usage(
        snippet_id=expand_data.snippet_id,
        source=expand_data.source,
        target_app=expand_data.target_app,
        target_domain=expand_data.target_domain,
    )

    return SnippetExpandResponse(
        content=expanded,
        cursor_position=cursor_pos,
        is_rich=snippet.is_rich,
    )


# Serve bundled openapi.json as a fast, deterministic fallback to avoid runtime generation.
@app.get("/openapi-bundled")
async def openapi_bundled():
    """Return the bundled openapi.json file if present."""
    import json
    import os
    from pathlib import Path

    base = getattr(__import__('sys'), '_MEIPASS', None) or os.path.dirname(__file__)
    candidates = [
        Path(base) / 'openapi.json',
        Path(base) / 'server' / 'openapi.json',
        Path(base) / '_internal' / 'server' / 'openapi.json',
    ]

    for c in candidates:
        if c.exists():
            with c.open('r', encoding='utf-8') as f:
                return JSONResponse(content=json.load(f))

    return JSONResponse(content={"error": "bundled openapi.json not found"}, status_code=404)


# Abreviaturas
@app.get("/api/abbreviations/{abbreviation}", response_model=Optional[APISnippet])
async def get_by_abbreviation(abbreviation: str):
    """Obtener snippet por abreviatura."""
    manager = get_snippet_manager()
    snippet = manager.get_snippet_by_abbreviation(abbreviation)

    if not snippet:
        raise HTTPException(status_code=404, detail="Abbreviation not found")

    return snippet


# Estadísticas
@app.get("/api/stats")
async def get_stats(snippet_id: Optional[str] = Query(None)):
    """Obtener estadísticas de uso."""
    manager = get_snippet_manager()
    stats = manager.get_usage_stats(snippet_id)
    return stats


# Export/Import
@app.get("/api/export")
async def export_snippets():
    """Exportar todos los snippets a JSON."""
    import tempfile
    from fastapi.responses import FileResponse

    # Lazy import DB to avoid heavy initialization at module import
    from core.database import get_db

    db = get_db()

    # Crear archivo temporal
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        temp_path = f.name

    # Exportar
    db.export_to_json(temp_path)

    return FileResponse(
        temp_path,
        media_type="application/json",
        filename="aparetext_snippets_export.json",
    )


@app.post("/api/import")
async def import_snippets(
    data: dict,
    replace: bool = Query(False, description="Reemplazar snippets existentes")
):
    """Importar snippets desde JSON."""
    try:
        from core.database import get_db
        from core.models import SnippetDB, SnippetVariableDB

        db = get_db()
        with db.get_session() as session:
            # Validar formato
            if 'snippets' not in data:
                raise HTTPException(status_code=400, detail="Invalid format: missing 'snippets' key")

            imported_count = 0
            skipped_count = 0

            for snippet_data in data['snippets']:
                try:
                    # Si replace=True, eliminar snippets con el mismo abbreviation
                    if replace and snippet_data.get('abbreviation'):
                        existing = session.query(SnippetDB).filter(
                            SnippetDB.abbreviation == snippet_data['abbreviation']
                        ).first()
                        if existing:
                            session.delete(existing)
                            session.commit()

                    # Crear snippet (sin incluir id para que se genere uno nuevo)
                    snippet_data_clean = {k: v for k, v in snippet_data.items() if k != 'id'}

                    # Extraer variables si existen
                    variables = snippet_data_clean.pop('variables', [])

                    # Convertir fechas de string a datetime
                    if 'created_at' in snippet_data_clean and isinstance(snippet_data_clean['created_at'], str):
                        snippet_data_clean['created_at'] = datetime.fromisoformat(snippet_data_clean['created_at'].replace('Z', '+00:00'))
                    if 'updated_at' in snippet_data_clean and isinstance(snippet_data_clean['updated_at'], str):
                        snippet_data_clean['updated_at'] = datetime.fromisoformat(snippet_data_clean['updated_at'].replace('Z', '+00:00'))

                    # Crear snippet
                    snippet = SnippetDB(**snippet_data_clean)
                    session.add(snippet)
                    session.flush()  # Para obtener el ID

                    # Crear variables asociadas
                    for var_data in variables:
                        var_data_clean = {k: v for k, v in var_data.items() if k != 'id'}
                        var_data_clean['snippet_id'] = snippet.id
                        variable = SnippetVariableDB(**var_data_clean)
                        session.add(variable)

                    imported_count += 1

                except Exception as e:
                    print(f"[ApareText] Error importing snippet: {e}")
                    skipped_count += 1
                    session.rollback()  # Rollback en caso de error
                    continue

            session.commit()

        return {
            "success": True,
            "imported": imported_count,
            "skipped": skipped_count,
            "message": f"Importados {imported_count} snippets ({skipped_count} omitidos)"
        }
    except Exception as e:
        print(f"[ApareText] Error in import: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Validación de template
@app.post("/api/validate-template")
async def validate_template(template: str):
    """Validar sintaxis de template."""
    parser = get_parser()
    is_valid, error_msg = parser.validate_template(template)

    if not is_valid:
        return JSONResponse(
            status_code=400,
            content={"valid": False, "error": error_msg},
        )

    info = parser.get_template_info(template)
    return {"valid": True, "info": info}


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handler para errores HTTP."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handler para errores generales."""
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)},
    )
