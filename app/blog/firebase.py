import os
from datetime import datetime
from bs4 import BeautifulSoup
import markdown
import re
from flask import current_app
from slugify import slugify

def get_db():
    db = current_app.config.get('firebase_db')
    if not db:
        current_app.logger.error("Firebase database not available")
        return None
    return db

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
    db = get_db()
    if not db:
        return None
        
    try:
        blogs_ref = db.collection('blogs')
        blogs = []
        for doc in blogs_ref.stream():
            blog_data = doc.to_dict()
            blog_data['id'] = doc.id
            blogs.append(blog_data)
        return sorted(blogs, key=lambda x: x.get('date', ''), reverse=True)
    except Exception as e:
        current_app.logger.error(f"Error fetching blogs: {str(e)}")
        return None

def get_blog_by_slug(slug):
    db = get_db()
    if not db:
        return None
        
    try:
        blogs_ref = db.collection('blogs')
        query = blogs_ref.where('slug', '==', slug).limit(1)
        docs = query.stream()
        for doc in docs:
            blog_data = doc.to_dict()
            blog_data['id'] = doc.id
            return blog_data
        return None
    except Exception as e:
        current_app.logger.error(f"Error fetching blog by slug: {str(e)}")
        return None

def create_blog(title, content, category, thumbnail_url=None):
    db = get_db()
    if not db:
        raise Exception("Firebase database not available")
        
    try:
        now = datetime.now()
        date_str = now.strftime('%B %d, %Y')
        date_iso = now.isoformat()
        
        # Create slug from title
        slug = slugify(title)
        
        # Extract first 200 characters as excerpt
        excerpt = content[:200] + '...' if len(content) > 200 else content
        
        # Extract keywords from content
        keywords = [word.strip() for word in category.split(',')]
        
        blog_data = {
            'title': title,
            'content': content,
            'category': category,
            'slug': slug,
            'date': date_str,
            'date_iso': date_iso,
            'excerpt': excerpt,
            'keywords': keywords
        }
        
        if thumbnail_url:
            blog_data['thumbnail'] = thumbnail_url
            
        db.collection('blogs').add(blog_data)
    except Exception as e:
        current_app.logger.error(f"Error creating blog: {str(e)}")
        raise

def update_blog(blog_id, title, content, category, thumbnail_url=None):
    db = get_db()
    if not db:
        raise Exception("Firebase database not available")
        
    try:
        # Extract first 200 characters as excerpt
        excerpt = content[:200] + '...' if len(content) > 200 else content
        
        # Extract keywords from content
        keywords = [word.strip() for word in category.split(',')]
        
        blog_data = {
            'title': title,
            'content': content,
            'category': category,
            'excerpt': excerpt,
            'keywords': keywords
        }
        
        if thumbnail_url:
            blog_data['thumbnail'] = thumbnail_url
            
        db.collection('blogs').document(blog_id).update(blog_data)
    except Exception as e:
        current_app.logger.error(f"Error updating blog: {str(e)}")
        raise

def delete_blog(blog_id):
    db = get_db()
    if not db:
        raise Exception("Firebase database not available")
        
    try:
        db.collection('blogs').document(blog_id).delete()
    except Exception as e:
        current_app.logger.error(f"Error deleting blog: {str(e)}")
        raise 