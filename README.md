# Krishna Kumar Soni - Portfolio Website

A modern, content-driven portfolio website built with Flask and modern web technologies. The site features a dynamic content management system using markdown files, SEO optimization, and integrated analytics.

## Tech Stack

### Backend
- **Flask** (v3.0.2): Python web framework for serving the application
- **Python** (3.x): Core programming language
- **Markdown**: Content management through markdown files
- **YAML**: Configuration management
- **Firebase**: Storage solution for media and assets

### Frontend
- **HTML/CSS/JavaScript**: Core frontend technologies
- **Node.js**: Supporting JavaScript runtime for specific utilities
- **Twilio**: Integration for communication features

## Project Structure

```
.
├── app/                    # Core application components
├── content/               # Markdown content files
│   ├── blogs/            # Blog post markdown files
│   ├── home/             # Home page content
│   ├── offerings/        # Services/offerings content
│   ├── solutions/        # Solutions page content
│   └── resume/           # Resume page content
├── static/               # Static assets
├── templates/            # HTML templates
├── app.py               # Main Flask application
├── blog_routes.py       # Blog-specific routes
├── requirements.txt     # Python dependencies
└── package.json         # Node.js dependencies
```

## Key Features

1. **Content Management System**
   - Markdown-based content management
   - Dynamic content rendering
   - SEO metadata extraction from markdown files

2. **Blog System**
   - Markdown-based blog posts
   - Automatic sitemap generation
   - SEO optimization

3. **Dynamic Routing**
   - Clean URL structure
   - Error handling (404, 500)
   - Static file serving

4. **SEO Optimization**
   - Dynamic meta tags
   - Sitemap.xml generation
   - robots.txt configuration

5. **Analytics & Tracking**
   - Custom tracking configuration
   - YAML-based tracking setup
   - API endpoint for tracking configuration

## Configuration

### Environment Variables (.env)
- `DATABASE_URL`: PostgreSQL database connection
- `HASH_SALT`: Salt for hashing functions
- `APP_SECRET`: Application secret key
- `TRACKER_SCRIPT_NAME`: Analytics script name
- `FIREBASE_*`: Firebase configuration
- `TWILIO_*`: Twilio configuration

### Firebase Configuration
The project uses Firebase for storage with the following configurations:
- API Key
- Project ID
- Auth Domain
- Storage Bucket
- Messaging Sender ID
- App ID
- Measurement ID

## Setup & Installation

1. **Python Environment Setup**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Node.js Dependencies**
   ```bash
   npm install
   ```

3. **Environment Configuration**
   - Copy `.env.example` to `.env`
   - Fill in required environment variables

4. **Content Setup**
   - Ensure content directory structure is in place
   - Add markdown files for pages

## Development

1. **Running Locally**
   ```bash
   flask run
   ```

2. **Content Management**
   - Add/edit markdown files in the `content/` directory
   - Follow markdown file structure for SEO metadata

3. **Template Modification**
   - Templates are in the `templates/` directory
   - Follow existing template structure for consistency

## Deployment

The project is configured for Vercel deployment with:
- Python 3.x runtime
- Flask WSGI application
- Automatic environment variable configuration

## Security Considerations

- Environment variables for sensitive data
- Firebase security rules
- Twilio authentication tokens
- CORS and security headers

## License

ISC License

## Author

Krishna Kumar Soni 

## Design System

### Core Design Principles
- Modern, clean aesthetic with focus on readability
- Consistent spacing and component patterns
- Responsive design with mobile-first approach
- Smooth transitions and micro-interactions
- Accessible color contrast and interactive states

### Color System
```css
/* Primary Colors */
--burnt-orange: #D35400      /* Brand primary */
--burnt-orange-light: #FF7D2A /* Hover states */
--burnt-orange-dark: #B24600  /* Active states */

/* Text Colors */
--text-dark: #2C3E50    /* Headers, important text */
--text-medium: #5D6D7E  /* Body text */
--text-light: #8395A7   /* Secondary text */

/* Accent Colors */
--funky-teal: #13B0A5
--funky-purple: #9D4EDD
--funky-yellow: #FFD60A
--funky-pink: #FF5A7E
```

### Typography
- **Primary Font**: 'Plus Jakarta Sans' - Body text, UI elements
- **Secondary Font**: 'Space Grotesk' - Headings, display text
- **Base Font Size**: 16px (1rem)
- **Scale**: Modular scale with 1.2 ratio

### Spacing System
```css
--spacing-unit: 8px
/* Usage: multiples of spacing unit */
- 0.5x (4px)  - Tiny elements
- 1x (8px)    - Small gaps
- 2x (16px)   - Standard spacing
- 3x (24px)   - Section spacing
- 4x (32px)   - Large sections
```

### Border Radius
```css
--border-radius-sm: 12px  /* Buttons, small elements */
--border-radius-md: 20px  /* Cards, containers */
--border-radius-lg: 32px  /* Large sections */
```

### Transitions
```css
--transition-fast: 0.2s ease
--transition-smooth: 0.3s cubic-bezier(0.4, 0, 0.2, 1)
--transition-bounce: 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275)
```

