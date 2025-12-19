"""
YOLO Detection Engine
Real-time object detection using YOLOv8
"""

import cv2
import numpy as np
from ultralytics import YOLO
import torch
from typing import List, Dict, Tuple
import time


class YOLODetector:
    """
    YOLO-based object detection for border threat identification
    """
    
    def __init__(self, model_path='yolov8n.pt', conf_threshold=0.75, device='auto'):
        """
        Initialize YOLO detector
        
        Args:
            model_path: Path to YOLO model weights
            conf_threshold: Confidence threshold for detections
            device: 'cuda', 'cpu', or 'auto'
        """
        self.conf_threshold = conf_threshold
        
        # Determine device
        if device == 'auto':
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device
            
        print(f"[YOLO] Initializing on device: {self.device}")
        
        # Load YOLO model
        try:
            self.model = YOLO(model_path)
            self.model.to(self.device)
            print(f"[YOLO] Model loaded successfully: {model_path}")
        except Exception as e:
            print(f"[YOLO] Error loading model: {e}")
            raise
            
        # Class mappings for border security
        self.threat_classes = {
            'person': 'human',
            'car': 'vehicle',
            'truck': 'vehicle',
            'motorcycle': 'vehicle',
            'bus': 'vehicle',
            'dog': 'animal',
            'horse': 'animal',
            'elephant': 'animal',
            'bear': 'animal',
            'zebra': 'animal',
            'giraffe': 'animal'
        }
        
    def detect(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect objects in a frame
        
        Args:
            frame: Input image (BGR format)
            
        Returns:
            List of detections with class, confidence, and bounding box
        """
        start_time = time.time()
        
        # Run inference
        results = self.model(frame, conf=self.conf_threshold, verbose=False)
        
        detections = []
        for result in results:
            boxes = result.boxes
            
            for box in boxes:
                # Extract data
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = self.model.names[class_id]
                
                # Map to threat categories
                threat_type = self.threat_classes.get(class_name, 'unknown')
                
                detection = {
                    'class': class_name,
                    'threat_type': threat_type,
                    'confidence': confidence,
                    'bbox': [int(x1), int(y1), int(x2), int(y2)],
                    'timestamp': time.time()
                }
                
                detections.append(detection)
        
        inference_time = time.time() - start_time
        fps = 1 / inference_time if inference_time > 0 else 0
        
        return detections, fps
    
    def draw_detections(self, frame: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """
        Draw bounding boxes and labels on frame
        
        Args:
            frame: Input image
            detections: List of detections
            
        Returns:
            Annotated frame
        """
        annotated_frame = frame.copy()
        
        # Color coding by threat type
        colors = {
            'human': (0, 0, 255),      # Red
            'vehicle': (0, 165, 255),  # Orange
            'animal': (0, 255, 0),     # Green
            'weapon': (255, 0, 0),     # Blue
            'unknown': (128, 128, 128) # Gray
        }
        
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            threat_type = det['threat_type']
            color = colors.get(threat_type, (255, 255, 255))
            
            # Draw bounding box
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            label = f"{det['class']}: {det['confidence']:.2f}"
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            
            # Background for text
            cv2.rectangle(annotated_frame, 
                         (x1, y1 - label_size[1] - 10),
                         (x1 + label_size[0], y1),
                         color, -1)
            
            # Text
            cv2.putText(annotated_frame, label, (x1, y1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        return annotated_frame
    
    def get_stats(self) -> Dict:
        """Get model statistics"""
        return {
            'model': str(self.model),
            'device': self.device,
            'conf_threshold': self.conf_threshold,
            'classes': len(self.model.names)
        }


if __name__ == "__main__":
    # Test the detector
    print("Testing YOLO Detector...")
    
    detector = YOLODetector()
    print(f"Stats: {detector.get_stats()}")
    
    # Test with webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("No webcam found. Test complete.")
    else:
        print("Press 'q' to quit")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            detections, fps = detector.detect(frame)
            annotated = detector.draw_detections(frame, detections)
            
            # Display FPS
            cv2.putText(annotated, f"FPS: {fps:.1f}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            cv2.imshow('YOLO Detection Test', annotated)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
