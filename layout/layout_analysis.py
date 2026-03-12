import cv2
import numpy as np

def check_chat_layout(image_path):
    """
    Analyzes the structure of chat bubbles in a screenshot.
    Looks for inconsistent bubble spacing or misaligned bubble edges.
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            return 0, []

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Edge detection to find bubbles
        edges = cv2.Canny(gray, 50, 150)
        
        # Morphological operations to group edges into blocks (bubbles)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 10))
        dilated = cv2.dilate(edges, kernel, iterations=2)
        
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        bubbles = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            # Filter out elements that don't match typical bubble aspect ratios/sizes
            if w > 100 and h > 30: 
                bubbles.append({'x': x, 'y': y, 'w': w, 'h': h})
                
        # Sort bubbles by Y position
        bubbles = sorted(bubbles, key=lambda b: b['y'])
        
        anomalies = []
        anomaly_score = 0
        
        if len(bubbles) > 1:
            # Check for irregular spacing between bubbles
            spacings = []
            for i in range(1, len(bubbles)):
                space = bubbles[i]['y'] - (bubbles[i-1]['y'] + bubbles[i-1]['h'])
                if space > 0:
                    spacings.append(space)
                    
            if spacings:
                median_space = np.median(spacings)
                for i in range(1, len(bubbles)):
                    space = bubbles[i]['y'] - (bubbles[i-1]['y'] + bubbles[i-1]['h'])
                    if space > 0:
                        # If the spacing is inexplicably different from the typical gap
                        diff = abs(space - median_space)
                        if diff > 15 and diff < 100: # Not a massive gap (which could just be an image/date separator), but a subtle one
                            anomaly_score += 25
                            anomalies.append({
                                'x': bubbles[i]['x'], 'y': bubbles[i]['y'] - int(space), 
                                'width': bubbles[i]['w'], 'height': int(space),
                                'type': 'Irregular Bubble Spacing'
                            })

        score = min(anomaly_score, 100)
        return score, anomalies

    except Exception as e:
        print(f"Error in layout analysis: {e}")
        return 0, []
