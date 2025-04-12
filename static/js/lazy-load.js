/**
 * Lazy loading implementation for images to improve page speed and Core Web Vitals
 */
document.addEventListener('DOMContentLoaded', function() {
    const lazyImages = document.querySelectorAll('[data-src]');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    
                    if (img.dataset.srcset) {
                        img.srcset = img.dataset.srcset;
                    }
                    
                    img.classList.add('loaded');
                    imageObserver.unobserve(img);
                    
                    // Track in GTM if available
                    if (window.dataLayer) {
                        window.dataLayer.push({
                            'event': 'image_loaded',
                            'image_url': img.src
                        });
                    }
                }
            });
        }, {
            rootMargin: '0px 0px 200px 0px' // Load images 200px before they appear in viewport
        });
        
        lazyImages.forEach(img => {
            imageObserver.observe(img);
        });
    } else {
        // Fallback for browsers that don't support IntersectionObserver
        lazyImages.forEach(img => {
            img.src = img.dataset.src;
            if (img.dataset.srcset) {
                img.srcset = img.dataset.srcset;
            }
        });
    }
}); 