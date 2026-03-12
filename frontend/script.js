document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const previewContainer = document.getElementById('preview-container');
    const imagePreview = document.getElementById('image-preview');
    const imageWrapper = document.getElementById('image-wrapper');
    const analyzeBtn = document.getElementById('analyze-btn');
    const loading = document.getElementById('loading');
    const resultsSection = document.getElementById('results-section');
    const resetBtn = document.getElementById('reset-btn');
    const downloadReportBtn = document.getElementById('download-report-btn');
    
    const scoreCirclePath = document.getElementById('score-circle-path');
    const scoreText = document.getElementById('score-text');
    const conclusionText = document.getElementById('conclusion-text');
    const issuesCard = document.getElementById('issues-card');
    const issuesList = document.getElementById('issues-list');

    let selectedFile = null;

    // Drag and Drop Events
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length) {
            handleFile(fileInput.files[0]);
        }
    });

    function handleFile(file) {
        if (!file.type.startsWith('image/')) {
            alert('Please upload an image file.');
            return;
        }
        
        selectedFile = file;
        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            dropZone.style.display = 'none';
            previewContainer.style.display = 'block';
            
            // Clear previous bounding boxes
            document.querySelectorAll('.bounding-box').forEach(el => el.remove());
        };
        reader.readAsDataURL(file);
    }

    // Reset flow
    resetBtn.addEventListener('click', () => {
        selectedFile = null;
        fileInput.value = '';
        dropZone.style.display = 'block';
        previewContainer.style.display = 'none';
        resultsSection.style.display = 'none';
        document.querySelectorAll('.bounding-box').forEach(el => el.remove());
    });

    // Analyze Button
    analyzeBtn.addEventListener('click', async () => {
        if (!selectedFile) return;

        // UI State: Loading
        analyzeBtn.style.display = 'none';
        loading.style.display = 'block';
        resultsSection.style.display = 'none';
        document.querySelectorAll('.bounding-box').forEach(el => el.remove());

        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            // Call the FastAPI Backend
            const response = await fetch('http://127.0.0.1:8000/analyze', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Server responded with status ${response.status}`);
            }

            const data = await response.json();
            displayResults(data);
        } catch (error) {
            console.error('Analysis error:', error);
            alert('Error running analysis. Is the FastAPI server running? ' + error.message);
            analyzeBtn.style.display = 'block';
            loading.style.display = 'none';
        }
    });

    function displayResults(data) {
        // UI State: Results
        loading.style.display = 'none';
        resultsSection.style.display = 'block';
        analyzeBtn.style.display = 'block';

        // 1. Plot Score
        const score = data.score;
        scoreText.textContent = `${score}%`;
        scoreCirclePath.setAttribute('stroke-dasharray', `${score}, 100`);

        // Set color based on score
        if (score >= 75) {
            scoreCirclePath.style.stroke = 'var(--success)';
            conclusionText.style.color = 'var(--success)';
        } else if (score >= 50) {
            scoreCirclePath.style.stroke = 'var(--warning)';
            conclusionText.style.color = 'var(--warning)';
        } else {
            scoreCirclePath.style.stroke = 'var(--danger)';
            conclusionText.style.color = 'var(--danger)';
        }

        conclusionText.textContent = data.conclusion;

        // 2. Display Issues
        if (data.issues && data.issues.length > 0) {
            issuesCard.style.display = 'block';
            issuesList.innerHTML = '';
            data.issues.forEach(issue => {
                const li = document.createElement('li');
                li.textContent = issue;
                issuesList.appendChild(li);
            });
        } else {
            issuesCard.style.display = 'none';
        }

        // 3. Setup PDF Download
        downloadReportBtn.href = `http://127.0.0.1:8000${data.report_url}`;

        // 4. Draw bounding boxes for suspicious regions
        // Wait for image to fully compute dimensions in CSS
        setTimeout(() => {
            if (data.suspicious_regions && data.suspicious_regions.length > 0) {
                drawBoundingBoxes(data.suspicious_regions);
            }
        }, 100);
    }

    function drawBoundingBoxes(regions) {
        // We need to scale the boxes from the original image dimensions to the rendered dimensions
        const imgCanvas = document.createElement('canvas');
        const ctx = imgCanvas.getContext('2d');
        const img = new Image();
        img.src = imagePreview.src;
        
        img.onload = () => {
            const originalWidth = img.width;
            const originalHeight = img.height;
            
            const renderedWidth = imagePreview.clientWidth;
            const renderedHeight = imagePreview.clientHeight;
            
            const scaleX = renderedWidth / originalWidth;
            const scaleY = renderedHeight / originalHeight;
            
            regions.forEach(region => {
                const box = document.createElement('div');
                box.className = 'bounding-box';
                // Some backends return x, y, width, height. Some return w, h.
                const w = region.width || region.w;
                const h = region.height || region.h;
                
                box.style.left = `${region.x * scaleX}px`;
                box.style.top = `${region.y * scaleY}px`;
                box.style.width = `${w * scaleX}px`;
                box.style.height = `${h * scaleY}px`;
                
                // Add tooltip with the anomaly type
                box.title = region.type || 'Anomaly Detected';
                
                imageWrapper.appendChild(box);
            });
        };
    }
});
