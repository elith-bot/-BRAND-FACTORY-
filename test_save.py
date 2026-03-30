import os
import sys
sys.path.append(r'c:\Users\Media\Desktop\BRAND  FACTORY')
from main import app, db, SiteContent
with app.app_context():
    r = SiteContent.query.first()
    if not r:
        r = SiteContent()
        db.session.add(r)
    
    r.hero_title_ar = 'TEST TITLE AR'
    r.section2_title_ar = 'TEST SECTION 2 AR'
    db.session.commit()
    
    # Reload and check
    db.session.expire_all()
    r2 = SiteContent.query.first()
    print(f"Verified Hero Title AR: '{r2.hero_title_ar}'")
    print(f"Verified Section 2 Title AR: '{r2.section2_title_ar}'")
