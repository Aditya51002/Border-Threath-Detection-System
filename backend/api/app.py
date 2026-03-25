"""
Flask API Server
RESTful API and WebSocket server for Border Threat Detection System
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
import sys
import time
import cv2
import base64
from datetime import datetime
import threading

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from detection.yolo_detector import YOLODetector
from detection.video_processor import VideoProcessor
from classification.threat_analyzer import ThreatAnalyzer
from alerts.alert_system import AlertSystem, AlertFilter
from database.db_manager import DatabaseManager
from config.settings import Config

# Initialize Flask app
app = Flask(__name__, 
            template_folder='../../frontend/dashboard',
            static_folder='../../frontend/assets',
            static_url_path='/static')
app.config['SECRET_KEY'] = Config.SECRET_KEY
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize components
db = DatabaseManager(Config.DATABASE_PATH)
detector = None
video_processor = None
threat_analyzer = ThreatAnalyzer()
alert_system = AlertSystem()
alert_filter = AlertFilter(cooldown_seconds=Config.ALERT_COOLDOWN_SECONDS)

# AI Command Agent
from api.llm_agent import StrategicAIAgent
ai_agent = StrategicAIAgent()

# Global state
processing_active = False
processing_thread = None


def init_detector():
    """Initialize YOLO detector"""
    global detector
    try:
        detector = YOLODetector(
            model_path=Config.YOLO_MODEL_PATH,
            conf_threshold=Config.CONFIDENCE_THRESHOLD,
            device=Config.DEVICE
        )
        return True
    except Exception as e:
        print(f"[API] Detector error: {e}")
        return False


def process_video_stream():
    """Background thread for real-time video processing"""
    global processing_active, video_processor
    
    frame_skip = 2
    frame_count = 0
    
    while processing_active:
        if video_processor is None:
            time.sleep(1)
            continue
        
        ret, frame = video_processor.read()
        if not ret or frame is None:
            time.sleep(0.1)
            continue
        
        frame_count += 1
        if frame_count % frame_skip != 0:
            continue
        
        try:
            detections, fps = detector.detect(frame)
            
            if detections:
                analyzed = threat_analyzer.analyze(detections, zone_type=Config.DEFAULT_ZONE_TYPE)
                
                for det in analyzed:
                    if det.get('threat_level', 0) >= Config.MIN_ALERT_LEVEL:
                        if alert_filter.should_alert(det):
                            db.save_detection(det, camera_id='default')
                            alert_system.send_alert(det)
                            
                            socketio.emit('new_alert', {
                                'detection': det,
                                'timestamp': datetime.now().isoformat()
                            })
                
                annotated_frame = detector.draw_detections(frame, analyzed)
                _, buffer = cv2.imencode('.jpg', annotated_frame)
                frame_data = base64.b64encode(buffer).decode('utf-8')
                
                socketio.emit('video_frame', {
                    'frame': frame_data,
                    'detections': len(detections),
                    'fps': fps
                })
        
        except Exception as e:
            print(f"[API] Stream error: {e}")
        
        time.sleep(0.033)


# === API ROUTES ===

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/status')
def get_status():
    return jsonify({
        'status': 'online',
        'version': Config.VERSION,
        'processing_active': processing_active,
        'detector_ready': detector is not None,
        'timestamp': datetime.now().isoformat()
    })


# STRATEGIC COMMAND ROUTES
@app.route('/api/ai/analyze')
def analyze_strategic_threats():
    try:
        recent_alerts = db.get_recent_alerts(limit=10)
        recent_detections = db.get_recent_detections(limit=20)
        analysis = ai_agent.analyze_threats(recent_alerts, recent_detections)
        return jsonify({
            'success': True,
            'analysis': analysis
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    data = request.json
    response = ai_agent.chat(data.get('query', ''))
    return jsonify({
        'success': True,
        'response': response
    })


@app.route('/api/config')
def get_config():
    """Get system configuration"""
    return jsonify({
        'app_name': Config.APP_NAME,
        'version': Config.VERSION,
        'google_maps_key': Config.GOOGLE_MAPS_API_KEY,
        'map_center': Config.DEFAULT_MAP_CENTER,
        'alert_levels': {
            '1': 'LOW',
            '2': 'MEDIUM',
            '3': 'HIGH',
            '4': 'CRITICAL'
        }
    })


@app.route('/api/statistics')
def get_statistics():
    """Get system statistics"""
    db_stats = db.get_statistics()
    alert_stats = alert_system.get_stats()
    
    return jsonify({
        'database': db_stats,
        'alerts': alert_stats,
        'uptime': int(time.time() - app.start_time) if hasattr(app, 'start_time') else 0
    })


@app.route('/api/detections/recent')
def get_recent_detections():
    """Get recent detections"""
    limit = request.args.get('limit', 50, type=int)
    detections = db.get_recent_detections(limit=limit)
    return jsonify(detections)


@app.route('/api/alerts/recent')
def get_recent_alerts():
    """Get recent alerts"""
    limit = request.args.get('limit', 50, type=int)
    alerts = db.get_recent_alerts(limit=limit)
    return jsonify(alerts)


@app.route('/api/cameras')
def get_cameras():
    """Get all cameras"""
    cameras = db.get_all_cameras()
    return jsonify(cameras)


@app.route('/api/cameras', methods=['POST'])
def add_camera():
    """Add a new camera"""
    data = request.json
    
    camera_id = db.add_camera(
        camera_id=data.get('camera_id'),
        name=data.get('name'),
        stream_url=data.get('stream_url'),
        location=data.get('location', {}),
        zone_type=data.get('zone_type', 'restricted')
    )
    
    return jsonify({'success': True, 'id': camera_id})


@app.route('/api/start', methods=['POST'])
def start_processing():
    """Start video processing"""
    global processing_active, processing_thread, video_processor
    
    if processing_active:
        return jsonify({'success': False, 'message': 'Already processing'})
    
    data = request.json
    source = data.get('source', 0)  # 0 for webcam
    
    # Initialize video processor
    video_processor = VideoProcessor(source=source)
    if not video_processor.start():
        return jsonify({'success': False, 'message': 'Failed to start video source'})
    
    # Start processing thread
    processing_active = True
    processing_thread = threading.Thread(target=process_video_stream, daemon=True)
    processing_thread.start()
    
    return jsonify({'success': True, 'message': 'Processing started'})


@app.route('/api/stop', methods=['POST'])
def stop_processing():
    """Stop video processing"""
    global processing_active, video_processor
    
    if not processing_active:
        return jsonify({'success': False, 'message': 'Not processing'})
    
    processing_active = False
    
    if video_processor:
        video_processor.stop()
        video_processor = None
    
    return jsonify({'success': True, 'message': 'Processing stopped'})


@app.route('/api/upload', methods=['POST'])
def upload_video():
    """Upload video file for processing"""
    if 'video' not in request.files:
        return jsonify({'success': False, 'message': 'No video file'})
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'})
    
    # Save file
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    filepath = os.path.join(Config.UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    
    return jsonify({'success': True, 'path': filepath})


# === WebSocket Events ===

@socketio.on('connect')
def handle_connect():
    """Client connected"""
    print(f"[WebSocket] Client connected: {request.sid}")
    emit('connected', {'message': 'Connected to Border Threat Detection System'})


@socketio.on('disconnect')
def handle_disconnect():
    """Client disconnected"""
    print(f"[WebSocket] Client disconnected: {request.sid}")


@socketio.on('request_frame')
def handle_frame_request():
    """Client requests current frame"""
    # Frame will be sent by processing thread
    pass


def main():
    """Start the server"""
    # Initialize
    app.start_time = time.time()
    
    print("="*70)
    print(f"  {Config.APP_NAME} - API Server")
    print(f"  Version: {Config.VERSION}")
    print("="*70)
    
    # Initialize detector
    if not init_detector():
        print("[ERROR] Failed to initialize YOLO detector")
        print("Make sure you have:")
        print("  1. Installed ultralytics: pip install ultralytics")
        print("  2. Downloaded YOLO model or it will auto-download")
        return
    
    # Start alert system
    alert_system.start()
    
    print(f"\n[Server] Starting on http://{Config.HOST}:{Config.PORT}")
    print(f"[Server] Dashboard: http://localhost:{Config.PORT}/")
    print(f"[Server] API: http://localhost:{Config.PORT}/api/status")
    print("\nPress Ctrl+C to stop\n")
    
    try:
        # Run server
        socketio.run(app, 
                    host=Config.HOST, 
                    port=Config.PORT, 
                    debug=Config.DEBUG,
                    allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print("\n[Server] Shutting down...")
        alert_system.stop()
        if video_processor:
            video_processor.stop()
        print("[Server] Stopped")


if __name__ == '__main__':
    main()

