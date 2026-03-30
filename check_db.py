import os
import sys
# Set up sys.path to find main.py or models
sys.path.append(r'c:\Users\Media\Desktop\BRAND  FACTORY')
from main import app, db, SiteContent
with app.app_context():
    records = SiteContent.query.all()
    print(f"Total SiteContent records: {len(records)}")
    for r in records:
        print(f"ID: {r.id}, Hero Title (EN): {r.hero_title_en}")
