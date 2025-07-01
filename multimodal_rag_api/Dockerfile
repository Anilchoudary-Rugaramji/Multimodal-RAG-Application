# Step 1: Start with Python installed
FROM python:3.11-slim

# Step 2: Install system dependencies including OpenGL for OpenCV
RUN apt-get update && apt-get install -y \
    libmagic1 \
    tesseract-ocr \
    poppler-utils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Step 3: Set up workspace inside container
WORKDIR /app

# Step 4: Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy your app code
COPY app ./app

# Step 6: Create folders for data storage
RUN mkdir -p data chroma_db

# Step 7: Tell Docker which port your app uses
EXPOSE 8000

# Step 8: Start the real FastAPI app with faster startup
CMD ["bash", "-c", "PORT=${PORT:-8000} && echo 'Starting Multimodal RAG API on port' $PORT && uvicorn app.main:app --host 0.0.0.0 --port $PORT --log-level info --timeout-keep-alive 120"] 