# Krishna Kumar Soni's Portfolio

A minimal, modern portfolio website built with Flask.

## Features
- Interactive bongo drums with keyboard shortcuts
- Responsive design
- Content management system
- Accessibility focused

## Setup

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the development server:
```bash
flask run
```

## Development

- `static/` - Contains all static assets
- `templates/` - Contains all Jinja2 templates
- `content/` - Contains all markdown content
- `app.py` - Main Flask application

## Production
For production deployment:
1. Set `FLASK_ENV=production`
2. Use a production WSGI server (e.g., Gunicorn)
3. Set up proper caching headers
4. Enable compression

## License
MIT 