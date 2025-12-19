"""
Video Processing Pipeline
Multi-threaded video capture and frame management
"""

import cv2
import numpy as np
from threading import Thread, Lock
from queue import Queue
import time
from typing import Optional, Tuple


class VideoProcessor:
    """
    Video stream processor with threading for smooth capture
    """
    
    def __init__(self, source=0, buffer_size=128):
        """
        Initialize video processor
        
        Args:
            source: Video source (0 for webcam, URL for RTSP/HTTP stream, or video file path)
            buffer_size: Maximum frames to buffer
        """
        self.source = source
        self.buffer_size = buffer_size
        
        # Threading components
        self.frame_queue = Queue(maxsize=buffer_size)
        self.capture_thread = None
        self.running = False
        self.lock = Lock()
        
        # Video capture
        self.cap = None
        
        # Stats
        self.frame_count = 0
        self.fps = 0
        self.start_time = None
        
    def start(self) -> bool:
        """Start video capture in separate thread"""
        if self.running:
            print("[Video] Already running")
            return False
        
        print(f"[Video] Starting capture from: {self.source}")
        
        # Initialize video capture
        self.cap = cv2.VideoCapture(self.source)
        
        if not self.cap.isOpened():
            print(f"[Video] Failed to open source: {self.source}")
            return False
        
        # Get video properties
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.source_fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        
        print(f"[Video] Resolution: {self.width}x{self.height}, FPS: {self.source_fps}")
        
        # Start capture thread
        self.running = True
        self.start_time = time.time()
        self.capture_thread = Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        
        print("[Video] Capture thread started")
        return True
    
    def _capture_loop(self):
        """Background thread for frame capture"""
        while self.running:
            ret, frame = self.cap.read()
            
            if not ret:
                print("[Video] Failed to read frame")
                self.running = False
                break
            
            # Add to queue (drop oldest if full)
            if not self.frame_queue.full():
                self.frame_queue.put(frame)
            else:
                # Drop oldest frame and add new one
                try:
                    self.frame_queue.get_nowait()
                    self.frame_queue.put(frame)
                except:
                    pass
            
            self.frame_count += 1
            
            # Calculate FPS every second
            elapsed = time.time() - self.start_time
            if elapsed > 1.0:
                self.fps = self.frame_count / elapsed
                self.frame_count = 0
                self.start_time = time.time()
    
    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Read next frame from queue
        
        Returns:
            (success, frame) tuple
        """
        if not self.running:
            return False, None
        
        try:
            frame = self.frame_queue.get(timeout=1.0)
            return True, frame
        except:
            return False, None
    
    def stop(self):
        """Stop video capture"""
        print("[Video] Stopping capture...")
        self.running = False
        
        if self.capture_thread:
            self.capture_thread.join(timeout=2.0)
        
        if self.cap:
            self.cap.release()
        
        print("[Video] Capture stopped")
    
    def get_stats(self) -> dict:
        """Get video statistics"""
        return {
            'source': str(self.source),
            'resolution': f"{self.width}x{self.height}",
            'fps': self.fps,
            'queue_size': self.frame_queue.qsize(),
            'running': self.running
        }
    
    def __del__(self):
        """Cleanup on deletion"""
        self.stop()


class MultiVideoProcessor:
    """
    Manage multiple video streams simultaneously
    """
    
    def __init__(self):
        self.processors = {}
        
    def add_stream(self, stream_id: str, source) -> bool:
        """Add a new video stream"""
        if stream_id in self.processors:
            print(f"[MultiVideo] Stream {stream_id} already exists")
            return False
        
        processor = VideoProcessor(source)
        if processor.start():
            self.processors[stream_id] = processor
            print(f"[MultiVideo] Added stream: {stream_id}")
            return True
        return False
    
    def remove_stream(self, stream_id: str):
        """Remove a video stream"""
        if stream_id in self.processors:
            self.processors[stream_id].stop()
            del self.processors[stream_id]
            print(f"[MultiVideo] Removed stream: {stream_id}")
    
    def read_all(self) -> dict:
        """Read frames from all streams"""
        frames = {}
        for stream_id, processor in self.processors.items():
            ret, frame = processor.read()
            if ret:
                frames[stream_id] = frame
        return frames
    
    def get_all_stats(self) -> dict:
        """Get stats for all streams"""
        return {
            stream_id: processor.get_stats()
            for stream_id, processor in self.processors.items()
        }
    
    def stop_all(self):
        """Stop all streams"""
        for processor in self.processors.values():
            processor.stop()
        self.processors.clear()


if __name__ == "__main__":
    # Test video processor
    print("Testing Video Processor...")
    
    # Test with webcam
    processor = VideoProcessor(source=0)
    
    if processor.start():
        print("Press 'q' to quit")
        
        while True:
            ret, frame = processor.read()
            
            if ret and frame is not None:
                # Display stats
                stats = processor.get_stats()
                cv2.putText(frame, f"FPS: {stats['fps']:.1f}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame, f"Queue: {stats['queue_size']}", (10, 70),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                cv2.imshow('Video Processor Test', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        processor.stop()
        cv2.destroyAllWindows()
    else:
        print("Failed to start video processor")
