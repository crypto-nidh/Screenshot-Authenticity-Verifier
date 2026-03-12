import cv2
import numpy as np
from forensics.ela import perform_ela

def detect_suspicious_regions(image_path):
    """
    Uses ELA output to find bounding boxes of highly modified regions.
    """
    _, ela_np, max_diff = perform_ela(image_path)
    if ela_np is None:
        return []
        
    gray = cv2.cvtColor(ela_np, cv2.COLOR_RGB2GRAY)
    
    # Thresholding to find areas with high ELA differences
    # The threshold depends heavily on the max_diff scale, but we enhanced it in perform_ela
    # so we can use a relative threshold. Adaptive threshold can also work.
    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
    
    # Morphological operations to close gaps
    kernel = np.ones((15, 15), np.uint8)
    closing = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    # Find contours
    contours, _ = cv2.findContours(closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    suspicious_regions = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 1000: # Filter out small noise
            x, y, w, h = cv2.boundingRect(cnt)
            suspicious_regions.append({"x": x, "y": y, "width": w, "height": h, "type": "ELA Anomaly"})
            
    return suspicious_regions
