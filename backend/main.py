import os
import shutil
import uuid
import torch
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image

# Import custom modules
from models.model import ScreenshotAuthenticator
from models.dataset import get_transforms
from forensics.ela import get_ela_score
from forensics.noise import perform_noise_analysis
from forensics.compression import detect_compression_artifacts
from forensics.region_detector import detect_suspicious_regions
from ocr.text_analysis import analyze_text_alignment
from layout.layout_analysis import check_chat_layout
from backend.scoring import calculate_authenticity_score
from backend.pdf_gen import generate_pdf_report

app = FastAPI(title="Screenshot Authenticity Verifier API")

# Setup CORS for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Load AI Model (Lazy load or global)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = ScreenshotAuthenticator(num_classes=2).to(device)
model_path = "models/saved_model.pth"

# Attempt to load weights if they exist
if os.path.exists(model_path):
    model.load_state_dict(torch.load(model_path, map_location=device))
    print("Loaded trained AI model.")
else:
    print("Warning: No trained model found at", model_path, "- Using initialized weights (mock output).")

@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    # 1. Save uploaded file
    file_ext = file.filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{file_ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # 2. Run AI Model Analysis
    try:
        transform = get_transforms()
        image = Image.open(filepath).convert('RGB')
        input_tensor = transform(image).unsqueeze(0).to(device)
        ai_prob_fake = model.predict_proba(input_tensor)
    except Exception as e:
        print(f"AI Model error: {e}")
        ai_prob_fake = 0.5 # Default to unsure if model fails
        
    # 3. Run Forensic Analysis
    ela_score = get_ela_score(filepath)
    noise_score = perform_noise_analysis(filepath)
    compression_score = detect_compression_artifacts(filepath)
    
    # 4. Run OCR & Layout Checks
    ocr_score, ocr_anomalies = analyze_text_alignment(filepath)
    layout_score, layout_anomalies = check_chat_layout(filepath)
    
    # 5. Extract bounding boxes for suspicious regions
    ela_regions = detect_suspicious_regions(filepath)
    
    all_suspicious_regions = ela_regions + ocr_anomalies + layout_anomalies
    
    # 6. Calculate Final Score
    final_score, issues, conclusion = calculate_authenticity_score(
        ai_score_prob=ai_prob_fake,
        ela_score=ela_score,
        noise_score=noise_score,
        compression_score=compression_score,
        ocr_score=ocr_score,
        layout_score=layout_score
    )
    
    # 7. Generate PDF Report
    report_filename = f"report_{uuid.uuid4()}.pdf"
    report_path = generate_pdf_report(filepath, final_score, issues, conclusion, report_filename)
    
    return JSONResponse({
        "status": "success",
        "score": final_score,
        "issues": issues,
        "conclusion": conclusion,
        "suspicious_regions": all_suspicious_regions,
        "report_url": f"/report/{report_filename}",
        "metrics": {
            "ai_prob_fake": ai_prob_fake,
            "ela_score": ela_score,
            "noise_score": noise_score,
            "compression_score": compression_score,
            "ocr_score": ocr_score,
            "layout_score": layout_score
        }
    })

@app.get("/report/{filename}")
async def get_report(filename: str):
    report_path = os.path.join("reports", filename)
    if os.path.exists(report_path):
        return FileResponse(report_path, media_type="application/pdf", filename=filename)
    return JSONResponse({"error": "Report not found"}, status_code=404)
