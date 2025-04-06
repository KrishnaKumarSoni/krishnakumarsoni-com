/**
 * Google Analytics Implementation with Custom Tracking Configuration
 */

// Initialize tracking configuration
let trackingConfig = null;

// Load tracking configuration from API or fallback to default
async function loadTrackingConfig() {
  try {
    // Try to load from API endpoint
    const response = await fetch('/api/tracking-config');
    
    if (!response.ok) {
      console.warn('Failed to load tracking configuration from API, using default config');
      // If API endpoint fails, use a default configuration for local testing
      setDefaultConfig();
      return;
    }
    
    // Parse the configuration
    trackingConfig = await response.json();
    console.log('Tracking configuration loaded from API');
    
  } catch (error) {
    console.error('Error loading tracking configuration:', error);
    // Set default config as fallback
    setDefaultConfig();
  } finally {
    // Initialize GA regardless of config source
    initializeGoogleAnalytics();
  }
}

// Set default config for local testing
function setDefaultConfig() {
  trackingConfig = {
    browser_fingerprint: { enabled: true, storage_duration: '30d' },
    location_data: { enabled: true },
    activity_metrics: { 
      enabled: true,
      collect: {
        session: ['session_id', 'start_time', 'end_time', 'duration'],
        page_views: ['url', 'title', 'time_spent', 'scroll_depth'],
        interactions: ['clicks', 'form_submissions', 'button_clicks', 'file_downloads', 'external_links']
      }
    },
    performance_metrics: { 
      enabled: true,
      collect: {
        page_load: ['time_to_first_byte', 'dom_load_time', 'full_page_load']
      }
    },
    privacy: {
      gdpr_compliant: true,
      anonymize_ip: true,
      cookie_consent_required: true
    }
  };
}

// Initialize Google Analytics
function initializeGoogleAnalytics() {
  if (!trackingConfig) {
    console.error('Tracking configuration not loaded');
    return;
  }

  console.log('Initializing Google Analytics');

  // Check if running locally and skip actual GA loading in development
  const isLocalhost = window.location.hostname === 'localhost' || 
                      window.location.hostname === '127.0.0.1';
  
  if (isLocalhost) {
    console.log('Running on localhost - using mock GA for development');
    // Create mock gtag function for local testing
    window.dataLayer = window.dataLayer || [];
    window.gtag = function() { 
      console.log('Mock gtag called with:', Array.from(arguments));
    };
    
    // Show cookie banner for testing UI
    if (trackingConfig.privacy?.cookie_consent_required) {
      setupCookieConsent();
    }
    return;
  }

  // Google Analytics 4 implementation - only runs in production
  const GA_MEASUREMENT_ID = 'G-8RPR9RZGKL'; // Updated with your actual GA4 measurement ID
  
  // Initialize dataLayer and gtag function
  window.dataLayer = window.dataLayer || [];
  
  // Create a more robust gtag function that handles CORS errors
  function gtag() {
    try {
      dataLayer.push(arguments);
    } catch (e) {
      console.error('Error in gtag:', e);
    }
  }
  window.gtag = gtag;
  
  // Add Google Analytics script with error handling
  try {
    const script = document.createElement('script');
    script.async = true;
    script.src = `https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`;
    script.onerror = function(e) {
      console.error('Failed to load Google Analytics script:', e);
      // Handle the error by using a more basic approach (navigator.sendBeacon)
      setupFallbackTracking();
    };
    document.head.appendChild(script);
    
    console.log('Setting up gtag');
    gtag('js', new Date());
    
    // Check for existing consent
    const hasConsent = localStorage.getItem('analytics_consent') === 'true';
    console.log('User has consent:', hasConsent);
    
    // First, set default consent state
    gtag('consent', 'default', {
      'analytics_storage': hasConsent ? 'granted' : 'denied',
      'ad_storage': 'denied',
      'wait_for_update': 500
    });
    
    // Then configure the GA property
    gtag('config', GA_MEASUREMENT_ID, {
      'anonymize_ip': trackingConfig.privacy?.anonymize_ip || true,
      'transport_type': 'beacon', // Use navigator.sendBeacon when possible
      'debug_mode': true // Enable debug mode for troubleshooting
    });
    
    // Set up cookie consent handlers if required
    if (trackingConfig.privacy?.cookie_consent_required && !hasConsent) {
      setupCookieConsent();
    }
    
    // Set up performance monitoring if enabled
    if (trackingConfig.performance_metrics?.enabled && window.PerformanceObserver) {
      setupPerformanceMonitoring();
    }
    
    // Track user interactions if enabled
    if (trackingConfig.activity_metrics?.enabled) {
      setupInteractionTracking();
    }
    
    // Send initial pageview if consent was already given
    if (hasConsent) {
      console.log('Sending initial pageview');
      sendPageView();
    }
  } catch (e) {
    console.error('Error initializing Google Analytics:', e);
    setupFallbackTracking();
  }
  
  console.log('Google Analytics initialized with ID:', GA_MEASUREMENT_ID);
}

