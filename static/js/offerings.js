document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded');
    const cartWidget = document.querySelector('.cart-widget');
    const cartCount = document.querySelector('.cart-count');
    const cartItems = document.querySelector('.cart-items');
    const expandCart = document.querySelector('.expand-cart');
    const cartDetails = document.querySelector('.cart-details');
    const payButton = document.querySelector('.pay-button');
    const payContainer = document.querySelector('.pay-container');
    const phoneContainer = document.querySelector('.phone-container');
    const phoneInputContainer = document.querySelector('.phone-input-container');
    const otpInputContainer = document.querySelector('.otp-input-container');
    const checkoutButton = document.querySelector('.checkout-button');
    const phoneInput = document.querySelector('.phone-input');
    const sendOtpButton = document.querySelector('.submit-phone');
    const closeBanner = document.querySelector('.close-banner');
    const totalPrice = document.querySelector('.total-price');
    const totalAmount = document.querySelector('.total-amount');
    const offeringCardsContainer = document.querySelector('.offering-cards-container');
    const otpInputs = document.querySelectorAll('.otp-inputs input');
    const verifyOtpButton = document.querySelector('.verify-otp');
    
    console.log('Container element found:', offeringCardsContainer);

    // Initialize state
    let selectedItems = new Set(JSON.parse(localStorage.getItem('cartItems')) || []);
    let isEmailMode = false;
    let OFFERINGS = [];
    let currentPhoneNumber = localStorage.getItem('currentPhoneNumber') || '';
    let authToken = localStorage.getItem('authToken');

    // Offering icons mapping
    const offeringIcons = {
        'for-students': 'ph-student',
        'for-early-professionals': 'ph-briefcase',
        'for-early-founders': 'ph-rocket-launch',
        'for-businesses': 'ph-buildings'
    };

    // Restore UI state based on auth
    function restoreUIState() {
        if (authToken) {
            // User is authenticated
            payButton.style.display = 'none';
            phoneInputContainer.style.display = 'none';
            otpInputContainer.style.display = 'none';
            checkoutButton.style.display = 'flex';
        } else if (currentPhoneNumber) {
            // Phone verification in progress
            payButton.style.display = 'none';
            phoneInputContainer.style.display = 'none';
            otpInputContainer.style.display = 'flex';
            checkoutButton.style.display = 'none';
            phoneInput.value = currentPhoneNumber;
        } else {
            // Initial state
            payButton.style.display = 'flex';
            phoneInputContainer.style.display = 'none';
            otpInputContainer.style.display = 'none';
            checkoutButton.style.display = 'none';
        }
    }

    // Initially hide the cart widget and details
    cartWidget.style.display = 'none';
    cartDetails.classList.remove('expanded');

    // Restore UI state
    restoreUIState();

    // Snackbar functionality
    function showSnackbar(message, type = 'error') {
        const snackbar = document.getElementById('snackbar');
        if (!snackbar) {
            // Create snackbar if it doesn't exist
            const newSnackbar = document.createElement('div');
            newSnackbar.id = 'snackbar';
            document.body.appendChild(newSnackbar);
        }
        const snackbarElement = document.getElementById('snackbar');
        snackbarElement.textContent = message;
        snackbarElement.className = `show ${type}`;
        setTimeout(() => {
            snackbarElement.className = '';
        }, 3000);
    }

    // Handle Pay button click
    payButton.addEventListener('click', function() {
        payButton.style.display = 'none';
        phoneInputContainer.style.display = 'flex';
        phoneInput.focus();
    });

    // Load intl-tel-input dynamically
    function loadIntlTelInput() {
        return new Promise((resolve, reject) => {
            // Load CSS
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = 'https://cdn.jsdelivr.net/npm/intl-tel-input@18.2.1/build/css/intlTelInput.css';
            document.head.appendChild(link);

            // Load main script
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/intl-tel-input@18.2.1/build/js/intlTelInput.min.js';
            script.onload = () => {
                // Load utils script
                const utilsScript = document.createElement('script');
                utilsScript.src = 'https://cdn.jsdelivr.net/npm/intl-tel-input@18.2.1/build/js/utils.js';
                utilsScript.onload = resolve;
                document.head.appendChild(utilsScript);
            };
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    // Initialize phone input
    let iti;
    if (phoneInput) {
        loadIntlTelInput().then(() => {
            iti = window.intlTelInput(phoneInput, {
                initialCountry: 'auto',
                geoIpLookup: function(callback) {
                    fetch('https://ipapi.co/json')
                        .then(res => res.json())
                        .then(data => callback(data.country_code))
                        .catch(() => callback('in')); // Default to India if geolocation fails
                },
                separateDialCode: true,
                utilsScript: 'https://cdn.jsdelivr.net/npm/intl-tel-input@18.2.1/build/js/utils.js',
            });

            // Format the phone number on input
            phoneInput.addEventListener('input', function() {
                if (this.value.startsWith('+')) {
                    this.value = this.value.substring(1);
                }
            });
        }).catch(error => {
            console.error('Failed to load intl-tel-input:', error);
        });
    }

    // Handle phone number submission
    if (sendOtpButton) {
        console.log('Submit phone button found:', sendOtpButton);
        sendOtpButton.addEventListener('click', async function(e) {
            console.log('Submit phone button clicked');
            e.preventDefault();
            
            if (!phoneInput.value.trim()) {
                showSnackbar('Please enter a phone number');
                return;
            }

            let phoneNumber = phoneInput.value.trim();
            
            // If intl-tel-input is loaded, use it for validation and formatting
            if (iti) {
                if (!iti.isValidNumber()) {
                    showSnackbar('Please enter a valid phone number');
                    return;
                }
                phoneNumber = iti.getNumber(); // This already includes the + prefix
            } else {
                // Basic validation if library fails to load
                if (!/^\+?\d{10,15}$/.test(phoneNumber)) {
                    showSnackbar('Please enter a valid phone number');
                    return;
                }
                // Add + prefix if not present
                if (!phoneNumber.startsWith('+')) {
                    phoneNumber = '+' + phoneNumber;
                }
            }

            console.log('Phone number entered:', phoneNumber);

            try {
                console.log('Sending OTP request...');
                const response = await fetch('/auth/send-otp', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ 
                        phone_number: phoneNumber // Send with + prefix
                    }),
                    credentials: 'include'
                });

                console.log('OTP response received:', response.status);
                const data = await response.json();
                console.log('OTP response data:', data);

                if (data.success) {
                    currentPhoneNumber = phoneNumber;
                    localStorage.setItem('currentPhoneNumber', phoneNumber);
                    phoneInputContainer.style.display = 'none';
                    otpInputContainer.style.display = 'flex';
                    otpInputs[0].focus();
                    otpInputs.forEach(input => input.value = '');
                    showSnackbar('OTP sent successfully', 'success');
                } else {
                    showSnackbar(data.message || 'Failed to send OTP');
                }
            } catch (error) {
                console.error('Error sending OTP:', error);
                showSnackbar('Failed to send OTP');
            }
        });
    }

    // Handle back buttons
    document.querySelectorAll('.back-button').forEach(button => {
        button.addEventListener('click', function() {
            const container = this.closest('.phone-input-container, .otp-input-container');
            container.style.display = 'none';
            if (container.classList.contains('phone-input-container')) {
                payButton.style.display = 'flex';
                phoneInput.value = '';
                localStorage.removeItem('currentPhoneNumber');
            } else {
                phoneInputContainer.style.display = 'flex';
                otpInputs.forEach(input => input.value = '');
            }
        });
    });

    // Handle OTP input navigation
    otpInputs.forEach((input, index) => {
        input.addEventListener('input', function() {
            if (this.value.length === 1) {
                if (index < otpInputs.length - 1) {
                    otpInputs[index + 1].focus();
                } else {
                    verifyOtpButton.focus();
                }
            }
        });

        input.addEventListener('keydown', function(e) {
            if (e.key === 'Backspace' && !this.value && index > 0) {
                otpInputs[index - 1].focus();
            }
        });
    });

    // Handle verify OTP button click
    verifyOtpButton.addEventListener('click', async function() {
        const otpCode = Array.from(otpInputs).map(input => input.value).join('');
        if (otpCode.length !== 6) {
            showSnackbar('Please enter a valid 6-digit OTP');
            return;
        }

        try {
            const response = await fetch('/auth/verify-otp', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    phone_number: currentPhoneNumber,
                    code: otpCode
                }),
                credentials: 'include'
            });

            const data = await response.json();
            if (data.success) {
                // Store auth token
                authToken = data.token;
                localStorage.setItem('authToken', authToken);
                
                // Update UI
                otpInputContainer.style.display = 'none';
                verifyOtpButton.style.display = 'none';
                
                if (phoneInput && phoneContainer) {
                    phoneInput.disabled = true;
                    
                    // Show success status
                    const verificationStatus = document.createElement('div');
                    verificationStatus.className = 'verification-success';
                    verificationStatus.innerHTML = '<i class="ph ph-check-circle"></i> Phone verified';
                    phoneContainer.appendChild(verificationStatus);
                }
                
                // Hide send OTP button if it exists
                if (sendOtpButton) {
                    sendOtpButton.style.display = 'none';
                }
                
                // Show checkout button
                if (checkoutButton) {
                    checkoutButton.style.display = 'flex';
                }
                
                showSnackbar('Phone verified successfully', 'success');
            } else {
                showSnackbar(data.message || 'Invalid OTP');
                
                // Clear OTP inputs on failure
                otpInputs.forEach(input => input.value = '');
                otpInputs[0].focus();
            }
        } catch (error) {
            console.error('Error verifying OTP:', error);
            showSnackbar('Failed to verify OTP');
        }
    });

    // Fetch offerings data
    console.log('Fetching offerings data...');
    fetch('/static/configurations/offerings.json')
        .then(response => {
            console.log('Fetch response:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Offerings data loaded:', data);
            OFFERINGS = data.offerings;
            if (offeringCardsContainer) {
                createOfferingCards();
                updateInitialState();
            } else {
                console.error('Offering cards container not found');
            }
        })
        .catch(error => {
            console.error('Error loading offerings configuration:', error);
        });

    function createOfferingCards() {
        console.log('Creating offering cards with data:', OFFERINGS);
        offeringCardsContainer.innerHTML = ''; // Clear existing cards
        
        OFFERINGS.forEach(offering => {
            console.log('Creating card for offering:', offering.id);
            const card = document.createElement('div');
            card.className = 'offering-card';
            card.dataset.id = offering.id;
            
            // Format prices
            const formattedPrice = new Intl.NumberFormat('en-IN', {
                style: 'currency',
                currency: 'INR',
                maximumFractionDigits: 0
            }).format(offering.price);
            
            const formattedOriginalPrice = new Intl.NumberFormat('en-IN', {
                style: 'currency',
                currency: 'INR',
                maximumFractionDigits: 0
            }).format(offering.original_price);

            // Create benefits list
            const benefitsList = offering.benefits.map(benefit => 
                `<li><i class="ph ph-check-circle"></i>${benefit}</li>`
            ).join('');

            // Add popular tag if marked as popular
            const popularTag = offering.popular ? '<div class="popular-tag">Popular</div>' : '';
            
            // Determine slots class
            const slotsClass = offering.slots_limited ? 'offering-slots limited' : 'offering-slots';

            card.innerHTML = `
                ${popularTag}
                <div class="offering-card-header">
                    <div class="offering-card-icon">
                        <i class="ph ${offeringIcons[offering.id] || 'ph-star'}"></i>
                    </div>
                    <h3>${offering.title}</h3>
                </div>
                <div class="offering-card-content">
                    <p>${offering.description}</p>
                    <div class="what-you-get">
                        <h4>What You Get:</h4>
                        <ul class="benefits-list">
                            ${benefitsList}
                        </ul>
                    </div>
                    <div class="offering-card-meta">
                        <div class="slots-container">
                            <span class="${slotsClass}">
                                <i class="ph ph-user-circle"></i>${offering.slots_left} slots left this month
                            </span>
                        </div>
                        <div class="price-container">
                            <span class="original-price">${formattedOriginalPrice}</span>
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
            
            offeringCardsContainer.appendChild(card);
            
            // Add event listeners for the buttons
            const ctaButton = card.querySelector('.offering-cta');
            const buyNowButton = card.querySelector('.buy-now-btn');
            
            ctaButton.addEventListener('click', function() {
                const productId = this.dataset.product;
                if (selectedItems.has(productId)) {
                    document.dispatchEvent(new CustomEvent('product:removed', { detail: { productId } }));
                } else {
                    document.dispatchEvent(new CustomEvent('product:added', { detail: { productId } }));
                }
            });
            
            buyNowButton.addEventListener('click', function() {
                const productId = this.dataset.product;
                // Clear cart first
                selectedItems.clear();
                // Add only this item
                document.dispatchEvent(new CustomEvent('product:added', { detail: { productId } }));
                // Show payment UI
                payButton.click();
            });
        });
    }

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

    // Initialize cart state
    updateCart();
    console.log('Cart initialized');
}); 