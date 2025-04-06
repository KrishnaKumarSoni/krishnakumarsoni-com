// Load products from the JSON configuration file
let PRODUCTS = [];

document.addEventListener('DOMContentLoaded', function() {
    // Fetch the product configuration
    fetch('/static/configurations/products.json')
        .then(response => response.json())
        .then(data => {
            PRODUCTS = data.products;
            // Dispatch an event to notify that products are loaded
            document.dispatchEvent(new CustomEvent('products:loaded'));
        })
        .catch(error => {
            console.error('Error loading products configuration:', error);
        });
}); 