"""
Database Models
SQLite database schema for Border Threat Detection System
"""

from datetime import datetime
import sqlite3
import json
from typing import List, Dict, Optional
import os


class DatabaseManager:
    """
    Manage database operations
    """
    
    def __init__(self, db_path='border_security.db'):
        """Initialize database manager"""
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn
    
    def init_database(self):
        """Create database tables if they don't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Detections table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                detection_id TEXT UNIQUE,
                timestamp TEXT NOT NULL,
                object_class TEXT,
                threat_type TEXT,
                confidence REAL,
                threat_score REAL,
                threat_level INTEGER,
                threat_label TEXT,
                bbox_x1 INTEGER,
                bbox_y1 INTEGER,
                bbox_x2 INTEGER,
                bbox_y2 INTEGER,
                latitude REAL,
                longitude REAL,
                zone_type TEXT,
                behavioral_note TEXT,
                camera_id TEXT,
                snapshot_path TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id TEXT UNIQUE,
                detection_id TEXT,
                timestamp TEXT NOT NULL,
                threat_label TEXT,
                message TEXT,
                latitude REAL,
                longitude REAL,
                status TEXT DEFAULT 'pending',
                acknowledged_by TEXT,
                acknowledged_at TEXT,
                dispatched_at TEXT,
                resolved_at TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (detection_id) REFERENCES detections(detection_id)
            )
        ''')
        
        # Cameras table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cameras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                camera_id TEXT UNIQUE,
                name TEXT,
                location_name TEXT,
                latitude REAL,
                longitude REAL,
                stream_url TEXT,
                zone_type TEXT,
                status TEXT DEFAULT 'active',
                last_heartbeat TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Users table (for authentication)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password_hash TEXT,
                role TEXT,
                full_name TEXT,
                email TEXT,
                phone TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_login TEXT
            )
        ''')
        
        # System logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                level TEXT,
                module TEXT,
                message TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
        print(f"[Database] Initialized at {self.db_path}")
    
    def save_detection(self, detection: Dict, location: Dict = None, camera_id: str = None) -> int:
        """Save detection to database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        detection_id = f"DET-{int(datetime.now().timestamp() * 1000)}"
        
        bbox = detection.get('bbox', [0, 0, 0, 0])
        loc = location or {}
        
        cursor.execute('''
            INSERT INTO detections (
                detection_id, timestamp, object_class, threat_type,
                confidence, threat_score, threat_level, threat_label,
                bbox_x1, bbox_y1, bbox_x2, bbox_y2,
                latitude, longitude, zone_type, behavioral_note, camera_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            detection_id,
            datetime.now().isoformat(),
            detection.get('class'),
            detection.get('threat_type'),
            detection.get('confidence'),
            detection.get('threat_score'),
            detection.get('threat_level'),
            detection.get('threat_label'),
            bbox[0], bbox[1], bbox[2], bbox[3],
            loc.get('lat', 0),
            loc.get('lon', 0),
            loc.get('zone_type', 'restricted'),
            detection.get('behavioral_note'),
            camera_id
        ))
        
        row_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return row_id
    
    def save_alert(self, alert: Dict) -> int:
        """Save alert to database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        det = alert.get('detection', {})
        loc = alert.get('location', {})
        
        cursor.execute('''
            INSERT INTO alerts (
                alert_id, timestamp, threat_label, message,
                latitude, longitude, status, dispatched_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            alert.get('id'),
            alert.get('timestamp'),
            det.get('threat_label'),
            det.get('behavioral_note'),
            loc.get('lat', 0),
            loc.get('lon', 0),
            alert.get('status', 'pending'),
            alert.get('dispatch_time')
        ))
        
        row_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return row_id
    
    def get_recent_detections(self, limit: int = 50) -> List[Dict]:
        """Get recent detections"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM detections 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_recent_alerts(self, limit: int = 50) -> List[Dict]:
        """Get recent alerts"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM alerts 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_statistics(self) -> Dict:
        """Get system statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total detections
        cursor.execute('SELECT COUNT(*) as count FROM detections')
        total_detections = cursor.fetchone()['count']
        
        # Detections by threat level
        cursor.execute('''
            SELECT threat_label, COUNT(*) as count 
            FROM detections 
            WHERE threat_label IS NOT NULL
            GROUP BY threat_label
        ''')
        by_level = {row['threat_label']: row['count'] for row in cursor.fetchall()}
        
        # Total alerts
        cursor.execute('SELECT COUNT(*) as count FROM alerts')
        total_alerts = cursor.fetchone()['count']
        
        # Active cameras
        cursor.execute('SELECT COUNT(*) as count FROM cameras WHERE status = "active"')
        active_cameras = cursor.fetchone()['count']
        
        conn.close()
        
        return {
            'total_detections': total_detections,
            'detections_by_level': by_level,
            'total_alerts': total_alerts,
            'active_cameras': active_cameras
        }
    
    def add_camera(self, camera_id: str, name: str, stream_url: str, 
                   location: Dict, zone_type: str = 'restricted') -> int:
        """Add a new camera"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO cameras (
                camera_id, name, location_name, latitude, longitude,
                stream_url, zone_type, status, last_heartbeat
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            camera_id,
            name,
            location.get('name', ''),
            location.get('lat', 0),
            location.get('lon', 0),
            stream_url,
            zone_type,
            'active',
            datetime.now().isoformat()
        ))
        
        row_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return row_id
    
    def get_all_cameras(self) -> List[Dict]:
        """Get all cameras"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM cameras')
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]


if __name__ == "__main__":
    # Test database
    print("Testing Database Manager...\n")
    
    # Initialize
    db = DatabaseManager('test_border.db')
    
    # Add test camera
    camera_id = db.add_camera(
        camera_id='CAM-001',
        name='Border Sector 7 - Camera 1',
        stream_url='rtsp://example.com/stream1',
        location={'name': 'Sector 7 Zone A', 'lat': 28.6139, 'lon': 77.2090},
        zone_type='restricted'
    )
    print(f"Added camera: ID {camera_id}")
    
    # Save test detection
    test_detection = {
        'class': 'person',
        'threat_type': 'human',
        'confidence': 0.92,
        'threat_score': 0.85,
        'threat_level': 4,
        'threat_label': 'CRITICAL',
        'bbox': [100, 100, 200, 300],
        'behavioral_note': 'Unauthorized personnel at night'
    }
    
    det_id = db.save_detection(
        test_detection,
        location={'lat': 28.6139, 'lon': 77.2090, 'zone_type': 'restricted'},
        camera_id='CAM-001'
    )
    print(f"Saved detection: ID {det_id}")
    
    # Get statistics
    stats = db.get_statistics()
    print(f"\nStatistics: {json.dumps(stats, indent=2)}")
    
    # Get recent detections
    detections = db.get_recent_detections(limit=5)
    print(f"\nRecent detections: {len(detections)}")
    for det in detections:
        print(f"  - {det['object_class']}: {det['threat_label']}")
    
    # Cleanup test DB
    os.remove('test_border.db')
    print("\nTest database removed")
