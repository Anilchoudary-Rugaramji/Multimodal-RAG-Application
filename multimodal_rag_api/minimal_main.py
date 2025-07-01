#!/usr/bin/env python3

import os
import sys

print("=== MINIMAL APP DEBUG ===")

try:
    print("1. Testing basic FastAPI...")
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    print("✅ FastAPI imported")
    
    print("2. Creating basic app...")
    app = FastAPI(title="Multimodal RAG API", version="1.0.0")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    def root():
        return {"message": "Multimodal RAG API is running."}
    
    @app.get("/health")
    def health():
        return {
            "status": "healthy",
            "openai_key_set": bool(os.getenv("OPENAI_API_KEY")),
            "port": os.getenv("PORT", "unknown")
        }
    
    print("✅ Basic app created")
    
    print("3. Testing app.api import...")
    try:
        from app.api import router
        print("✅ API router imported")
        app.include_router(router)
        print("✅ Router included")
    except Exception as e:
        print(f"❌ API import failed: {e}")
        # Continue without API router for now
    
    print("4. Starting uvicorn...")
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"Starting on port {port}")
    
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
    
except Exception as e:
    print(f"❌ STARTUP ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 