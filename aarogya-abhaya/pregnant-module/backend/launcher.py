# backend/launcher.py
import subprocess
import sys
import os
import time

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_menu():
    clear_screen()
    print("=" * 60)
    print("     🤰 PREGNANT WOMEN POSTURE DETECTION SYSTEM")
    print("=" * 60)
    print("1. 🏋️  Start Squat Posture Detection")
    print("2. 🪑  Start Sitting Posture Detection")
    print("3. 🚀  Start FastAPI Server")
    print("4. 📷  Check Camera Status")
    print("5. ❌  Exit")
    print("=" * 60)

def check_camera_status():
    """Quick check if camera is available"""
    import cv2
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        ret, frame = cap.read()
        cap.release()
        if ret:
            print("✅ Camera is available")
            return True
    print("❌ Camera is not available or in use")
    return False

def main():
    while True:
        print_menu()
        choice = input("Select option (1-5): ").strip()
        
        if choice == '1':
            print("\n🏋️  Starting Squat Detector...")
            print("Press Ctrl+C to return to menu")
            time.sleep(1)
            try:
                # Run squat detector from posture folder
                subprocess.run([sys.executable, "posture/live_posture_detection.py"])
            except KeyboardInterrupt:
                print("\n🔙 Returning to menu...")
            except Exception as e:
                print(f"\n❌ Error: {e}")
                input("Press Enter to continue...")
                
        elif choice == '2':
            print("\n🪑 Starting Sitting Posture Detector...")
            print("Press Ctrl+C to return to menu")
            time.sleep(1)
            try:
                # Run sitting detector from sitting_posture_module folder
                subprocess.run([sys.executable, "sitting_posture_module/live_sitting_posture.py"])
            except KeyboardInterrupt:
                print("\n🔙 Returning to menu...")
            except Exception as e:
                print(f"\n❌ Error: {e}")
                input("Press Enter to continue...")
                
        elif choice == '3':
            print("\n🚀 Starting FastAPI Server...")
            print("Press Ctrl+C to stop server")
            print("Server running at: http://localhost:8000")
            print("API docs at: http://localhost:8000/docs")
            time.sleep(1)
            try:
                # Run FastAPI from root directory (one level up)
                os.chdir("..")  # Go to root directory where main.py is
                subprocess.run([
                    sys.executable, "-m", "uvicorn", "main:app",
                    "--host", "0.0.0.0", "--port", "8000", "--reload"
                ])
            except KeyboardInterrupt:
                print("\n🔙 Returning to menu...")
            finally:
                os.chdir("backend")  # Return to backend directory
                
        elif choice == '4':
            print("\n📷 Checking Camera Status...")
            check_camera_status()
            print("\nPress Enter to continue...")
            input()
            
        elif choice == '5':
            print("\n👋 Exiting...")
            sys.exit(0)
            
        else:
            print("\n❌ Invalid option! Press Enter to continue...")
            input()

if __name__ == "__main__":
    # Change to backend directory if not already there
    if os.path.basename(os.getcwd()) != "backend":
        backend_path = os.path.join(os.getcwd(), "backend")
        if os.path.exists(backend_path):
            os.chdir(backend_path)
    main()