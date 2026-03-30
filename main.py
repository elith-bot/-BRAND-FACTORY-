import os
import shutil
import time
from flask import Flask, render_template, url_for, send_from_directory, session, redirect, request, g, Blueprint, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image, ImageOps
from functools import wraps

app_version = str(int(time.time()))

# --- 1. إعدادات المسارات ---
_basedir = os.path.dirname(os.path.abspath(__file__))
final_upload_path = os.path.join(_basedir, 'src/static/uploads')
instance_path = os.path.join(_basedir, 'instance')
db_path = os.path.join(instance_path, 'database.db')

os.makedirs(final_upload_path, exist_ok=True)
os.makedirs(instance_path, exist_ok=True)

# --- 2. تهيئة Flask ---
app = Flask(__name__,
            template_folder=os.path.join(_basedir, 'src/templates'),
            static_folder=os.path.join(_basedir, 'src/static'))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico')

app.config.update(
    SQLALCHEMY_DATABASE_URI='sqlite:///' + db_path,
    SECRET_KEY='brand-factory-pro-key-2026', # المستخدم في الجلسات وللأمان
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    CACHE_ID=app_version
)
import json
app.jinja_env.filters['from_json'] = json.loads
app.jinja_env.add_extension('jinja2.ext.do')

db = SQLAlchemy(app)

# --- 3. الموديلات (دعم اللغتين والكورسات) ---
class AdminUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    passcode_hash = db.Column(db.String(200), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False, default='admin') # 'owner' or 'admin'
class ProjectMedia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(128), nullable=False)
    media_type = db.Column(db.String(20))  # 'image' or 'video'
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title_ar = db.Column(db.String(100), nullable=False)
    title_en = db.Column(db.String(100), nullable=False)
    description_ar = db.Column(db.Text, nullable=True)
    description_en = db.Column(db.Text, nullable=True)
    is_featured = db.Column(db.Boolean, default=False)
    cover_media = db.Column(db.String(128), nullable=True)
    cover_media_type = db.Column(db.String(20), nullable=True) # 'image' or 'video'
    media_items = relationship('ProjectMedia', backref='project', cascade="all, delete-orphan")

    @property
    def thumbnail(self):
        if self.cover_media and self.cover_media_type == 'image':
            return self.cover_media
        for m in self.media_items:
            if m.media_type == 'image':
                return m.path
        return None

class SiteContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    about_us_ar = db.Column(db.Text, nullable=True)
    about_us_en = db.Column(db.Text, nullable=True)
    contact_info_ar = db.Column(db.Text, nullable=True)
    contact_info_en = db.Column(db.Text, nullable=True)
    hero_title_ar = db.Column(db.String(200), nullable=True)
    hero_title_en = db.Column(db.String(200), nullable=True)
    hero_subtitle_ar = db.Column(db.String(300), nullable=True)
    hero_subtitle_en = db.Column(db.String(300), nullable=True)
    
    # Hero Background
    hero_bg_type = db.Column(db.String(20), default='image') # 'image', 'video', 'color'
    hero_bg_media = db.Column(db.String(255), nullable=True)
    hero_bg_color = db.Column(db.String(7), default='#6B21C8')
    
    # Section 2 Background (Portfolio)
    section2_bg_type = db.Column(db.String(20), default='color') 
    section2_bg_media = db.Column(db.String(255), nullable=True)
    section2_bg_color = db.Column(db.String(7), default='#FDCC04')
    
    # Section 3 Background (About)
    about_bg_type = db.Column(db.String(20), default='color')
    about_bg_media = db.Column(db.String(255), nullable=True)
    about_bg_color = db.Column(db.String(7), default='#0A0A0A')

    # Section 4 Background (Learning)
    learning_bg_type = db.Column(db.String(20), default='color')
    learning_bg_media = db.Column(db.String(255), nullable=True)
    learning_bg_color = db.Column(db.String(7), default='#0A0A0A')

    # Section 5 Background (Contact)
    contact_bg_type = db.Column(db.String(20), default='color')
    contact_bg_media = db.Column(db.String(255), nullable=True)
    contact_bg_color = db.Column(db.String(7), default='#0A0A0A')

    # Color customization fields
    hero_title_color = db.Column(db.String(7), default='#ffffff')
    hero_text_color = db.Column(db.String(7), default='#ffffff')
    hero_btn_bg_color = db.Column(db.String(7), default='#6B21C8')
    hero_btn_text_color = db.Column(db.String(7), default='#FDCC04')

    section2_title_color = db.Column(db.String(7), default='#ffffff')
    section2_text_color = db.Column(db.String(7), default='#ffffff')
    section2_btn_bg_color = db.Column(db.String(7), default='#6B21C8')
    section2_btn_text_color = db.Column(db.String(7), default='#FDCC04')

    about_title_color = db.Column(db.String(7), default='#ffffff')
    about_text_color = db.Column(db.String(7), default='#ffffff')
    about_btn_bg_color = db.Column(db.String(7), default='#6B21C8')
    about_btn_text_color = db.Column(db.String(7), default='#FDCC04')

    learning_title_color = db.Column(db.String(7), default='#ffffff')
    learning_text_color = db.Column(db.String(7), default='#ffffff')
    learning_btn_bg_color = db.Column(db.String(7), default='#6B21C8')
    learning_btn_text_color = db.Column(db.String(7), default='#FDCC04')

    contact_title_color = db.Column(db.String(7), default='#ffffff')
    contact_text_color = db.Column(db.String(7), default='#ffffff')
    contact_btn_bg_color = db.Column(db.String(7), default='#6B21C8')
    contact_btn_text_color = db.Column(db.String(7), default='#FDCC04')
    
    bg_color = db.Column(db.String(7), nullable=True, default='#000000') # Global fallback
    contact_phone = db.Column(db.String(50), nullable=True)
    contact_whatsapp = db.Column(db.String(50), nullable=True)
    contact_telegram = db.Column(db.String(200), nullable=True)
    contact_email = db.Column(db.String(100), nullable=True)
    contact_facebook = db.Column(db.String(200), nullable=True)
    contact_instagram = db.Column(db.String(200), nullable=True)
    contact_tiktok = db.Column(db.String(200), nullable=True)
    contact_gps = db.Column(db.String(500), nullable=True)
    
    # Advanced Typography & Dynamic Elements
    hero_title_font = db.Column(db.Text, nullable=True)
    hero_subtitle_font = db.Column(db.Text, nullable=True)
    section2_title_font = db.Column(db.Text, nullable=True)
    about_title_font = db.Column(db.Text, nullable=True)
    learning_title_font = db.Column(db.Text, nullable=True)
    contact_title_font = db.Column(db.Text, nullable=True)
    global_font = db.Column(db.Text, nullable=True)
    dynamic_elements_json = db.Column(db.Text, nullable=True) # Element Library storage

    # Missing section titles
    section2_title_ar = db.Column(db.String(200), nullable=True)
    section2_title_en = db.Column(db.String(200), nullable=True)
    section2_text_ar = db.Column(db.Text, nullable=True)
    section2_text_en = db.Column(db.Text, nullable=True)
    
    about_title_ar = db.Column(db.String(200), nullable=True)
    about_title_en = db.Column(db.String(200), nullable=True)
    
    learning_title_ar = db.Column(db.String(200), nullable=True)
    learning_title_en = db.Column(db.String(200), nullable=True)
    learning_text_ar = db.Column(db.Text, nullable=True)
    learning_text_en = db.Column(db.Text, nullable=True)
    
    contact_title_ar = db.Column(db.String(200), nullable=True)
    contact_title_en = db.Column(db.String(200), nullable=True)
    
    menu_left_style = db.Column(db.Text, nullable=True) # JSON or CSS string for background
    menu_right_style = db.Column(db.Text, nullable=True)

class TeamMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_ar = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100), nullable=False)
    position_ar = db.Column(db.String(100), nullable=False)
    position_en = db.Column(db.String(100), nullable=False)
    bio_ar = db.Column(db.Text, nullable=True)
    bio_en = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(128), nullable=True)
    facebook = db.Column(db.String(200), nullable=True)
    twitter = db.Column(db.String(200), nullable=True)
    instagram = db.Column(db.String(200), nullable=True)
    linkedin = db.Column(db.String(200), nullable=True)

class PricingPackage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_ar = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100), nullable=False)
    description_ar = db.Column(db.String(255), nullable=True)
    description_en = db.Column(db.String(255), nullable=True)
    side = db.Column(db.String(10), default='left') # 'left' or 'right'
    order_index = db.Column(db.Integer, default=0)
    items = relationship('PricingItem', backref='package', cascade="all, delete-orphan")

class PricingItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_ar = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100), nullable=False)
    price = db.Column(db.String(50), nullable=True)
    description_ar = db.Column(db.String(255), nullable=True)
    description_en = db.Column(db.String(255), nullable=True)
    category_ar = db.Column(db.String(100), nullable=True)
    category_en = db.Column(db.String(100), nullable=True)
    side = db.Column(db.String(10), default='left') # 'left' or 'right'
    alignment = db.Column(db.String(10), default='left') # 'left', 'center', 'right'
    order_index = db.Column(db.Integer, default=0)
    package_id = db.Column(db.Integer, db.ForeignKey('pricing_package.id'), nullable=True)

class CourseMedia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(128), nullable=False)
    media_type = db.Column(db.String(20)) # 'image' or 'video'
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title_ar = db.Column(db.String(100), nullable=False)
    title_en = db.Column(db.String(100), nullable=False)
    description_ar = db.Column(db.Text, nullable=True)
    description_en = db.Column(db.Text, nullable=True)
    is_featured = db.Column(db.Boolean, default=False)
    cover_media = db.Column(db.String(128), nullable=True)
    cover_media_type = db.Column(db.String(20), nullable=True) # 'image' or 'video'
    media_items = relationship('CourseMedia', backref='course', cascade="all, delete-orphan")

    @property
    def thumbnail(self):
        if self.cover_media and self.cover_media_type == 'image':
            return self.cover_media
        for m in self.media_items:
            if m.media_type == 'image':
                return m.path
        return None


# --- 4. إعدادات اللغة والجلسات ---
@app.before_request
def before_request():
    g.lang = session.get('lang', 'ar') # اللغة الافتراضية عربي

@app.context_processor
def inject_global_data():
    # Cache SiteContent in g to avoid repeated DB queries per request
    if not hasattr(g, '_site_content'):
        g._site_content = SiteContent.query.first()
    return dict(lang=g.lang, global_site_content=g._site_content, cache_id=app_version)

@app.route('/set_lang/<lang>')
def set_lang(lang):
    if lang in ['ar', 'en']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('index'))

# --- SEO: robots.txt & sitemap.xml ---
@app.route('/robots.txt')
def robots():
    return send_from_directory(app.static_folder, 'robots.txt')

