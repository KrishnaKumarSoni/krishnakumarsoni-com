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

# Firebase Authentication Setup

This application uses Firebase for authentication and storage. Follow these steps to properly set up Firebase credentials:

## For Development

1. Create a `.env` file at the root of the project with the following Firebase configuration variables:

```
# Firebase Configuration (Storage)
FIREBASE_API_KEY=your-api-key
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_AUTH_DOMAIN=your-auth-domain
FIREBASE_STORAGE_BUCKET=your-storage-bucket
FIREBASE_MESSAGING_SENDER_ID=your-sender-id
FIREBASE_APP_ID=your-app-id
FIREBASE_MEASUREMENT_ID=your-measurement-id

# Firebase Auth Configuration
AUTH_PROJECT_ID=your-auth-project-id
AUTH_PRIVATE_KEY_ID=your-private-key-id
AUTH_PRIVATE_KEY=your-private-key
AUTH_CLIENT_EMAIL=your-client-email
AUTH_CLIENT_ID=your-client-id
AUTH_CLIENT_CERT_URL=your-client-cert-url
```

## For Vercel Deployment

When deploying to Vercel, add these environment variables in the Vercel dashboard:

1. Go to your project in the Vercel dashboard
2. Go to Settings > Environment Variables
3. Add all the Firebase configuration variables from your `.env` file

### Important: Handling the Private Key in Vercel

For the `AUTH_PRIVATE_KEY` in Vercel:

1. Download a fresh service account key from the Firebase console (JSON format)
2. Open the JSON file and copy the `private_key` value
3. Paste it directly into Vercel without any further formatting - Vercel will properly handle the newlines

## Authentication Issues Troubleshooting

If you encounter authentication issues:

1. Make sure all environment variables are correctly set
2. Verify that your Firebase service account has proper permissions
3. For local development, you can regenerate the credentials file by running:

```
python generate_credentials.py
```

This will create a `firebase-credentials.json` file from your environment variables that can be used for local development.

## Folder Structure

```
/app
  /auth
    routes.py   # Authentication routes
    firebase.py # Firebase auth functions
  firebase_config.py # Firebase initialization
``` 