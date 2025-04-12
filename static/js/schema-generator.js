/**
 * Generate and inject schema.org structured data for pages that don't have custom schema
 */
document.addEventListener('DOMContentLoaded', function() {
    // Only generate schema if none exists already
    if (document.querySelectorAll('script[type="application/ld+json"]').length === 0) {
        // Get meta values
        const title = document.title || 'Krishna Kumar Soni';
        const description = document.querySelector('meta[name="description"]')?.content || 
                           'Product Development & Management Specialist';
        const url = window.location.href;
        const ogImage = document.querySelector('meta[property="og:image"]')?.content;
        
        // Create basic WebPage schema
        const schema = {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": title,
            "description": description,
            "url": url
        };
        
        // Add image if available
        if (ogImage) {
            schema.image = ogImage;
        }
        
        // Add the schema to the page
        const script = document.createElement('script');
        script.type = 'application/ld+json';
        script.textContent = JSON.stringify(schema);
        document.head.appendChild(script);
    }
}); 