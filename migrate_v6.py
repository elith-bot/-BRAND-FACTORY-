import os
import sqlite3

_basedir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(_basedir, 'instance', 'database.db')

def migrate():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("Creating pricing_package table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pricing_package (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name_ar TEXT NOT NULL,
                name_en TEXT NOT NULL,
                description_ar TEXT,
                description_en TEXT,
                side TEXT DEFAULT 'left',
                order_index INTEGER DEFAULT 0
            )
        ''')

        print("Adding package_id to pricing_item table...")
        # Check if package_id exists first
        cursor.execute("PRAGMA table_info(pricing_item)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'package_id' not in columns:
            cursor.execute('ALTER TABLE pricing_item ADD COLUMN package_id INTEGER REFERENCES pricing_package(id)')
            print("package_id column added.")
        else:
            print("package_id column already exists.")

        conn.commit()
        print("Migration v6 successful.")

    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
