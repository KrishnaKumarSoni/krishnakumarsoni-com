/**
 * This script generates dynamic Open Graph images for pages without custom thumbnails.
 * It can be used to create social sharing preview images on-the-fly.
 */
document.addEventListener('DOMContentLoaded', function() {
    // Check if we need to generate an OG image (only run in admin/dev mode)
    const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    const ogImage = document.querySelector('meta[property="og:image"]');
    
    if (isLocal && ogImage && ogImage.content.includes('og-image.jpg')) {
        console.log('Generating dynamic OG image for local development...');
        
        // Get page title and description
        const title = document.title || 'Krishna Kumar Soni';
        const description = document.querySelector('meta[name="description"]')?.content || 
                           'Product Development & Management Specialist';
        
        // We would integrate with a service like https://og-image.vercel.app/ here
        // For now we'll just log the values
        console.log('Title for OG Image:', title);
        console.log('Description for OG Image:', description);
        
        // A real implementation would make an API call to generate the image
        // and then update the og:image meta tag
    }
}); 