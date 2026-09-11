# run_all.py (in C:\Project\pregnant module)
import subprocess
import sys
import os
import time
import threading

def run_camera_api():
    """Run the camera API server"""
    print("🚀 Starting Camera API Server...")
    os.chdir("backend")
    subprocess.run([sys.executable, "camera_api.py"])
    os.chdir("..")

def main():
    print("=" * 60)
    print("     🤰 PREGNANT MODULE CAMERA SERVER")
    print("=" * 60)
    
    # Start camera API
    camera_thread = threading.Thread(target=run_camera_api, daemon=True)
    camera_thread.start()
    
    print("\n✅ Camera server started!")
    print("📌 Camera API: http://localhost:5001")
    print("\nPress Ctrl+C to stop the server...")
    
    try:
        # Keep the main thread running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down camera server...")
        # Kill all Python processes (Windows specific)
        if os.name == 'nt':
            os.system("taskkill /F /IM python.exe")
        sys.exit(0)

if __name__ == "__main__":
    main()