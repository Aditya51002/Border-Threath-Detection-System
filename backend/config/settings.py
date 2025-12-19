"""
Configuration Settings
"""

import os
from datetime import timedelta


class Config:
    """Application configuration"""
    
    # Application
    APP_NAME = "Border Threat Detection System"
    VERSION = "1.0.0"
    DEBUG = True
    
    # Server
    HOST = "0.0.0.0"
    PORT = 5000
    
    # Database
    DATABASE_PATH = "border_security.db"
    
    # YOLO Detection
    YOLO_MODEL_PATH = "models/yolov8n.pt"  # or yolov8s.pt, yolov8m.pt for better accuracy
    CONFIDENCE_THRESHOLD = 0.75
    DEVICE = "cpu"  # Using CPU (change to "cuda" if you have NVIDIA GPU with CUDA installed)
    
    # Video Processing
    VIDEO_BUFFER_SIZE = 128
    DEFAULT_FPS = 30
    FRAME_WIDTH = 416  # Reduced from 640 for better FPS
    FRAME_HEIGHT = 416  # Reduced from 480 for better FPS
    
    # Threat Analysis
    NIGHT_HOURS_START = 20  # 8 PM
    NIGHT_HOURS_END = 6      # 6 AM
    DEFAULT_ZONE_TYPE = "restricted"
    
    # Alert System
    ALERT_COOLDOWN_SECONDS = 30
    MIN_ALERT_LEVEL = 2  # MEDIUM (1=LOW, 2=MEDIUM, 3=HIGH, 4=CRITICAL)
    
    # Alert Channels
    ENABLE_SMS_ALERTS = False
    ENABLE_EMAIL_ALERTS = False
    ENABLE_WEBSOCKET_ALERTS = True
    
    # Twilio (for SMS)
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")
    ALERT_PHONE_NUMBERS = os.getenv("ALERT_PHONE_NUMBERS", "").split(",")
    
    # Email (SMTP)
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    ALERT_EMAILS = os.getenv("ALERT_EMAILS", "").split(",")
    
    # Google Maps
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
    DEFAULT_MAP_CENTER = {"lat": 28.6139, "lon": 77.2090}  # New Delhi
    DEFAULT_MAP_ZOOM = 12
    
    # File Storage
    UPLOAD_FOLDER = "uploads"
    SNAPSHOT_FOLDER = "snapshots"
    VIDEO_ARCHIVE_FOLDER = "archives"
    MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100 MB
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production")
    JWT_EXPIRATION = timedelta(hours=24)
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FILE = "logs/border_security.log"
    
    # Performance
    MAX_WORKERS = 4
    ENABLE_GPU = True
    
    @classmethod
    def get_config_dict(cls) -> dict:
        """Get configuration as dictionary"""
        return {
            key: getattr(cls, key)
            for key in dir(cls)
            if not key.startswith('_') and key.isupper()
        }


# Development config
class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE_PATH = "dev_border_security.db"


# Production config
class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = "WARNING"


# Testing config
class TestingConfig(Config):
    TESTING = True
    DATABASE_PATH = ":memory:"


# Config mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
