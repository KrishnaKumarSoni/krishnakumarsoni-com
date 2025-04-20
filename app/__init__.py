# This file marks the app directory as a Python package
# Keep it empty to avoid circular imports
from flask import Flask, render_template, jsonify, request, send_from_directory, Response
from flask_cors import CORS
from flask_session import Session
from pathlib import Path
import yaml
import markdown
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import re
from .firebase_config import db, storage_bucket
import tempfile

load_dotenv()

# Global app instance
_app = None

def create_app():
    global _app
    if _app is not None:
        return _app

    # Initialize Flask app with correct template and static folders
    _app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static',
                static_url_path='/static')
    
    # Configure CORS to allow credentials
    CORS(_app, supports_credentials=True)
    
    # Configure session
    _app.config.update(
        SECRET_KEY=os.getenv('APP_SECRET', 'dev-secret-key'),
        SESSION_TYPE='filesystem',  # Use filesystem to store session data
        SESSION_FILE_DIR=tempfile.gettempdir(),
        SESSION_COOKIE_SECURE=False,  # Set to True in production with HTTPS
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=timedelta(minutes=5)
    )
    
    # Initialize Flask-Session
    Session(_app)
    
    # Make Firebase services available to the app
    _app.config['firebase_db'] = db
    _app.config['firebase_storage'] = storage_bucket
    
    # Register blueprints
    from .auth.routes import auth_bp
    from .blog import init_blog_routes
    
    _app.register_blueprint(auth_bp)
    init_blog_routes(_app)
    
    # Configure upload directory
    if os.environ.get('VERCEL'):
        # Use /tmp for uploads in Vercel environment
        upload_folder = os.path.join(tempfile.gettempdir(), 'uploads')
    else:
        # Use static/uploads for local development
        upload_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../static/uploads')
    
    # Create upload directory if it doesn't exist
    os.makedirs(upload_folder, exist_ok=True)
    _app.config['UPLOAD_FOLDER'] = upload_folder
    
    # Register core routes
    register_core_routes(_app)
    
    return _app

def register_core_routes(app):
    @app.route('/')
    def index():
        metadata = get_metadata_from_markdown('home')
        return render_template('index.html', 
                             active_page='home',
                             meta_title=metadata["title"] or "Home",
                             meta_description=metadata["description"] or "Professional portfolio of Krishna Kumar Soni - Product Development, Management, and Technical Solutions")

    @app.route('/offerings')
    def offerings():
        metadata = get_metadata_from_markdown('offerings')
        offerings_data = get_offerings_data()
        return render_template('pages/offerings.html', 
                             active_page='offerings',
                             offerings=offerings_data,
                             meta_title=metadata["title"] or "My Offerings",
                             meta_description=metadata["description"] or "Professional services including Product Development, Product Management, Training & Workshops.")

    @app.route('/solutions')
    def solutions():
        metadata = get_metadata_from_markdown('solutions')
        content = get_section_content('solutions')
        return render_template('pages/solutions.html', 
                             active_page='solutions',
                             content=content,
                             meta_title=metadata["title"] or "Solutions",
                             meta_description=metadata["description"] or "Innovative solutions for product development and management challenges.")

    @app.route('/resume')
    def resume():
        metadata = get_metadata_from_markdown('resume')
        content = get_section_content('resume')
        return render_template('pages/resume.html', 
                             active_page='resume',
                             content=content,
                             meta_title=metadata["title"] or "Resume",
                             meta_description=metadata["description"] or "Professional resume of Krishna Kumar Soni - Experience, skills, and qualifications.")

    @app.route('/tools')
    def tools():
        return render_template('pages/tools.html',
                             active_page='tools',
                             meta_title="Tools",
                             meta_description="Useful tools and resources for product development and management.")

    @app.route('/static/configurations/<path:filename>')
    def serve_configurations(filename):
        try:
            return send_from_directory(os.path.join(app.static_folder, 'configurations'), filename)
        except Exception as e:
            app.logger.error(f"Error serving configuration file {filename}: {str(e)}")
            return jsonify({"error": "Configuration file not found"}), 404

    @app.route('/api/tracking-config')
    def tracking_config():
        try:
            config_path = os.path.join('static', 'configurations', 'tracking.yaml')
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
                return jsonify(config)
        except Exception as e:
            app.logger.error(f"Error loading tracking config: {str(e)}")
            return jsonify({"error": "Failed to load tracking configuration"}), 500

    @app.route('/sitemap.xml')
    def sitemap():
        try:
            root = ET.Element('urlset')
            root.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
            
            main_pages = ['', 'offerings', 'solutions', 'resume', 'tools', 'blogs']
            for page in main_pages:
                url = ET.SubElement(root, 'url')
                loc = ET.SubElement(url, 'loc')
                loc.text = f"{app.config['SITE_URL']}/{page}" if page else app.config['SITE_URL']
                lastmod = ET.SubElement(url, 'lastmod')
                lastmod.text = datetime.now().strftime('%Y-%m-%d')
                changefreq = ET.SubElement(url, 'changefreq')
                changefreq.text = 'weekly'
                priority = ET.SubElement(url, 'priority')
                priority.text = '1.0' if not page else '0.8'
            
            xml_content = ET.tostring(root, encoding='utf-8')
            return Response(xml_content, mimetype='application/xml')
        except Exception as e:
            app.logger.error(f"Error generating sitemap: {str(e)}")
            return Response("Error generating sitemap", status=500)

    @app.route('/robots.txt')
    def robots():
        robots_content = f"""User-agent: *
Allow: /
Sitemap: {app.config['SITE_URL']}/sitemap.xml
"""
        return Response(robots_content, mimetype='text/plain')

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html', meta_title="Page Not Found"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html', meta_title="Server Error"), 500

# Helper functions
def get_markdown_content(directory, filename='index.md'):
    """Get content from markdown file"""
    file_path = Path('content') / directory / filename
    if not file_path.exists():
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        return markdown.markdown(content)

def get_section_content(section_name):
    """Get content for a specific section"""
    return get_markdown_content(section_name)

def get_metadata_from_markdown(directory, filename='index.md'):
    """Extract title and meta description from markdown content"""
    file_path = Path('content') / directory / filename
    if not file_path.exists():
        return {"title": "", "description": ""}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
        title = lines[0].strip('# ') if lines and lines[0].startswith('#') else ""
        
        # Extract first paragraph for description
        description = ""
        for line in lines[1:]:
            if line.strip() and not line.startswith('#'):
                description = re.sub(r'[#*`_]', '', line).strip()
                break
                
        return {"title": title, "description": description}

def get_offerings_data():
    """Get offerings data from markdown and structure it for the template"""
    content = get_section_content('offerings')
    if not content:
        return {
            'product_development': [],
            'product_management': [],
            'training_workshops': []
        }
    
    file_path = Path('content') / 'offerings' / 'index.md'
    offerings = {
        'product_development': [],
        'product_management': [],
        'training_workshops': []
    }
    
    current_section = None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('## Product Development'):
                current_section = 'product_development'
            elif line.startswith('## Product Management'):
                current_section = 'product_management'
            elif line.startswith('## Training & Workshops'):
                current_section = 'training_workshops'
            elif line.startswith('- ') and current_section:
                offering = line[2:].strip()
                offerings[current_section].append(offering)
    
    return offerings

__all__ = ['create_app', 'db', 'storage_bucket'] 