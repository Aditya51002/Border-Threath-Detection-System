# Detection module
from .yolo_detector import YOLODetector
from .video_processor import VideoProcessor, MultiVideoProcessor

__all__ = ['YOLODetector', 'VideoProcessor', 'MultiVideoProcessor']
