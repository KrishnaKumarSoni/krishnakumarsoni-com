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
    
    // Initialize selectedItems from localStorage or create new Set
    let selectedItems = new Set(JSON.parse(localStorage.getItem('cartItems')) || []);
    let isEmailMode = false;

    // Initially hide the cart widget and details
    cartWidget.style.display = 'none';
    cartDetails.classList.remove('expanded');

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
        
        // Update cart items
        cartItems.innerHTML = '';
        selectedItems.forEach(productId => {
            // Find the product in the PRODUCTS array
            const product = PRODUCTS.find(p => p.id === productId);
            if (product) {
                const itemElement = document.createElement('div');
                itemElement.className = 'cart-item';
                itemElement.innerHTML = `
                    <span class="item-name">${product.title}</span>
                    <span class="item-price">₹0</span>
                `;
                cartItems.appendChild(itemElement);
            }
        });
    }

    function clearCart() {
        selectedItems.clear();
        
        // Deselect all product cards
        document.querySelectorAll('.product-card').forEach(card => {
            card.classList.remove('selected');
            const addButton = card.querySelector('.add-to-cart');
            if (addButton) {
                addButton.innerHTML = '<i class="ph ph-shopping-cart-simple"></i> Add to Cart';
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
        
        // Make sure the product card is visually selected
        const productCard = document.querySelector(`.product-card[data-id="${productId}"]`);
        if (productCard) {
            productCard.classList.add('selected');
            const addButton = productCard.querySelector('.add-to-cart');
            if (addButton) {
                addButton.innerHTML = '<i class="ph ph-check"></i> Selected';
            }
        }
    });

    document.addEventListener('product:removed', function(e) {
        const productId = e.detail.productId;
        selectedItems.delete(productId);
        updateCart();
        
        // Make sure the product card is visually unselected
        const productCard = document.querySelector(`.product-card[data-id="${productId}"]`);
        if (productCard) {
            productCard.classList.remove('selected');
            const addButton = productCard.querySelector('.add-to-cart');
            if (addButton) {
                addButton.innerHTML = '<i class="ph ph-shopping-cart-simple"></i> Add to Cart';
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
            document.querySelectorAll('.product-card').forEach(card => {
                card.classList.remove('selected');
                const addButton = card.querySelector('.add-to-cart');
                if (addButton) {
                    addButton.innerHTML = '<i class="ph ph-shopping-cart-simple"></i> Add to Cart';
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
        document.querySelectorAll('.product-card').forEach(card => {
            const productId = card.dataset.id;
            if (selectedItems.has(productId)) {
                card.classList.add('selected');
                const addButton = card.querySelector('.add-to-cart');
                if (addButton) {
                    addButton.innerHTML = '<i class="ph ph-check"></i> Selected';
                }
            }
        });
    }

    // Initialize cart state
    updateCart();
    console.log('Cart initialized');
}); 