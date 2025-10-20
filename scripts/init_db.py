#!/usr/bin/env python3
"""Initialize database tables."""

import sys
sys.path.insert(0, '/Users/manishkatyan/work/revdog-leanflow')

from src.database.connection import init_db

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("✅ Database initialized successfully!")
    print("Database file: leanflow.db")
