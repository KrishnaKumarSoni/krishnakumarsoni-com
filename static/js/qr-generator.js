/**
 * QR Code Placeholder Generator
 * Creates a placeholder QR image using canvas
 */
document.addEventListener('DOMContentLoaded', function() {
    createQrPlaceholder();
});

function createQrPlaceholder() {
    // Create a canvas element
    const canvas = document.createElement('canvas');
    canvas.width = 180;
    canvas.height = 180;
    
    const ctx = canvas.getContext('2d');
    
    // Fill background
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw placeholder pattern with real QR code structure
    
    // Set colors
    const dotColor = '#D35400';
    ctx.fillStyle = dotColor;
    
    // Draw the three finder patterns (large squares in corners)
    drawFinderPattern(ctx, 20, 20, 40);
    drawFinderPattern(ctx, canvas.width - 60, 20, 40);
    drawFinderPattern(ctx, 20, canvas.width - 60, 40);
    
    // Draw alignment pattern (smaller square usually in bottom right)
    drawAlignmentPattern(ctx, canvas.width - 40, canvas.height - 40, 20);
    
    // Draw timing patterns (dotted lines connecting finder patterns)
    drawTimingPatterns(ctx, 40, dotColor);
    
    // Draw random data dots
    drawRandomData(ctx, dotColor, 4);
    
    // Convert to data URL
    const dataUrl = canvas.toDataURL('image/png');
    
    // Store in localStorage to use as placeholder
    localStorage.setItem('qrPlaceholder', dataUrl);
    
    // Find all QR code image elements and set this as default src if empty
    document.querySelectorAll('img#payment-qr-code').forEach(img => {
        if (!img.getAttribute('src') || img.getAttribute('src') === '/static/images/qr-placeholder.png') {
            img.src = dataUrl;
        }
    });
    
    return dataUrl;
}

// Draw a QR finder pattern (the three large squares in corners)
function drawFinderPattern(ctx, x, y, size) {
    // Outer square
    ctx.fillStyle = '#D35400';
    ctx.fillRect(x, y, size, size);
    
    // Middle white square
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(x + size/7, y + size/7, size - 2*size/7, size - 2*size/7);
    
    // Inner colored square
    ctx.fillStyle = '#D35400';
    ctx.fillRect(x + 2*size/7, y + 2*size/7, size - 4*size/7, size - 4*size/7);
}

// Draw alignment pattern (smaller square in bottom right)
function drawAlignmentPattern(ctx, x, y, size) {
    // Outer square
    ctx.fillStyle = '#D35400';
    ctx.fillRect(x - size/2, y - size/2, size, size);
    
    // Middle white square
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(x - size/2 + size/5, y - size/2 + size/5, size - 2*size/5, size - 2*size/5);
    
    // Inner colored dot
    ctx.fillStyle = '#D35400';
    ctx.beginPath();
    ctx.arc(x, y, size/5, 0, Math.PI * 2);
    ctx.fill();
}

// Draw timing patterns (dotted lines connecting finder patterns)
function drawTimingPatterns(ctx, offset, color) {
    const dotSize = 5;
    const gap = 5;
    
    ctx.fillStyle = color;
    
    // Horizontal timing pattern
    for (let x = offset + 10; x < ctx.canvas.width - offset - 10; x += (dotSize + gap)) {
        ctx.beginPath();
        ctx.arc(x, offset, dotSize/2, 0, Math.PI * 2);
        ctx.fill();
    }
    
    // Vertical timing pattern
    for (let y = offset + 10; y < ctx.canvas.height - offset - 10; y += (dotSize + gap)) {
        ctx.beginPath();
        ctx.arc(offset, y, dotSize/2, 0, Math.PI * 2);
        ctx.fill();
    }
}

// Draw random data dots to simulate QR data
function drawRandomData(ctx, color, dotSize) {
    const width = ctx.canvas.width;
    const height = ctx.canvas.height;
    const padding = 20;
    const grid = Math.floor((width - 2 * padding) / (dotSize * 2));
    
    ctx.fillStyle = color;
    
    // Create a grid-like pattern of dots for more realistic QR appearance
    for (let i = 0; i < grid; i++) {
        for (let j = 0; j < grid; j++) {
            // Skip areas where finder patterns and alignment patterns are
            if ((i < 7 && j < 7) || 
                (i < 7 && j > grid - 8) || 
                (i > grid - 8 && j < 7) ||
                (i > grid - 5 && j > grid - 5)) {
                continue;
            }
            
            // 40% chance to draw a dot
            if (Math.random() < 0.4) {
                const x = padding + i * dotSize * 2;
                const y = padding + j * dotSize * 2;
                
                ctx.beginPath();
                ctx.arc(x, y, dotSize, 0, Math.PI * 2);
                ctx.fill();
            }
        }
    }
}

// Make the function accessible globally
window.createQrPlaceholder = createQrPlaceholder; 