from PIL import Image, ImageDraw, ImageFont
import os

# Create icons directory
os.makedirs('static/icons', exist_ok=True)

# Icon sizes needed
sizes = [72, 96, 128, 144, 152, 192, 384, 512]

# Colors
bg_color = '#0f172a'
icon_color = '#22d3ee'
text_color = '#ffffff'

for size in sizes:
    # Create image
    img = Image.new('RGB', (size, size), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Draw shield shape (simplified)
    center = size // 2
    margin = size // 4
    
    # Draw shield border
    draw.ellipse([margin, margin, size - margin, size - margin], 
                 outline=icon_color, width=max(2, size // 32))
    
    # Draw 'S' in the center
    try:
        font = ImageFont.truetype("arial.ttf", size // 2)
    except:
        font = ImageFont.load_default()
    
    draw.text((center - size//6, center - size//4), "🛡️", 
              fill=icon_color, font=font)
    
    # Save icon
    img.save(f'static/icons/icon-{size}.png')
    print(f'Created icon-{size}.png')

print('All icons created successfully!')