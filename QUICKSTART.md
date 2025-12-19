# 🛡️ Border Threat Detection System - Quick Start

Welcome to the Border Threat Detection System! This guide will help you get started quickly.

## 📋 Prerequisites

- Python 3.8+ installed
- Webcam (optional, for testing)
- 4GB RAM minimum
- Internet connection (for initial setup)

## ⚡ Quick Installation

### Windows

1. **Open PowerShell** in the project directory

2. **Create virtual environment:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. **Install dependencies:**
```powershell
pip install -r requirements.txt
```

4. **Run the application:**
```powershell
python run.py
```

5. **Open your browser:**
```
http://localhost:5000
```

### Linux/Mac

1. **Open Terminal** in the project directory

2. **Create virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run the application:**
```bash
python run.py
```

5. **Open your browser:**
```
http://localhost:5000
```

## 🎯 First Test

1. Click the **"Start"** button in the dashboard
2. Allow webcam access if prompted
3. Watch AI detection in real-time!
4. Move in front of camera to see person detection
5. Check the alerts panel for threat analysis

## 📚 Need More Help?

- **Installation Issues:** See [INSTALLATION.md](INSTALLATION.md)
- **Usage Guide:** See [USER_MANUAL.md](USER_MANUAL.md)
- **Full Documentation:** See main [README.md](../README.md)

## 🐛 Common Issues

**Issue: "No module named 'cv2'"**
```bash
pip install opencv-python
```

**Issue: "Failed to open video source"**
- Try camera index 1 or 2 instead of 0
- Check webcam permissions in system settings

**Issue: "YOLO model not found"**
```bash
python models/training/download_model.py
```

## 🎉 You're All Set!

The system is now running and detecting threats in real-time. Enjoy exploring the features!

For hackathon demonstration, prepare:
- ✅ Working video feed
- ✅ Sample detections showing different threat levels
- ✅ Live map with location markers
- ✅ Alert notifications

---

**Made with ❤️ for Border Security**
