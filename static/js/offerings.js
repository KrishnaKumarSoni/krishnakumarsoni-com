document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded');
    const cartWidget = document.querySelector('.cart-widget');
    const cartCount = document.querySelector('.cart-count');
    const cartItems = document.querySelector('.cart-items');
    const expandCart = document.querySelector('.expand-cart');
    const cartDetails = document.querySelector('.cart-details');
    const payButton = document.querySelector('.pay-button');
    const payContainer = document.querySelector('.pay-container');
    const emailInput = document.querySelector('.email-input');
    const submitEmail = document.querySelector('.submit-email');
    const closeBanner = document.querySelector('.close-banner');
    const totalPrice = document.querySelector('.total-price');
    const totalAmount = document.querySelector('.total-amount');
    
    // Initialize selectedItems from localStorage or create new Set
    let selectedItems = new Set(JSON.parse(localStorage.getItem('cartItems')) || []);
    let isEmailMode = false;
    let OFFERINGS = [];

    // Initially hide the cart widget and details
    cartWidget.style.display = 'none';
    cartDetails.classList.remove('expanded');

    // Fetch offerings data
    fetch('/static/configurations/offerings.json')
        .then(response => response.json())
        .then(data => {
            OFFERINGS = data.offerings;
            updateInitialState();
        })
        .catch(error => {
            console.error('Error loading offerings configuration:', error);
        });

    function updateInitialState() {
        // Set initial state for offering cards based on localStorage
        document.querySelectorAll('.offering-card').forEach(card => {
            const productId = card.dataset.id;
            const ctaButton = card.querySelector('.offering-cta');
            
            if (selectedItems.has(productId)) {
                ctaButton.innerHTML = '<i class="ph ph-check"></i> Selected';
            }
        });
        
        // Initialize cart
        updateCart();
    }

    function updateCart() {
        const count = selectedItems.size;
        cartCount.textContent = count;
        
        // Save to localStorage
        localStorage.setItem('cartItems', JSON.stringify([...selectedItems]));
        
        // Update nav badge count
        updateNavBadge(count);
        
        // Show/hide cart widget based on selection
        if (count > 0) {
            cartWidget.style.display = 'block';
            cartWidget.offsetHeight; // Trigger reflow
            cartWidget.classList.add('visible');
        } else {
            cartWidget.classList.remove('visible');
            setTimeout(() => {
                if (selectedItems.size === 0) {
                    cartWidget.style.display = 'none';
                }
            }, 300);
        }
        
        // Calculate total price
        let total = 0;
        
        // Update cart items
        cartItems.innerHTML = '';
        selectedItems.forEach(productId => {
            // Find the offering in the OFFERINGS array
            const offering = OFFERINGS.find(o => o.id === productId);
            if (offering) {
                const itemElement = document.createElement('div');
                itemElement.className = 'cart-item';
                
                // Format price with commas for thousands
                const formattedPrice = new Intl.NumberFormat('en-IN', {
                    style: 'currency',
                    currency: 'INR',
                    maximumFractionDigits: 0
                }).format(offering.price);
                
                itemElement.innerHTML = `
                    <span class="item-name">${offering.title}</span>
                    <span class="item-price">${formattedPrice}</span>
                `;
                cartItems.appendChild(itemElement);
                
                total += offering.price;
            }
        });
        
        // Format total with commas for thousands
        const formattedTotal = new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            maximumFractionDigits: 0
        }).format(total);
        
        // Update total display
        totalPrice.textContent = formattedTotal;
        totalAmount.textContent = formattedTotal;
    }

    function clearCart() {
        selectedItems.clear();
        
        // Deselect all offering cards
        document.querySelectorAll('.offering-card').forEach(card => {
            const ctaButton = card.querySelector('.offering-cta');
            if (ctaButton) {
                ctaButton.innerHTML = '<i class="ph ph-shopping-cart-simple"></i> Add to Cart';
            }
        });
        
        updateCart();
    }

    // Function to update the nav badge
    function updateNavBadge(count) {
        // Update all instances of the offerings nav badge (in case there are multiple)
        const navBadges = document.querySelectorAll('.offerings-badge');
        navBadges.forEach(badge => {
            if (count > 0) {
                badge.textContent = count;
                badge.style.display = 'flex';
            } else {
                badge.style.display = 'none';
            }
        });
    }

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

    // Listen for product added/removed events
    document.addEventListener('product:added', function(e) {
        const productId = e.detail.productId;
        selectedItems.add(productId);
        updateCart();
        
        // Make sure the offering card button is visually selected
        const offeringCard = document.querySelector(`.offering-card[data-id="${productId}"]`);
        if (offeringCard) {
            const ctaButton = offeringCard.querySelector('.offering-cta');
            if (ctaButton) {
                ctaButton.innerHTML = '<i class="ph ph-check"></i> Selected';
            }
        }
    });

    document.addEventListener('product:removed', function(e) {
        const productId = e.detail.productId;
        selectedItems.delete(productId);
        updateCart();
        
        // Make sure the offering card button is visually unselected
        const offeringCard = document.querySelector(`.offering-card[data-id="${productId}"]`);
        if (offeringCard) {
            const ctaButton = offeringCard.querySelector('.offering-cta');
            if (ctaButton) {
                ctaButton.innerHTML = '<i class="ph ph-shopping-cart-simple"></i> Add to Cart';
            }
        }
    });

    expandCart.addEventListener('click', function() {
        const isExpanded = cartDetails.classList.contains('expanded');
        cartDetails.classList.toggle('expanded');
        this.classList.toggle('expanded');
        
        // Always use Phosphor Icons for consistency
        if (isExpanded) {
            this.querySelector('i').className = 'ph ph-caret-down';
        } else {
            this.querySelector('i').className = 'ph ph-caret-up';
        }
    });

    payButton.addEventListener('click', function() {
        console.log('Pay button clicked');
        if (!isEmailMode) {
            payContainer.classList.add('show-email');
            isEmailMode = true;
            setTimeout(() => {
                emailInput.focus();
            }, 300);
        }
    });

    // Handle back button click
    const backButton = document.querySelector('.back-button');
    if (backButton) {
        backButton.addEventListener('click', function() {
            console.log('Back button clicked');
            payContainer.classList.remove('show-email');
            isEmailMode = false;
        });
    }

    function handleEmailSubmit(e) {
        e && e.preventDefault();
        console.log('Handling email submit');
        const email = emailInput.value.trim();
        
        if (email && isValidEmail(email)) {
            console.log('Email submitted:', email);
            payContainer.classList.remove('show-email');
            isEmailMode = false;
            emailInput.value = '';
            
            // Show thank you state first
            cartWidget.classList.add('thank-you-state');
            
            // Clear cart items but maintain visibility
            selectedItems.clear();
            document.querySelectorAll('.offering-card').forEach(card => {
                const ctaButton = card.querySelector('.offering-cta');
                if (ctaButton) {
                    ctaButton.innerHTML = '<i class="ph ph-shopping-cart-simple"></i> Add to Cart';
                }
            });
            
            // Clear localStorage cart
            localStorage.removeItem('cartItems');
            // Update nav badge
            updateNavBadge(0);
        } else {
            emailInput.reportValidity();
        }
    }

    submitEmail.addEventListener('click', handleEmailSubmit);
    
    emailInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleEmailSubmit(e);
        }
    });

    closeBanner.addEventListener('click', function() {
        console.log('Close banner clicked');
        
        // Remove visible class first to start fade out
        cartWidget.classList.remove('visible');
        
        // Wait for fade out, then remove thank you state and hide
        setTimeout(() => {
            cartWidget.classList.remove('thank-you-state');
            cartWidget.style.display = 'none';
        }, 300);
        
        // Clear cart when closing thank you banner
        clearCart();
    });

    function isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    // Mark selected products based on localStorage data when page loads
    if (selectedItems.size > 0) {
        document.querySelectorAll('.offering-card').forEach(card => {
            const productId = card.dataset.id;
            if (selectedItems.has(productId)) {
                const ctaButton = card.querySelector('.offering-cta');
                if (ctaButton) {
                    ctaButton.innerHTML = '<i class="ph ph-check"></i> Selected';
                }
            }
        });
    }

    // Initialize cart state
    updateCart();
    console.log('Cart initialized');
}); 