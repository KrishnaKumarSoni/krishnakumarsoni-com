/**
 * Cookie Consent Manager for Google Tag Manager
 */

// Initialize consent state
function initConsentManager() {
  // Ensure GTM dataLayer exists
  window.dataLayer = window.dataLayer || [];
  
  // Function to check if GTM is loaded
  function isGTMLoaded() {
    return window.google_tag_manager && window.google_tag_manager['GTM-WVZMW542'];
  }
  
  // Function to initialize consent state
  function initializeConsent() {
    // Check if consent was already given
    const hasConsent = localStorage.getItem('analytics_consent') === 'true';
    
    if (hasConsent) {
      // If consent was previously given, update GTM
      window.dataLayer.push({
        'event': 'consent_update',
        'analytics_storage': 'granted',
        'ad_storage': 'denied',
        'functionality_storage': 'granted',
        'personalization_storage': 'denied',
        'security_storage': 'granted'
      });
      console.log('Consent granted - GTM updated');
    } else {
      // If no consent yet or consent denied, default to denied
      window.dataLayer.push({
        'event': 'consent_default',
        'analytics_storage': 'denied',
        'ad_storage': 'denied', 
        'functionality_storage': 'denied',
        'personalization_storage': 'denied',
        'security_storage': 'granted' // Security cookies are always allowed
      });
      console.log('No consent - showing banner');
      showConsentBanner();
    }
    
    // Check if consent has expired
    checkConsentExpiry();
  }
  
  // Wait for GTM to load before initializing consent
  let attempts = 0;
  const maxAttempts = 5;
  const checkGTM = setInterval(() => {
    attempts++;
    if (isGTMLoaded()) {
      clearInterval(checkGTM);
      initializeConsent();
      console.log('GTM loaded - consent initialized');
    } else if (attempts >= maxAttempts) {
      clearInterval(checkGTM);
      console.error('GTM failed to load after ' + maxAttempts + ' attempts');
      initializeConsent(); // Initialize anyway to ensure basic functionality
    }
  }, 1000);
}

// Show the cookie consent banner
function showConsentBanner() {
  // Check if banner already exists
  if (document.getElementById('cookie-consent-banner')) {
    return;
  }
  
  // Create the banner
  const banner = document.createElement('div');
  banner.id = 'cookie-consent-banner';
  banner.className = 'cookie-consent-banner';
  
  // Add styles
  const style = document.createElement('style');
  style.textContent = `
    .cookie-consent-banner {
      position: fixed;
      bottom: 0;
      left: 0;
      right: 0;
      padding: 16px 24px;
      background: var(--bg-surface, #f8f9fa);
      box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
      z-index: 9999;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-family: 'Inter', sans-serif;
    }
    .cookie-consent-banner p {
      margin: 0;
      font-size: 14px;
      color: var(--text-primary, #333);
    }
    .cookie-consent-banner a {
      color: var(--burnt-orange, #d35400);
      text-decoration: none;
    }
    .cookie-consent-banner a:hover {
      text-decoration: underline;
    }
    .cookie-consent-buttons {
      display: flex;
      gap: 10px;
    }
    .cookie-accept-button {
      background: var(--burnt-orange, #d35400);
      color: white;
      border: none;
      padding: 8px 16px;
      border-radius: 4px;
      cursor: pointer;
      font-weight: 500;
    }
    .cookie-reject-button {
      background: transparent;
      border: 1px solid #6c757d;
      color: #6c757d;
      padding: 8px 16px;
      border-radius: 4px;
      cursor: pointer;
    }
  `;
  document.head.appendChild(style);
  
  // Set the banner content
  banner.innerHTML = `
    <div>
      <p>
        We use cookies to improve your experience. By continuing to use this site, you agree to our 
        <a href="/privacy">Privacy Policy</a>.
      </p>
    </div>
    <div class="cookie-consent-buttons">
      <button id="accept-cookies" class="cookie-accept-button">Accept</button>
      <button id="reject-cookies" class="cookie-reject-button">Reject</button>
    </div>
  `;
  
  // Add the banner to the page
  document.body.appendChild(banner);
  
  // Add event listeners
  document.getElementById('accept-cookies').addEventListener('click', function() {
    giveConsent();
  });
  
  document.getElementById('reject-cookies').addEventListener('click', function() {
    rejectConsent();
  });
}

// Set consent as granted
function giveConsent() {
  // Store consent in localStorage
  localStorage.setItem('analytics_consent', 'true');
  
  // Set consent expiry (30 days)
  const expiryDate = new Date();
  expiryDate.setDate(expiryDate.getDate() + 30);
  localStorage.setItem('analytics_consent_expiry', expiryDate.toISOString());
  
  // Update GTM with consent
  window.dataLayer.push({
    'event': 'consent_update',
    'analytics_storage': 'granted',
    'ad_storage': 'denied',
    'functionality_storage': 'granted', 
    'personalization_storage': 'denied',
    'security_storage': 'granted'
  });
  
  // Hide the banner
  hideConsentBanner();
  
  // Log for debugging
  console.log('Analytics consent granted');
}

// Set consent as rejected
function rejectConsent() {
  // Store rejection in localStorage
  localStorage.setItem('analytics_consent', 'false');
  
  // Set rejection expiry (30 days)
  const expiryDate = new Date();
  expiryDate.setDate(expiryDate.getDate() + 30);
  localStorage.setItem('analytics_consent_expiry', expiryDate.toISOString());
  
  // Update GTM with rejection
  window.dataLayer.push({
    'event': 'consent_update',
    'analytics_storage': 'denied',
    'ad_storage': 'denied',
    'functionality_storage': 'denied',
    'personalization_storage': 'denied',
    'security_storage': 'granted'
  });
  
  // Hide the banner
  hideConsentBanner();
  
  // Log for debugging
  console.log('Analytics consent rejected');
}

// Hide the consent banner
function hideConsentBanner() {
  const banner = document.getElementById('cookie-consent-banner');
  if (banner) {
    banner.remove();
  }
}

// Check if consent has expired
function checkConsentExpiry() {
  const expiryDateStr = localStorage.getItem('analytics_consent_expiry');
  if (expiryDateStr) {
    const expiryDate = new Date(expiryDateStr);
    if (new Date() > expiryDate) {
      // Consent has expired, remove it and show banner again
      localStorage.removeItem('analytics_consent');
      localStorage.removeItem('analytics_consent_expiry');
      showConsentBanner();
    }
  }
}

// Initialize when the DOM is ready
document.addEventListener('DOMContentLoaded', initConsentManager); 