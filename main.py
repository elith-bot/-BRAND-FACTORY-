import os
import shutil
from flask import Flask, render_template, url_for, send_from_directory, session, redirect, request, g, Blueprint, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image, ImageOps
from functools import wraps

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
    SECRET_KEY='photogenic-pro-key-99', # المستخدم في الجلسات وللأمان
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

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
    hero_bg_media = db.Column(db.String(255), nullable=True)
    bg_color = db.Column(db.String(7), nullable=True, default='#000000')
    contact_phone = db.Column(db.String(50), nullable=True)
    contact_whatsapp = db.Column(db.String(50), nullable=True)
    contact_telegram = db.Column(db.String(200), nullable=True)
    contact_email = db.Column(db.String(100), nullable=True)
    contact_facebook = db.Column(db.String(200), nullable=True)
    contact_instagram = db.Column(db.String(200), nullable=True)
    contact_tiktok = db.Column(db.String(200), nullable=True)
    contact_gps = db.Column(db.String(500), nullable=True)

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
    content = SiteContent.query.first()
    return dict(lang=g.lang, global_site_content=content)

@app.route('/set_lang/<lang>')
def set_lang(lang):
    if lang in ['ar', 'en']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('index'))


# --- 5. معالجة الملفات المرفوعة ---
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
    if request.method == 'POST':
        if not content:
            content = SiteContent()
            db.session.add(content)
            
        content.about_us_ar = request.form.get('about_us_ar')
        content.about_us_en = request.form.get('about_us_en')
        content.contact_info_ar = request.form.get('contact_info_ar')
        content.contact_info_en = request.form.get('contact_info_en')
        content.hero_title_ar = request.form.get('hero_title_ar')
        content.hero_title_en = request.form.get('hero_title_en')
        content.hero_subtitle_ar = request.form.get('hero_subtitle_ar')
        content.hero_subtitle_en = request.form.get('hero_subtitle_en')
        content.bg_color = request.form.get('bg_color') or '#000000'
        
        # New Contact Fields
        content.contact_phone = request.form.get('contact_phone')
        content.contact_whatsapp = request.form.get('contact_whatsapp')
        content.contact_telegram = request.form.get('contact_telegram')
        content.contact_email = request.form.get('contact_email')
        content.contact_facebook = request.form.get('contact_facebook')
        content.contact_instagram = request.form.get('contact_instagram')
        content.contact_tiktok = request.form.get('contact_tiktok')
        content.contact_gps = request.form.get('contact_gps')
        
        # Handle Hero Background Upload
        file = request.files.get('hero_bg')
        if file and file.filename != '':
            filename, _ = process_any_file(file)
            if filename:
                content.hero_bg_media = filename

        db.session.commit()
        flash('Site Content updated successfully!', 'success')
        return redirect(url_for('admin.site_content'))
        
    return render_template('admin/site_content.html', content=content)

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

app.register_blueprint(admin_bp)

# --- 7. المسارات (Routes) للزوار ---
@app.route("/")
def index():
    content = SiteContent.query.first()
    
    # Try fetching featured projects first
    projects = Project.query.filter_by(is_featured=True).order_by(Project.id.desc()).limit(3).all()
    if len(projects) == 0:
        projects = Project.query.order_by(Project.id.desc()).limit(3).all()
        
    # Try fetching featured courses first
    courses = Course.query.filter_by(is_featured=True).order_by(Course.id.desc()).limit(3).all()
    if len(courses) == 0:
        courses = Course.query.order_by(Course.id.desc()).limit(3).all()
        
    return render_template('index.html', site_content=content, projects=projects, courses=courses)

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
