import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, 'instance', 'database.db')

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("ALTER TABLE site_content ADD COLUMN bg_color VARCHAR(7) DEFAULT '#000000'")
    conn.commit()
    print("Migration successful: bg_color added to site_content.")
except Exception as e:
    print(f"Migration error (might already exist): {e}")
finally:
    conn.close()
