"""
Python backend for ApareText Electron app.
Provides functions that can be called from Node.js via python-shell.
"""

import sys
import json
import os
from typing import Optional

# Add the parent directory to sys.path so we can import core
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.database import get_db
from core.snippet_manager import SnippetManager
from core.template_parser import TemplateParser
from core.models import Snippet

# Initialize database and manager
db = get_db()
manager = SnippetManager(db)
parser = TemplateParser()

def health():
    """Health check."""
    print(json.dumps({"status": "healthy"}))

def root():
    """Root endpoint."""
    print(json.dumps({"message": "ApareText API", "version": "0.1.0"}))

def get_snippets():
    """Get all snippets."""
    snippets = manager.get_all_snippets()
    result = [snippet.dict() for snippet in snippets]
    print(json.dumps(result))

def search_snippets(query: str):
    """Search snippets."""
    snippets = manager.search_snippets(query)
    result = [snippet.dict() for snippet in snippets]
    print(json.dumps(result))

def get_snippet(snippet_id: str):
    """Get a specific snippet."""
    snippet = manager.get_snippet(snippet_id)
    if snippet:
        print(json.dumps(snippet.dict()))
    else:
        print(json.dumps(None))

def create_snippet(data: dict):
    """Create a new snippet."""
    snippet = Snippet(**data)
    created = manager.create_snippet(snippet)
    print(json.dumps(created.dict()))

def update_snippet(snippet_id: str, data: dict):
    """Update a snippet."""
    snippet = Snippet(**data)
    updated = manager.update_snippet(snippet_id, snippet)
    if updated:
        print(json.dumps(updated.dict()))
    else:
        print(json.dumps(None))

def delete_snippet(snippet_id: str):
    """Delete a snippet."""
    success = manager.delete_snippet(snippet_id)
    print(json.dumps({"success": success}))

def expand_snippet(data: dict):
    """Expand a snippet."""
    abbreviation = data.get("abbreviation")
    variables = data.get("variables", {})
    snippet = manager.get_snippet_by_abbreviation(abbreviation)
    if snippet:
        expanded = parser.parse(snippet.content, variables)
        manager.increment_usage(snippet.id)
        print(json.dumps({"expanded": expanded}))
    else:
        print(json.dumps({"error": "Snippet not found"}))

def get_stats():
    """Get usage stats."""
    stats = manager.get_usage_stats()
    print(json.dumps(stats))

def export_snippets():
    """Export snippets to JSON."""
    # For simplicity, export to a temp file and return the path
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        db.export_to_json(f.name)
        print(json.dumps({"path": f.name}))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No function specified"}))
        sys.exit(1)

    func = sys.argv[1]
    args = sys.argv[2:]

    try:
        if func == "health":
            health()
        elif func == "root":
            root()
        elif func == "get_snippets":
            get_snippets()
        elif func == "search_snippets" and args:
            search_snippets(args[0])
        elif func == "get_snippet" and args:
            get_snippet(args[0])
        elif func == "create_snippet" and args:
            data = json.loads(args[0])
            create_snippet(data)
        elif func == "update_snippet" and len(args) >= 2:
            snippet_id = args[0]
            data = json.loads(args[1])
            update_snippet(snippet_id, data)
        elif func == "delete_snippet" and args:
            delete_snippet(args[0])
        elif func == "expand_snippet" and args:
            data = json.loads(args[0])
            expand_snippet(data)
        elif func == "get_stats":
            get_stats()
        elif func == "export_snippets":
            export_snippets()
        else:
            print(json.dumps({"error": "Unknown function"}))
    except Exception as e:
        print(json.dumps({"error": str(e)}))