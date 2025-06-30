# Step 1: Start with Python installed
FROM python:3.11-slim

# Step 2: Install system dependencies for python-magic and PDF processing
RUN apt-get update && apt-get install -y \
    libmagic1 \
    libmagic-dev \
    && rm -rf /var/lib/apt/lists/*

# Step 3: Set up workspace inside container
WORKDIR /app

# Step 4: Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Step 5: Copy your app code from the subdirectory
COPY multimodal_rag_api/app ./app

# Step 6: Create folders for data storage
RUN mkdir -p data chroma_db

# Step 7: Tell Docker which port your app uses
EXPOSE 8000

# Step 8: Command to start your FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 