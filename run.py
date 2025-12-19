"""
Run the Border Threat Detection System
Simple startup script
"""

import os
import sys
import subprocess

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import flask
        import cv2
        import ultralytics
        print("✓ All dependencies installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("\nPlease install dependencies:")
        print("  pip install -r requirements.txt")
        return False

def check_model():
    """Check if YOLO model exists"""
    model_path = "models/yolov8n.pt"
    if os.path.exists(model_path):
        print(f"✓ YOLO model found: {model_path}")
        return True
    else:
        print(f"✗ YOLO model not found: {model_path}")
        print("\nDownloading model...")
        try:
            subprocess.run([sys.executable, "models/training/download_model.py"])
            return True
        except Exception as e:
            print(f"Error downloading model: {e}")
            return False

def main():
    print("="*70)
    print("  🛡️  Border Threat Detection System")
    print("="*70)
    print()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check model
    if not check_model():
        print("\nYou can manually download the model:")
        print("  python models/training/download_model.py")
        sys.exit(1)
    
    print("\n" + "="*70)
    print("  Starting server...")
    print("="*70)
    print()
    
    # Run the server
    try:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        subprocess.run([sys.executable, "backend/api/app.py"])
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
