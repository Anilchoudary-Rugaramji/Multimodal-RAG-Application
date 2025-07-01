#!/usr/bin/env python3

import os
import sys

print("=== DEBUG START ===")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"Available files: {os.listdir('.')}")
print(f"OPENAI_API_KEY set: {bool(os.getenv('OPENAI_API_KEY'))}")
print(f"PORT: {os.getenv('PORT', 'not set')}")

try:
    print("Testing basic FastAPI import...")
    from fastapi import FastAPI
    print("✅ FastAPI imported successfully")
    
    print("Testing app creation...")
    app = FastAPI(title="Debug API")
    
    @app.get("/")
    def root():
        return {"status": "working", "port": os.getenv("PORT", "unknown")}
        
    print("✅ Basic app created successfully")
    
    print("Testing uvicorn import...")
    import uvicorn
    print("✅ Uvicorn imported successfully")
    
    # Try to start the server
    port = int(os.getenv("PORT", 8000))
    print(f"Starting server on port {port}...")
    
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 