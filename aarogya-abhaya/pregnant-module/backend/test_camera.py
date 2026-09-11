# backend/test_camera.py
import cv2
from camera_manager import camera_manager
import uuid
import time

def test_camera():
    module_id = f"test_{uuid.uuid4().hex[:8]}"
    
    print(f"🧪 Testing camera with module ID: {module_id}")
    
    # Acquire camera
    if camera_manager.acquire_camera(module_id):
        print("✅ Camera acquired successfully")
        
        # Test capture
        frame = camera_manager.get_frame(module_id)
        if frame is not None:
            print(f"✅ Frame captured successfully")
            print(f"   Frame shape: {frame.shape}")
            print(f"   Frame size: {frame.size} pixels")
        else:
            print("❌ Failed to capture frame")
        
        # Release camera
        camera_manager.release_camera(module_id)
        print("✅ Camera released")
    else:
        print("❌ Failed to acquire camera")

if __name__ == "__main__":
    test_camera()