# Step 1: Start with Python installed
FROM python:3.11-slim

# Step 2: Set up workspace inside container
WORKDIR /app

# Step 3: Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Step 4: Copy your app code from the subdirectory
COPY multimodal_rag_api/app ./app

# Step 5: Create folders for data storage
RUN mkdir -p data chroma_db

# Step 6: Tell Docker which port your app uses
EXPOSE 8000

# Step 7: Command to start your FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 