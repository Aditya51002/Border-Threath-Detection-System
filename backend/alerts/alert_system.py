"""
Alert Management System
Multi-channel alert dispatch (Console, SMS, Email simulation)
"""

import time
from datetime import datetime
from typing import Dict, List
from queue import Queue
from threading import Thread
import json


class AlertSystem:
    """
    Manage and dispatch alerts across multiple channels
    """
    
    def __init__(self):
        """Initialize alert system"""
        self.alert_queue = Queue()
        self.alert_history = []
        self.running = False
        self.dispatch_thread = None
        
        # Alert channels configuration
        self.channels = {
            'console': True,
            'sms': False,  # Requires Twilio API
            'email': False,  # Requires SMTP setup
            'websocket': False  # For real-time dashboard
        }
        
        # Alert statistics
        self.stats = {
            'total_alerts': 0,
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0
        }
    
    def start(self):
        """Start alert dispatch thread"""
        if self.running:
            print("[Alert] Already running")
            return
        
        self.running = True
        self.dispatch_thread = Thread(target=self._dispatch_loop, daemon=True)
        self.dispatch_thread.start()
        print("[Alert] Alert system started")
    
    def stop(self):
        """Stop alert dispatch"""
        self.running = False
        if self.dispatch_thread:
            self.dispatch_thread.join(timeout=2.0)
        print("[Alert] Alert system stopped")
    
    def _dispatch_loop(self):
        """Background thread for alert dispatch"""
        while self.running:
            try:
                alert = self.alert_queue.get(timeout=1.0)
                self._dispatch_alert(alert)
            except:
                continue
    
    def send_alert(self, detection: Dict, location: Dict = None):
        """
        Queue an alert for dispatch
        
        Args:
            detection: Detection data with threat analysis
            location: GPS coordinates (optional)
        """
        alert = {
            'id': f"ALT-{int(time.time() * 1000)}",
            'timestamp': datetime.now().isoformat(),
            'detection': detection,
            'location': location or {'lat': 0, 'lon': 0},
            'status': 'pending'
        }
        
        self.alert_queue.put(alert)
        
    def _dispatch_alert(self, alert: Dict):
        """
        Dispatch alert to configured channels
        """
        threat_level = alert['detection'].get('threat_label', 'UNKNOWN')
        
        # Update statistics
        self.stats['total_alerts'] += 1
        level_key = threat_level.lower()
        if level_key in self.stats:
            self.stats[level_key] += 1
        
        # Dispatch to channels based on threat level
        if threat_level in ['CRITICAL', 'HIGH']:
            # High priority - all channels
            self._send_console(alert)
            if self.channels['sms']:
                self._send_sms(alert)
            if self.channels['email']:
                self._send_email(alert)
            if self.channels['websocket']:
                self._send_websocket(alert)
        elif threat_level == 'MEDIUM':
            # Medium priority - console and email
            self._send_console(alert)
            if self.channels['email']:
                self._send_email(alert)
        else:
            # Low priority - console only
            self._send_console(alert)
        
        # Save to history
        alert['status'] = 'dispatched'
        alert['dispatch_time'] = datetime.now().isoformat()
        self.alert_history.append(alert)
        
        # Keep only last 1000 alerts in memory
        if len(self.alert_history) > 1000:
            self.alert_history = self.alert_history[-1000:]
    
    def _send_console(self, alert: Dict):
        """Print alert to console"""
        det = alert['detection']
        loc = alert['location']
        
        print("\n" + "="*70)
        print(f"🚨 [{alert['id']}] {det.get('threat_label', 'ALERT')} THREAT DETECTED")
        print("="*70)
        print(f"Time: {alert['timestamp']}")
        print(f"Object: {det.get('class', 'Unknown')}")
        print(f"Confidence: {det.get('confidence', 0)*100:.1f}%")
        print(f"Threat Score: {det.get('threat_score', 0):.2f}")
        print(f"Location: {loc.get('lat', 0):.6f}, {loc.get('lon', 0):.6f}")
        print(f"Note: {det.get('behavioral_note', 'N/A')}")
        print("="*70 + "\n")
    
    def _send_sms(self, alert: Dict):
        """Send SMS alert (placeholder - requires Twilio)"""
        # In production, integrate Twilio API
        print(f"[SMS] Would send: {alert['id']} to registered numbers")
        
        # Example Twilio integration:
        # from twilio.rest import Client
        # client = Client(account_sid, auth_token)
        # message = client.messages.create(
        #     body=f"ALERT: {alert['detection']['threat_label']} threat detected",
        #     from_='+1234567890',
        #     to='+0987654321'
        # )
    
    def _send_email(self, alert: Dict):
        """Send email alert (placeholder - requires SMTP)"""
        print(f"[Email] Would send: {alert['id']} to registered emails")
        
        # Example SMTP integration:
        # import smtplib
        # from email.mime.text import MIMEText
        # msg = MIMEText(f"Alert details: {json.dumps(alert, indent=2)}")
        # msg['Subject'] = f"Border Alert: {alert['detection']['threat_label']}"
        # smtp.send_message(msg)
    
    def _send_websocket(self, alert: Dict):
        """Send WebSocket alert (placeholder)"""
        print(f"[WebSocket] Would broadcast: {alert['id']}")
        # In production, integrate with WebSocket server
    
    def get_stats(self) -> Dict:
        """Get alert statistics"""
        return self.stats.copy()
    
    def get_recent_alerts(self, count: int = 10) -> List[Dict]:
        """Get recent alerts"""
        return self.alert_history[-count:]
    
    def clear_history(self):
        """Clear alert history"""
        self.alert_history.clear()
        print("[Alert] History cleared")


