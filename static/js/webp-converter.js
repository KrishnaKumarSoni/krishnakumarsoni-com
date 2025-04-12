/**
 * WebP image conversion helper for admin use only
 * This script helps convert images to WebP format for better performance
 * It runs only in localhost/development environment
 */
document.addEventListener('DOMContentLoaded', function() {
    // Only run in local development
    const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    
    if (!isLocal) return;
    
    // Check if we're on an admin page with image upload capabilities
    const imageUploads = document.querySelectorAll('input[type="file"][accept*="image"]');
    
    if (imageUploads.length === 0) return;
    
    // Add conversion helper notice
    const adminSection = document.querySelector('.admin-section') || document.body;
    const notice = document.createElement('div');
    notice.className = 'webp-converter-notice';
    notice.innerHTML = `
        <h3>Image Optimization</h3>
        <p>Images uploaded will be automatically optimized for web performance:</p>
        <ul>
            <li>Converted to WebP format for faster loading</li>
            <li>Resized to appropriate dimensions</li>
            <li>Compressed for optimal file size</li>
        </ul>
        <p>For best SEO results, remember to:</p>
        <ul>
            <li>Use descriptive filenames (e.g., "product-development-workshop.jpg")</li>
            <li>Always add ALT text describing the image</li>
        </ul>
    `;
    
    // Add notice styling
    notice.style.backgroundColor = '#f8f9fa';
    notice.style.padding = '15px';
    notice.style.borderRadius = '5px';
    notice.style.marginBottom = '20px';
    notice.style.border = '1px solid #dee2e6';
    
    // Insert at the top of upload forms
    adminSection.insertBefore(notice, adminSection.firstChild);
    
    console.log('WebP converter helper initialized in development mode');
}); 