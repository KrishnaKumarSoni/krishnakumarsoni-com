import os
from datetime import datetime
from bs4 import BeautifulSoup
import markdown
import re
from flask import current_app

def get_db():
    return current_app.config['firebase_db']

def get_storage():
    return current_app.config['firebase_storage']

def generate_keywords(title, excerpt, category):
    """Generate keywords from blog content"""
    combined = f"{title} {excerpt} {category}"
    words = re.sub(r'[^\w\s]', '', combined.lower()).split()
    stop_words = {'the', 'is', 'and', 'to', 'a', 'in', 'that', 'of', 'i', 'it', 'for', 'with'}
    keywords = [word for word in words if word not in stop_words and len(word) > 3]
    return list(set(keywords[:10]))

def extract_headings(html_content):
    """Extract headings from HTML content and generate table of contents."""
    soup = BeautifulSoup(html_content, 'html.parser')
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    toc = []
    
    for i, heading in enumerate(headings):
        heading_id = f'heading-{i}'
        heading['id'] = heading_id
        level = int(heading.name[1])
        toc.append({
            'text': heading.text,
            'id': heading_id,
            'level': level
        })
    
    return toc, str(soup)

def format_blog_data(blog_data, doc_id=None):
    """Format blog data for display"""
    if isinstance(blog_data['date'], datetime):
        date_obj = blog_data['date']
    else:
        # If it's a Firestore Timestamp
        date_obj = blog_data['date'].datetime()
    
    formatted_data = {
        'id': doc_id,
        'title': blog_data['title'],
        'content': blog_data['content'],
        'category': blog_data['category'],
        'date': date_obj.strftime('%B %d, %Y'),
        'date_iso': date_obj.isoformat(),
        'excerpt': blog_data['excerpt'],
        'slug': blog_data['slug'],
        'keywords': blog_data['keywords'],
        'thumbnail': blog_data.get('thumbnail')
    }
    return formatted_data

def get_all_blogs():
    """Get all blogs from Firestore"""
    blogs_ref = get_db().collection('blogs')
    blogs = []
    
    for doc in blogs_ref.order_by('date', direction='DESCENDING').stream():
        blog_data = doc.to_dict()
        formatted_blog = format_blog_data(blog_data, doc.id)
        blogs.append(formatted_blog)
    
    return blogs

def get_blog_by_slug(slug):
    """Get a specific blog by slug"""
    blogs_ref = get_db().collection('blogs')
    query = blogs_ref.where('slug', '==', slug).limit(1).stream()
    
    for doc in query:
        blog_data = doc.to_dict()
        formatted_blog = format_blog_data(blog_data, doc.id)
        
        # Convert markdown content to HTML and extract TOC
        html_content = markdown.markdown(formatted_blog['content'])
        toc, html_content = extract_headings(html_content)
        formatted_blog['content'] = html_content
        formatted_blog['toc'] = toc
        
        return formatted_blog
    
    return None

def create_blog(title, content, category, thumbnail_url=None):
    """Create a new blog in Firestore"""
    # Create slug from title
    slug = '-'.join(title.lower().split())
    
    # Convert content to HTML for excerpt
    html_content = markdown.markdown(content)
    soup = BeautifulSoup(html_content, 'html.parser')
    excerpt = soup.p.text if soup.p else ""
    
    # Generate keywords
    keywords = generate_keywords(title, excerpt, category)
    
    # Prepare blog data
    now = datetime.now()
    blog_data = {
        'title': title,
        'content': content,
        'category': category,
        'date': now,
        'excerpt': excerpt,
        'slug': slug,
        'keywords': keywords,
        'thumbnail': thumbnail_url
    }
    
    # Save to Firestore
    blogs_ref = get_db().collection('blogs')
    doc_ref = blogs_ref.document()  # Auto-generate ID
    doc_ref.set(blog_data)
    
    return doc_ref.id

def update_blog(blog_id, title, content, category, thumbnail_url=None):
    """Update an existing blog in Firestore"""
    # Get blog reference
    blog_ref = get_db().collection('blogs').document(blog_id)
    
    # Convert content to HTML for excerpt
    html_content = markdown.markdown(content)
    soup = BeautifulSoup(html_content, 'html.parser')
    excerpt = soup.p.text if soup.p else ""
    
    # Generate keywords
    keywords = generate_keywords(title, excerpt, category)
    
    # Prepare update data
    update_data = {
        'title': title,
        'content': content,
        'category': category,
        'excerpt': excerpt,
        'keywords': keywords,
    }
    
    if thumbnail_url:
        update_data['thumbnail'] = thumbnail_url
    
    # Update in Firestore
    blog_ref.update(update_data)
    
def delete_blog(blog_id):
    """Delete a blog from Firestore"""
    blog_ref = get_db().collection('blogs').document(blog_id)
    blog_ref.delete() 