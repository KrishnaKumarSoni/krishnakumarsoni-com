/**
 * Google Tag Manager Event Tracking
 */

// Initialize event tracking
function initGTMEventTracking() {
  // Ensure dataLayer exists
  window.dataLayer = window.dataLayer || [];
  
  // Track page views (for single-page applications, if needed)
  function trackPageView() {
    window.dataLayer.push({
      'event': 'page_view',
      'page_location': window.location.href,
      'page_path': window.location.pathname,
      'page_title': document.title
    });
  }
  
  // Track clicks on links and buttons
  function setupClickTracking() {
    document.addEventListener('click', function(e) {
      const target = e.target.closest('a, button');
      if (!target) return;
      
      if (target.tagName === 'A') {
        const isExternal = target.hostname !== window.location.hostname;
        const isDownload = target.hasAttribute('download');
        const linkText = target.innerText || target.getAttribute('aria-label') || 'unknown';
        
        if (isExternal) {
          window.dataLayer.push({
            'event': 'external_link_click',
            'link_url': target.href,
            'link_text': linkText
          });
        } else if (isDownload) {
          window.dataLayer.push({
            'event': 'file_download',
            'file_url': target.href,
            'file_name': target.href.split('/').pop() || 'unknown'
          });
        } else {
          window.dataLayer.push({
            'event': 'link_click',
            'link_url': target.href,
            'link_text': linkText
          });
        }
      } else if (target.tagName === 'BUTTON') {
        window.dataLayer.push({
          'event': 'button_click',
          'button_text': target.innerText || target.getAttribute('aria-label') || 'unknown',
          'button_id': target.id || 'unknown'
        });
      }
    });
  }
  
  // Track form submissions
  function setupFormTracking() {
    document.addEventListener('submit', function(e) {
      const form = e.target;
      
      window.dataLayer.push({
        'event': 'form_submit',
        'form_id': form.id || form.action || 'unknown'
      });
    });
  }
  
  // Track scroll depth
  function setupScrollTracking() {
    let maxScrollPercentage = 0;
    
    window.addEventListener('scroll', function() {
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
          window.dataLayer.push({
            'event': 'scroll_depth',
            'scroll_depth_threshold': `${maxScrollPercentage}%`,
            'scroll_depth_value': maxScrollPercentage
          });
        }
      }
    }, { passive: true });
  }
  
  // Track performance metrics
  function trackPerformance() {
    if (!window.PerformanceObserver) return;
    
    // Track Largest Contentful Paint
    new PerformanceObserver((entryList) => {
      const entries = entryList.getEntries();
      const lcpEntry = entries[entries.length - 1];
      
      window.dataLayer.push({
        'event': 'performance',
        'metric_name': 'lcp',
        'metric_value': Math.round(lcpEntry.startTime + lcpEntry.duration),
        'metric_unit': 'ms'
      });
    }).observe({ type: 'largest-contentful-paint', buffered: true });
    
    // Track First Input Delay
    new PerformanceObserver((entryList) => {
      const entries = entryList.getEntries();
      entries.forEach((entry) => {
        window.dataLayer.push({
          'event': 'performance',
          'metric_name': 'fid',
          'metric_value': Math.round(entry.processingStart - entry.startTime),
          'metric_unit': 'ms'
        });
      });
    }).observe({ type: 'first-input', buffered: true });
    
    // Track page load metrics
    window.addEventListener('load', () => {
      setTimeout(() => {
        const perfData = window.performance.timing;
        const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
        
        window.dataLayer.push({
          'event': 'performance',
          'metric_name': 'page_load',
          'metric_value': pageLoadTime,
          'metric_unit': 'ms'
        });
      }, 0);
    });
  }
  
  // Initialize all tracking
  setupClickTracking();
  setupFormTracking();
  setupScrollTracking();
  trackPerformance();
}

// Run when DOM is loaded
document.addEventListener('DOMContentLoaded', initGTMEventTracking); 