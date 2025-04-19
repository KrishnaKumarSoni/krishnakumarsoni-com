import os
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, jsonify, current_app
from werkzeug.utils import secure_filename
from .firebase import get_all_blogs, get_blog_by_slug, create_blog, update_blog, delete_blog

def get_storage():
    return current_app.config['firebase_storage']

def init_blog_routes(app):
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')

    def blogs():
        # Get all blogs from Firebase
        blogs = get_all_blogs()
        
        return render_template('pages/blogs.html', 
                             blogs=blogs,
                             meta_title="Blog | Krishna Kumar Soni",
                             meta_description="Read articles on product development, management, and technical solutions by Krishna Kumar Soni.",
                             meta_keywords="blogs, articles, product development, product management, tech insights",
                             is_local=request.host.startswith('127.0.0.1') or request.host.startswith('localhost'))

    def blog(slug):
        # Get blog from Firebase
        blog_data = get_blog_by_slug(slug)
        if not blog_data:
            return redirect(url_for('blogs'))
        
        # Structured data
        blog_json_ld = {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": blog_data['title'],
            "datePublished": blog_data['date_iso'],
            "dateModified": blog_data['date_iso'],
            "description": blog_data['excerpt'],
            "keywords": ', '.join(blog_data['keywords']),
            "author": {
                "@type": "Person",
                "name": "Krishna Kumar Soni"
            }
        }
        
        if blog_data.get('thumbnail'):
            blog_json_ld["image"] = blog_data['thumbnail']
        
        return render_template('pages/blog.html', 
                             blog=blog_data,
                             meta_title=f"{blog_data['title']} | Krishna Kumar Soni Blog",
                             meta_description=blog_data['excerpt'],
                             meta_keywords=', '.join(blog_data['keywords']),
                             og_image=blog_data.get('thumbnail'),
                             blog_json_ld=blog_json_ld)

    def add_blog():
        if not (request.host.startswith('127.0.0.1') or request.host.startswith('localhost')):
            return redirect(url_for('blogs'))
            
        title = request.form.get('title')
        category = request.form.get('category')
        content = request.form.get('content')
        thumbnail = request.files.get('thumbnail')
        
        if not all([title, category, content]):
            flash('All fields are required')
            return redirect(url_for('blogs'))
        
        # Handle thumbnail upload to Firebase Storage if present
        thumbnail_url = None
        if thumbnail:
            filename = secure_filename(thumbnail.filename)
            blob = get_storage().blob(f'blog-thumbnails/{filename}')
            blob.upload_from_string(
                thumbnail.read(),
                content_type=thumbnail.content_type
            )
            thumbnail_url = blob.public_url
        
        # Create blog in Firebase
        create_blog(title, content, category, thumbnail_url)
        
        flash('Blog post created successfully!')
        return redirect(url_for('blogs'))

    def edit_blog():
        if not (request.host.startswith('127.0.0.1') or request.host.startswith('localhost')):
            return redirect(url_for('blogs'))
            
        blog_id = request.form.get('blog_id')
        title = request.form.get('title')
        category = request.form.get('category')
        content = request.form.get('content')
        thumbnail = request.files.get('thumbnail')
        
        if not all([blog_id, title, category, content]):
            flash('All fields are required')
            return redirect(url_for('blogs'))
        
        # Handle thumbnail upload if present
        thumbnail_url = None
        if thumbnail:
            filename = secure_filename(thumbnail.filename)
            blob = get_storage().blob(f'blog-thumbnails/{filename}')
            blob.upload_from_string(
                thumbnail.read(),
                content_type=thumbnail.content_type
            )
            thumbnail_url = blob.public_url
        
        # Update blog in Firebase
        update_blog(blog_id, title, content, category, thumbnail_url)
        
        flash('Blog post updated successfully!')
        return redirect(url_for('blogs'))

    def delete_blog_route():
        if not (request.host.startswith('127.0.0.1') or request.host.startswith('localhost')):
            return jsonify({'success': False, 'message': 'Unauthorized'})
            
        blog_id = request.form.get('blog_id')
        if not blog_id:
            return jsonify({'success': False, 'message': 'Blog ID is required'})
        
        try:
            delete_blog(blog_id)
            return jsonify({'success': True, 'message': 'Blog deleted successfully'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})

    # Register routes
    app.add_url_rule('/blogs', 'blogs', blogs, methods=['GET'])
    app.add_url_rule('/blog/<slug>', 'blog', blog, methods=['GET'])
    app.add_url_rule('/blog/add', 'add_blog', add_blog, methods=['POST'])
    app.add_url_rule('/blog/edit', 'edit_blog', edit_blog, methods=['POST'])
    app.add_url_rule('/blog/delete', 'delete_blog', delete_blog_route, methods=['POST']) 