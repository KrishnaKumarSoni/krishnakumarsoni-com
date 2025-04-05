// Audio Controller
class AudioController {
  constructor() {
    this.audioElements = {};
    this.loadAudioElements();
    this.setupEventListeners();
  }

  loadAudioElements() {
    const keys = ['c', 'v', 'b', 'n'];
    keys.forEach((key, index) => {
      const audio = document.getElementById(`bongo${index + 1}`);
      if (audio) {
        this.audioElements[key] = audio;
      } else {
        console.error(`Audio element for key ${key} not found`);
      }
    });
  }

  setupEventListeners() {
    // Keyboard events
    document.addEventListener('keydown', (e) => this.handleKeyPress(e));

    // Click events
    document.querySelectorAll('.bongo').forEach(bongo => {
      bongo.addEventListener('click', () => {
        const key = bongo.dataset.key;
        this.playSound(key);
      });
    });
  }

  handleKeyPress(e) {
    const key = e.key.toLowerCase();
    if (['c', 'v', 'b', 'n'].includes(key)) {
      this.playSound(key);
    }
  }

  playSound(key) {
    const audio = this.audioElements[key];
    const bongo = document.querySelector(`.bongo[data-key="${key}"]`);
    
    if (!audio || !bongo) {
      console.error(`Required elements for key ${key} not found`);
      return;
    }

    try {
      // Reset and play audio
      audio.currentTime = 0;
      audio.play().catch(err => {
        console.error('Audio playback failed:', err);
      });

      // Visual feedback
      bongo.classList.add('playing');
      setTimeout(() => bongo.classList.remove('playing'), 100);
    } catch (error) {
      console.error('Error playing sound:', error);
    }
  }
}

// Lazy Loading
class LazyLoader {
  constructor() {
    this.setupIntersectionObserver();
  }

  setupIntersectionObserver() {
    const options = {
      root: null,
      rootMargin: '50px',
      threshold: 0.1
    };

    const observer = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          this.loadElement(entry.target);
          observer.unobserve(entry.target);
        }
      });
    }, options);

    // Observe images and audio elements
    document.querySelectorAll('img[data-src], audio[data-src]').forEach(element => {
      observer.observe(element);
    });
  }

  loadElement(element) {
    const src = element.dataset.src;
    if (!src) return;

    if (element.tagName.toLowerCase() === 'img') {
      element.src = src;
    } else if (element.tagName.toLowerCase() === 'audio') {
      element.src = src;
    }
    
    element.removeAttribute('data-src');
  }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  new AudioController();
  new LazyLoader();
}); 