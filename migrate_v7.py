import sqlite3
import os

db_path = r'c:\Users\Media\Desktop\BRAND  FACTORY\instance\database.db'

def list_columns(cursor, table_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    return [row[1] for row in cursor.fetchall()]

def migrate():
    if not os.path.exists(db_path):
        print("Database not found!")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    columns = list_columns(cursor, 'site_content')
    
    new_columns = [
        ('section2_title_ar', 'VARCHAR(200)'),
        ('section2_title_en', 'VARCHAR(200)'),
        ('section2_text_ar', 'TEXT'),
        ('section2_text_en', 'TEXT'),
        ('about_title_ar', 'VARCHAR(200)'),
        ('about_title_en', 'VARCHAR(200)'),
        ('learning_title_ar', 'VARCHAR(200)'),
        ('learning_title_en', 'VARCHAR(200)'),
        ('learning_text_ar', 'TEXT'),
        ('learning_text_en', 'TEXT'),
        ('contact_title_ar', 'VARCHAR(200)'),
        ('contact_title_en', 'VARCHAR(200)')
    ]

    for col_name, col_type in new_columns:
        if col_name not in columns:
            print(f"Adding column {col_name}...")
            cursor.execute(f"ALTER TABLE site_content ADD COLUMN {col_name} {col_type}")
        else:
            print(f"Column {col_name} already exists.")

    conn.commit()
    conn.close()
    print("Migration V7 completed successfully.")

if __name__ == '__main__':
    migrate()
