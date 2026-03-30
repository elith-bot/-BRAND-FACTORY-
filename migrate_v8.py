import os
from main import app, db
from sqlalchemy import text

def migrate():
    with app.app_context():
        try:
            # Check if column exists (optional but safe)
            with db.engine.connect() as conn:
                # SQLite doesn't support 'IF NOT EXISTS' for columns directly in all versions, 
                # but we can check if it fails or use PRAGMA.
                conn.execute(text("ALTER TABLE pricing_item ADD COLUMN alignment VARCHAR(10) DEFAULT 'left'"))
                conn.commit()
                print("Successfully added 'alignment' column to pricing_item table.")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("Column 'alignment' already exists.")
            else:
                print(f"Error during migration: {e}")

if __name__ == "__main__":
    migrate()
