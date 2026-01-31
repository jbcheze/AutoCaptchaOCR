# ================================================================================================================================
# CAPTCHA GENERATOR
# The goal is to generate captchas like images for train set.
# ================================================================================================================================

import os
import random
from PIL import Image, ImageDraw, ImageFont

class CaptchaGenerator:
    def __init__(self, width=120, height=72):
        self.width = width
        self.height = height
    
    def generate_text(self, length=6):
        # ================================================================================================================================
        # Generating random 6 characters
        # ================================================================================================================================
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        return ''.join(random.choice(chars) for _ in range(length))
    
    def generate_captcha(self, text=None):
        # ================================================================================================================================
        # Generating images (bg, text, font, colours, noise)
        # ================================================================================================================================
        if text is None:
            text = self.generate_text()
        
        # Bg colours
        bg_color = (random.randint(220, 255),) * 3
        image = Image.new('RGB', (self.width, self.height), bg_color)
        draw = ImageDraw.Draw(image)
        
        # Load font
        try:
            font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 32)
        except:
            font = ImageFont.load_default()
        
        # Text colours
        text_color = (random.randint(20, 80),)*3
        
        # Center text
        bbox = draw.textbbox((0, 0), text, font=font)
        x = (self.width - (bbox[2] - bbox[0]))//2
        y = (self.height - (bbox[3] - bbox[1]))//2
        
        draw.text((x, y), text, fill=text_color, font=font)
        
        # Add noise lines
        for _ in range(2):
            x1, y1 = random.randint(0, self.width), random.randint(0, self.height)
            x2, y2 = random.randint(0, self.width), random.randint(0, self.height)
            draw.line([(x1, y1), (x2, y2)], fill=(120, 120, 120), width=1)
        
        return image, text
    
    def labeling(self, num_images, output_dir='captcha_dataset'):
        # ================================================================================================================================
        # Labeling
        # ================================================================================================================================
        os.makedirs(output_dir, exist_ok=True)
        
        labels = []
        
        for i in range(num_images):
            # Generate CAPTCHA
            image, text = self.generate_captcha()
            
            # Filename with label: captcha_00001_ABC123.png
            filename = f'captcha_{i:05d}_{text}.png'
            filepath = os.path.join(output_dir, filename)
            image.save(filepath)
            
            # Also save to labels.txt
            labels.append(f'{filename}\t{text}')
        
        # Save labels file
        labels_path = os.path.join(output_dir, 'labels.txt')
        with open(labels_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(labels))
        
        print(f'Created {num_images} images in {output_dir}/')
        print(f'Labels saved to {labels_path}')


if __name__ == '__main__':
    generator = CaptchaGenerator()
    
    print("Starting generation")
    generator.labeling(1000, 'data/finetunning_benchmarking_scraped/captchas_generated')
    print("DONE")