@app.route('/sitemap.xml')
def sitemap():
    from flask import make_response
    pages = []
    # Static pages
    for route in ['index', 'portfolio', 'team', 'learning']:
        pages.append(url_for(route, _external=True))
    # Dynamic project pages
    for project in Project.query.all():
        pages.append(url_for('project_detail', project_id=project.id, _external=True))
    # Dynamic course pages
    for course in Course.query.all():
        pages.append(url_for('course_detail', course_id=course.id, _external=True))
    
    xml_urls = '\n'.join(
        f'  <url><loc>{page}</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>'
        for page in pages
    )
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{xml_urls}
</urlset>'''
    response = make_response(xml)
    response.headers['Content-Type'] = 'application/xml'
    return response

# --- 5. معالجة الملفات المرفوعة و التدفق المستمر ---
@app.route('/static/uploads/<path:filename>')
def serve_uploads(filename):
    file_path = os.path.join(final_upload_path, filename)
    if os.path.exists(file_path):
        # Using conditional=True enables HTTP Range Requests (206 Partial Content)
        # This is critical for mobile browsers to stream MP4 videos incrementally
        # rather than downloading the entire file before playback.
        max_age = 31536000 # 1 year cache for static media
        return send_file(file_path, conditional=True, max_age=max_age)
    else:
        return "File not found", 404

def process_any_file(file_data):
    filename = secure_filename(file_data.filename)
    if not filename: return None

    save_path = os.path.join(final_upload_path, filename)
    file_data.save(save_path)

    ext = os.path.splitext(filename)[1].lower()
    
    # Extended comprehensive lists of web formats
    video_exts = ['.mp4', '.mov', '.avi', '.wmv', '.webm', '.mkv', '.flv', '.ogg', '.m4v']
    image_exts = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp', '.tiff']
    
    media_type = 'video' if ext in video_exts else 'image'

    # Only attempt Pillow optimization on standard raster formats
    if media_type == 'image' and ext in ['.jpg', '.jpeg', '.png', '.webp', '.bmp']:
        try:
            with Image.open(save_path) as img:
                img = ImageOps.exif_transpose(img)
                if img.width > 1920:
                    img.thumbnail((1920, 1920), Image.LANCZOS)
                
                # PNG cannot be saved with optimize=True easily unless mode is correct, keep simple for formats
                if ext in ['.jpg', '.jpeg', '.webp']:
                    img.save(save_path, optimize=True, quality=85)
                else:
                    img.save(save_path)
        except Exception as e:
            print(f"Image Optimization Skipped for {filename}: {e}")

    return filename, media_type


# --- 6. حماية صفحات الأدمن (Custom Login Decorator) ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# --- إعداد بلوبرنت بلوحة التحكم (Admin Blueprint) ---
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
def restrict_admin_access():
    allowed_endpoints = ['admin.login', 'admin.forgot_password']
    # If the user tries to access any admin route (except login/forgot), ensure they are logged in
    if request.endpoint and request.endpoint.startswith('admin.') and request.endpoint not in allowed_endpoints:
        if not session.get('admin_logged_in'):
            flash('Please log in to access the Control Panel.', 'error')
            return redirect(url_for('admin.login'))

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        passcode = request.form.get('passcode')
        
        # Determine if default login since DB is reset
        users_exist = AdminUser.query.count() > 0
        if not users_exist and passcode == 'admin123':
            session['admin_logged_in'] = True
            session['admin_role'] = 'owner'
            return redirect(url_for('admin.dashboard'))
            
        # Secure Hash Check
        if passcode:
            users = AdminUser.query.all()
            for user in users:
                if check_password_hash(user.passcode_hash, passcode):
                    session['admin_logged_in'] = True
                    session['admin_role'] = user.role
                    return redirect(url_for('admin.dashboard'))
                
        flash('Invalid Passcode', 'error')
    return render_template('admin/login.html')

import random
@admin_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    step = 'request_otp'
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'request_otp':
            role = request.form.get('role')
            session['reset_role'] = role
            # Generate mock OTP
            otp = str(random.randint(100000, 999999))
            session['mock_otp'] = otp
            print(f"==========\n[MOCK SMS TO OWNER]\nOTP for resetting {role}: {otp}\n==========")
            flash('Verification code sent to Owner via SMS.', 'success')
            step = 'verify_otp'
        elif action == 'verify_otp':
            user_otp = request.form.get('otp')
            new_passcode = request.form.get('new_passcode')
            if user_otp == session.get('mock_otp'):
                target_role = session.get('reset_role')
                user = AdminUser.query.filter_by(role=target_role).first()
                if user:
                    user.passcode_hash = generate_password_hash(new_passcode)
                    db.session.commit()
                    flash('Passcode reset successfully. You can now login.', 'success')
                    # Clear session
                    session.pop('mock_otp', None)
                    session.pop('reset_role', None)
                    return redirect(url_for('admin.login'))
            else:
                flash('Invalid Verification Code.', 'error')
                step = 'verify_otp'
                
    return render_template('admin/forgot_password.html', step=step)

@admin_bp.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_role', None)
    return redirect(url_for('admin.login'))

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('admin/dashboard.html')

@admin_bp.route('/users', methods=['GET', 'POST'])
@login_required
def users():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add_user':
            if session.get('admin_role') != 'owner':
                flash('Only owners can perform this action.', 'error')
                return redirect(url_for('admin.users'))
            
            new_passcode = request.form.get('new_passcode')
            role = request.form.get('role')
            user = AdminUser(passcode_hash=generate_password_hash(new_passcode), role=role)
            db.session.add(user)
            db.session.commit()
            flash('New user added.', 'success')
            
        elif action == 'change_passcode':
            old_passcode = request.form.get('old_passcode')
            new_passcode = request.form.get('new_passcode')
            
            users_list = AdminUser.query.all()
            current_user = None
            for u in users_list:
                if check_password_hash(u.passcode_hash, old_passcode):
                    current_user = u
                    break
                    
            if current_user:
                current_user.passcode_hash = generate_password_hash(new_passcode)
                db.session.commit()
                flash('Passcode upgraded successfully. Please use it next time.', 'success')
            else:
                flash('Incorrect old passcode.', 'error')
                
        return redirect(url_for('admin.users'))

    all_users = AdminUser.query.all() if session.get('admin_role') == 'owner' else []
    return render_template('admin/users.html', admin_users=all_users, current_role=session.get('admin_role'))

@admin_bp.route('/users/delete/<int:id>', methods=['POST'])
@login_required
def delete_user(id):
    if session.get('admin_role') != 'owner':
        flash('Permission denied.', 'error')
        return redirect(url_for('admin.users'))
        
    if AdminUser.query.count() <= 1:
        flash('Cannot delete the last remaining owner.', 'error')
        return redirect(url_for('admin.users'))
        
    user = AdminUser.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('User access revoked.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/site-content', methods=['GET', 'POST'])
@login_required
def site_content():
    content = SiteContent.query.first()
    if not content:
        content = SiteContent()
        db.session.add(content)
        db.session.commit()
    
    print(f"DEBUG: Unified Manager LOAD - Hero Title AR: '{content.hero_title_ar}'")

    if request.method == 'POST':
        print(f"DEBUG: Unified Manager SAVE - Incoming Hero Title AR: '{request.form.get('hero_title_ar')}'")
            
        content.about_us_ar = request.form.get('about_us_ar')
        content.about_us_en = request.form.get('about_us_en')
        content.contact_info_ar = request.form.get('contact_info_ar')
        content.contact_info_en = request.form.get('contact_info_en')
        content.hero_title_ar = request.form.get('hero_title_ar')
        content.hero_title_en = request.form.get('hero_title_en')
        content.hero_subtitle_ar = request.form.get('hero_subtitle_ar')
        content.hero_subtitle_en = request.form.get('hero_subtitle_en')
        content.bg_color = request.form.get('bg_color') or '#000000'
        
        # New Background Options
        content.hero_bg_type = request.form.get('hero_bg_type', 'image')
        content.hero_bg_color = request.form.get('hero_bg_color') or '#6B21C8'
        
        content.section2_bg_type = request.form.get('section2_bg_type', 'color')
        content.section2_bg_color = request.form.get('section2_bg_color') or '#FDCC04'

        content.about_bg_type = request.form.get('about_bg_type', 'color')
        content.about_bg_color = request.form.get('about_bg_color') or '#0A0A0A'

        content.learning_bg_type = request.form.get('learning_bg_type', 'color')
        content.learning_bg_color = request.form.get('learning_bg_color') or '#0A0A0A'

        content.contact_bg_type = request.form.get('contact_bg_type', 'color')
        content.contact_bg_color = request.form.get('contact_bg_color') or '#0A0A0A'

        # Color Fields
        content.hero_title_color = request.form.get('hero_title_color') or '#ffffff'
        content.hero_text_color = request.form.get('hero_text_color') or '#ffffff'
        content.hero_btn_bg_color = request.form.get('hero_btn_bg_color') or '#6B21C8'
        content.hero_btn_text_color = request.form.get('hero_btn_text_color') or '#FDCC04'

        content.section2_title_color = request.form.get('section2_title_color') or '#ffffff'
        content.section2_text_color = request.form.get('section2_text_color') or '#ffffff'
        content.section2_btn_bg_color = request.form.get('section2_btn_bg_color') or '#6B21C8'
        content.section2_btn_text_color = request.form.get('section2_btn_text_color') or '#FDCC04'

        content.about_title_color = request.form.get('about_title_color') or '#ffffff'
        content.about_text_color = request.form.get('about_text_color') or '#ffffff'
        content.about_btn_bg_color = request.form.get('about_btn_bg_color') or '#6B21C8'
        content.about_btn_text_color = request.form.get('about_btn_text_color') or '#FDCC04'

        content.learning_title_color = request.form.get('learning_title_color') or '#ffffff'
        content.learning_text_color = request.form.get('learning_text_color') or '#ffffff'
        content.learning_btn_bg_color = request.form.get('learning_btn_bg_color') or '#6B21C8'
        content.learning_btn_text_color = request.form.get('learning_btn_text_color') or '#FDCC04'

        content.contact_title_color = request.form.get('contact_title_color') or '#ffffff'
        content.contact_text_color = request.form.get('contact_text_color') or '#ffffff'
        content.contact_btn_bg_color = request.form.get('contact_btn_bg_color') or '#6B21C8'
        content.contact_btn_text_color = request.form.get('contact_btn_text_color') or '#FDCC04'

        # New Contact Fields
        content.contact_phone = request.form.get('contact_phone')
        content.contact_whatsapp = request.form.get('contact_whatsapp')
        content.contact_telegram = request.form.get('contact_telegram')
        content.contact_email = request.form.get('contact_email')
        content.contact_facebook = request.form.get('contact_facebook')
        content.contact_instagram = request.form.get('contact_instagram')
        content.contact_tiktok = request.form.get('contact_tiktok')
        content.contact_gps = request.form.get('contact_gps')
        
        # New Typography Fields
        content.hero_title_font = request.form.get('hero_title_font')
        content.hero_subtitle_font = request.form.get('hero_subtitle_font')
        content.section2_title_font = request.form.get('section2_title_font')
        content.about_title_font = request.form.get('about_title_font')
        content.learning_title_font = request.form.get('learning_title_font')
        content.contact_title_font = request.form.get('contact_title_font')
        content.global_font = request.form.get('global_font')
        
        # Save Newly Added Section Fields
        content.section2_title_ar = request.form.get('section2_title_ar')
        content.section2_title_en = request.form.get('section2_title_en')
        content.section2_text_ar = request.form.get('section2_text_ar')
        content.section2_text_en = request.form.get('section2_text_en')
        
        content.about_title_ar = request.form.get('about_title_ar')
        content.about_title_en = request.form.get('about_title_en')
        
        content.learning_title_ar = request.form.get('learning_title_ar')
        content.learning_title_en = request.form.get('learning_title_en')
        content.learning_text_ar = request.form.get('learning_text_ar')
        content.learning_text_en = request.form.get('learning_text_en')
        
        content.contact_title_ar = request.form.get('contact_title_ar')
        content.contact_title_en = request.form.get('contact_title_en')
        
        # Handle Media Uploads for all sections
        def handle_upload(field_name):
            f = request.files.get(field_name)
            if f and f.filename != '':
                fn, _ = process_any_file(f)
                return fn
            return None

        h_media = handle_upload('hero_bg')
        if h_media: content.hero_bg_media = h_media

        s2_media = handle_upload('section2_bg_media')
        if s2_media: content.section2_bg_media = s2_media

        about_media = handle_upload('about_bg_media')
        if about_media: content.about_bg_media = about_media

        learning_media = handle_upload('learning_bg_media')
        if learning_media: content.learning_bg_media = learning_media

        contact_media = handle_upload('contact_bg_media')
        if contact_media: content.contact_bg_media = contact_media

        # Bulk Pricing Updates
        for key in request.form:
            if key.startswith('item_name_ar_'):
                item_id = key.split('_')[-1]
                p_item = PricingItem.query.get(item_id)
                if p_item: p_item.name_ar = request.form.get(key)
            elif key.startswith('item_name_en_'):
                item_id = key.split('_')[-1]
                p_item = PricingItem.query.get(item_id)
                if p_item: p_item.name_en = request.form.get(key)
            elif key.startswith('item_price_'):
                item_id = key.split('_')[-1]
                p_item = PricingItem.query.get(item_id)
                if p_item: p_item.price = request.form.get(key)
            elif key.startswith('pkg_name_ar_'):
                pkg_id = key.split('_')[-1]
                pkg = PricingPackage.query.get(pkg_id)
                if pkg: pkg.name_ar = request.form.get(key)
            elif key.startswith('pkg_name_en_'):
                pkg_id = key.split('_')[-1]
                pkg = PricingPackage.query.get(pkg_id)
                if pkg: pkg.name_en = request.form.get(key)

        db.session.commit()
        flash('Site Content updated successfully!', 'success')
        return redirect(url_for('admin.site_content'))
        
    pricing_left = PricingPackage.query.filter_by(side='left').order_by(PricingPackage.order_index.asc()).all()
    pricing_right = PricingPackage.query.filter_by(side='right').order_by(PricingPackage.order_index.asc()).all()
    standalone_items = PricingItem.query.filter_by(package_id=None).all()

    return render_template('admin/site_content.html', 
                           content=content,
                           pricing_left=pricing_left,
                           pricing_right=pricing_right,
                           standalone_items=standalone_items)

@admin_bp.route('/live-editor')
@login_required
def live_editor():
    import time
    content = SiteContent.query.first()
    lang = session.get('lang', 'ar')
    cache_id = int(time.time())
    return render_template('admin/live_editor.html', content=content, lang=lang, cache_id=cache_id)
@admin_bp.route('/menu-live-editor')
@login_required
def menu_live_editor():
    site_content = SiteContent.query.first()
    pricing_left = PricingPackage.query.filter_by(side='left').order_by(PricingPackage.order_index.asc()).all()
    pricing_right = PricingPackage.query.filter_by(side='right').order_by(PricingPackage.order_index.asc()).all()
    standalone_items = PricingItem.query.filter_by(package_id=None).all()
    lang = session.get('lang', 'ar')
    return render_template('admin/menu_editor.html', 
                           site_content=site_content,
                           pricing_left=pricing_left,
                           pricing_right=pricing_right,
                           standalone_items=standalone_items,
                           lang=lang,
                           cache_id=int(time.time()))

@admin_bp.route('/live-editor/save', methods=['POST'])
@login_required
def save_live_editor():
    data = request.get_json()
    if not data:
        return {"error": "No data"}, 400
    
    content = SiteContent.query.first()
    if not content:
        content = SiteContent()
        db.session.add(content)
    
    # Mapping for fields and styles
    for item in data.get('changes', []):
        field = item.get('field', '')
        value = item.get('value', '')
        
        # 1. Handle PricingPackage: pkg_name_{lang}_{id}
        if field.startswith('pkg_name_'):
            parts = field.split('_')
            if len(parts) >= 4:
                lang_code = parts[2]
                pkg_id = parts[3]
                pkg = PricingPackage.query.get(pkg_id)
                if pkg:
                    if lang_code == 'ar': pkg.name_ar = value
                    else: pkg.name_en = value
            continue

        # 2. Handle PricingItem: item_name_{lang}_{id}
        if field.startswith('item_name_'):
            parts = field.split('_')
            if len(parts) >= 4:
                lang_code = parts[2]
                item_id = parts[3]
                pitem = PricingItem.query.get(item_id)
                if pitem:
                    if lang_code == 'ar': pitem.name_ar = value
                    else: pitem.name_en = value
            continue

        # 3. Handle PricingItem Price: item_price_{id}
        if field.startswith('item_price_'):
            parts = field.split('_')
            if len(parts) >= 3:
                item_id = parts[2]
                pitem = PricingItem.query.get(item_id)
                if pitem:
                    pitem.price = value
            continue

        # 4. Handle SiteContent fields (hero_title_en, hero_title_ar, etc.)
        if hasattr(content, field):
            setattr(content, field, value)
    
    # Handle dynamic elements
    if 'dynamic_elements' in data:
        content.dynamic_elements_json = data['dynamic_elements']

    # 5. Handle Structured Menu State (Advanced Menu Editor)
    if 'menu_state' in data:
        menu_state = data['menu_state']
        # Robustness: ensure menu_state is a dict
        if isinstance(menu_state, str):
            try:
                import json
                menu_state = json.loads(menu_state)
            except Exception as e:
                print(f"ERROR: Failed to parse menu_state string: {e}")
                menu_state = {}
        
        if not isinstance(menu_state, dict):
            print(f"ERROR: menu_state is {type(menu_state)}, expected dict")
            menu_state = {}

        for side in ['left', 'right']:
            active_pkg_ids = []
            for p_idx, pkg_data in enumerate(menu_state.get(side, [])):
                pkg = None
                if pkg_data.get('id'):
                    pkg = PricingPackage.query.get(pkg_data['id'])
                
                if not pkg:
                    # Create NEW Package
                    pkg = PricingPackage(
                        name_en=pkg_data.get('name_en', 'New Package'),
                        name_ar=pkg_data.get('name_ar', 'باقة جديدة'),
                        side=side,
                        order_index=p_idx
                    )
                    db.session.add(pkg)
                    db.session.flush() # get pkg.id
                else:
                    # Update Existing Package
                    if pkg_data.get('name_en'): pkg.name_en = pkg_data['name_en']
                    if pkg_data.get('name_ar'): pkg.name_ar = pkg_data['name_ar']
                    pkg.side = side
                    pkg.order_index = p_idx
                
                active_pkg_ids.append(pkg.id)
                
                active_item_ids = []
                for itm_idx, itm_data in enumerate(pkg_data.get('items', [])):
                    itm_id = itm_data.get('id')
                    # Cast string ID to int if necessary
                    if itm_id and str(itm_id).isdigit(): itm_id = int(itm_id)

                    if itm_id:
                        # Update Existing Item
                        pitem = PricingItem.query.get(itm_id)
                        if pitem:
                            pitem.name_ar = itm_data.get('name_ar', pitem.name_ar)
                            pitem.name_en = itm_data.get('name_en', pitem.name_en or pitem.name_ar)
                            pitem.price = itm_data.get('price', pitem.price)
                            pitem.alignment = itm_data.get('alignment', 'right')
                            pitem.order_index = itm_idx
                            pitem.package_id = pkg.id
                            pitem.side = side # CRITICAL FIX
                            active_item_ids.append(pitem.id)
                    else:
                        # Create NEW Item
                        new_item = PricingItem(
                            package_id=pkg.id,
                            name_ar=itm_data.get('name_ar', 'عنصر جديد'),
                            name_en=itm_data.get('name_en', itm_data.get('name_ar', 'New Item')),
                            price=itm_data.get('price', '0'),
                            alignment=itm_data.get('alignment', 'right'),
                            order_index=itm_idx,
                            side=side # CRITICAL FIX
                        )
                        db.session.add(new_item)
                        db.session.flush()
                        active_item_ids.append(new_item.id)
                
                # DELETE missing items from this package
                for pitem in pkg.items:
                    if pitem.id not in active_item_ids:
                        db.session.delete(pitem)

            # DELETE missing packages for this side
            for pkg_to_del in PricingPackage.query.filter_by(side=side).all():
                if pkg_to_del.id not in active_pkg_ids:
                    db.session.delete(pkg_to_del)

        # Update Menu Styles
        if 'menu_styles' in data:
            menu_styles = data['menu_styles']
            if isinstance(menu_styles, str):
                try:
                    import json
                    menu_styles = json.loads(menu_styles)
                except:
                    menu_styles = {}
            
            if isinstance(menu_styles, dict):
                if menu_styles.get('left'):
                    content.menu_left_style = menu_styles['left']
                if menu_styles.get('right'):
                    content.menu_right_style = menu_styles['right']

    db.session.commit()
    return {"status": "success"}

@admin_bp.route('/team', methods=['GET', 'POST'])
@login_required
def team():
    if request.method == 'POST':
        member = TeamMember(
            name_ar=request.form.get('name_ar'),      name_en=request.form.get('name_en'),
            position_ar=request.form.get('position_ar'), position_en=request.form.get('position_en'),
            bio_ar=request.form.get('bio_ar'),           bio_en=request.form.get('bio_en'),
            facebook=request.form.get('facebook'),       twitter=request.form.get('twitter'),
            instagram=request.form.get('instagram'),     linkedin=request.form.get('linkedin')
        )
        file = request.files.get('image')
        if file and file.filename:
            res = process_any_file(file)
            if res:
                member.image = res[0]
        
        db.session.add(member)
        db.session.commit()
        flash('Team member added.', 'success')
        return redirect(url_for('admin.team'))
        
    members = TeamMember.query.all()
    return render_template('admin/team.html', members=members)

@admin_bp.route('/team/delete/<int:id>', methods=['POST'])
@login_required
def delete_team(id):
    member = TeamMember.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    flash('Team member deleted.', 'success')
    return redirect(url_for('admin.team'))

@admin_bp.route('/projects', methods=['GET', 'POST'])
@login_required
def projects():
    if request.method == 'POST':
        project = Project(
            title_ar=request.form.get('title_ar'),             title_en=request.form.get('title_en'),
            description_ar=request.form.get('description_ar'), description_en=request.form.get('description_en'),
            is_featured=True if request.form.get('is_featured') else False
        )
        cover = request.files.get('cover_media')
        if cover and cover.filename:
            res = process_any_file(cover)
            if res:
                project.cover_media = res[0]
                project.cover_media_type = res[1]
                
        db.session.add(project)
        db.session.flush() # to get project.id
        
        files = request.files.getlist('upload_media')
        for f in files:
            if f.filename:
                res = process_any_file(f)
                if res:
                    fname, mtype = res
                    new_media = ProjectMedia(path=fname, media_type=mtype, project_id=project.id)
                    db.session.add(new_media)
        
        db.session.commit()
        flash('Project added successfully.', 'success')
        return redirect(url_for('admin.projects'))
        
    projects_list = Project.query.order_by(Project.id.desc()).all()
    return render_template('admin/projects.html', projects=projects_list)

@admin_bp.route('/projects/delete/<int:id>', methods=['POST'])
@login_required
def delete_project(id):
    project = Project.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted.', 'success')
    return redirect(url_for('admin.projects'))

@admin_bp.route('/courses', methods=['GET', 'POST'])
@login_required
def courses():
    if request.method == 'POST':
        course = Course(
            title_ar=request.form.get('title_ar'),             title_en=request.form.get('title_en'),
            description_ar=request.form.get('description_ar'), description_en=request.form.get('description_en'),
            is_featured=True if request.form.get('is_featured') else False
        )
        cover = request.files.get('cover_media')
        if cover and cover.filename:
            res = process_any_file(cover)
            if res:
                course.cover_media = res[0]
                course.cover_media_type = res[1]
                
        db.session.add(course)
        db.session.flush()
        
        files = request.files.getlist('upload_media')
        for f in files:
            if f.filename:
                res = process_any_file(f)
                if res:
                    fname, mtype = res
                    new_media = CourseMedia(path=fname, media_type=mtype, course_id=course.id)
                    db.session.add(new_media)
        
        db.session.commit()
        flash('Course added successfully.', 'success')
        return redirect(url_for('admin.courses'))
        
    courses_list = Course.query.order_by(Course.id.desc()).all()
    return render_template('admin/courses.html', courses=courses_list)

@admin_bp.route('/courses/delete/<int:id>', methods=['POST'])
@login_required
def delete_course(id):
    course = Course.query.get_or_404(id)
    db.session.delete(course)
    db.session.commit()
    flash('Course deleted.', 'success')
    return redirect(url_for('admin.courses'))

# -------- NEW EDIT ENDPOINTS --------
@admin_bp.route('/team/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_team(id):
    member = TeamMember.query.get_or_404(id)
    if request.method == 'POST':
        member.name_ar = request.form.get('name_ar')
        member.name_en = request.form.get('name_en')
        member.position_ar = request.form.get('position_ar')
        member.position_en = request.form.get('position_en')
        member.bio_ar = request.form.get('bio_ar')
        member.bio_en = request.form.get('bio_en')
        member.facebook = request.form.get('facebook')
        member.twitter = request.form.get('twitter')
        member.instagram = request.form.get('instagram')
        member.linkedin = request.form.get('linkedin')
        
        file = request.files.get('image')
        if file and file.filename:
            res = process_any_file(file)
            if res: member.image = res[0]
            
        db.session.commit()
        flash('Team member updated.', 'success')
        return redirect(url_for('admin.team'))
    return render_template('admin/team_edit.html', member=member)

@admin_bp.route('/projects/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_project(id):
    project = Project.query.get_or_404(id)
    if request.method == 'POST':
        project.title_ar = request.form.get('title_ar')
        project.title_en = request.form.get('title_en')
        project.description_ar = request.form.get('description_ar')
        project.description_en = request.form.get('description_en')
        project.is_featured = True if request.form.get('is_featured') else False
        
        cover = request.files.get('cover_media')
        if cover and cover.filename:
            res = process_any_file(cover)
            if res:
                project.cover_media = res[0]
                project.cover_media_type = res[1]
                
        files = request.files.getlist('upload_media')
        for f in files:
            if f.filename:
                res = process_any_file(f)
                if res:
                    m = ProjectMedia(path=res[0], media_type=res[1], project_id=project.id)
                    db.session.add(m)
                    
        db.session.commit()
        flash('Project updated.', 'success')
        return redirect(url_for('admin.edit_project', id=project.id))
    return render_template('admin/project_edit.html', project=project)

@admin_bp.route('/projects/delete_media/<int:media_id>', methods=['POST'])
@login_required
def delete_project_media(media_id):
    m = ProjectMedia.query.get_or_404(media_id)
    db.session.delete(m)
    db.session.commit()
    flash('Media fragment removed layer.', 'success')
    return redirect(request.referrer)

@admin_bp.route('/courses/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_course(id):
    course = Course.query.get_or_404(id)
    if request.method == 'POST':
        course.title_ar = request.form.get('title_ar')
        course.title_en = request.form.get('title_en')
        course.description_ar = request.form.get('description_ar')
        course.description_en = request.form.get('description_en')
        course.is_featured = True if request.form.get('is_featured') else False
        
        cover = request.files.get('cover_media')
        if cover and cover.filename:
            res = process_any_file(cover)
            if res:
                course.cover_media = res[0]
                course.cover_media_type = res[1]
                
        files = request.files.getlist('upload_media')
        for f in files:
            if f.filename:
                res = process_any_file(f)
                if res:
                    m = CourseMedia(path=res[0], media_type=res[1], course_id=course.id)
                    db.session.add(m)
                    
        db.session.commit()
        flash('Course updated.', 'success')
        return redirect(url_for('admin.edit_course', id=course.id))
    return render_template('admin/course_edit.html', course=course)

@admin_bp.route('/courses/delete_media/<int:media_id>', methods=['POST'])
@login_required
def delete_course_media(media_id):
    m = CourseMedia.query.get_or_404(media_id)
    db.session.delete(m)
    db.session.commit()
    flash('Media fragment removed.', 'success')
    return redirect(request.referrer)

@admin_bp.route('/pricing', methods=['GET', 'POST'])
@login_required
def pricing():
    packages = PricingPackage.query.order_by(PricingPackage.order_index.asc()).all()
    # Also get items that don't have a package just in case
    standalone_items = PricingItem.query.filter_by(package_id=None).order_by(PricingItem.order_index.asc()).all()
    return render_template('admin/pricing.html', packages=packages, standalone_items=standalone_items)

@admin_bp.route('/pricing/packages/add', methods=['GET', 'POST'])
@login_required
def add_pricing_package():
    if request.method == 'POST':
        package = PricingPackage(
            name_ar=request.form.get('name_ar'),
            name_en=request.form.get('name_en'),
            description_ar=request.form.get('description_ar'),
            description_en=request.form.get('description_en'),
            side=request.form.get('side', 'left'),
            order_index=int(request.form.get('order_index', 0))
        )
        db.session.add(package)
        db.session.commit()
        flash('Pricing package added.', 'success')
        return redirect(url_for('admin.pricing'))
    return render_template('admin/pricing_package_form.html', package=None)

@admin_bp.route('/pricing/packages/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_pricing_package(id):
    package = PricingPackage.query.get_or_404(id)
    if request.method == 'POST':
        package.name_ar = request.form.get('name_ar')
        package.name_en = request.form.get('name_en')
        package.description_ar = request.form.get('description_ar')
        package.description_en = request.form.get('description_en')
        package.side = request.form.get('side', 'left')
        package.order_index = int(request.form.get('order_index', 0))
        db.session.commit()
        flash('Pricing package updated.', 'success')
        return redirect(url_for('admin.pricing'))
    return render_template('admin/pricing_package_form.html', package=package)

@admin_bp.route('/pricing/packages/delete/<int:id>', methods=['POST'])
@login_required
def delete_pricing_package(id):
    package = PricingPackage.query.get_or_404(id)
    db.session.delete(package)
    db.session.commit()
    flash('Pricing package deleted.', 'success')
    return redirect(url_for('admin.pricing'))

@admin_bp.route('/pricing/add', methods=['GET', 'POST'])
@login_required
def add_pricing_item():
    packages = PricingPackage.query.all()
    if request.method == 'POST':
        item = PricingItem(
            name_ar=request.form.get('name_ar'),
            name_en=request.form.get('name_en'),
            price=request.form.get('price'),
            description_ar=request.form.get('description_ar'),
            description_en=request.form.get('description_en'),
            category_ar=request.form.get('category_ar'),
            category_en=request.form.get('category_en'),
            side=request.form.get('side', 'left'),
            order_index=int(request.form.get('order_index', 0)),
            package_id=request.form.get('package_id') if request.form.get('package_id') else None
        )
        db.session.add(item)
        db.session.commit()
        flash('Pricing item added.', 'success')
        return redirect(url_for('admin.pricing'))
    return render_template('admin/pricing_form.html', item=None, packages=packages)

@admin_bp.route('/pricing/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_pricing_item(id):
    item = PricingItem.query.get_or_404(id)
    packages = PricingPackage.query.all()
    if request.method == 'POST':
        item.name_ar = request.form.get('name_ar')
        item.name_en = request.form.get('name_en')
        item.price = request.form.get('price')
        item.description_ar = request.form.get('description_ar')
        item.description_en = request.form.get('description_en')
        item.category_ar = request.form.get('category_ar')
        item.category_en = request.form.get('category_en')
        item.side = request.form.get('side', 'left')
        item.order_index = int(request.form.get('order_index', 0))
        item.package_id = request.form.get('package_id') if request.form.get('package_id') else None
        
        db.session.commit()
        flash('Pricing item updated.', 'success')
        return redirect(url_for('admin.pricing'))
    return render_template('admin/pricing_form.html', item=item, packages=packages)

@admin_bp.route('/pricing/delete/<int:id>', methods=['POST'])
@login_required
def delete_pricing_item(id):
    item = PricingItem.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Pricing item deleted.', 'success')
    return redirect(request.referrer)

@admin_bp.route('/pricing/reorder', methods=['POST'])
@login_required
def reorder_pricing():
    data = request.get_json()
    if not data:
        return {"error": "No data received"}, 400
    
    try:
        # data should be a list of {id: int, order_index: int, package_id: int|None, side: str|None}
        for item_data in data:
            item = PricingItem.query.get(item_data['id'])
            if item:
                item.order_index = item_data['order_index']
                item.package_id = item_data['package_id']
                if 'side' in item_data and item_data['side']:
                    item.side = item_data['side']
        db.session.commit()
        return {"status": "success"}
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500

@admin_bp.route('/pricing/update-inline', methods=['POST'])
@login_required
def update_pricing_inline():
    data = request.get_json()
    if not data or 'id' not in data:
        return {"error": "Missing item ID"}, 400
    
    item = PricingItem.query.get_or_404(data['id'])
    field = data.get('field')
    value = data.get('value')
    
    if field in ['name_ar', 'name_en', 'price', 'description_ar', 'description_en']:
        setattr(item, field, value)
        db.session.commit()
        return {"status": "success"}
    
    return {"error": "Invalid field"}, 400

app.register_blueprint(admin_bp)

# --- 7. المسارات (Routes) للزوار ---
@app.route("/")
def index():
    edit_mode = request.args.get('edit') == 'true'
    lang = session.get('lang', 'ar')
    site_content = SiteContent.query.first()
    projects = Project.query.order_by(Project.id.desc()).limit(6).all()
    
    # Fetch Pricing Packages split by side
    pricing_left = PricingPackage.query.filter_by(side='left').order_by(PricingPackage.order_index.asc()).all()
    pricing_right = PricingPackage.query.filter_by(side='right').order_by(PricingPackage.order_index.asc()).all()
    standalone_items = PricingItem.query.filter_by(package_id=None).all() # Just in case

    return render_template('index.html',
                           lang=lang,
                           edit_mode=edit_mode,
                           site_content=site_content,
                           projects=projects,
                           pricing_left=pricing_left,
                           pricing_right=pricing_right,
                           standalone_items=standalone_items,
                           cache_id=app.config['CACHE_ID'])

@app.route("/portfolio")
def portfolio():
    projects = Project.query.all()
    return render_template('portfolio.html', projects=projects)

@app.route("/project/<int:project_id>")
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template('project_detail.html', project=project)

@app.route("/team")
def team():
    team_members = TeamMember.query.all()
    return render_template('team.html', team_members=team_members)

@app.route("/learning")
def learning():
    courses = Course.query.all()
    return render_template('learning.html', courses=courses)

@app.route("/course/<int:course_id>")
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template('course_detail.html', course=course)


# --- 8. التشغيل والتهيئة ---
with app.app_context():
    db.create_all()
    if AdminUser.query.count() == 0:
        default_owner = AdminUser(passcode_hash=generate_password_hash('owner123'), role='owner')
        db.session.add(default_owner)
        db.session.commit()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
