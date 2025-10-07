"""
Utilidades de mantenimiento de la base de datos.

Uso:
    python scripts/db_maintenance.py --check          # Verificar integridad
    python scripts/db_maintenance.py --clean-empty    # Limpiar snippets vacíos
    python scripts/db_maintenance.py --stats          # Ver estadísticas
"""

import argparse
import sqlite3
from pathlib import Path
from datetime import datetime


class DBMaintenance:
    """Herramientas de mantenimiento de la base de datos."""
    
    def __init__(self, db_path: str = None):
        """Inicializar con ruta a la base de datos."""
        if db_path is None:
            db_path = Path.home() / ".aparetext" / "aparetext.db"
        self.db_path = Path(db_path)
        
    def get_connection(self):
        """Obtener conexión a la base de datos."""
        return sqlite3.connect(self.db_path)
    
    def check_integrity(self):
        """Verificar integridad de la base de datos."""
        print("🔍 Verificando integridad de la base de datos...\n")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Verificar snippets
        cursor.execute("SELECT COUNT(*) FROM snippets")
        total_snippets = cursor.fetchone()[0]
        print(f"📊 Total snippets: {total_snippets}")
        
        # Verificar snippets con problemas
        cursor.execute("""
            SELECT COUNT(*) FROM snippets 
            WHERE snippet_type = 'text' 
            AND (content_text IS NULL OR LENGTH(content_text) = 0)
            AND (content_html IS NULL OR LENGTH(content_html) = 0)
        """)
        empty_text = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM snippets 
            WHERE snippet_type = 'image' 
            AND (image_data IS NULL OR LENGTH(image_data) = 0)
        """)
        empty_image = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM snippets WHERE snippet_type IS NULL")
        null_type = cursor.fetchone()[0]
        
        print(f"⚠️  Snippets TEXT vacíos: {empty_text}")
        print(f"⚠️  Snippets IMAGE vacíos: {empty_image}")
        print(f"⚠️  Snippets sin tipo: {null_type}")
        
        # Verificar variables
        cursor.execute("SELECT COUNT(*) FROM snippet_variables")
        total_vars = cursor.fetchone()[0]
        print(f"\n📝 Total variables: {total_vars}")
        
        # Verificar logs de uso
        cursor.execute("SELECT COUNT(*) FROM usage_logs")
        total_logs = cursor.fetchone()[0]
        print(f"📈 Total registros de uso: {total_logs}")
        
        conn.close()
        
        if empty_text > 0 or empty_image > 0 or null_type > 0:
            print("\n⚠️  Se encontraron problemas. Ejecuta --clean-empty para limpiar.")
        else:
            print("\n✅ Base de datos íntegra.")
    
    def clean_empty_snippets(self):
        """Limpiar snippets vacíos."""
        print("🧹 Limpiando snippets vacíos...\n")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Encontrar snippets vacíos
        cursor.execute("""
            SELECT id, name, snippet_type FROM snippets 
            WHERE (
                (snippet_type = 'text' AND 
                 (content_text IS NULL OR LENGTH(content_text) = 0) AND
                 (content_html IS NULL OR LENGTH(content_html) = 0))
                OR
                (snippet_type = 'image' AND 
                 (image_data IS NULL OR LENGTH(image_data) = 0))
                OR
                snippet_type IS NULL
            )
        """)
        
        empty_snippets = cursor.fetchall()
        
        if not empty_snippets:
            print("✅ No hay snippets vacíos.")
            conn.close()
            return
        
        print(f"Encontrados {len(empty_snippets)} snippets vacíos:")
        for id, name, stype in empty_snippets:
            print(f"  - {name} (tipo: {stype or 'NULL'})")
        
        confirm = input("\n¿Eliminar estos snippets? (s/N): ")
        if confirm.lower() != 's':
            print("❌ Operación cancelada.")
            conn.close()
            return
        
        # Eliminar
        for id, _, _ in empty_snippets:
            cursor.execute("DELETE FROM snippets WHERE id = ?", (id,))
        
        conn.commit()
        conn.close()
        
        print(f"✅ {len(empty_snippets)} snippets eliminados.")
    
    def show_stats(self):
        """Mostrar estadísticas de la base de datos."""
        print("📊 Estadísticas de ApareText\n")
        print("=" * 60)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Por tipo
        cursor.execute("""
            SELECT snippet_type, COUNT(*) FROM snippets 
            GROUP BY snippet_type
        """)
        print("\n📝 Snippets por tipo:")
        for stype, count in cursor.fetchall():
            print(f"  {stype or 'Sin tipo'}: {count}")
        
        # Por tags
        cursor.execute("SELECT tags FROM snippets WHERE tags IS NOT NULL")
        all_tags = {}
        for (tags_str,) in cursor.fetchall():
            if tags_str:
                tags = tags_str.split(',')
                for tag in tags:
                    tag = tag.strip()
                    all_tags[tag] = all_tags.get(tag, 0) + 1
        
        if all_tags:
            print("\n🏷️  Tags más usados:")
            sorted_tags = sorted(all_tags.items(), key=lambda x: x[1], reverse=True)[:10]
            for tag, count in sorted_tags:
                print(f"  {tag}: {count}")
        
        # Snippets más usados
        cursor.execute("""
            SELECT s.name, s.abbreviation, COUNT(u.id) as uses
            FROM snippets s
            LEFT JOIN usage_logs u ON s.id = u.snippet_id
            GROUP BY s.id
            ORDER BY uses DESC
            LIMIT 10
        """)
        print("\n⭐ Snippets más usados:")
        for name, abbr, uses in cursor.fetchall():
            print(f"  {name} (;{abbr or 'sin abrev.'}): {uses} usos")
        
        # Uso en últimos 7 días
        cursor.execute("""
            SELECT COUNT(*) FROM usage_logs 
            WHERE timestamp >= datetime('now', '-7 days')
        """)
        recent_uses = cursor.fetchone()[0]
        print(f"\n📈 Usos en últimos 7 días: {recent_uses}")
        
        conn.close()
        print("\n" + "=" * 60)


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description="Mantenimiento de base de datos de ApareText")
    parser.add_argument("--check", action="store_true", help="Verificar integridad")
    parser.add_argument("--clean-empty", action="store_true", help="Limpiar snippets vacíos")
    parser.add_argument("--stats", action="store_true", help="Mostrar estadísticas")
    parser.add_argument("--db", type=str, help="Ruta a la base de datos (opcional)")
    
    args = parser.parse_args()
    
    maintenance = DBMaintenance(args.db)
    
    if args.check:
        maintenance.check_integrity()
    elif args.clean_empty:
        maintenance.clean_empty_snippets()
    elif args.stats:
        maintenance.show_stats()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
