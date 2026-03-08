# ── Stage: runtime ────────────────────────────────────────────────────────────
FROM python:3.12-slim

# System dependencies
#   libgl1 + libglib2.0-0 → OpenCV
#   ffmpeg                 → audio/video processing
#   poppler-utils          → pdf2image
#   libpango-1.0-0 …       → weasyprint (PDF rendering), install if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    ffmpeg \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Create data directory for local storage
RUN mkdir -p data

EXPOSE 8000

# Production: 4 workers; override CMD for development (--reload)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
