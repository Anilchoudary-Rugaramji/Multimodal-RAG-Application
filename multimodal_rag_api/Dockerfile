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

# Step 5: Copy your app code and startup script
COPY app ./app
COPY start.sh ./start.sh

# Step 6: Make startup script executable and create folders
RUN chmod +x ./start.sh && mkdir -p data chroma_db

# Step 7: Tell Docker which port your app uses
EXPOSE 8000

# Step 8: Use startup script to handle PORT environment variable
CMD ["./start.sh"] 