// Function to send pageview using sendBeacon if available
function sendPageView() {
  try {
    gtag('event', 'page_view', {
      page_title: document.title,
      page_location: window.location.href,
      page_path: window.location.pathname
    });
  } catch (e) {
    console.error('Error sending pageview:', e);
    // Fallback to sendBeacon
    if (navigator.sendBeacon) {
      const GA_MEASUREMENT_ID = 'G-8RPR9RZGKL';
      const payload = {
        v: 2,
        tid: GA_MEASUREMENT_ID,
        t: 'pageview',
        dl: window.location.href,
        dt: document.title,
        dr: document.referrer
      };
      
      try {
        navigator.sendBeacon(
          'https://www.google-analytics.com/collect',
          JSON.stringify(payload)
        );
      } catch (beaconError) {
        console.error('SendBeacon failed:', beaconError);
      }
    }
  }
}

// Setup fallback tracking using navigator.sendBeacon
function setupFallbackTracking() {
  console.log('Setting up fallback tracking with sendBeacon');
  
  // Create simple tracker using sendBeacon
  window.sendAnalyticsEvent = function(eventName, eventParams) {
    if (navigator.sendBeacon) {
      const GA_MEASUREMENT_ID = 'G-8RPR9RZGKL';
      const payload = {
        v: 2,
        tid: GA_MEASUREMENT_ID,
        t: 'event',
        ec: eventParams?.event_category || 'event',
        ea: eventName,
        el: eventParams?.event_label,
        ev: eventParams?.value
      };
      
      try {
        navigator.sendBeacon(
          'https://www.google-analytics.com/collect',
          JSON.stringify(payload)
        );
        return true;
      } catch (e) {
        console.error('SendBeacon failed:', e);
        return false;
      }
    }
    return false;
  };
  
  // Send initial pageview
  sendPageView();
  
  // Monitor all clicks
  document.addEventListener('click', function(e) {
    const target = e.target.closest('a, button');
    if (!target) return;
    
    const eventData = {
      event_category: 'Engagement',
      event_label: target.innerText || target.id || 'unknown',
      value: 1
    };
    
    window.sendAnalyticsEvent('click', eventData);
  });
}

// Setup cookie consent functionality
function setupCookieConsent() {
  // Check if user has already given consent
  const hasConsent = localStorage.getItem('analytics_consent') === 'true';
  
  if (hasConsent) {
    // If user has given consent, update Google Analytics settings
    gtag('consent', 'update', {
      'analytics_storage': 'granted'
    });
  } else {
    // If no consent yet, show cookie banner
    showCookieBanner();
  }
  
  // Check if consent has expired
  const expiryDateStr = localStorage.getItem('analytics_consent_expiry');
  if (expiryDateStr) {
    const expiryDate = new Date(expiryDateStr);
    if (new Date() > expiryDate) {
      // Consent has expired, remove it and show banner again
      localStorage.removeItem('analytics_consent');
      localStorage.removeItem('analytics_consent_expiry');
      showCookieBanner();
    }
  }
}

