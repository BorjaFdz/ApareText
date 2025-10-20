#!/usr/bin/env python3
"""
Health check script for ApareText system.
Verifies database connectivity, server status, and configuration.
"""

import sys
import os
import sqlite3
import requests
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Tuple

class HealthChecker:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.checks = []
        self.passed = 0
        self.failed = 0

    def check(self, name: str, func) -> bool:
        """Run a health check and record the result."""
        try:
            result = func()
            if result:
                self.checks.append((name, "PASS", ""))
                self.passed += 1
                return True
            else:
                self.checks.append((name, "FAIL", "Check returned False"))
                self.failed += 1
                return False
        except Exception as e:
            self.checks.append((name, "FAIL", str(e)))
            self.failed += 1
            return False

    def check_database(self) -> bool:
        """Check database connectivity and basic structure."""
        db_path = self.project_root / "aparetext.db"
        if not db_path.exists():
            return False

        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            # Check if snippets table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='snippets'")
            if not cursor.fetchone():
                conn.close()
                return False

            # Check if we can query snippets
            cursor.execute("SELECT COUNT(*) FROM snippets")
            count = cursor.fetchone()[0]

            conn.close()
            return True
        except Exception:
            return False

    def check_server_config(self) -> bool:
        """Check server configuration file."""
        config_path = self.project_root / "server" / "config.py"
        if not config_path.exists():
            return False

        try:
            # Import config module
            sys.path.insert(0, str(self.project_root / "server"))
            import config

            # Try to validate config
            if hasattr(config, 'validate_config'):
                config.validate_config()
            return True
        except Exception:
            return False
        finally:
            # Clean up sys.path
            if str(self.project_root / "server") in sys.path:
                sys.path.remove(str(self.project_root / "server"))

    def check_python_dependencies(self) -> bool:
        """Check if required Python packages are installed."""
        required_packages = [
            'fastapi', 'uvicorn', 'sqlalchemy', 'pydantic',
            'pyinstaller', 'requests'
        ]

        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                return False
        return True

    def check_electron_app(self) -> bool:
        """Check if Electron app structure is intact."""
        electron_path = self.project_root / "electron-app"
        required_files = [
            "package.json",
            "main.js",
            "manager.html",
            "palette.html"
        ]

        for file in required_files:
            if not (electron_path / file).exists():
                return False
        return True

    def check_node_dependencies(self) -> bool:
        """Check if Node.js dependencies are installed."""
        electron_path = self.project_root / "electron-app"
        node_modules = electron_path / "node_modules"

        if not node_modules.exists():
            return False

        # Check for key electron packages
        key_packages = ["electron", "electron-builder"]
        for package in key_packages:
            if not (node_modules / package).exists():
                return False
        return True

    def run_all_checks(self) -> bool:
        """Run all health checks."""
        print("🔍 Running ApareText Health Check...\n")

        self.check("Database connectivity", self.check_database)
        self.check("Server configuration", self.check_server_config)
        self.check("Python dependencies", self.check_python_dependencies)
        self.check("Electron app structure", self.check_electron_app)
        self.check("Node.js dependencies", self.check_node_dependencies)

        # Print results
        print("Results:")
        print("-" * 50)
        for name, status, error in self.checks:
            icon = "✅" if status == "PASS" else "❌"
            print(f"{icon} {name}: {status}")
            if error:
                print(f"   Error: {error}")

        print("-" * 50)
        print(f"Total: {self.passed + self.failed} checks")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")

        return self.failed == 0

def main():
    checker = HealthChecker()
    success = checker.run_all_checks()

    if success:
        print("\n🎉 All health checks passed!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {checker.failed} health check(s) failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()