"""
Download YOLO Model
Automatically download YOLOv8 model if not present
"""

import os
from ultralytics import YOLO

def download_model(model_name='yolov8n.pt'):
    """Download YOLO model"""
    model_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(model_dir, model_name)
    
    if os.path.exists(model_path):
        print(f"[Model] Already exists: {model_path}")
        return model_path
    
    print(f"[Model] Downloading {model_name}...")
    try:
        # This will automatically download the model
        model = YOLO(model_name)
        print(f"[Model] Downloaded successfully to: {model_path}")
        return model_path
    except Exception as e:
        print(f"[Model] Error downloading: {e}")
        return None

if __name__ == "__main__":
    print("YOLO Model Downloader")
    print("=" * 50)
    
    # Available models (nano is fastest, x is most accurate)
    models = ['yolov8n.pt', 'yolov8s.pt', 'yolov8m.pt']
    
    print("\nAvailable models:")
    for i, model in enumerate(models, 1):
        print(f"{i}. {model}")
    
    print("\nDownloading yolov8n.pt (recommended for testing)...")
    download_model('yolov8n.pt')
    
    print("\nDone! Model is ready to use.")