// Setup performance monitoring using PerformanceObserver
function setupPerformanceMonitoring() {
  const perfMetrics = trackingConfig.performance_metrics;
  const samplingRate = perfMetrics.sampling_rate || 100;
  
  // Apply sampling - only track for a percentage of sessions
  if (Math.random() * 100 > samplingRate) {
    return;
  }
  
  // Track web vitals if page_load metrics are enabled
  if (perfMetrics.collect?.page_load) {
    // Track LCP (Largest Contentful Paint)
    new PerformanceObserver((entryList) => {
      const entries = entryList.getEntries();
      const lcpEntry = entries[entries.length - 1];
      
      gtag('event', 'web_vitals', {
        event_category: 'Performance',
        event_label: 'LCP',
        value: Math.round(lcpEntry.startTime + lcpEntry.duration),
        non_interaction: true
      });
    }).observe({ type: 'largest-contentful-paint', buffered: true });
    
    // Track FID (First Input Delay)
    new PerformanceObserver((entryList) => {
      const entries = entryList.getEntries();
      entries.forEach((entry) => {
        gtag('event', 'web_vitals', {
          event_category: 'Performance',
          event_label: 'FID',
          value: Math.round(entry.processingStart - entry.startTime),
          non_interaction: true
        });
      });
    }).observe({ type: 'first-input', buffered: true });
    
    // Track CLS (Cumulative Layout Shift)
    let clsValue = 0;
    new PerformanceObserver((entryList) => {
      const entries = entryList.getEntries();
      entries.forEach((entry) => {
        if (!entry.hadRecentInput) {
          clsValue += entry.value;
        }
      });
      
      gtag('event', 'web_vitals', {
        event_category: 'Performance',
        event_label: 'CLS',
        value: Math.round(clsValue * 1000),
        non_interaction: true
      });
    }).observe({ type: 'layout-shift', buffered: true });
  }
  
  // Track page load performance
  window.addEventListener('load', () => {
    setTimeout(() => {
      const navigationEntry = performance.getEntriesByType('navigation')[0];
      const paintEntries = performance.getEntriesByType('paint');
      
      const performanceMetrics = {};
      
      // Add metrics based on configuration
      if (perfMetrics.collect?.page_load?.includes('time_to_first_byte')) {
        performanceMetrics.ttfb = Math.round(navigationEntry.responseStart);
      }
      
      if (perfMetrics.collect?.page_load?.includes('dom_load_time')) {
        performanceMetrics.domLoadTime = Math.round(navigationEntry.domContentLoadedEventEnd);
      }
      
      if (perfMetrics.collect?.page_load?.includes('full_page_load')) {
        performanceMetrics.fullPageLoad = Math.round(navigationEntry.loadEventEnd);
      }
      
      if (perfMetrics.collect?.page_load?.includes('first_contentful_paint')) {
        const fcp = paintEntries.find(e => e.name === 'first-paint');
        if (fcp) {
          performanceMetrics.firstPaint = Math.round(fcp.startTime);
        }
      }
      
      gtag('event', 'page_performance', {
        ...performanceMetrics,
        non_interaction: true
      });
    }, 0);
  });
}

