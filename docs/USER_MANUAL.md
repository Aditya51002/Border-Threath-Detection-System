# Border Threat Detection System - User Manual

## 📖 User Guide

### Table of Contents
1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [Starting Detection](#starting-detection)
4. [Understanding Alerts](#understanding-alerts)
5. [Using the Map](#using-the-map)
6. [Managing Cameras](#managing-cameras)

---

## Getting Started

### First Time Setup
1. Install the system following [INSTALLATION.md](INSTALLATION.md)
2. Run the server: `python run.py`
3. Open browser: `http://localhost:5000`
4. Dashboard will load automatically

---

## Dashboard Overview

### Top Navigation Bar
- **System Status Badge:** Shows ONLINE/OFFLINE status
- **Current Time:** Real-time clock
- **Refresh Button:** Reload the dashboard

### Statistics Cards (Top Row)
1. **Total Detections** (Blue): Total objects detected
2. **Critical Alerts** (Red): Number of critical threats
3. **High Threats** (Orange): Number of high-priority threats
4. **Active Cameras** (Green): Number of cameras online

### Main Video Feed (Left Panel)
- **Live Stream:** Real-time video with AI detection overlay
- **FPS Counter:** Frames per second indicator
- **Detection Counter:** Number of objects in current frame
- **Control Buttons:**
  - ▶️ **Start:** Begin video processing
  - ⏹️ **Stop:** Stop video processing
  - 📤 **Upload Video:** Process recorded video

### Threat Location Map (Bottom Left)
- Shows geographic location of detected threats
- Color-coded markers:
  - 🔴 Red: Critical threats
  - 🟠 Orange: High threats
  - 🟡 Yellow: Medium threats
  - 🟢 Green: Low threats

### Alerts Panel (Right Top)
- Real-time alert notifications
- Shows latest 20 alerts
- Alert information:
  - Threat level (CRITICAL, HIGH, MEDIUM, LOW)
  - Time of detection
  - Object type
  - Behavioral note

### Detection Log (Right Bottom)
- Chronological list of all detections
- Useful for tracking activity patterns

---

## Starting Detection

### Option 1: Webcam Detection
1. Click **"Start"** button
2. Browser may ask for webcam permission - click "Allow"
3. Wait 2-3 seconds for initialization
4. Live video feed will appear with AI detection

### Option 2: Upload Video File
1. Click **"Upload Video"** button
2. Select video file (MP4, AVI, MOV)
3. System will process and display results

### Option 3: IP Camera/RTSP Stream
Use API to add camera:
```bash
curl -X POST http://localhost:5000/api/cameras \
  -H "Content-Type: application/json" \
  -d '{
    "camera_id": "CAM-001",
    "name": "Main Gate Camera",
    "stream_url": "rtsp://192.168.1.100:554/stream",
    "location": {"lat": 28.6139, "lon": 77.2090},
    "zone_type": "restricted"
  }'
```

---

## Understanding Alerts

### Threat Levels

#### 🔴 CRITICAL (Score: 0.8 - 1.0)
- **Triggers:**
  - Weapon detection
  - Unauthorized person in restricted zone at night
  - High-confidence threats
- **Actions:**
  - Immediate alert to all channels
  - Auto-escalation to senior officer
  - Siren activation (if configured)

#### 🟠 HIGH (Score: 0.6 - 0.8)
- **Triggers:**
  - Person in restricted zone during day
  - Vehicle moving at high speed
  - Multiple persons detected
- **Actions:**
  - Dashboard alert
  - SMS to on-duty personnel
  - Email notification

#### 🟡 MEDIUM (Score: 0.4 - 0.6)
- **Triggers:**
  - Vehicle in patrolled zone
  - Person in buffer zone
- **Actions:**
  - Dashboard alert
  - Email notification

#### 🟢 LOW (Score: 0.0 - 0.4)
- **Triggers:**
  - Wildlife/animals
  - Low-confidence detections
- **Actions:**
  - Dashboard log only
  - No immediate alert

### Alert Information
Each alert contains:
- **Unique ID:** For tracking and reference
- **Timestamp:** When threat was detected
- **Object Type:** Person, Vehicle, Animal, etc.
- **Confidence:** AI confidence percentage
- **Threat Score:** Calculated risk score
- **Location:** GPS coordinates (if available)
- **Behavioral Note:** Context-aware description

---

## Using the Map

### Features
- **Real-time Markers:** New threats appear immediately
- **Color Coding:** Visual threat level indication
- **Click Markers:** View alert details
- **Zoom/Pan:** Navigate to specific locations

### Interpreting the Map
- **Cluster of Markers:** High-activity zone
- **Isolated Markers:** Single incidents
- **Pattern Recognition:** Identify breach patterns

---

## Managing Cameras

### View All Cameras
```bash
curl http://localhost:5000/api/cameras
```

### Add Camera
```bash
curl -X POST http://localhost:5000/api/cameras \
  -H "Content-Type: application/json" \
  -d '{
    "camera_id": "CAM-002",
    "name": "East Perimeter",
    "stream_url": "rtsp://camera-ip:554/stream",
    "location": {
      "name": "Sector 5 East",
      "lat": 28.6200,
      "lon": 77.2150
    },
    "zone_type": "restricted"
  }'
```

### Zone Types
- **restricted:** No access allowed (highest sensitivity)
- **patrolled:** Limited authorized access
- **public:** Normal access (lowest sensitivity)

---

## Best Practices

### 1. Monitoring
- Check dashboard every 30 minutes
- Review detection log daily
- Analyze threat patterns weekly

### 2. Response Protocol
**For CRITICAL alerts:**
1. Verify threat via live video
2. Dispatch nearest patrol unit
3. Alert senior officer
4. Document incident

**For HIGH alerts:**
1. Review video footage
2. Assess threat validity
3. Take appropriate action
4. Log response

### 3. False Positive Handling
- Mark false positives in system
- Adjust sensitivity if needed
- Train staff to recognize patterns

### 4. System Maintenance
- Restart server weekly
- Clear old logs monthly
- Update YOLO model quarterly
- Test cameras daily

---

## Keyboard Shortcuts

- **F5:** Refresh dashboard
- **Ctrl + R:** Reload page
- **Esc:** Close alert details

---

## Troubleshooting

### Video not showing
- Check camera permissions
- Verify camera is connected
- Try different browser (Chrome recommended)

### No alerts appearing
- Ensure "Start" was clicked
- Check minimum alert level in settings
- Verify detection is working (see FPS counter)

### Map not loading
- Add Google Maps API key
- Check internet connection
- Clear browser cache

---

## Support

**Technical Issues:**
- Check logs in `logs/border_security.log`
- Review API status: `http://localhost:5000/api/status`

**Contact:**
- GitHub: [Create an issue](https://github.com/yourusername/border-threat-detection/issues)
- Email: support@example.com

---

## Appendix

### API Endpoints
- `GET /api/status` - System status
- `GET /api/statistics` - Statistics
- `GET /api/detections/recent` - Recent detections
- `GET /api/alerts/recent` - Recent alerts
- `GET /api/cameras` - All cameras
- `POST /api/start` - Start processing
- `POST /api/stop` - Stop processing
- `POST /api/upload` - Upload video

### Configuration Files
- `.env` - Environment variables
- `backend/config/settings.py` - System settings
- `backend/database/db_manager.py` - Database schema

---

**Last Updated:** December 2025  
**Version:** 1.0.0
