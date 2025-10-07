#!/usr/bin/env python3
"""
Script de prueba rápida para las nuevas funcionalidades
"""

import requests
import json
from datetime import datetime

API_URL = "http://127.0.0.1:46321"

def test_stats():
    """Probar endpoint de estadísticas"""
    print("\n🧪 Testing /api/stats...")
    try:
        response = requests.get(f"{API_URL}/api/stats")
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Total uses: {data.get('total_uses', 0)}")
        print(f"   Top snippets: {len(data.get('top_snippets', []))}")
        print("   ✅ Stats OK")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_export():
    """Probar endpoint de export"""
    print("\n🧪 Testing /api/export...")
    try:
        response = requests.get(f"{API_URL}/api/export")
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Version: {data.get('version')}")
        print(f"   Snippets: {len(data.get('snippets', []))}")
        print(f"   Exported at: {data.get('exported_at')}")
        print("   ✅ Export OK")
        return data
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def test_import(data):
    """Probar endpoint de import"""
    print("\n🧪 Testing /api/import...")
    if not data:
        print("   ⚠️  No hay datos para importar (export falló)")
        return
    
    try:
        response = requests.post(f"{API_URL}/api/import", json=data)
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   Imported: {result.get('imported', 0)}")
        print(f"   Skipped: {result.get('skipped', 0)}")
        print(f"   Message: {result.get('message')}")
        print("   ✅ Import OK")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_health():
    """Probar health check"""
    print("\n🧪 Testing /health...")
    try:
        response = requests.get(f"{API_URL}/health")
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Status: {data.get('status')}")
        print(f"   Snippets count: {data.get('snippets_count')}")
        print("   ✅ Health OK")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def main():
    print("=" * 60)
    print("🚀 ApareText - Testing Quick Wins Features")
    print("=" * 60)
    
    # 1. Health check
    test_health()
    
    # 2. Estadísticas
    test_stats()
    
    # 3. Export
    export_data = test_export()
    
    # 4. Import (usando datos del export)
    test_import(export_data)
    
    print("\n" + "=" * 60)
    print("✅ Todas las pruebas completadas")
    print("=" * 60)
    print("\n📝 Siguiente paso: Probar en la UI de Electron")
    print("   1. Abrir Manager")
    print("   2. Probar botones Export/Import/Stats")
    print("   3. Editar snippet y ver preview en tiempo real")
    print("   4. Abrir Palette y probar búsqueda fuzzy")

if __name__ == "__main__":
    main()
