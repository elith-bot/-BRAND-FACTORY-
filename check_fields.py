import os
import sys
sys.path.append(r'c:\Users\Media\Desktop\BRAND  FACTORY')
from main import app, db, SiteContent
with app.app_context():
    r = SiteContent.query.first()
    if r:
        print(f"ID: {r.id}")
        print(f"hero_title_ar: '{r.hero_title_ar}'")
        print(f"section2_title_ar: '{r.section2_title_ar}'")
        print(f"about_title_ar: '{r.about_title_ar}'")
    else:
        print("No record found")
