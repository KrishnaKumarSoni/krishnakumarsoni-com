from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from pathlib import Path
import yaml
import markdown
import os
from blog_routes import init_blog_routes

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for flash messages

# Configuration
app.config.update(
    DEBUG=True,
    CONTENT_DIR=Path('content')
)

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
    # Keep existing template rendering for home page since it has special interactive elements
    return render_template('index.html', active_page='home')

@app.route('/offerings')
def offerings():
    # Get offerings data from markdown
    offerings_data = get_offerings_data()
    
    return render_template('pages/offerings.html', 
                         active_page='offerings',
                         offerings=offerings_data)

@app.route('/solutions')
def solutions():
    content = get_section_content('solutions')
    return render_template('pages/solutions.html', 
                         active_page='solutions',
                         content=content)

@app.route('/resume')
def resume():
    content = get_section_content('resume')
    return render_template('pages/resume.html', 
                         active_page='resume',
                         content=content)

# Initialize blog routes
init_blog_routes(app)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Create uploads directory if it doesn't exist
    uploads_dir = os.path.join(app.static_folder, 'uploads')
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
    
    app.run(host='0.0.0.0', debug=True, port=8082) 