### Component Library

#### Buttons
1. **Primary Button (connect-btn)**
   - Orange gradient background
   - White text
   - Hover: Scale + color shift
   - Active: Press animation
   ```css
   padding: 1rem 2.5rem
   border-radius: var(--border-radius-md)
   font-weight: 500
   ```

2. **Secondary Button (visit-button)**
   - Solid orange background
   - White text
   - Hover: Lift animation
   ```css
   padding: 0.75rem 2rem
   border-radius: var(--border-radius-sm)
   ```

3. **Action Button (add-to-cart)**
   - Gradient background
   - Icon + text combination
   - Hover: Scale + shadow
   ```css
   padding: 0.75rem 1.75rem
   border-radius: 16px
   box-shadow: 0 2px 4px rgba(211, 84, 0, 0.2)
   ```

#### Cards
1. **Offering Cards**
   ```css
   background: #fff
   border: 1px solid rgba(0, 0, 0, 0.08)
   padding: 1.25rem
   border-radius: 16px
   transition: transform 0.2s ease
   ```

2. **Product Cards**
   - Hover animations
   - Selected state styling
   - Action button integration

### Layout System
1. **Container Widths**
   ```css
   .container {
     max-width: 1200px  /* Main container */
   }
   .content-width {
     max-width: 900px   /* Content areas */
   }
   ```

2. **Grid System**
   - Responsive grid using CSS Grid
   - Auto-fit columns with minmax
   ```css
   grid-template-columns: repeat(auto-fit, minmax(300px, 1fr))
   gap: 1.5rem
   ```

### Responsive Breakpoints
```css
/* Mobile First Approach */
@media (max-width: 480px)  { /* Small mobile */ }
@media (max-width: 768px)  { /* Tablet/Mobile */ }
@media (max-width: 1200px) { /* Desktop */ }
```

### CSS Architecture
- **Modular CSS**: Each component has its own CSS file
- **Base Styles**: Global resets and variables
- **Component Styles**: Isolated component styling
- **Utility Classes**: Common helper classes
- **Page-Specific Styles**: Custom page layouts

### Best Practices
1. **CSS Variables**
   - Centralized in base.css
   - Consistent naming convention
   - Easy theme customization

2. **Performance**
   - Minimal nesting
   - Optimized selectors
   - Reusable components

3. **Accessibility**
   - High contrast colors
   - Focus states
   - Touch targets (min 44px)
   - Screen reader support

4. **Mobile Optimization**
   - Touch-friendly interactions
   - Responsive images
   - Flexible layouts
   - iOS/Android compatibility 

## Design System Architecture

The design system follows a modular architecture to ensure consistency, reduce duplication, and make design changes easier to manage.

### Directory Structure
```
static/css/
├── design-system/
│   ├── tokens/
│   │   ├── _colors.css      # Color system variables
│   │   ├── _typography.css  # Typography scale and fonts
│   │   ├── _spacing.css     # Spacing units and scale
│   │   └── _layout.css      # Layout tokens (breakpoints, containers)
│   └── components/
│       ├── _buttons.css     # Button components
│       └── _cards.css       # Card components
├── base.css                 # Base styles and resets
├── main.css                # Main entry point
└── [component].css         # Individual component styles
```

### Design Tokens

1. **Colors**
   ```css
   --color-brand-primary: #D35400;
   --color-text-primary: #2C3E50;
   --gradient-brand-primary: linear-gradient(...);
   ```

2. **Typography**
   ```css
   --font-family-primary: 'Plus Jakarta Sans'...;
   --font-size-base: 1rem;
   --line-height-normal: 1.5;
   ```

3. **Spacing**
   ```css
   --spacing-unit: 8px;
   --spacing-md: calc(var(--spacing-unit) * 2);
   --section-spacing-lg: var(--spacing-3xl);
   ```

4. **Layout**
   ```css
   --radius-md: 20px;
   --container-max-width: 1200px;
   --transition-smooth: 0.3s cubic-bezier(...);
   ```

### Component System

Components follow a consistent pattern using design tokens:

```css
.component {
  /* Use spacing tokens */
  padding: var(--spacing-md);
  
  /* Use color tokens */
  background: var(--color-background-primary);
  color: var(--color-text-primary);
  
  /* Use layout tokens */
  border-radius: var(--radius-md);
  transition: var(--transition-smooth);
}
```

### Usage Guidelines

1. **Token Usage**
   - Always use design tokens instead of hard-coded values
   - Follow the established naming conventions
   - Use semantic token names when possible

2. **Component Creation**
   - Extend base components using modifiers
   - Follow BEM naming convention
   - Keep components single-responsibility

3. **Responsive Design**
   - Use breakpoint tokens for media queries
   - Follow mobile-first approach
   - Use fluid spacing when appropriate

4. **Performance**
   - Minimize selector specificity
   - Use CSS custom properties for dynamic values
   - Avoid deep nesting

### File Import Order
1. Design Tokens
2. Base Styles
3. Components
4. Layout Components
5. UI Components
6. Page Sections
7. Page-specific Styles

This ensures proper cascade and specificity management. 