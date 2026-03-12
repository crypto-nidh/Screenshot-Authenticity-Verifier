# Screenshot Authenticity Verifier

A full-stack AI/ML cybersecurity project to detect whether chat screenshots from platforms like WhatsApp, Instagram, Telegram, and Snapchat are real or manipulated.

## Features
- **Frontend**: Clean, modern UI with drag-and-drop image upload and visual bounding boxes for manipulated regions.
- **Backend**: FastAPI server running the models and forensics.
- **AI Model**: PyTorch-based CNN (MobileNetV2) to classify images as real or fake.
- **Forensics**: 
  - Error Level Analysis (ELA)
  - Pixel Noise Analysis
  - Compression Artifact Detection
- **OCR**: Text extraction and layout/alignment anomaly detection using Tesseract.
- **Reporting**: Automated PDF report generation with ReportLab.

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Tesseract OCR (Required for text analysis):
- **Linux**: `sudo apt install tesseract-ocr`
- **Mac**: `brew install tesseract`
- **Windows**: Download the installer from the official repository and add it to your PATH.

## Project Structure

- `dataset/`: Place your training images here.
  - `dataset/real/`: Authentic screenshots.
  - `dataset/fake/`: Manipulated screenshots.
- `models/`: PyTorch datasets, model definitions, and training scripts.
- `forensics/`: Digital image forensics algorithms.
- `ocr/` & `layout/`: Text alignment and structural analysis.
- `backend/`: FastAPI application and scoring logic.
- `frontend/`: HTML, CSS, and JS web interface.
- `reports/`: Generated PDF forensics reports.
- `uploads/`: Temporary storage for uploaded images.

## Model Training

Before using the AI model, you need to train it on your manual dataset.
1. Populate `dataset/real` and `dataset/fake` with images.
2. Run the training script:
```bash
python -m models.train
```
This will save the trained weights to `models/saved_model.pth`. The API will automatically load this file if it exists.

## Running the Application

1. **Start the Backend API:**
```bash
uvicorn backend.main:app --reload
```
The API will run on `http://127.0.0.1:8000`.

2. **Open the Frontend:**
Simply open `frontend/index.html` in your web browser. Drag and drop a screenshot to see the analysis!
