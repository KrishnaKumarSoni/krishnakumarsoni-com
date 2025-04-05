document.addEventListener('DOMContentLoaded', () => {
    const magnets = document.querySelectorAll('.magnet');
    const container = document.querySelector('.magnet-container');
    const magnetPlayground = document.querySelector('.magnet-playground');
    
    // Create audio element for snap sound
    const snapSound = new Audio('/static/assets/snap_trimmed.wav');
    snapSound.volume = 0.6;
    
    const containerBounds = {
        min: 0,
        max: container?.offsetWidth - 80 || 820
    };

    let magnetStates = {
        left: { polarity: 'N', position: 0 },
        right: { polarity: 'N', position: 0 }
    };

    let hasInitialized = false;
    let lastAttracted = false;
    let isInViewport = false;

    // Initialize magnets in touching position immediately
    function initializeMagnets() {
        const centerOffset = containerBounds.max / 2;
        // Position magnets touching each other
        const leftMagnet = document.querySelector('.magnet.left');
        const rightMagnet = document.querySelector('.magnet.right');
        
        if (!leftMagnet || !rightMagnet) return;

        // Set initial positions - touching in the center
        leftMagnet.style.transition = 'none';
        rightMagnet.style.transition = 'none';
        leftMagnet.style.left = `${centerOffset - 40}px`;
        rightMagnet.style.left = `${centerOffset + 40}px`;
        
        // Force browser reflow
        leftMagnet.offsetHeight;
        rightMagnet.offsetHeight;
        
        // Reset transitions
        leftMagnet.style.transition = '';
        rightMagnet.style.transition = '';
    }

    function calculateTransitionDuration(distance, isAttraction) {
        const baseSpeed = isAttraction ? 400 : 600;
        const maxSpeed = isAttraction ? 200 : 400;
        const scaleFactor = isAttraction ? 0.3 : 0.5;
        
        const duration = Math.max(
            maxSpeed,
            baseSpeed * Math.pow(Math.min(distance / 200, 1), scaleFactor)
        );
        
        return duration;
    }

    function updateMagnetPositions(instant = false) {
        const leftMagnet = document.querySelector('.magnet.left');
        const rightMagnet = document.querySelector('.magnet.right');
        
        if (!leftMagnet || !rightMagnet) return;

        const areAttracted = magnetStates.left.polarity !== magnetStates.right.polarity;
        const currentDistance = Math.abs(magnetStates.right.position - magnetStates.left.position);
        
        let newLeftPos, newRightPos;
        const centerOffset = containerBounds.max / 2;

        if (areAttracted) {
            newLeftPos = centerOffset - 40;
            newRightPos = centerOffset + 40;
            
            if (!lastAttracted && !instant) {
                snapSound.currentTime = 0;
                snapSound.play().catch(e => console.log('Sound play prevented'));
            }
        } else {
            // Always move to full repulsion
            newLeftPos = containerBounds.min;
            newRightPos = containerBounds.max;
        }

        lastAttracted = areAttracted;

        const duration = instant ? 0 : calculateTransitionDuration(currentDistance, areAttracted);
        const easingFunction = areAttracted 
            ? 'cubic-bezier(0.15, 0, 0.15, 1)'
            : 'cubic-bezier(0.25, 0.1, 0.25, 1)';
        
        const transitionStyle = `left ${duration}ms ${easingFunction}`;
        
        leftMagnet.style.transition = transitionStyle;
        rightMagnet.style.transition = transitionStyle;

        leftMagnet.style.left = `${newLeftPos}px`;
        rightMagnet.style.left = `${newRightPos}px`;

        magnetStates.left.position = newLeftPos;
        magnetStates.right.position = newRightPos;
    }

    function togglePolarity(magnet) {
        const isLeft = magnet.classList.contains('left');
        const magnetState = isLeft ? magnetStates.left : magnetStates.right;
        
        magnetState.polarity = magnetState.polarity === 'N' ? 'S' : 'N';
        magnet.dataset.polarity = magnetState.polarity;
        
        updateMagnetPositions();
    }

    // Handle window resize
    window.addEventListener('resize', () => {
        containerBounds.max = container.offsetWidth - 80;
        updateMagnetPositions();
    });

    // Intersection Observer for viewport detection
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !isInViewport) {
                isInViewport = true;
                // Initialize touching position
                initializeMagnets();
                // Trigger repulsion after a brief moment
                setTimeout(() => {
                    updateMagnetPositions();
                }, 100);
            } else if (!entry.isIntersecting && isInViewport) {
                isInViewport = false;
                hasInitialized = false;
                // Reset to touching position when out of viewport
                initializeMagnets();
            }
        });
    }, {
        threshold: [0.5],
        rootMargin: '-10% 0px'
    });

    if (magnetPlayground) {
        // Set initial touching position
        initializeMagnets();
        observer.observe(magnetPlayground);
    }

    magnets.forEach(magnet => {
        magnet.addEventListener('click', () => togglePolarity(magnet));
    });

    // Add keyboard shortcut for random polarity toggle
    document.addEventListener('keydown', (event) => {
        if (event.key.toLowerCase() === 'm' && magnetPlayground) {
            // Only proceed if magnets section is in viewport
            const rect = magnetPlayground.getBoundingClientRect();
            const isVisible = rect.top < window.innerHeight && rect.bottom > 0;
            
            if (isVisible) {
                // Randomly select left or right magnet
                const randomMagnet = Math.random() < 0.5 ? 
                    document.querySelector('.magnet.left') : 
                    document.querySelector('.magnet.right');
                    
                if (randomMagnet) {
                    togglePolarity(randomMagnet);
                }
            }
        }
    });
}); 