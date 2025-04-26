document.addEventListener('DOMContentLoaded', function() {
    // Get drawer elements
    const drawerOverlay = document.querySelector('.drawer-overlay');
    const drawer = document.querySelector('.drawer');
    const drawerClose = document.querySelector('.drawer-close');
    
    // Function to open drawer
    function openDrawer() {
        drawer.classList.add('open');
        drawerOverlay.classList.add('open');
        document.body.style.overflow = 'hidden'; // Prevent scrolling when drawer is open
    }
    
    // Function to close drawer
    function closeDrawer() {
        drawer.classList.remove('open');
        drawerOverlay.classList.remove('open');
        document.body.style.overflow = ''; // Restore scrolling
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
    
    // OTP Verification Flow
    setupVerificationFlow();
    
    function setupVerificationFlow() {
        // Get verification elements
        const phoneStep = document.getElementById('phone-step');
        const otpStep = document.getElementById('otp-step');
        const successStep = document.getElementById('success-step');
        const sendOtpBtn = document.getElementById('send-otp-btn');
        const verifyOtpBtn = document.getElementById('verify-otp-btn');
        const resendOtpBtn = document.getElementById('resend-otp-btn');
        const continueBtn = document.getElementById('continue-btn');
        const backToPhoneBtn = document.querySelector('.back-to-phone-btn');
        const phoneInput = document.querySelector('.phone-input');
        const userPhoneSpan = document.querySelector('.user-phone');
        const otpInputs = document.querySelectorAll('.otp-input');
        
        // Country code dropdown
        const countryToggle = document.querySelector('.country-code-toggle');
        const countryDropdown = document.querySelector('.country-dropdown');
        const countryList = document.getElementById('country-list');
        const countrySearchInput = document.querySelector('.country-search-input');
        
        // Variables
        let selectedCountryCode = '+91';
        let resendTimer;
        let resendSeconds = 30;
        
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
            sendOtpBtn.addEventListener('click', function() {
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
            verifyOtpBtn.addEventListener('click', function() {
                const otp = Array.from(otpInputs).map(input => input.value).join('');
                
                if (otp.length !== 6) {
                    // Show error - OTP is incomplete
                    return;
                }
                
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
            resendOtpBtn.addEventListener('click', function() {
                if (this.disabled) return;
                
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
        
        // Continue button
        if (continueBtn) {
            continueBtn.addEventListener('click', function() {
                // Reset the verification flow to initial state
                successStep.classList.add('hidden');
                phoneStep.classList.remove('hidden');
                
                // Clear the phone input
                phoneInput.value = '';
                
                // Close the drawer
                closeDrawer();
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
    }
    
    // Export drawer functions for external use
    window.drawer = {
        open: openDrawer,
        close: closeDrawer
    };
}); 