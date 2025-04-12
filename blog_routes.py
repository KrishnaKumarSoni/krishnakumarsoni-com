import os
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, jsonify
import markdown
import frontmatter
from werkzeug.utils import secure_filename
import re
from bs4 import BeautifulSoup

def init_blog_routes(app):
    BLOG_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'content', 'blogs')
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    
    def parse_date(date_str):
        """Parse date string into datetime object"""
        try:
            # Try parsing with ordinal indicator (e.g., "March 29th, 2024")
            date_str = date_str.replace('st,', ',').replace('nd,', ',').replace('rd,', ',').replace('th,', ',')
            return datetime.strptime(date_str.strip(), '%B %d, %Y')
        except ValueError:
            # If parsing fails, return current date
            return datetime.now()

    def get_blog_metadata(filename):
        filepath = os.path.join(BLOG_FOLDER, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Parse the first line as title and second line as date
        lines = content.split('\n')
        title = lines[0].strip()
        date_str = lines[1].strip() if len(lines) > 1 else ""
        
        # Parse the date
        date_obj = parse_date(date_str)
        
        # Get the excerpt from the first paragraph after title and date
        content_lines = [line for line in lines[3:] if line.strip()]
        excerpt = content_lines[0] if content_lines else ""
        
        # Clean excerpt from markdown syntax
        excerpt = re.sub(r'[#*`_]', '', excerpt).strip()
        
        # Get category from filename (you can modify this logic)
        category = filename.split('-')[0].replace('-', ' ').title()
        
        # Get the raw content (for editing)
        content = '\n'.join(lines[3:]) if len(lines) > 3 else ""
        
        # Generate keywords from content
        keywords = generate_keywords(title, excerpt, category)
        
        return {
            'title': title,
            'date': date_obj.strftime('%B %d, %Y'),
            'date_iso': date_obj.isoformat(),
            'excerpt': excerpt,
            'category': category,
            'content': content,
            'slug': os.path.splitext(filename)[0],
            'keywords': keywords,
            'thumbnail': url_for('static', filename=f'uploads/{os.path.splitext(filename)[0]}.jpg', _external=True)
                if os.path.exists(os.path.join(UPLOAD_FOLDER, f'{os.path.splitext(filename)[0]}.jpg'))
                else None
        }

    def generate_keywords(title, excerpt, category):
        """Generate keywords from blog content"""
        # Combine title, excerpt and category
        combined = f"{title} {excerpt} {category}"
        # Remove special chars and split
        words = re.sub(r'[^\w\s]', '', combined.lower()).split()
        # Remove common words
        stop_words = {'the', 'is', 'and', 'to', 'a', 'in', 'that', 'of', 'i', 'it', 'for', 'with'}
        keywords = [word for word in words if word not in stop_words and len(word) > 3]
        # Return unique keywords
        return ', '.join(set(keywords[:10]))
    
    def extract_headings(html_content):
        """Extract h2 and h3 headings from HTML content for blog table of contents"""
        soup = BeautifulSoup(html_content, 'html.parser')
        headings = []
        
        for heading in soup.find_all(['h2', 'h3']):
            # Generate an ID from the heading text
            heading_id = re.sub(r'[^\w\s-]', '', heading.text.lower())
            heading_id = re.sub(r'[\s-]+', '-', heading_id).strip('-')
            
            # Set the ID in the HTML
            heading['id'] = heading_id
            
            headings.append({
                'level': int(heading.name[1]),
                'text': heading.text,
                'id': heading_id
            })
            
        return headings, str(soup)

    def blogs():
        # Get all markdown files from the blogs folder
        blog_files = [f for f in os.listdir(BLOG_FOLDER) if f.endswith('.md')]
        blogs = []
        
        for filename in blog_files:
            try:
                blogs.append(get_blog_metadata(filename))
            except Exception as e:
                app.logger.error(f"Error processing blog {filename}: {str(e)}")
                continue
            
        # Sort blogs by date, newest first
        blogs.sort(key=lambda x: datetime.strptime(x['date'], '%B %d, %Y'), reverse=True)
        
        return render_template('pages/blogs.html', 
                             blogs=blogs,
                             meta_title="Blog | Krishna Kumar Soni",
                             meta_description="Read articles on product development, management, and technical solutions by Krishna Kumar Soni.",
                             meta_keywords="blogs, articles, product development, product management, tech insights",
                             is_local=request.host.startswith('127.0.0.1') or request.host.startswith('localhost'))

    def blog(slug):
        filepath = os.path.join(BLOG_FOLDER, f'{slug}.md')
        if not os.path.exists(filepath):
            return redirect(url_for('blogs'))
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Convert markdown to HTML
        html_content = markdown.markdown(content)
        
        # Extract headings for table of contents and update HTML
        toc, html_content = extract_headings(html_content)
        
        blog_data = get_blog_metadata(f'{slug}.md')
        blog_data['content'] = html_content
        blog_data['toc'] = toc
        
        # Structured data
        blog_json_ld = {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": blog_data['title'],
            "datePublished": blog_data['date_iso'],
            "dateModified": blog_data['date_iso'],
            "description": blog_data['excerpt'],
            "keywords": blog_data['keywords'],
            "author": {
                "@type": "Person",
                "name": "Krishna Kumar Soni"
            }
        }
        
        if blog_data['thumbnail']:
            blog_json_ld["image"] = blog_data['thumbnail']
        
        return render_template('pages/blog.html', 
                             blog=blog_data,
                             meta_title=f"{blog_data['title']} | Krishna Kumar Soni Blog",
                             meta_description=blog_data['excerpt'],
                             meta_keywords=blog_data['keywords'],
                             og_image=blog_data['thumbnail'],
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
            
        # Create slug from title
        slug = '-'.join(title.lower().split())
        
        # Save the markdown file
        filepath = os.path.join(BLOG_FOLDER, f'{slug}.md')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f'{title}\n')
            f.write(f'{datetime.now().strftime("%B %d, %Y")}\n\n')
            f.write(content)
            
        # Save thumbnail if provided
        if thumbnail:
            filename = secure_filename(f'{slug}.jpg')
            thumbnail.save(os.path.join(UPLOAD_FOLDER, filename))
            
        return redirect(url_for('blogs'))

    def edit_blog():
        if not (request.host.startswith('127.0.0.1') or request.host.startswith('localhost')):
            return redirect(url_for('blogs'))
            
        slug = request.form.get('slug')
        title = request.form.get('title')
        category = request.form.get('category')
        content = request.form.get('content')
        thumbnail = request.files.get('thumbnail')
        
        if not all([slug, title, category, content]):
            flash('All fields are required')
            return redirect(url_for('blogs'))
            
        # Get the original file to preserve the date
        filepath = os.path.join(BLOG_FOLDER, f'{slug}.md')
        if not os.path.exists(filepath):
            flash('Blog post not found')
            return redirect(url_for('blogs'))
            
        try:
            # Read the original date
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.read().split('\n')
                original_date = lines[1] if len(lines) > 1 else datetime.now().strftime('%B %d, %Y')
            
            # Create new slug from category and title
            title_slug = '-'.join(title.lower().split())
            category_slug = '-'.join(category.lower().split())
            new_slug = f'{category_slug}-{title_slug}'
            new_filepath = os.path.join(BLOG_FOLDER, f'{new_slug}.md')
            
            # Check if new path would overwrite a different existing file
            if new_filepath != filepath and os.path.exists(new_filepath):
                flash('A blog post with this title already exists')
                return redirect(url_for('blogs'))
            
            # Save the updated markdown file
            with open(new_filepath, 'w', encoding='utf-8') as f:
                f.write(f'{title}\n')
                f.write(f'{original_date}\n\n')
                f.write(content)
            
            # If filename changed, handle file moves
            if new_filepath != filepath:
                # Remove old markdown file
                os.remove(filepath)
                
                # Handle thumbnail rename
                old_thumb = os.path.join(UPLOAD_FOLDER, f'{slug}.jpg')
                new_thumb = os.path.join(UPLOAD_FOLDER, f'{new_slug}.jpg')
                if os.path.exists(old_thumb):
                    os.rename(old_thumb, new_thumb)
            
            # Handle new thumbnail upload
            if thumbnail:
                filename = secure_filename(f'{new_slug}.jpg')
                thumbnail_path = os.path.join(UPLOAD_FOLDER, filename)
                thumbnail.save(thumbnail_path)
            
            flash('Blog updated successfully')
            return redirect(url_for('blogs'))
            
        except Exception as e:
            app.logger.error(f"Error updating blog: {str(e)}")
            flash('Error updating blog')
            return redirect(url_for('blogs'))

    # Register routes after all functions are defined
    app.add_url_rule('/blogs', 'blogs', blogs)
    app.add_url_rule('/blog/<slug>', 'blog', blog)
    app.add_url_rule('/add_blog', 'add_blog', add_blog, methods=['POST'])
    app.add_url_rule('/edit_blog', 'edit_blog', edit_blog, methods=['POST']) 