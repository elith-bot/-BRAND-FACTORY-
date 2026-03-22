import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, 'instance', 'database.db')

def migrate():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # New columns for About, Learning, and Contact Sections
        sections = ['about', 'learning', 'contact']
        columns = []
        for sec in sections:
            columns.append((f"{sec}_bg_type", "VARCHAR(20) DEFAULT 'color'"))
            columns.append((f"{sec}_bg_media", "VARCHAR(255)"))
            columns.append((f"{sec}_bg_color", "VARCHAR(7) DEFAULT '#0A0A0A'"))
        
        for col_name, col_def in columns:
            try:
                cursor.execute(f"ALTER TABLE site_content ADD COLUMN {col_name} {col_def}")
                print(f"Added column: {col_name}")
            except Exception as e:
                print(f"Column {col_name} might already exist: {e}")
        
        conn.commit()
        print("Migration successful.")
    except Exception as e:
        print(f"Migration error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
