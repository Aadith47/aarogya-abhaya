# backend/camera_manager.py
import cv2
import threading
import time
from datetime import datetime

class CameraManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.cap = None
        self.is_open = False
        self.current_user = None
        self.last_access = None
        self.error_count = 0
        self.max_errors = 5
        self.camera_index = 0  # Default camera index
        
    def acquire_camera(self, user_id, timeout=5):
        """Acquire camera with timeout"""
        with self._lock:
            start_time = time.time()
            
            if self.current_user == user_id and self.cap is not None:
                self.last_access = datetime.now()
                return True
            
            while time.time() - start_time < timeout:
                try:
                    if self.cap is None:
                        # Try different camera indices on Windows
                        for idx in [0, 1, -1]:  # Try common indices
                            self.cap = cv2.VideoCapture(idx)
                            if self.cap.isOpened():
                                self.camera_index = idx
                                break
                        
                        if not self.cap or not self.cap.isOpened():
                            self.cap = None
                            time.sleep(0.5)
                            continue
                        
                        # Set camera properties
                        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                        self.cap.set(cv2.CAP_PROP_FPS, 30)
                        
                        # Test read
                        ret, frame = self.cap.read()
                        if not ret or frame is None:
                            self.cap.release()
                            self.cap = None
                            time.sleep(0.5)
                            continue
                            
                        self.is_open = True
                        self.current_user = user_id
                        self.last_access = datetime.now()
                        self.error_count = 0
                        print(f"[CAMERA] ✅ Acquired by {user_id} (Index: {self.camera_index})")
                        return True
                    else:
                        print(f"[CAMERA] ⚠️ In use by {self.current_user}")
                        return False
                        
                except Exception as e:
                    print(f"[CAMERA] ❌ Error acquiring: {e}")
                    time.sleep(0.5)
                    
            return False
    
    def release_camera(self, user_id):
        """Release camera if owned by user_id"""
        with self._lock:
            if self.current_user == user_id and self.cap is not None:
                try:
                    self.cap.release()
                    print(f"[CAMERA] ✅ Released by {user_id}")
                except Exception as e:
                    print(f"[CAMERA] ❌ Error releasing: {e}")
                finally:
                    self.cap = None
                    self.is_open = False
                    self.current_user = None
                    self.last_access = None
                    self.error_count = 0
                return True
        return False
    
    def get_frame(self, user_id):
        """Get current frame if user owns camera"""
        with self._lock:
            if self.current_user != user_id or self.cap is None:
                return None
                
            try:
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    self.last_access = datetime.now()
                    self.error_count = 0
                    return frame
                else:
                    self.error_count += 1
                    if self.error_count >= self.max_errors:
                        print(f"[CAMERA] ⚠️ Too many errors, releasing...")
                        self._force_release()
                    return None
                    
            except Exception as e:
                print(f"[CAMERA] ❌ Frame error: {e}")
                self.error_count += 1
                return None
    
    def _force_release(self):
        """Force release camera on error"""
        if self.cap:
            try:
                self.cap.release()
            except:
                pass
        self.cap = None
        self.is_open = False
        self.current_user = None
    
    def get_status(self):
        """Get camera status"""
        with self._lock:
            return {
                'in_use': self.current_user is not None,
                'current_user': self.current_user,
                'last_access': self.last_access,
                'error_count': self.error_count,
                'camera_index': self.camera_index if self.cap else None
            }

# Global instance
camera_manager = CameraManager()