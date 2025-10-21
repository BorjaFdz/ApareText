"""
API REST con FastAPI.
"""

from datetime import datetime
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .config import CORS_ORIGINS

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

# Crear app
app = FastAPI(
    title="ApareText API",
    description="API REST para gestión de snippets",
    version="0.1.0"
)

# CORS - permitir solo localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "ApareText API is running"}

@app.get("/api/snippets")
async def get_snippets():
    manager = get_snippet_manager()
    snippets = manager.get_all_snippets()
    return {"snippets": [s.model_dump() for s in snippets]}

@app.post("/api/import")
async def import_snippets(data: dict):
    """Importar snippets desde datos JSON."""
    import tempfile
    import os
    from core.database import get_db
    
    try:
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            import json
            json.dump(data, f)
            temp_path = f.name
        
        # Importar desde el archivo temporal
        db = get_db()
        result = db.import_from_json(temp_path)
        
        # Limpiar archivo temporal
        os.unlink(temp_path)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error importing snippets: {str(e)}")

# Dependencias
def get_snippet_manager():
    """Obtener instancia de SnippetManager."""
    from core.database import get_db
    from core.snippet_manager import SnippetManager
    
    db = get_db()
    return SnippetManager(db)
