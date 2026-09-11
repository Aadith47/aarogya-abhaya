# main.py (in root directory)
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
from io import BytesIO
from PIL import Image
import time
from contextlib import asynccontextmanager
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))
from camera_manager import camera_manager

# =============================
# LIFESPAN MANAGER
# =============================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 FastAPI server starting...")
    print("📌 Note: Camera access is not available via FastAPI endpoints")
    print("📌 Use the dedicated client applications for real-time video")
    yield
    # Shutdown
    print("👋 FastAPI server shutting down...")
    # Ensure no camera is locked
    if camera_manager.get_status()['in_use']:
        print("⚠️ Warning: Camera still in use during shutdown")

# =============================
# FASTAPI APP
# =============================
app = FastAPI(
    title="Pregnant Women Posture Module",
    description="API for posture analysis of pregnant women",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================
# HELPER FUNCTIONS
# =============================
def process_image(image_data: bytes):
    """Process uploaded image"""
    try:
        # Convert bytes to image
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Could not decode image")
        return img
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image: {str(e)}")

# =============================
# ROUTES
# =============================
@app.get("/")
async def home():
    """Root endpoint"""
    return {
        "message": "🤰 Pregnant Women Posture Module API",
        "version": "1.0.0",
        "endpoints": {
            "GET /": "This info",
            "GET /health": "Health check",
            "GET /camera-status": "Check camera availability",
            "POST /posture-check/": "Analyze a single image",
            "POST /analyze-batch/": "Analyze multiple images"
        },
        "client_applications": {
            "squat_detection": "Run: python backend/posture/live_posture_detection.py",
            "sitting_detection": "Run: python backend/posture/sitting_posture_module/live_sitting_posture.py"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "camera_status": camera_manager.get_status()['in_use']
    }

@app.get("/camera-status")
async def camera_status():
    """Check camera status"""
    status = camera_manager.get_status()
    return {
        "camera_in_use": status['in_use'],
        "current_user": status['current_user'],
        "message": "Camera is busy" if status['in_use'] else "Camera is available"
    }

@app.post("/posture-check/")
async def posture_check(file: UploadFile = File(...)):
    """
    Analyze a single image for posture
    
    This endpoint processes a single image and returns posture analysis.
    For real-time video, use the dedicated client applications.
    """
    try:
        # Read uploaded file
        contents = await file.read()
        
        # Check file size
        if len(contents) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=400, detail="File too large (max 10MB)")
        
        # Check if camera is in use (just for information)
        camera_status = camera_manager.get_status()
        
        # Process image
        img = process_image(contents)
        
        # Here you would add your posture analysis logic
        # For now, return basic info
        
        return JSONResponse({
            "filename": file.filename,
            "size": len(contents),
            "dimensions": f"{img.shape[1]}x{img.shape[0]}",
            "camera_status": "in_use" if camera_status['in_use'] else "available",
            "message": "Image received successfully",
            "note": "This is a placeholder. Add your posture analysis logic here."
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-batch/")
async def analyze_batch(files: list[UploadFile] = File(...)):
    """
    Analyze multiple images (batch processing)
    """
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed")
    
    results = []
    
    for file in files:
        try:
            contents = await file.read()
            if len(contents) > 10 * 1024 * 1024:  # 10MB limit
                results.append({
                    "filename": file.filename,
                    "status": "failed",
                    "error": "File too large"
                })
                continue
                
            img = process_image(contents)
            results.append({
                "filename": file.filename,
                "size": len(contents),
                "dimensions": f"{img.shape[1]}x{img.shape[0]}",
                "status": "processed"
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "failed",
                "error": str(e)
            })
    
    return {
        "total": len(files),
        "successful": sum(1 for r in results if r["status"] == "processed"),
        "failed": sum(1 for r in results if r["status"] == "failed"),
        "results": results
    }

# =============================
# RUN CONFIGURATION
# =============================
if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("🚀 Starting FastAPI server...")
    print("📚 API documentation: http://localhost:8000/docs")
    print("🏠 Main endpoint: http://localhost:8000")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000)