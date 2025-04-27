from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, send_from_directory, Response
from pathlib import Path
import yaml
import markdown
import os
from blog_routes import init_blog_routes
from otp_routes import init_otp_routes
from payment_routes import init_payment_routes
from firebase_service import init_firebase, get_firestore_db
from datetime import datetime
import xml.etree.ElementTree as ET
import re

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for flash messages

# Configuration
app.config.update(
    DEBUG=True,
    CONTENT_DIR=Path('content'),
    SITE_URL='https://krishnakumarsoni.com'  # Update with your actual domain
)

# Initialize Firebase at application startup, only once
# This is a singleton pattern where we initialize Firebase once globally
# and reuse the same instance throughout the application lifecycle.
# The firebase_service.py module maintains this instance and provides
# accessor functions to interact with Firebase.
#
# Benefits:
# - Single connection point to Firebase
# - Authentication happens only once
# - Reduced startup time for routes and API endpoints
# - Consistent state across the application
firebase_app = init_firebase()
if firebase_app:
    print("Firebase initialized successfully at app startup")
else:
    print("Failed to initialize Firebase at app startup")

def get_markdown_content(directory, filename='index.md'):
    """Get content from markdown file"""
    file_path = app.config['CONTENT_DIR'] / directory / filename
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
    file_path = app.config['CONTENT_DIR'] / directory / filename
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
    
    # Parse the markdown content to extract offerings
    # This assumes a specific structure in the markdown file
    file_path = app.config['CONTENT_DIR'] / 'offerings' / 'index.md'
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
                # Remove the '- ' and add to current section
                offering = line[2:].strip()
                offerings[current_section].append(offering)
    
    return offerings

@app.route('/')
def index():
    # Get metadata for SEO
    metadata = get_metadata_from_markdown('home')
    # Keep existing template rendering for home page since it has special interactive elements
    return render_template('index.html', 
                         active_page='home',
                         meta_title=metadata["title"] or "Home",
                         meta_description=metadata["description"] or "Professional portfolio of Krishna Kumar Soni - Product Development, Management, and Technical Solutions")

@app.route('/offerings')
def offerings():
    # Get metadata for SEO
    metadata = get_metadata_from_markdown('offerings')
    # Get offerings data from markdown
    offerings_data = get_offerings_data()
    
    return render_template('pages/offerings.html', 
                         active_page='offerings',
                         offerings=offerings_data,
                         meta_title=metadata["title"] or "My Offerings",
                         meta_description=metadata["description"] or "Professional services including Product Development, Product Management, Training & Workshops.")

@app.route('/static/configurations/<path:filename>')
def serve_configurations(filename):
    # Serve files from the configurations directory in static
    return send_from_directory('static/configurations', filename)

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

@app.route('/solutions')
def solutions():
    # Get metadata for SEO
    metadata = get_metadata_from_markdown('solutions')
    content = get_section_content('solutions')
    return render_template('pages/solutions.html', 
                         active_page='solutions',
                         content=content,
                         meta_title=metadata["title"] or "Solutions",
                         meta_description=metadata["description"] or "Innovative solutions for product development and management challenges.")

@app.route('/resume')
def resume():
    # Get metadata for SEO
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

@app.route('/sitemap.xml')
def sitemap():
    """Generate a sitemap.xml file"""
    try:
        root = ET.Element('urlset')
        root.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
        
        # Add main pages
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
        
        # Add blog posts
        blog_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'content', 'blogs')
        if os.path.exists(blog_folder):
            blog_files = [f for f in os.listdir(blog_folder) if f.endswith('.md')]
            for blog_file in blog_files:
                slug = os.path.splitext(blog_file)[0]
                url = ET.SubElement(root, 'url')
                loc = ET.SubElement(url, 'loc')
                loc.text = f"{app.config['SITE_URL']}/blog/{slug}"
                lastmod = ET.SubElement(url, 'lastmod')
                # Use file modification date
                file_path = os.path.join(blog_folder, blog_file)
                lastmod.text = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d')
                changefreq = ET.SubElement(url, 'changefreq')
                changefreq.text = 'monthly'
                priority = ET.SubElement(url, 'priority')
                priority.text = '0.7'
        
        # Return XML content
        xml_content = ET.tostring(root, encoding='utf-8')
        return Response(xml_content, mimetype='application/xml')
    except Exception as e:
        app.logger.error(f"Error generating sitemap: {str(e)}")
        return Response("Error generating sitemap", status=500)

@app.route('/robots.txt')
def robots():
    """Serve robots.txt file"""
    robots_content = f"""User-agent: *
Allow: /
Sitemap: {app.config['SITE_URL']}/sitemap.xml
"""
    return Response(robots_content, mimetype='text/plain')

@app.route('/api/test-firebase')
def test_firebase():
    """Test Firebase connection and return status"""
    try:
        # Try to initialize Firebase
        app = init_firebase()
        
        if not app:
            return jsonify({
                "status": "error",
                "message": "Failed to initialize Firebase app"
            }), 500
        
        # Try to get a Firestore DB reference
        db = get_firestore_db()
        
        if not db:
            return jsonify({
                "status": "error",
                "message": "Failed to get Firestore DB"
            }), 500
        
        # Try a simple query to confirm connectivity
        try:
            # Try to get a reference to a collection
            users_ref = db.collection('users')
            # Try to get a single document
            query = users_ref.limit(1).get()
            doc_exists = len(list(query)) > 0
            
            return jsonify({
                "status": "success",
                "message": "Firebase connection successful",
                "has_documents": doc_exists
            })
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Firebase query failed: {str(e)}"
            }), 500
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Firebase test failed: {str(e)}"
        }), 500

# Initialize blog routes
init_blog_routes(app)

# Initialize OTP verification routes
init_otp_routes(app)

# Initialize payment routes
init_payment_routes(app)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', meta_title="Page Not Found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html', meta_title="Server Error"), 500

if __name__ == '__main__':
    # Create uploads directory if it doesn't exist
    uploads_dir = os.path.join(app.static_folder, 'uploads')
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
    
    # Create directory for social sharing images if it doesn't exist
    og_images_dir = os.path.join(app.static_folder, 'images')
    if not os.path.exists(og_images_dir):
        os.makedirs(og_images_dir)
    
    app.run(host='0.0.0.0', debug=True, port=8082) 