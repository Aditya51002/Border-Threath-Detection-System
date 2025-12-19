# Border Threat Detection System - Installation Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Git
- Webcam or video source (optional for testing)

### Installation Steps

#### 1. Clone the repository
```bash
git clone https://github.com/yourusername/border-threat-detection.git
cd border-threat-detection
```

#### 2. Create virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install dependencies
```bash
pip install -r requirements.txt
```

**Note:** If you encounter issues with PyTorch, install it separately:
```bash
# For GPU (CUDA 11.8)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# For CPU only
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

#### 4. Download YOLO model
```bash
python models/training/download_model.py
```

#### 5. Configure environment (Optional)
```bash
# Copy environment template
copy .env.example .env

# Edit .env and add your API keys
# - Google Maps API key (for map visualization)
# - Twilio credentials (for SMS alerts)
# - Email SMTP settings (for email alerts)
```

#### 6. Run the application
```bash
python backend/api/app.py
```

#### 7. Access the dashboard
Open your browser and go to:
```
http://localhost:5000
```

## 📝 Configuration

### Google Maps API Key
To enable the location map:
1. Get API key from [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Maps JavaScript API
3. Add key to `.env` file or directly in `frontend/dashboard/index.html`

### Camera Setup
To connect IP cameras or RTSP streams:
1. Start the server
2. Use the API to add cameras:
```bash
curl -X POST http://localhost:5000/api/cameras \
  -H "Content-Type: application/json" \
  -d '{
    "camera_id": "CAM-001",
    "name": "Border Sector 1",
    "stream_url": "rtsp://your-camera-url",
    "location": {"lat": 28.6139, "lon": 77.2090},
    "zone_type": "restricted"
  }'
```

## 🧪 Testing

### Test with Webcam
1. Click "Start" button in the dashboard
2. Allow webcam access
3. Watch real-time detection

### Test with Video File
1. Click "Upload Video" button
2. Select a video file
3. System will process and show detections

### Test Individual Components
```bash
# Test YOLO detector
python backend/detection/yolo_detector.py

# Test video processor
python backend/detection/video_processor.py

# Test threat analyzer
python backend/classification/threat_analyzer.py

# Test alert system
python backend/alerts/alert_system.py

# Test database
python backend/database/db_manager.py
```

## 🔧 Troubleshooting

### Issue: "No module named 'ultralytics'"
**Solution:**
```bash
pip install ultralytics
```

### Issue: "CUDA not available"
**Solution:** Install PyTorch with CUDA support or use CPU mode (slower)
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Issue: "Failed to open video source"
**Solution:** 
- Check webcam permissions
- Try different source index: 0, 1, 2
- Verify RTSP stream URL is correct

### Issue: "Google Maps not loading"
**Solution:**
- Add valid Google Maps API key
- Enable Maps JavaScript API in Google Cloud Console
- Check browser console for errors

## 📦 Directory Structure
```
border-threat-detection/
├── backend/
│   ├── detection/        # YOLO detection & video processing
│   ├── classification/   # Threat analysis
│   ├── alerts/          # Alert system
│   ├── database/        # Database management
│   ├── api/             # Flask server
│   └── config/          # Configuration
├── frontend/
│   ├── dashboard/       # HTML dashboard
│   └── assets/          # CSS, JS, images
├── models/              # YOLO model files
├── requirements.txt     # Python dependencies
└── README.md           # Documentation
```

## 🎯 Next Steps

1. **Customize Threat Levels:** Edit `backend/classification/threat_analyzer.py`
2. **Add SMS/Email Alerts:** Configure Twilio and SMTP in `.env`
3. **Add More Cameras:** Use `/api/cameras` endpoint
4. **Train Custom Model:** See `models/training/` for dataset preparation
5. **Deploy to Production:** Use Gunicorn + Nginx for production deployment

## 📞 Support

For issues or questions:
- GitHub Issues: [Create an issue](https://github.com/yourusername/border-threat-detection/issues)
- Email: your.email@example.com

## 📄 License

MIT License - See LICENSE file for details