// Setup user interaction tracking
function setupInteractionTracking() {
  const activityMetrics = trackingConfig.activity_metrics;
  const interactionConfig = activityMetrics.collect?.interactions || [];
  const pageViewConfig = activityMetrics.collect?.page_views || [];
  
  // Track clicks on buttons and links
  if (interactionConfig.includes('clicks') || 
      interactionConfig.includes('external_links') || 
      interactionConfig.includes('file_downloads')) {
    document.addEventListener('click', (event) => {
      const target = event.target.closest('a, button');
      if (!target) return;
      
      if (target.tagName === 'A') {
        const isExternal = target.hostname !== window.location.hostname;
        const isDownload = target.hasAttribute('download');
        
        if (isExternal && interactionConfig.includes('external_links')) {
          gtag('event', 'external_link_click', {
            event_category: 'Engagement',
            event_label: target.href,
            value: 1
          });
        } else if (isDownload && interactionConfig.includes('file_downloads')) {
          gtag('event', 'file_download', {
            event_category: 'Engagement',
            event_label: target.href,
            value: 1
          });
        }
      } else if (target.tagName === 'BUTTON' && interactionConfig.includes('button_clicks')) {
        gtag('event', 'button_click', {
          event_category: 'Engagement',
          event_label: target.textContent || target.id || 'unknown',
          value: 1
        });
      }
    });
  }
  
  // Track form submissions
  if (interactionConfig.includes('form_submissions')) {
    document.addEventListener('submit', (event) => {
      const form = event.target;
      
      gtag('event', 'form_submission', {
        event_category: 'Engagement',
        event_label: form.id || form.action || 'unknown',
        value: 1
      });
    });
  }
  
  // Track scroll depth
  if (pageViewConfig.includes('scroll_depth')) {
    let maxScrollPercentage = 0;
    window.addEventListener('scroll', () => {
      const scrollHeight = Math.max(
        document.body.scrollHeight, 
        document.documentElement.scrollHeight,
        document.body.offsetHeight, 
        document.documentElement.offsetHeight,
        document.body.clientHeight, 
        document.documentElement.clientHeight
      );
      
      const scrollTop = Math.max(
        window.pageYOffset,
        document.documentElement.scrollTop,
        document.body.scrollTop
      );
      
      const trackHeight = scrollHeight - window.innerHeight;
      const scrollPercentage = Math.floor((scrollTop / trackHeight) * 100);
      
      if (scrollPercentage > maxScrollPercentage) {
        maxScrollPercentage = scrollPercentage;
        
        // Report at 25%, 50%, 75%, and 90% scroll depth
        if (maxScrollPercentage === 25 || maxScrollPercentage === 50 || 
            maxScrollPercentage === 75 || maxScrollPercentage === 90) {
          gtag('event', 'scroll_depth', {
            event_category: 'Engagement',
            event_label: `${maxScrollPercentage}%`,
            value: maxScrollPercentage,
            non_interaction: true
          });
        }
      }
    }, { passive: true });
  }
  
  // Track session timing
  if (activityMetrics.collect?.session?.includes('duration')) {
    // Set session start time
    const sessionStartTime = new Date();
    localStorage.setItem('session_start_time', sessionStartTime.toISOString());
    
    // Track session end on page unload
    window.addEventListener('beforeunload', () => {
      const startTime = new Date(localStorage.getItem('session_start_time'));
      const endTime = new Date();
      const durationInSeconds = Math.floor((endTime - startTime) / 1000);
      
      gtag('event', 'session_end', {
        event_category: 'Session',
        event_label: 'Duration',
        value: durationInSeconds,
        non_interaction: true
      });
    });
  }
}

// Simple cookie banner functions - implement according to your UI
function showCookieBanner() {
  // Check if banner already exists
  if (document.getElementById('cookie-consent-banner')) {
    return;
  }
  
  const banner = document.createElement('div');
  banner.id = 'cookie-consent-banner';
  banner.className = 'cookie-consent-banner';
  
  // Add styles to match your site design
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
  
  // Append banner to document body
  document.body.appendChild(banner);
  
  // Add direct click handlers with debug logs
  const acceptButton = document.getElementById('accept-cookies');
  if (acceptButton) {
    acceptButton.addEventListener('click', function() {
      console.log('Accept button clicked');
      
      // Store consent in localStorage
      localStorage.setItem('analytics_consent', 'true');
      
      // Update consent in Google Analytics
      gtag('consent', 'update', {
        'analytics_storage': 'granted'
      });
      
      // Set expiration date based on storage_duration if available
      if (trackingConfig && trackingConfig.browser_fingerprint?.storage_duration) {
        const duration = trackingConfig.browser_fingerprint.storage_duration;
        // Parse duration (e.g., "30d" for 30 days)
        const match = duration.match(/^(\d+)([dmy])$/);
        if (match) {
          const value = parseInt(match[1]);
          const unit = match[2];
          const expiryDate = new Date();
          
          switch(unit) {
            case 'd': expiryDate.setDate(expiryDate.getDate() + value); break;
            case 'm': expiryDate.setMonth(expiryDate.getMonth() + value); break;
            case 'y': expiryDate.setFullYear(expiryDate.getFullYear() + value); break;
          }
          
          localStorage.setItem('analytics_consent_expiry', expiryDate.toISOString());
        }
      }
      
      // Send an initial pageview event using the more reliable function
      sendPageView();
      
      // Hide the banner
      hideCookieBanner();
    });
  } else {
    console.error('Accept button not found');
  }
  
  const rejectButton = document.getElementById('reject-cookies');
  if (rejectButton) {
    rejectButton.addEventListener('click', function() {
      console.log('Reject button clicked');
      localStorage.removeItem('analytics_consent');
      hideCookieBanner();
    });
  }
}

function hideCookieBanner() {
  const banner = document.getElementById('cookie-consent-banner');
  if (banner) {
    banner.remove();
  }
}

// Initialize tracking when the page loads
document.addEventListener('DOMContentLoaded', loadTrackingConfig); 