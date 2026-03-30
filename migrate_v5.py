import sqlite3
import os

def migrate():
    db_path = 'instance/database.db'
    if not os.path.exists(db_path):
        print("Database not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create PricingItem table
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pricing_item (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name_ar TEXT NOT NULL,
                name_en TEXT NOT NULL,
                price TEXT,
                description_ar TEXT,
                description_en TEXT,
                category_ar TEXT,
                category_en TEXT,
                side TEXT DEFAULT 'left',
                order_index INTEGER DEFAULT 0
            )
        ''')
        print("Created pricing_item table.")
    except Exception as e:
        print(f"Error creating pricing_item table: {e}")

    conn.commit()
    conn.close()
    print("Migration v5 completed.")

if __name__ == "__main__":
    migrate()
