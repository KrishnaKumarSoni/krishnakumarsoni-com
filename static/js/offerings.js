document.addEventListener('DOMContentLoaded', function() {
    console.log('Offerings page loaded');
    
    // Offering-specific functionality
    const offeringCardsContainer = document.querySelector('.offering-cards-container');
    
    // Offering icons
    const offeringIcons = {
        'for-students': 'ph-student',
        'for-early-professionals': 'ph-briefcase',
        'for-early-founders': 'ph-rocket-launch',
        'for-businesses': 'ph-buildings'
    };
    
    // Define which offering is popular
    const popularOffering = 'for-early-professionals';
    
    // Original prices for display
    const originalPrices = {
        'for-students': '₹999',
        'for-early-professionals': '₹2999',
        'for-early-founders': '₹10,999',
        'for-businesses': '₹24,999'
    };
    
    // Handle image loading errors
    document.addEventListener('error', function(e) {
        const target = e.target;
        // If the error occurred on an image element within a product card
        if (target.tagName.toLowerCase() === 'img' && target.closest('.product-image')) {
            console.log('Image failed to load:', target.src);
            // Set placeholder image with correct path
            target.src = '/static/images/placeholder.jpg';
            // Add class for styling
            target.classList.add('placeholder-img');
        }
    }, true); // Use capture to catch the error before it bubbles
    
    // Fetch offerings data
    fetch('/static/configurations/offerings.json')
        .then(response => response.json())
        .then(data => {
            const offerings = data.offerings;
            
            // Create offering cards for all offerings
            offerings.forEach(offering => {
                const offeringCard = document.createElement('div');
                offeringCard.className = 'offering-card';
                offeringCard.dataset.id = offering.id;
                
                // Format price with comma for thousands
                const formattedPrice = new Intl.NumberFormat('en-IN', {
                    style: 'currency',
                    currency: 'INR',
                    maximumFractionDigits: 0
                }).format(offering.price);
                
                // Determine if slots are limited
                const slotsClass = offering.slots_limited ? 'offering-slots limited' : 'offering-slots';
                
                // Create benefits list HTML
                let benefitsHTML = '';
                if (offering.benefits && offering.benefits.length > 0) {
                    benefitsHTML = '<div class="what-you-get"><h4>What You Get:</h4><ul class="benefits-list">';
                    offering.benefits.forEach(benefit => {
                        benefitsHTML += `<li><i class="ph ph-check-circle"></i>${benefit}</li>`;
                    });
                    benefitsHTML += '</ul></div>';
                }
                
                // Add popular tag if marked as popular
                const popularTag = offering.id === popularOffering ? '<div class="popular-tag">Popular</div>' : '';
                
                offeringCard.innerHTML = `
                    ${popularTag}
                    <div class="offering-card-header">
                        <div class="offering-card-icon">
                            <i class="ph ${offeringIcons[offering.id] || 'ph-star'}"></i>
                        </div>
                        <h3>${offering.title}</h3>
                    </div>
                    <div class="offering-card-content">
                        <p>${offering.description}</p>
                        ${benefitsHTML}
                        <div class="offering-card-meta">
                            <div class="slots-container">
                                <span class="${slotsClass}">
                                    <i class="ph ph-user-circle"></i>${offering.slots_left} slots left this month
                                </span>
                            </div>
                            <div class="price-container">
                                <span class="original-price">${originalPrices[offering.id] || formattedPrice}</span>
                                <span class="offering-price">${formattedPrice}</span>
                            </div>
                        </div>
                    </div>
                    <div class="offering-card-footer">
                        <button class="offering-cta" data-product="${offering.id}">
                            <i class="ph ph-shopping-cart-simple"></i> Add to Cart
                        </button>
                        <button class="buy-now-btn" data-product="${offering.id}">
                            <i class="ph ph-lightning"></i> Buy Now
                        </button>
                    </div>
                `;
                
                offeringCardsContainer.appendChild(offeringCard);
            });
            
            // Set up event listeners for all offering cards
            document.querySelectorAll('.offering-cta').forEach(button => {
                button.addEventListener('click', function() {
                    const productId = this.dataset.product;
                    
                    // Get cart items from localStorage
                    const cartItems = new Set(JSON.parse(localStorage.getItem('cartItems')) || []);
                    
                    // Toggle selected state
                    if (cartItems.has(productId)) {
                        // Trigger product:removed event
                        const event = new CustomEvent('product:removed', {
                            detail: { productId }
                        });
                        document.dispatchEvent(event);
                    } else {
                        // Trigger product:added event
                        const event = new CustomEvent('product:added', {
                            detail: { productId }
                        });
                        document.dispatchEvent(event);
                    }
                });
                
                // Set initial state based on localStorage
                const productId = button.dataset.product;
                const cartItems = new Set(JSON.parse(localStorage.getItem('cartItems')) || []);
                if (cartItems.has(productId)) {
                    button.innerHTML = '<i class="ph ph-check"></i> Selected';
                }
            });
            
            // Set up Buy Now buttons (will be implemented later)
            document.querySelectorAll('.buy-now-btn').forEach(button => {
                button.addEventListener('click', function() {
                    const productId = this.dataset.product;
                    console.log('Buy Now clicked for product:', productId);
                    // Functionality will be added later
                });
            });
        })
        .catch(error => {
            console.error('Error loading offerings configuration:', error);
        });
}); 