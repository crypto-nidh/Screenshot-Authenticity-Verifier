import cv2
import pytesseract
import numpy as np

def analyze_text_alignment(image_path):
    """
    Extracts text bounding boxes to look for misalignment often found in edited chat screenshots.
    Returns an anomaly score and potential misaligned bounding boxes.
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            return 0, []
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Use pytesseract to get bounding boxes
        # Output format: level, page_num, block_num, par_num, line_num, word_num, left, top, width, height, conf, text
        data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
        
        words = []
        for i in range(len(data['text'])):
            if int(data['conf'][i]) > 50 and data['text'][i].strip() != '':
                words.append({
                    'text': data['text'][i],
                    'left': data['left'][i],
                    'top': data['top'][i],
                    'width': data['width'][i],
                    'height': data['height'][i]
                })

        if not words:
            return 0, []

        # Analyze horizontal alignment properties across lines
        # Group by rough lines (Y-axis proximity)
        lines = {}
        for w in words:
            # group by roughly the same top value (+/- 10 pixels)
            line_idx = w['top'] // 20
            if line_idx not in lines:
                lines[line_idx] = []
            lines[line_idx].append(w)
            
        anomalies = []
        anomaly_score = 0.0
        
        # We can perform simple checks: 
        # For messenger apps, messages in the same column should have consistent left/right anchors
        left_anchors = [line[0]['left'] for line in lines.values() if line]
        
        if len(left_anchors) > 2:
            # If an anchor is significantly different from others, it might be an edited word/line.
            median_left = np.median(left_anchors)
            for key, line in lines.items():
                first_word = line[0]
                # If a line starts neither left-aligned nor somewhat right-aligned (which is expected in chat)
                diff_to_median = abs(first_word['left'] - median_left)
                
                # Check if it deviates strangely (not perfectly aligned but close)
                # Chat bubbles usually align perfectly. If it's off by 2-10 pixels, it's highly suspicious (paste artifact)
                if 2 < diff_to_median < 15:
                    anomaly_score += 20
                    anomalies.append({
                        "x": first_word['left'], 
                        "y": first_word['top'], 
                        "width": sum(w['width'] for w in line) + len(line)*5, 
                        "height": first_word['height'],
                        "type": "Text Alignment Anomaly"
                    })
                    
        score = min(anomaly_score, 100)
        return score, anomalies
    except Exception as e:
        print(f"Error in OCR analysis: {e}. Ensure Tesseract is installed.")
        return 0, []
