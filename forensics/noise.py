import cv2
import numpy as np

def perform_noise_analysis(image_path):
    """
    Detects pixel noise inconsistencies.
    Edited areas often have different noise levels than original regions.
    """
    try:
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return 0
            
        # Apply median blur to estimate the noise-free image
        blurred = cv2.medianBlur(img, 3)
        
        # Extract noise by subtracting blurred from original
        noise = cv2.absdiff(img, blurred)
        
        # Divide into grids and analyze noise variance per block
        h, w = noise.shape
        grid_size = 32
        
        block_variances = []
        for y in range(0, h, grid_size):
            for x in range(0, w, grid_size):
                block = noise[y:y+grid_size, x:x+grid_size]
                if block.size > 0:
                    var = np.var(block)
                    block_variances.append(var)
                    
        # If variances fluctuate wildly, it indicates tampering
        std_of_variances = np.std(block_variances)
        mean_var = np.mean(block_variances)
        
        if mean_var == 0:
            return 0
            
        # Relative noise inconsistency score
        inconsistency_ratio = std_of_variances / mean_var
        
        # Heuristic scaling
        score = min((inconsistency_ratio / 1.5) * 100, 100)
        return score
        
    except Exception as e:
        print(f"Error in noise analysis: {e}")
        return 0
