def calculate_authenticity_score(ai_score_prob, ela_score, noise_score, compression_score, ocr_score, layout_score):
    """
    Combines various forensic and AI metrics into a single authenticity score.
    Returns: 
        final_score: 0-100% (100% means completely authentic, 0% means definitely fake)
        issues: List of detected string issues
    """
    
    issues = []
    
    # AI Score (prob of being FAKE)
    ai_penalty = ai_score_prob * 100
    if ai_penalty > 50:
        issues.append("AI model detected manipulated visual patterns")
        
    if ela_score > 30:
        issues.append("Inconsistent error levels detected (possible recompression)")
        
    if noise_score > 15:
        issues.append("Pixel noise inconsistency (possible spliced region)")
        
    if compression_score > 20:
        issues.append("JPEG block artifacts mismatch")
        
    if ocr_score > 15:
        issues.append("Text alignment anomalies detected")
        
    if layout_score > 20:
        issues.append("Chat bubble layout spacing anomalies")
        
    # Weighted calculation
    # We invert the penalties so 100 means real.
    
    # Weights sum to 1.0
    weights = {
        'ai': 0.35,
        'ela': 0.15,
        'noise': 0.10,
        'compression': 0.15,
        'ocr': 0.15,
        'layout': 0.10
    }
    
    total_penalty = (
        ai_penalty * weights['ai'] +
        ela_score * weights['ela'] +
        noise_score * weights['noise'] +
        compression_score * weights['compression'] +
        ocr_score * weights['ocr'] +
        layout_score * weights['layout']
    )
    
    final_score = max(0.0, 100.0 - total_penalty)
    
    conclusion = "The screenshot appears to be authentic."
    if final_score < 50:
        conclusion = "The screenshot is highly likely to be manipulated."
    elif final_score < 75:
        conclusion = "The screenshot may have been manipulated. Proceed with caution."
        
    return int(final_score), issues, conclusion
