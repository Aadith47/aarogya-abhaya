# live_sitting_posture.py
import cv2
from ultralytics import YOLO
import uuid
import signal
import sys
import os
from pathlib import Path
import numpy as np
import torch
import torchvision.transforms as transforms

# Add parent directory to path to import camera_manager
sys.path.append(str(Path(__file__).parent.parent))
from camera_manager import camera_manager

# Module ID for camera management
MODULE_ID = f"sitting_{uuid.uuid4().hex[:8]}"

# =============================
# LOAD MODEL WITH PATH DEBUGGING
# =============================
def find_model_file():
    """Search for the sitting posture model file"""
    possible_paths = [
        # Relative to current file
        os.path.join(os.path.dirname(__file__), "runs/classify/train/weights/best.pt"),
        os.path.join(os.path.dirname(__file__), "../../runs/classify/train/weights/best.pt"),
        os.path.join(os.path.dirname(__file__), "../../../runs/classify/train/weights/best.pt"),
        "runs/classify/train/weights/best.pt"
    ]
    
    print("🔍 Searching for sitting posture model...")
    for i, path in enumerate(possible_paths, 1):
        abs_path = os.path.abspath(path)
        print(f"{i}. Checking: {abs_path}")
        if os.path.exists(abs_path):
            print(f"   ✅ FOUND at: {abs_path}")
            return abs_path
    
    return None

# Find and load model
model_path = find_model_file()
model = None

if model_path and os.path.exists(model_path):
    try:
        model = YOLO(model_path)
        print("\n✅ Sitting posture model loaded successfully!")
        print(f"   Model classes: {model.names}")
        
        # Define image transform for preprocessing
        transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
    except Exception as e:
        print(f"\n❌ Error loading model: {e}")
else:
    print("\n⚠️  Sitting posture model not found.")
    print("   Please train the model first using: python train_sitting_model.py")

# =============================
# SIGNAL HANDLER
# =============================
def signal_handler(sig, frame):
    print("\n🛑 Shutting down sitting posture detector...")
    camera_manager.release_camera(MODULE_ID)
    cv2.destroyAllWindows()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# =============================
# FIXED: Direct tensor prediction
# =============================
def predict_with_model(model, frame, transform):
    """Direct tensor-based prediction that bypasses PIL issues"""
    try:
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Apply transforms directly to get tensor
        input_tensor = transform(frame_rgb)
        
        # Add batch dimension
        input_batch = input_tensor.unsqueeze(0)
        
        # Move to CPU (or GPU if available)
        input_batch = input_batch.to('cpu')
        
        # Run inference
        with torch.no_grad():
            results = model(input_batch)
        
        return results
        
    except Exception as e:
        print(f"Tensor prediction failed: {e}")
        return None

# =============================
# MAIN LOOP
# =============================
def main():
    print(f"\n🪑 Starting sitting posture detector (Module ID: {MODULE_ID})")
    print("📷 Attempting to acquire camera...")
    
    # Acquire camera
    if not camera_manager.acquire_camera(MODULE_ID, timeout=10):
        print("❌ Failed to acquire camera. Is another application using it?")
        input("\nPress Enter to continue...")
        return
    
    print("✅ Camera acquired successfully!")
    print("\n📌 Controls:")
    print("   - Press 'ESC' to quit")
    print("   - Press 'r' to reset")
    
    if model is None:
        print("\n⚠️  No model loaded. Cannot run detection.")
        camera_manager.release_camera(MODULE_ID)
        input("\nPress Enter to exit...")
        return
    
    frame_count = 0
    fps = 0
    start_time = cv2.getTickCount()
    
    try:
        while True:
            # Get frame from camera manager
            frame = camera_manager.get_frame(MODULE_ID)
            
            if frame is None:
                print("⚠️ Lost camera connection. Attempting to reconnect...")
                if not camera_manager.acquire_camera(MODULE_ID, timeout=5):
                    break
                continue
            
            # Calculate FPS
            frame_count += 1
            if frame_count >= 30:
                end_time = cv2.getTickCount()
                fps = 30 / ((end_time - start_time) / cv2.getTickFrequency())
                start_time = end_time
                frame_count = 0
            
            # Run prediction using tensor method
            try:
                # For Ultralytics YOLO, we can also use their built-in prediction
                # This is the simplest approach that should work
                results = model(frame)  # Try direct prediction first
                
                # If direct prediction fails, use tensor method
                if results is None:
                    results = predict_with_model(model, frame, transform)
                    
            except Exception as e:
                # Fallback to tensor method
                results = predict_with_model(model, frame, transform)
            
            if results is not None:
                # Handle different result types
                if hasattr(results, 'probs'):
                    # Direct YOLO result
                    probs = results.probs
                    class_id = probs.top1
                    confidence = probs.top1conf
                    class_names = model.names
                    label = class_names[class_id]
                    
                elif isinstance(results, list) and len(results) > 0:
                    # List of results
                    if hasattr(results[0], 'probs'):
                        probs = results[0].probs
                        class_id = probs.top1
                        confidence = probs.top1conf
                        class_names = model.names
                        label = class_names[class_id]
                    else:
                        label = "unknown"
                        confidence = 0
                        class_id = -1
                else:
                    label = "unknown"
                    confidence = 0
                    class_id = -1
                
                # Posture warning logic
                if label == "correct" or class_id == 0:
                    color = (0, 255, 0)
                    message = "✅ Good Posture"
                else:
                    color = (0, 0, 255)
                    message = "❌ Bad Posture!"
                
                # Display information
                cv2.putText(frame, message, (20, 50),
                           cv2.FONT_HERSHEY_SIMPLEX, 1,
                           color, 3)
                
                cv2.putText(frame, f"{label} ({confidence:.2f})", (20, 100),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                           color, 2)
            else:
                cv2.putText(frame, "Processing...", (20, 50),
                           cv2.FONT_HERSHEY_SIMPLEX, 1,
                           (255, 255, 0), 3)
            
            # Always show FPS
            cv2.putText(frame, f"FPS: {fps:.1f}", (20, 150),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            cv2.putText(frame, "Press ESC to quit", (20, 180),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            cv2.imshow("Sitting Posture Detection", frame)
            
            # Check for ESC key
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC key
                break
            elif key == ord('r'):
                print("🔄 Reset")
    
    finally:
        # Cleanup
        camera_manager.release_camera(MODULE_ID)
        cv2.destroyAllWindows()
        print("👋 Sitting posture detector stopped")

if __name__ == "__main__":
    main()