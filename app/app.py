from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, send_from_directory, Response
from flask_cors import CORS
from flask_session import Session
from pathlib import Path
import yaml
import markdown
import os
from dotenv import load_dotenv
from datetime import datetime
import xml.etree.ElementTree as ET
import re
from .auth.routes import auth_bp
from .firebase_config import initialize_firebase
from .blog import init_blog_routes
from . import create_app

load_dotenv()

# Create the app instance
app = create_app()

# Initialize Firebase
db, storage_bucket = initialize_firebase()
if not db or not storage_bucket:
    raise ValueError("Failed to initialize Firebase")

# Make Firebase services available to the app
app.config['firebase_db'] = db
app.config['firebase_storage'] = storage_bucket

# Register blueprints
app.register_blueprint(auth_bp)

# Initialize blog routes
init_blog_routes(app)

# Create required directories
for directory in [
    os.path.join(app.static_folder, 'uploads'),
    os.path.join(app.static_folder, 'images'),
    os.path.join(os.path.dirname(app.root_path), 'flask_session')
]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# Register routes
@app.route('/')
def index():
    metadata = get_metadata_from_markdown('home')
    return render_template('index.html', 
                         active_page='home',
                         meta_title=metadata["title"] or "Home",
                         meta_description=metadata["description"] or "Professional portfolio of Krishna Kumar Soni - Product Development, Management, and Technical Solutions")

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8082) 