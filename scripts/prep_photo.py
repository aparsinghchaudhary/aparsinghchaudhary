import sys
import cv2
import numpy as np
from PIL import Image
from rembg import remove

def process_portrait(input_path="hero.png", output_path="source-prepped.png"):
    print(f"Reading input image from {input_path}...")
    with open(input_path, 'rb') as f:
        input_data = f.read()
    
    # Remove background using U2Net
    print("Removing background with U2Net...")
    output_bg_removed = remove(input_data)
    
    # Convert to PIL Image
    from io import BytesIO
    pil_img = Image.open(BytesIO(output_bg_removed)).convert("RGBA")
    
    # Create black background layer
    background = Image.new("RGBA", pil_img.size, (13, 13, 13, 255))
    alpha_composite = Image.alpha_composite(background, pil_img).convert("L")
    
    # Contrast enhancement (CLAHE via OpenCV)
    np_img = np.array(alpha_composite)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(np_img)
    
    # Save prepped image
    result_img = Image.fromarray(enhanced)
    result_img.save(output_path)
    print(f"Saved optimized source image to {output_path}")

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "hero.png"
    process_portrait(path)
