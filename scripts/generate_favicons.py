from PIL import Image
import os

def generate_favicons():
    # Input logo path
    logo_path = 'static/images/kks-logo.png'
    favicon_dir = 'static/images/favicon'
    
    # Create favicon directory if it doesn't exist
    os.makedirs(favicon_dir, exist_ok=True)
    
    # Open the logo image
    img = Image.open(logo_path)
    
    # Convert to RGBA if not already
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Create a white background image
    def create_favicon(size):
        # Create a white background
        background = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        
        # Calculate the size to maintain aspect ratio
        ratio = min(size/img.width, size/img.height)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        
        # Resize the logo
        resized_img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # Calculate position to center the logo
        position = ((size - new_size[0])//2, (size - new_size[1])//2)
        
        # Paste the logo onto the background
        background.paste(resized_img, position, resized_img)
        return background
    
    # Generate different sizes
    sizes = {
        'favicon-16x16.png': 16,
        'favicon-32x32.png': 32,
        'apple-touch-icon.png': 180,
        'android-chrome-192x192.png': 192,
        'android-chrome-512x512.png': 512
    }
    
    for filename, size in sizes.items():
        favicon = create_favicon(size)
        favicon.save(os.path.join(favicon_dir, filename), 'PNG')

if __name__ == '__main__':
    generate_favicons() 