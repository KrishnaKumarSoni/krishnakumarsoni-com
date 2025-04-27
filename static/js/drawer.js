document.addEventListener('DOMContentLoaded', function() {
    // Get drawer elements
    const drawerOverlay = document.querySelector('.drawer-overlay');
    const drawer = document.querySelector('.drawer');
    const drawerClose = document.querySelector('.drawer-close');
    
    // Verification flow elements
    const phoneStep = document.getElementById('phone-step');
    const otpStep = document.getElementById('otp-step');
    const successStep = document.getElementById('success-step');
    const paymentStep = document.getElementById('payment-step');
    
    // Global timer variables
    let qrRefreshInterval = null;
    let qrRefreshSeconds = 60;
    const qrCountdown = document.getElementById('qr-countdown');
    
    // Global function to clear QR timer
    function clearGlobalQrTimer() {
        console.log("Clearing global QR timer");
        if (qrRefreshInterval) {
            clearInterval(qrRefreshInterval);
            qrRefreshInterval = null;
        }
        qrRefreshSeconds = 60;
        if (qrCountdown) {
            qrCountdown.textContent = qrRefreshSeconds;
        }
    }
    
    // Function to check if user is already verified
    function checkVerificationStatus() {
        if (isUserVerified()) {
            // Skip to payment step directly
            showPaymentStep();
        } else {
            // Start with phone verification
            resetVerificationFlow();
        }
    }
    
    // Function to check if user is verified from localStorage
    function isUserVerified() {
        return localStorage.getItem('phoneVerified') === 'true';
    }
    
    // Reset verification flow to initial state
    function resetVerificationFlow() {
        if (phoneStep) phoneStep.classList.remove('hidden');
        if (otpStep) otpStep.classList.add('hidden');
        if (successStep) successStep.classList.add('hidden');
        if (paymentStep) paymentStep.classList.add('hidden');
    }
    
    // Function to open drawer
    function openDrawer() {
        drawer.classList.add('open');
        drawerOverlay.classList.add('open');
        document.body.style.overflow = 'hidden'; // Prevent scrolling when drawer is open
        
        // Check if user is already verified
        checkVerificationStatus();
    }
    
    // Function to close drawer
    function closeDrawer() {
        drawer.classList.remove('open');
        drawerOverlay.classList.remove('open');
        document.body.style.overflow = ''; // Restore scrolling
        
        // Clear QR refresh timer when drawer is closed
        clearGlobalQrTimer();
    }
    
    // Handle click on close button
    if (drawerClose) {
        drawerClose.addEventListener('click', closeDrawer);
    }
    
    // Handle click on overlay (close drawer when clicking outside)
    if (drawerOverlay) {
        drawerOverlay.addEventListener('click', closeDrawer);
    }
    
    // Handle ESC key to close drawer
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && drawer.classList.contains('open')) {
            closeDrawer();
        }
    });
    
    // Start QR refresh timer function (global)
    function startGlobalQrTimer() {
        // First clear any existing timer
        clearGlobalQrTimer();
        
        // Reset timer
        qrRefreshSeconds = 60;
        if (qrCountdown) {
            qrCountdown.textContent = qrRefreshSeconds;
        }
        
        // Hide refresh animation if it's showing
        const refreshAnimation = document.querySelector('.refresh-animation');
        if (refreshAnimation) {
            refreshAnimation.classList.remove('active');
        }
        
        // Start new interval
        qrRefreshInterval = setInterval(function() {
            qrRefreshSeconds--;
            
            if (qrCountdown) {
                qrCountdown.textContent = qrRefreshSeconds;
            }
            
            if (qrRefreshSeconds <= 0) {
                clearInterval(qrRefreshInterval);
                qrRefreshInterval = null;
                
                // Show refresh animation
                if (refreshAnimation) {
                    refreshAnimation.classList.add('active');
                    
                    // Refresh QR code after animation
                    setTimeout(function() {
                        // Only refresh if drawer is still open
                        if (drawer.classList.contains('open')) {
                            setupVerificationFlow().showPaymentStepImpl();
                        }
                    }, 1500);
                } else {
                    // No animation, refresh immediately if drawer is still open
                    if (drawer.classList.contains('open')) {
                        setupVerificationFlow().showPaymentStepImpl();
                    }
                }
            }
        }, 1000);
    }
    
    // OTP Verification Flow
    setupVerificationFlow();
    
    // Show payment step function (simplified version for global scope)
    async function showPaymentStep() {
        // Only proceed if elements exist
        if (!paymentStep) return;
        
        // Hide other steps
        if (phoneStep) phoneStep.classList.add('hidden');
        if (otpStep) otpStep.classList.add('hidden');
        if (successStep) successStep.classList.add('hidden');
        paymentStep.classList.remove('hidden');
        
        // Rest of the implementation is in setupVerificationFlow
        setupVerificationFlow().showPaymentStepImpl();
    }
    
    function setupVerificationFlow() {
        // Get verification elements
        const sendOtpBtn = document.getElementById('send-otp-btn');
        const verifyOtpBtn = document.getElementById('verify-otp-btn');
        const resendOtpBtn = document.getElementById('resend-otp-btn');
        const continueBtn = document.getElementById('continue-btn');
        const backToPhoneBtn = document.querySelector('.back-to-phone-btn');
        const phoneInput = document.querySelector('.phone-input');
        const userPhoneSpan = document.querySelector('.user-phone');
        const otpInputs = document.querySelectorAll('.otp-input');
        const paymentQrCode = document.getElementById('payment-qr-code');
        const upiIdDisplay = document.getElementById('upi-id-display');
        const amountValue = document.querySelector('.amount-value');
        const upiAppBtn = document.getElementById('upi-app-btn');
        
        // Country code dropdown
        const countryToggle = document.querySelector('.country-code-toggle');
        const countryDropdown = document.querySelector('.country-dropdown');
        const countryList = document.getElementById('country-list');
        const countrySearchInput = document.querySelector('.country-search-input');
        
        // Variables
        let selectedCountryCode = '+91';
        let resendTimer;
        let resendSeconds = 30;
        let currentPhoneNumber = '';
        
        // QR refresh timer variables
        let currentUpiUrl = '';
        
        // Get cart amount from the DOM or localStorage if available
        function getCartAmount() {
            // First try to get total from the cart widget in the DOM
            const totalPriceElement = document.querySelector('.total-price');
            if (totalPriceElement) {
                // Extract the number from the formatted price (e.g., "₹1,000.00" -> 1000)
                const priceText = totalPriceElement.textContent.trim();
                // Remove currency symbol, commas and convert to number
                const amount = parseFloat(priceText.replace(/[₹,]/g, ''));
                if (!isNaN(amount)) {
                    return amount;
                }
            }
            
            // If DOM element is not available, try localStorage
            const cartItems = JSON.parse(localStorage.getItem('cartItems')) || [];
            if (cartItems.length > 0) {
                try {
                    // Get offerings data to calculate total
                    const offerings = JSON.parse(localStorage.getItem('offeringsData')) || [];
                    if (offerings.length > 0) {
                        // Calculate total from selected items
                        return cartItems.reduce((total, itemId) => {
                            const item = offerings.find(o => o.id === itemId);
                            return total + (item ? item.price : 0);
                        }, 0);
                    }
                } catch (e) {
                    console.error('Error calculating cart amount from localStorage:', e);
                }
            }
            
            // Fallback amount if no other source is available
            return 1000.00;
        }
        
        // Countries list - comprehensive list with flags, country codes
        const countries = [
            { name: "India", code: "+91", flag: "🇮🇳" },
            { name: "United States", code: "+1", flag: "🇺🇸" },
            { name: "United Kingdom", code: "+44", flag: "🇬🇧" },
            { name: "Afghanistan", code: "+93", flag: "🇦🇫" },
            { name: "Albania", code: "+355", flag: "🇦🇱" },
            { name: "Algeria", code: "+213", flag: "🇩🇿" },
            { name: "Andorra", code: "+376", flag: "🇦🇩" },
            { name: "Angola", code: "+244", flag: "🇦🇴" },
            { name: "Argentina", code: "+54", flag: "🇦🇷" },
            { name: "Armenia", code: "+374", flag: "🇦🇲" },
            { name: "Australia", code: "+61", flag: "🇦🇺" },
            { name: "Austria", code: "+43", flag: "🇦🇹" },
            { name: "Azerbaijan", code: "+994", flag: "🇦🇿" },
            { name: "Bahrain", code: "+973", flag: "🇧🇭" },
            { name: "Bangladesh", code: "+880", flag: "🇧🇩" },
            { name: "Belarus", code: "+375", flag: "🇧🇾" },
            { name: "Belgium", code: "+32", flag: "🇧🇪" },
            { name: "Bhutan", code: "+975", flag: "🇧🇹" },
            { name: "Brazil", code: "+55", flag: "🇧🇷" },
            { name: "Canada", code: "+1", flag: "🇨🇦" },
            { name: "China", code: "+86", flag: "🇨🇳" },
            { name: "Colombia", code: "+57", flag: "🇨🇴" },
            { name: "Croatia", code: "+385", flag: "🇭🇷" },
            { name: "Cuba", code: "+53", flag: "🇨🇺" },
            { name: "Czech Republic", code: "+420", flag: "🇨🇿" },
            { name: "Denmark", code: "+45", flag: "🇩🇰" },
            { name: "Egypt", code: "+20", flag: "🇪🇬" },
            { name: "Finland", code: "+358", flag: "🇫🇮" },
            { name: "France", code: "+33", flag: "🇫🇷" },
            { name: "Germany", code: "+49", flag: "🇩🇪" },
            { name: "Greece", code: "+30", flag: "🇬🇷" },
            { name: "Hong Kong", code: "+852", flag: "🇭🇰" },
            { name: "Hungary", code: "+36", flag: "🇭🇺" },
            { name: "Iceland", code: "+354", flag: "🇮🇸" },
            { name: "Indonesia", code: "+62", flag: "🇮🇩" },
            { name: "Iran", code: "+98", flag: "🇮🇷" },
            { name: "Iraq", code: "+964", flag: "🇮🇶" },
            { name: "Ireland", code: "+353", flag: "🇮🇪" },
            { name: "Israel", code: "+972", flag: "🇮🇱" },
            { name: "Italy", code: "+39", flag: "🇮🇹" },
            { name: "Japan", code: "+81", flag: "🇯🇵" },
            { name: "Jordan", code: "+962", flag: "🇯🇴" },
            { name: "Kenya", code: "+254", flag: "🇰🇪" },
            { name: "Kuwait", code: "+965", flag: "🇰🇼" },
            { name: "Malaysia", code: "+60", flag: "🇲🇾" },
            { name: "Maldives", code: "+960", flag: "🇲🇻" },
            { name: "Mexico", code: "+52", flag: "🇲🇽" },
            { name: "Mongolia", code: "+976", flag: "🇲🇳" },
            { name: "Morocco", code: "+212", flag: "🇲🇦" },
            { name: "Nepal", code: "+977", flag: "🇳🇵" },
            { name: "Netherlands", code: "+31", flag: "🇳🇱" },
            { name: "New Zealand", code: "+64", flag: "🇳🇿" },
            { name: "Nigeria", code: "+234", flag: "🇳🇬" },
            { name: "Norway", code: "+47", flag: "🇳🇴" },
            { name: "Oman", code: "+968", flag: "🇴🇲" },
            { name: "Pakistan", code: "+92", flag: "🇵🇰" },
            { name: "Philippines", code: "+63", flag: "🇵🇭" },
            { name: "Poland", code: "+48", flag: "🇵🇱" },
            { name: "Portugal", code: "+351", flag: "🇵🇹" },
            { name: "Qatar", code: "+974", flag: "🇶🇦" },
            { name: "Russia", code: "+7", flag: "🇷🇺" },
            { name: "Saudi Arabia", code: "+966", flag: "🇸🇦" },
            { name: "Singapore", code: "+65", flag: "🇸🇬" },
            { name: "South Africa", code: "+27", flag: "🇿🇦" },
            { name: "South Korea", code: "+82", flag: "🇰🇷" },
            { name: "Spain", code: "+34", flag: "🇪🇸" },
            { name: "Sri Lanka", code: "+94", flag: "🇱🇰" },
            { name: "Sweden", code: "+46", flag: "🇸🇪" },
            { name: "Switzerland", code: "+41", flag: "🇨🇭" },
            { name: "Syria", code: "+963", flag: "🇸🇾" },
            { name: "Taiwan", code: "+886", flag: "🇹🇼" },
            { name: "Thailand", code: "+66", flag: "🇹🇭" },
            { name: "Turkey", code: "+90", flag: "🇹🇷" },
            { name: "Ukraine", code: "+380", flag: "🇺🇦" },
            { name: "United Arab Emirates", code: "+971", flag: "🇦🇪" },
            { name: "Vietnam", code: "+84", flag: "🇻🇳" },
            { name: "Yemen", code: "+967", flag: "🇾🇪" },
            { name: "Zimbabwe", code: "+263", flag: "🇿🇼" }
        ];
        
        // Local storage function
        function saveVerificationStatus(phoneNumber) {
            localStorage.setItem('phoneVerified', 'true');
            localStorage.setItem('verifiedPhone', phoneNumber);
            localStorage.setItem('verifiedAt', new Date().toISOString());
        }
        
        // Browser fingerprint for Firebase
        function getBrowserFingerprint() {
            return {
                userAgent: navigator.userAgent,
                language: navigator.language,
                platform: navigator.platform,
                screenWidth: window.screen.width,
                screenHeight: window.screen.height,
                colorDepth: window.screen.colorDepth,
                timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                timestamp: new Date().toISOString()
            };
        }
        
        // Helper functions for API calls
        async function callApi(endpoint, data) {
            try {
                // Set a timeout for the fetch request
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 20000); // 20 second timeout
                
                const response = await fetch(`/api/${endpoint}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data),
                    signal: controller.signal
                });
                
                // Clear the timeout
                clearTimeout(timeoutId);
                
                // Handle non-200 responses
                if (!response.ok) {
                    console.error(`${endpoint} API error:`, response.status, response.statusText);
                    return {
                        status: 'error',
                        message: `Server error (${response.status}). Please try again later.`
                    };
                }
                
                return await response.json();
            } catch (error) {
                console.error(`Error calling ${endpoint} API:`, error);
                
                // Check if it's an abort error (timeout)
                if (error.name === 'AbortError') {
                    return {
                        status: 'error',
                        message: 'Request timed out. The server is taking too long to respond.'
                    };
                }
                
                return {
                    status: 'error',
                    message: 'Network error. Please try again.'
                };
            }
        }
        
        async function sendOtpToPhone(phoneNumber, countryCode) {
            return await callApi('otp/send', {
                phone_number: phoneNumber,
                country_code: countryCode
            });
        }
        
        async function verifyOtpFromPhone(phoneNumber, countryCode, otp) {
            console.log(`Verifying OTP: ${otp} for phone: ${countryCode}${phoneNumber}`);
            
            // Get the browser fingerprint for verification
            const fingerprint = getBrowserFingerprint();
            
            // Add current timestamp to request
            fingerprint.request_time = new Date().toISOString();
            
            // Add some retry logic for robustness
            let retryCount = 0;
            const maxRetries = 2;
            
            while (retryCount <= maxRetries) {
                try {
                    const response = await callApi('otp/verify', {
                        phone_number: phoneNumber,
                        country_code: countryCode,
                        otp: otp,
                        browser_data: fingerprint
                    });
                    
                    console.log("OTP verification response:", response);
                    
                    // Success case - no need to retry
                    if (response.status === 'success') {
                        return response;
                    }
                    
                    // If we got a response but it's an error, retry only for certain errors
                    if (response.status === 'error') {
                        if (response.message && (
                            response.message.includes('timeout') || 
                            response.message.includes('network error') ||
                            response.message.includes('taking too long')
                        )) {
                            console.warn(`Retry ${retryCount + 1}/${maxRetries} for OTP verification due to: ${response.message}`);
                            retryCount++;
                            
                            // Wait a bit before retrying
                            await new Promise(resolve => setTimeout(resolve, 1000));
                            continue;
                        }
                        
                        // For other error types, don't retry
                        return response;
                    }
                    
                    // Any other response just return it
                    return response;
                } catch (error) {
                    console.error("Exception during OTP verification:", error);
                    
                    retryCount++;
                    if (retryCount > maxRetries) {
                        return {
                            status: 'error',
                            message: 'Maximum retry attempts exceeded. Please try again later.'
                        };
                    }
                    
                    // Wait a bit before retrying
                    await new Promise(resolve => setTimeout(resolve, 1000));
                }
            }
            
            // This should never happen due to the returns in the loop
            return {
                status: 'error',
                message: 'Unexpected error during verification. Please try again.'
            };
        }
        
        async function resendOtpToPhone(phoneNumber, countryCode) {
            return await callApi('otp/resend', {
                phone_number: phoneNumber,
                country_code: countryCode
            });
        }
        
        async function generatePaymentQR(phoneNumber, amount) {
            console.log("Generating payment QR for:", phoneNumber, amount);
            return await callApi('payment/generate-qr', {
                amount: amount,
                phone_number: phoneNumber,
                browser_data: getBrowserFingerprint(),
                transaction_note: "Payment for order"
            });
        }
        
        // Detailed showPaymentStep implementation
        async function showPaymentStepImpl() {
            try {
                // Check if drawer is open - don't proceed if closed
                if (!drawer.classList.contains('open')) {
                    console.log("Drawer is closed, skipping QR refresh");
                    return;
                }
                
                // Get the actual amount
                const amount = getCartAmount();
                console.log("Cart amount for QR generation:", amount);
                
                // Format amount display
                const formattedAmount = new Intl.NumberFormat('en-IN', { 
                    style: 'currency', 
                    currency: 'INR',
                    maximumFractionDigits: 2
                }).format(amount);
                
                if (amountValue) {
                    amountValue.textContent = formattedAmount;
                    console.log("Updated amount display:", formattedAmount);
                }
                
                // Get verified phone from localStorage or use current
                const verifiedPhone = localStorage.getItem('verifiedPhone') || `${selectedCountryCode}${currentPhoneNumber}`;
                console.log("Using verified phone for payment:", verifiedPhone);
                
                // Generate QR code
                console.log("Calling generatePaymentQR with:", verifiedPhone, amount);
                const response = await generatePaymentQR(verifiedPhone, amount);
                console.log("QR generation response:", response);
                
                // Check again if drawer is open - in case it was closed during the API call
                if (!drawer.classList.contains('open')) {
                    console.log("Drawer was closed during QR generation, aborting");
                    return;
                }
                
                if (response.status === 'success') {
                    // Set QR code image
                    if (paymentQrCode) {
                        console.log("QR code data length:", response.qr_code.length);
                        paymentQrCode.src = response.qr_code;
                        paymentQrCode.onerror = function() {
                            console.error("Failed to load QR code image");
                            // Reset to placeholder if loading fails
                            paymentQrCode.src = '/static/images/qr-placeholder.png';
                        };
                    }
                    
                    // Store UPI URL for the app button
                    if (response.upi_details && response.upi_details.upi_url) {
                        currentUpiUrl = response.upi_details.upi_url;
                        
                        // Setup UPI app button
                        if (upiAppBtn) {
                            upiAppBtn.onclick = function() {
                                window.location.href = currentUpiUrl;
                            };
                        }
                    } else if (response.upi_details && response.upi_details.upi_id) {
                        // Construct UPI URL if not provided directly
                        const upiId = response.upi_details.upi_id;
                        currentUpiUrl = `upi://pay?pa=${upiId}&am=${amount}&pn=${response.upi_details.merchant_name || 'Krishna Kumar Soni'}&tn=${response.upi_details.transaction_note || 'Payment for order'}`;
                        
                        // Setup UPI app button
                        if (upiAppBtn) {
                            upiAppBtn.onclick = function() {
                                window.location.href = currentUpiUrl;
                            };
                        }
                    }
                    
                    // Only start timer if drawer is still open
                    if (drawer.classList.contains('open')) {
                        // First clear any existing timer to prevent multiple timers
                        clearGlobalQrTimer();
                        
                        // Then start a new QR refresh timer
                        startGlobalQrTimer();
                    }
                } else {
                    // Handle error
                    console.error("Failed to generate QR code:", response);
                    alert(response.message || 'Failed to generate payment QR code');
                    
                    // Use placeholder image if available
                    if (paymentQrCode) {
                        paymentQrCode.src = localStorage.getItem('qrPlaceholder') || '/static/images/qr-placeholder.png';
                    }
                }
            } catch (error) {
                console.error("Error in showPaymentStepImpl:", error);
                alert('An error occurred while preparing payment information');
            }
        }
        
        // Populate countries
        function populateCountries() {
            if (!countryList) return;
            
            countryList.innerHTML = '';
            
            countries.forEach(country => {
                const option = document.createElement('div');
                option.className = 'country-option';
                option.setAttribute('data-code', country.code);
                option.setAttribute('data-country', country.name);
                
                if (country.code === selectedCountryCode) {
                    option.classList.add('selected');
                }
                
                option.innerHTML = `
                    <span class="country-flag">${country.flag}</span>
                    <span class="country-name">${country.name}</span>
                    <span class="country-code">${country.code}</span>
                `;
                
                countryList.appendChild(option);
            });
            
            // Add event listeners to country options
            attachCountryOptionListeners();
        }
        
        // Attach event listeners to country options
        function attachCountryOptionListeners() {
            const countryOptions = document.querySelectorAll('.country-option');
            
            countryOptions.forEach(option => {
                option.addEventListener('click', function() {
                    const code = this.getAttribute('data-code');
                    const flag = this.querySelector('.country-flag').textContent;
                    
                    selectedCountryCode = code;
                    
                    // Update toggle button
                    countryToggle.querySelector('.country-flag').textContent = flag;
                    countryToggle.querySelector('.country-code').textContent = code;
                    
                    // Update selected state
                    countryOptions.forEach(opt => opt.classList.remove('selected'));
                    this.classList.add('selected');
                    
                    // Close dropdown
                    countryDropdown.style.display = 'none';
                });
            });
        }
        
        // Initialize the countries list
        populateCountries();
        
        // Toggle country dropdown
        if (countryToggle) {
            countryToggle.addEventListener('click', function(e) {
                e.stopPropagation();
                countryDropdown.style.display = countryDropdown.style.display === 'block' ? 'none' : 'block';
            });
            
            // Close dropdown when clicking outside
            document.addEventListener('click', function() {
                countryDropdown.style.display = 'none';
            });
            
            countryDropdown.addEventListener('click', function(e) {
                e.stopPropagation();
            });
        }
        
        // Country search functionality
        if (countrySearchInput) {
            countrySearchInput.addEventListener('input', function() {
                const searchValue = this.value.toLowerCase();
                
                const countryOptions = document.querySelectorAll('.country-option');
                countryOptions.forEach(option => {
                    const countryName = option.getAttribute('data-country').toLowerCase();
                    if (countryName.includes(searchValue)) {
                        option.style.display = 'flex';
                    } else {
                        option.style.display = 'none';
                    }
                });
            });
        }
        
        // OTP input handling
        otpInputs.forEach((input, index) => {
            // Auto-focus next input when a digit is entered
            input.addEventListener('input', function() {
                if (this.value.length === 1) {
                    if (index < otpInputs.length - 1) {
                        otpInputs[index + 1].focus();
                    } else {
                        this.blur(); // Remove focus on last input after filling
                    }
                }
            });
            
            // Handle backspace to go to previous input
            input.addEventListener('keydown', function(e) {
                if (e.key === 'Backspace' && !this.value && index > 0) {
                    otpInputs[index - 1].focus();
                }
            });
        });
        
        // Send OTP button
        if (sendOtpBtn) {
            sendOtpBtn.addEventListener('click', async function() {
                const phoneNumber = phoneInput.value.trim();
                
                if (!phoneNumber) {
                    // Show error - phone number is required
                    phoneInput.focus();
                    return;
                }
                
                if (phoneNumber.length < 10) {
                    // Show error - phone number is invalid
                    phoneInput.focus();
                    return;
                }
                
                // Show loading state
                sendOtpBtn.disabled = true;
                sendOtpBtn.innerHTML = 'Sending... <i class="ph ph-spinner ph-spin"></i>';
                
                // Call API to send OTP
                const response = await sendOtpToPhone(phoneNumber, selectedCountryCode);
                
                // Reset button state
                sendOtpBtn.disabled = false;
                sendOtpBtn.innerHTML = 'Send Code <i class="ph ph-arrow-right"></i>';
                
                if (response.status === 'error') {
                    // Show error message
                    alert(response.message || 'Failed to send OTP. Please try again.');
                    return;
                }
                
                // Store the current phone number
                currentPhoneNumber = phoneNumber;
                
                // Show the OTP verification step
                phoneStep.classList.add('hidden');
                otpStep.classList.remove('hidden');
                
                // Update the phone number display
                userPhoneSpan.textContent = `${selectedCountryCode} ${phoneNumber}`;
                
                // Focus the first OTP input
                if (otpInputs.length) {
                    otpInputs[0].focus();
                }
                
                // Start resend timer
                startResendTimer();
            });
        }
        
        // Verify OTP button
        if (verifyOtpBtn) {
            verifyOtpBtn.addEventListener('click', async function() {
                const otp = Array.from(otpInputs).map(input => input.value).join('');
                
                if (otp.length !== 6) {
                    // Show error - OTP is incomplete
                    return;
                }
                
                // Show loading state
                verifyOtpBtn.disabled = true;
                verifyOtpBtn.innerHTML = 'Verifying... <i class="ph ph-spinner ph-spin"></i>';
                
                // Call API to verify OTP
                const response = await verifyOtpFromPhone(currentPhoneNumber, selectedCountryCode, otp);
                
                // Reset button state
                verifyOtpBtn.disabled = false;
                verifyOtpBtn.innerHTML = 'Verify <i class="ph ph-check"></i>';
                
                if (response.status === 'error') {
                    // Show error message
                    alert(response.message || 'Failed to verify OTP. Please try again.');
                    return;
                }
                
                // Format full phone number
                const formattedPhone = `${selectedCountryCode}${currentPhoneNumber}`;
                
                // Save verification status in localStorage
                saveVerificationStatus(formattedPhone);
                
                // Show success step
                otpStep.classList.add('hidden');
                successStep.classList.remove('hidden');
                
                // Clear the OTP inputs
                otpInputs.forEach(input => {
                    input.value = '';
                });
                
                // Clear any active timer
                clearInterval(resendTimer);
            });
        }
        
        // Back to phone button
        if (backToPhoneBtn) {
            backToPhoneBtn.addEventListener('click', function() {
                // Show phone step again
                otpStep.classList.add('hidden');
                phoneStep.classList.remove('hidden');
                
                // Clear the OTP inputs
                otpInputs.forEach(input => {
                    input.value = '';
                });
                
                // Clear any active timer
                clearInterval(resendTimer);
            });
        }
        
        // Resend OTP button
        if (resendOtpBtn) {
            resendOtpBtn.addEventListener('click', async function() {
                if (this.disabled) return;
                
                // Show loading state
                this.disabled = true;
                const originalText = this.innerHTML;
                this.innerHTML = 'Sending... <i class="ph ph-spinner ph-spin"></i>';
                
                // Call API to resend OTP
                const response = await resendOtpToPhone(currentPhoneNumber, selectedCountryCode);
                
                if (response.status === 'error') {
                    // Show error message
                    alert(response.message || 'Failed to resend OTP. Please try again.');
                    
                    // Reset button state without starting timer
                    this.disabled = false;
                    this.innerHTML = originalText;
                    return;
                }
                
                // Reset button state
                this.innerHTML = originalText;
                
                // Reset and start the timer
                startResendTimer();
                
                // Clear the OTP inputs and focus the first one
                otpInputs.forEach(input => {
                    input.value = '';
                });
                
                if (otpInputs.length) {
                    otpInputs[0].focus();
                }
            });
        }
        
        // Continue button (after verification success)
        if (continueBtn) {
            continueBtn.addEventListener('click', function() {
                // Show payment step
                showPaymentStepImpl();
            });
        }
        
        // Start resend timer function
        function startResendTimer() {
            // Disable resend button
            if (resendOtpBtn) {
                resendOtpBtn.disabled = true;
            }
            
            // Reset seconds
            resendSeconds = 30;
            updateResendTimerDisplay();
            
            // Clear any existing timer
            clearInterval(resendTimer);
            
            // Start new timer
            resendTimer = setInterval(function() {
                resendSeconds--;
                updateResendTimerDisplay();
                
                if (resendSeconds <= 0) {
                    clearInterval(resendTimer);
                    if (resendOtpBtn) {
                        resendOtpBtn.disabled = false;
                        document.querySelector('.resend-timer').textContent = '';
                    }
                }
            }, 1000);
        }
        
        // Update timer display
        function updateResendTimerDisplay() {
            const timerElement = document.querySelector('.resend-timer');
            if (timerElement) {
                const minutes = Math.floor(resendSeconds / 60);
                const seconds = resendSeconds % 60;
                timerElement.textContent = `(${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')})`;
            }
        }
        
        // Return object with internal functions that need to be accessed from outside
        return {
            showPaymentStepImpl,
            clearQrRefreshTimer: clearGlobalQrTimer
        };
    }
    
    // Export drawer functions for external use
    window.drawer = {
        open: openDrawer,
        close: closeDrawer
    };
}); 