class AlertFilter:
    """
    Filter and deduplicate alerts to prevent spam
    """
    
    def __init__(self, cooldown_seconds: int = 30):
        """
        Args:
            cooldown_seconds: Minimum time between duplicate alerts
        """
        self.cooldown = cooldown_seconds
        self.recent_alerts = {}
    
    def should_alert(self, detection: Dict) -> bool:
        """
        Check if alert should be sent based on deduplication logic
        
        Args:
            detection: Detection data
            
        Returns:
            True if alert should be sent
        """
        # Create unique key for detection type
        key = f"{detection.get('class', '')}_{detection.get('threat_level', 0)}"
        
        current_time = time.time()
        
        # Check if similar alert was sent recently
        if key in self.recent_alerts:
            last_time = self.recent_alerts[key]
            if current_time - last_time < self.cooldown:
                return False  # Skip - too soon
        
        # Update last alert time
        self.recent_alerts[key] = current_time
        
        # Clean old entries
        self._cleanup()
        
        return True
    
    def _cleanup(self):
        """Remove old entries from recent alerts"""
        current_time = time.time()
        keys_to_remove = [
            key for key, timestamp in self.recent_alerts.items()
            if current_time - timestamp > self.cooldown * 2
        ]
        for key in keys_to_remove:
            del self.recent_alerts[key]


if __name__ == "__main__":
    # Test alert system
    print("Testing Alert System...\n")
    
    alert_system = AlertSystem()
    alert_filter = AlertFilter(cooldown_seconds=5)
    
    alert_system.start()
    
    # Test alerts
    test_detections = [
        {
            'class': 'person',
            'threat_type': 'human',
            'confidence': 0.95,
            'threat_score': 0.85,
            'threat_level': 4,
            'threat_label': 'CRITICAL',
            'behavioral_note': 'Unauthorized personnel at night'
        },
        {
            'class': 'car',
            'threat_type': 'vehicle',
            'confidence': 0.88,
            'threat_score': 0.65,
            'threat_level': 3,
            'threat_label': 'HIGH',
            'behavioral_note': 'Suspicious vehicle activity'
        },
        {
            'class': 'dog',
            'threat_type': 'animal',
            'confidence': 0.75,
            'threat_score': 0.20,
            'threat_level': 1,
            'threat_label': 'LOW',
            'behavioral_note': 'Wildlife - low threat'
        }
    ]
    
    print("Sending test alerts...")
    for i, det in enumerate(test_detections):
        if alert_filter.should_alert(det):
            location = {'lat': 28.6139 + i*0.001, 'lon': 77.2090 + i*0.001}
            alert_system.send_alert(det, location)
            time.sleep(0.5)
    
    time.sleep(2)
    
    print("\n=== Alert Statistics ===")
    print(json.dumps(alert_system.get_stats(), indent=2))
    
    alert_system.stop()
