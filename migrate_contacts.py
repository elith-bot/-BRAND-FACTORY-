import sqlite3

def migrate():
    try:
        conn = sqlite3.connect('instance/database.db')
        cursor = conn.cursor()
        
        # Add new columns to site_content
        columns = [
            "contact_phone VARCHAR(50)",
            "contact_whatsapp VARCHAR(50)",
            "contact_telegram VARCHAR(200)",
            "contact_email VARCHAR(100)",
            "contact_facebook VARCHAR(200)",
            "contact_instagram VARCHAR(200)",
            "contact_tiktok VARCHAR(200)",
            "contact_gps VARCHAR(500)"
        ]
        
        for col in columns:
            try:
                cursor.execute(f"ALTER TABLE site_content ADD COLUMN {col};")
                print(f"Added {col}")
            except sqlite3.OperationalError as e:
                # Column might already exist
                print(f"Skipped {col}: {e}")
                
        conn.commit()
        conn.close()
        print("Migration complete!")
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
