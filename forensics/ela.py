import cv2
import numpy as np
import os
from PIL import Image, ImageChops, ImageEnhance

def perform_ela(image_path, quality=90):
    """
    Performs Error Level Analysis on an image.
    Saves a temporary JPEG at a specific quality and compares it to the original.
    """
    temp_filename = "temp_ela.jpg"
    
    try:
        original = Image.open(image_path).convert('RGB')
        
        # Save temp image at given quality
        original.save(temp_filename, 'JPEG', quality=quality)
        
        # Open temp image
        temp_img = Image.open(temp_filename)
        
        # Calculate the absolute difference between original and temp
        ela_img = ImageChops.difference(original, temp_img)
        
        # Calculate ELA value (max diff) to extract features/score
        extrema = ela_img.getextrema()
        max_diff = max([ex[1] for ex in extrema])
        
        # Scale to improve visibility
        if max_diff == 0:
            scale = 1
        else:
            scale = 255.0 / max_diff
            
        ela_img = ImageEnhance.Brightness(ela_img).enhance(scale)
        
        # Convert to numpy array for OpenCV processing if needed
        ela_np = np.array(ela_img)
        
        # Clean up
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
            
        return ela_img, ela_np, max_diff
    except Exception as e:
        print(f"Error in ELA: {e}")
        return None, None, 0

def get_ela_score(image_path):
    """
    Returns a simple score based on ELA anomalies.
    High standard deviation in ELA typically points to modification.
    """
    _, ela_np, _ = perform_ela(image_path)
    if ela_np is None:
        return 0
        
    # Convert to grayscale
    gray = cv2.cvtColor(ela_np, cv2.COLOR_RGB2GRAY)
    
    # Analyze the standard deviation of blocks to find inconsistencies
    std_dev = np.std(gray)
    
    # Normalize score somewhat (heuristic: normal range 10-30, tampered > 30)
    score = min((std_dev / 40.0) * 100, 100)
    return score
