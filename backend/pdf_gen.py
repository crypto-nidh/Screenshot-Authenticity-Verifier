import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime

def generate_pdf_report(image_path, score, issues, conclusion, output_filename="report.pdf"):
    """
    Generates a PDF forensic analysis report.
    """
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)
    
    pdf_path = os.path.join(reports_dir, output_filename)
    
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 20)
    c.drawString(1 * inch, height - 1 * inch, "Screenshot Authenticity Verifier Report")
    
    # Timestamp
    c.setFont("Helvetica", 12)
    c.drawString(1 * inch, height - 1.3 * inch, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Image (draw thumbnail)
    c.drawString(1 * inch, height - 1.8 * inch, "Analyzed Image:")
    try:
        c.drawImage(image_path, 1 * inch, height - 4 * inch, width=3*inch, preserveAspectRatio=True)
    except Exception as e:
        c.drawString(1 * inch, height - 2 * inch, f"(Could not load image: {e})")
        
    # Analysis Results
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1 * inch, height - 4.5 * inch, "Analysis Results")
    
    c.setFont("Helvetica", 12)
    # Color based on score
    if score >= 75:
        c.setFillColor(colors.green)
    elif score >= 50:
        c.setFillColor(colors.orange)
    else:
        c.setFillColor(colors.red)
        
    c.drawString(1 * inch, height - 4.8 * inch, f"Authenticity Score: {score}%")
    c.setFillColor(colors.black)
    
    # Conclusion
    c.setFont("Helvetica-Italic", 12)
    c.drawString(1 * inch, height - 5.2 * inch, f"Conclusion: {conclusion}")
    
    # Issues
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1 * inch, height - 5.8 * inch, "Detected Issues:")
    
    c.setFont("Helvetica", 12)
    y_pos = height - 6.2 * inch
    if not issues:
        c.drawString(1.2 * inch, y_pos, "None detected.")
    else:
        for idx, issue in enumerate(issues):
            c.drawString(1.2 * inch, y_pos, f"- {issue}")
            y_pos -= 0.3 * inch

    c.save()
    return pdf_path
