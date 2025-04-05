document.addEventListener('DOMContentLoaded', () => {
    const bongos = document.querySelectorAll('.bongo');
    
    // Create an AudioContext for lower latency playback with optimal settings
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    const audioContext = new AudioContext({
        latencyHint: 'interactive',
        sampleRate: 44100
    });
    
    // Audio buffer storage
    const buffers = { 'c': null, 'v': null, 'b': null, 'n': null };
    
    // File mapping
    const fileMap = {
        'c': '/static/assets/Bongo2_trimmed.wav',
        'v': '/static/assets/Bongo3_trimmed.wav',
        'b': '/static/assets/Bongo4_trimmed.wav',
        'n': '/static/assets/Bongo1_trimmed.wav'
    };
    
    // Preload all audio files into buffers
    function loadSounds() {
        const promises = Object.entries(fileMap).map(([key, url]) => {
            return fetch(url)
                .then(response => response.arrayBuffer())
                .then(arrayBuffer => audioContext.decodeAudioData(arrayBuffer))
                .then(audioBuffer => {
                    buffers[key] = audioBuffer;
                });
        });
        
        return Promise.all(promises);
    }
    
    // Ultra-low-latency sound playback function - creates new AudioBufferSourceNode each time
    function playBongo(key) {
        const bongo = document.querySelector(`.bongo[data-key="${key}"]`);
        if (!buffers[key] || !bongo) return;
        
        // Create a new source for each playback to allow overlapping sounds
        const source = audioContext.createBufferSource();
        source.buffer = buffers[key];
        
        // Connect directly to destination for lowest latency
        source.connect(audioContext.destination);
        
        // Start playback immediately with no delay
        source.start(0);
        
        // Add visual feedback using minimal processing
        bongo.classList.add('playing');
        
        // Schedule removal with minimal delay
        setTimeout(() => {
            bongo.classList.remove('playing');
        }, 50);
    }
    
    // Initialize - resume audio context and load sounds
    function init() {
        // Resume AudioContext immediately
        audioContext.resume();
        
        // Handle all interaction types to unblock audio on iOS/mobile
        ['touchstart', 'mousedown', 'keydown'].forEach(event => {
            document.addEventListener(event, function unlockAudio() {
                audioContext.resume().then(() => {
                    document.removeEventListener(event, unlockAudio);
                });
            }, { once: true, passive: true });
        });
        
        // Load all sound buffers
        loadSounds().then(() => {
            // Handle clicks with optimized event handling
            bongos.forEach(bongo => {
                // Use minimal handler for instant response
                const handler = (e) => {
                    if (e.type === 'touchstart') e.preventDefault();
                    const key = bongo.dataset.key;
                    playBongo(key);
                };
                
                // Register for both mouse and touch with optimizations
                bongo.addEventListener('mousedown', handler, { passive: true });
                bongo.addEventListener('touchstart', handler, { passive: false });
            });
            
            // Handle keyboard events
            document.addEventListener('keydown', (e) => {
                const key = e.key.toLowerCase();
                if (['c', 'v', 'b', 'n'].includes(key)) {
                    playBongo(key);
                }
            }, { passive: true });
        });
    }
    
    // Start initialization
    init();
}); 