"""
API REST con FastAPI.
"""

from datetime import datetime
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from core.database import Database, get_db
from core.models import Snippet, SnippetVariable
from core.snippet_manager import SnippetManager
from core.template_parser import TemplateParser

# Crear app
app = FastAPI(
    title="ApareText API",
    description="API REST para gestión de snippets",
    version="0.1.0",
)

# CORS - permitir solo localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:46321",
        "http://127.0.0.1:46321",
        "chrome-extension://*",
        "moz-extension://*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependencias
def get_snippet_manager() -> SnippetManager:
    """Obtener instancia de SnippetManager."""
    db = get_db()
    return SnippetManager(db)


def get_parser() -> TemplateParser:
    """Obtener instancia de TemplateParser."""
    return TemplateParser()


# Modelos de request/response
class SnippetCreate(BaseModel):
    """Request para crear snippet."""

    name: str
    abbreviation: Optional[str] = None
    tags: list[str] = []
    content_text: Optional[str] = None
    content_html: Optional[str] = None
    is_rich: bool = False
    scope_type: str = "global"
    scope_values: list[str] = []
    variables: list[SnippetVariable] = []


class SnippetUpdate(BaseModel):
    """Request para actualizar snippet."""

    name: Optional[str] = None
    abbreviation: Optional[str] = None
    tags: Optional[list[str]] = None
    content_text: Optional[str] = None
    content_html: Optional[str] = None
    is_rich: Optional[bool] = None
    scope_type: Optional[str] = None
    scope_values: Optional[list[str]] = None
    variables: Optional[list[SnippetVariable]] = None
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
    db = get_db()
    manager = SnippetManager(db)
    snippets = manager.get_all_snippets()

    return {
        "status": "healthy",
        "database": "connected",
        "snippets_count": len(snippets),
    }


# CRUD Snippets
@app.get("/api/snippets", response_model=list[Snippet])
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


@app.get("/api/snippets/{snippet_id}", response_model=Snippet)
async def get_snippet(snippet_id: str):
    """Obtener snippet por ID."""
    manager = get_snippet_manager()
    snippet = manager.get_snippet(snippet_id)

    if not snippet:
        raise HTTPException(status_code=404, detail="Snippet not found")

    return snippet


@app.post("/api/snippets", response_model=Snippet, status_code=201)
async def create_snippet(snippet_data: SnippetCreate):
    """Crear nuevo snippet."""
    manager = get_snippet_manager()

    # Crear snippet desde request
    snippet = Snippet(
        name=snippet_data.name,
        abbreviation=snippet_data.abbreviation,
        tags=snippet_data.tags,
        content_text=snippet_data.content_text,
        content_html=snippet_data.content_html,
        is_rich=snippet_data.is_rich,
        scope_type=snippet_data.scope_type,
        scope_values=snippet_data.scope_values,
        variables=snippet_data.variables,
    )

    created = manager.create_snippet(snippet)
    return created


@app.put("/api/snippets/{snippet_id}", response_model=Snippet)
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
                value = [SnippetVariable(**v) if isinstance(v, dict) else v for v in value]
            
            setattr(existing, key, value)

    # Actualizar timestamp
    existing.updated_at = datetime.utcnow()
    
    updated = manager.update_snippet(snippet_id, existing)
    return updated


@app.delete("/api/snippets/{snippet_id}", status_code=204)
async def delete_snippet(snippet_id: str):
    """Eliminar snippet."""
    manager = get_snippet_manager()
    success = manager.delete_snippet(snippet_id)

    if not success:
        raise HTTPException(status_code=404, detail="Snippet not found")

    return None


# Búsqueda
@app.get("/api/snippets/search/{query}", response_model=list[Snippet])
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


# Abreviaturas
@app.get("/api/abbreviations/{abbreviation}", response_model=Optional[Snippet])
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
    replace: bool = Query(False, description="Reemplazar snippets existentes")
):
    """Importar snippets desde JSON."""
    # TODO: Implementar upload de archivo
    raise HTTPException(status_code=501, detail="Not implemented yet")


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
