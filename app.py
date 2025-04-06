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

# Fallback product data when config file isn't available
FALLBACK_PRODUCTS = [
    {
        "id": "ai-product-consult",
        "title": "AI-First Product Strategy",
        "description": "Design and roadmap AI-native workflows, products, or tools for your enterprise use case. From LLM-powered automation to internal tool augmentation, get a strategic plan ready for execution.",
        "category": "ai",
        "type": "consultation",
        "category_color": "#9C27B0",
        "price": 75000,
        "image": "placeholder.jpg"
    },
    {
        "id": "enterprise-mvp-roadmap",
        "title": "MVP Planning & Rapid Roadmapping",
        "description": "1-2 week deep dive to plan your next product module or MVP — from use case definition, feature prioritization, UX flows, and vendor stack recommendations.",
        "category": "development",
        "type": "consultation",
        "category_color": "#4CAF50",
        "price": 50000,
        "image": "placeholder.jpg"
    },
    {
        "id": "figma-infra-audit",
        "title": "Design Ops & Figma Infra Audit",
        "description": "Evaluate and streamline your team's Figma design workflows, reusable components, tokens, and design-to-dev handoff processes.",
        "category": "design",
        "type": "consultation",
        "category_color": "#FF5722",
        "price": 45000,
        "image": "placeholder.jpg"
    },
    {
        "id": "ai-poc-delivery",
        "title": "Custom AI Tool / POC Development",
        "description": "Build a working AI prototype or workflow using GPT-4, automation scripts, and web UIs tailored to your specific business use case. Suitable for marketing ops, cold outreach, CRM enrichment, internal R&D, or support.",
        "category": "ai",
        "type": "development",
        "category_color": "#9C27B0",
        "price": 150000,
        "image": "placeholder.jpg"
    },
    {
        "id": "fintech-product-squad",
        "title": "Embedded Fintech Product Builder",
        "description": "Launch or revamp B2B fintech workflows — insurance, lending, payouts, compliance. 2-8 week engagement with PRD, GTM support, and feature delivery guidance.",
        "category": "fintech",
        "type": "development",
        "category_color": "#2196F3",
        "price": 200000,
        "image": "placeholder.jpg"
    }
]

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

def get_config_path(filename):
    """Get the absolute path to a config file"""
    # Try different possible locations
    possible_paths = [
        os.path.join(os.getcwd(), 'config', filename),  # Local development
        os.path.join(os.path.dirname(__file__), 'config', filename),  # Relative to app.py
        os.path.join('/var/task/config', filename),  # Vercel serverless
    ]
    
    app.logger.debug(f"Current working directory: {os.getcwd()}")
    app.logger.debug(f"__file__ directory: {os.path.dirname(__file__)}")
    
    for path in possible_paths:
        app.logger.debug(f"Trying path: {path}")
        if os.path.exists(path):
            app.logger.debug(f"Found config at: {path}")
            return path
    
    app.logger.error(f"Config file {filename} not found. Tried paths: {possible_paths}")
    raise FileNotFoundError(f"Config file {filename} not found in any of the expected locations")

@app.route('/')
def index():
    # Keep existing template rendering for home page since it has special interactive elements
    return render_template('index.html', active_page='home')

@app.route('/offerings')
def offerings():
    try:
        # Try to read products from YAML config
        try:
            config_path = get_config_path('products.yaml')
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
                products = config['products']
        except Exception as e:
            app.logger.warning(f"Could not load products from YAML: {str(e)}. Using fallback data.")
            products = FALLBACK_PRODUCTS
            
        return render_template('pages/offerings.html', products=products)
    except Exception as e:
        app.logger.error(f"Error in offerings route: {str(e)}")
        return render_template('500.html'), 500

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
    # In production, we might want to be more careful about what error details we expose
    error_message = str(e)
    app.logger.error(f"500 error: {error_message}")
    return render_template('500.html', error_message=error_message), 500

if __name__ == '__main__':
    # Create uploads directory if it doesn't exist
    uploads_dir = os.path.join(app.static_folder, 'uploads')
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
    
    app.run(host='0.0.0.0', debug=True, port=8082) 