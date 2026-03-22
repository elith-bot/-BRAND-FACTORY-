import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, 'instance', 'database.db')

def migrate():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # New columns for Hero Section
        columns = [
            ("hero_bg_type", "VARCHAR(20) DEFAULT 'image'"),
            ("hero_bg_color", "VARCHAR(7) DEFAULT '#6B21C8'"),
            ("section2_bg_type", "VARCHAR(20) DEFAULT 'color'"),
            ("section2_bg_media", "VARCHAR(255)"),
            ("section2_bg_color", "VARCHAR(7) DEFAULT '#FDCC04'")
        ]
        
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
