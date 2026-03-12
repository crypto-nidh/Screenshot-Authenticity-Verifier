import cv2
import numpy as np

def detect_compression_artifacts(image_path):
    """
    Detects anomalies in JPEG compression artifacts by checking 8x8 block boundaries.
    JPEG compresses images in 8x8 blocks. Discontinuities at these boundaries
    can indicate pasting/editing.
    """
    try:
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return 0
            
        h, w = img.shape
        
        # Need at least an 8x8 image
        if h < 8 or w < 8:
            return 0
            
        img = np.float32(img)
        
        # Calculate horizontal and vertical differences
        diff_h = np.abs(img[:, :-1] - img[:, 1:])
        diff_v = np.abs(img[:-1, :] - img[1:, :])
        
        # Extract block boundary differences (multiples of 8)
        # horizontal boundaries
        b_h = diff_h[:, 7::8]
        # non-boundaries horizontal
        # We sample columns that are NOT multiples of 8
        nb_indices_h = [i for i in range(diff_h.shape[1]) if (i + 1) % 8 != 0]
        nb_h = diff_h[:, nb_indices_h]
        
        # vertical boundaries
        b_v = diff_v[7::8, :]
        # non-boundaries vertical
        nb_indices_v = [i for i in range(diff_v.shape[0]) if (i + 1) % 8 != 0]
        nb_v = diff_v[nb_indices_v, :]
        
        # Averages
        mean_b_h = np.mean(b_h) if b_h.size > 0 else 0
        mean_nb_h = np.mean(nb_h) if nb_h.size > 0 else 0
        
        mean_b_v = np.mean(b_v) if b_v.size > 0 else 0
        mean_nb_v = np.mean(nb_v) if nb_v.size > 0 else 0
        
        # Block artifact measure
        bam_h = mean_b_h / max(mean_nb_h, 1e-5)
        bam_v = mean_b_v / max(mean_nb_v, 1e-5)
        
        bam_avg = (bam_h + bam_v) / 2.0
        
        # Simple scoring heuristic.
        # Normal JPEG usually has BAM < 2.0.
        # High BAM means strong compression block edges. 
        # Inconsistencies or extreme values can mean editing.
        # For our specific case, just detecting if artifacts are highly visible.
        if bam_avg < 1.0:
            return 0 # Smooth/uncompressed
            
        score = min(((bam_avg - 1.0) / 3.0) * 100, 100)
        return score
        
    except Exception as e:
        print(f"Error in compression analysis: {e}")
        return 0
