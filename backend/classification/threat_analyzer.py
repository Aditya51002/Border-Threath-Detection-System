"""
Threat Analysis and Classification
Intelligent threat level assessment
"""

import time
from datetime import datetime
from typing import Dict, List
import numpy as np


class ThreatAnalyzer:
    """
    Analyze detections and classify threat levels
    """
    
    # Threat levels
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    
    THREAT_LABELS = {
        LOW: "LOW",
        MEDIUM: "MEDIUM",
        HIGH: "HIGH",
        CRITICAL: "CRITICAL"
    }
    
    def __init__(self):
        """Initialize threat analyzer"""
        # Time-based risk factors
        self.night_hours = (20, 6)  # 8 PM to 6 AM considered high risk
        
        # Threat scoring weights
        self.weights = {
            'object_type': 0.3,
            'time_factor': 0.2,
            'zone_factor': 0.25,
            'behavior': 0.15,
            'confidence': 0.1
        }
        
        # Object threat scores (0-1 scale)
        self.object_scores = {
            'human': 0.7,
            'vehicle': 0.6,
            'animal': 0.1,
            'weapon': 1.0,
            'drone': 0.9,
            'unknown': 0.5
        }
        
        # Track objects for behavioral analysis
        self.object_history = {}
        
    def analyze(self, detections: List[Dict], location: Dict = None, zone_type: str = "restricted") -> List[Dict]:
        """
        Analyze detections and assign threat levels
        
        Args:
            detections: List of detected objects
            location: GPS coordinates (lat, lon)
            zone_type: "restricted", "patrolled", or "public"
            
        Returns:
            Detections with added threat analysis
        """
        analyzed = []
        
        for det in detections:
            threat_score = self._calculate_threat_score(det, zone_type)
            threat_level = self._score_to_level(threat_score)
            
            det['threat_score'] = threat_score
            det['threat_level'] = threat_level
            det['threat_label'] = self.THREAT_LABELS[threat_level]
            det['analysis_time'] = datetime.now().isoformat()
            
            # Add behavioral context
            det['behavioral_note'] = self._get_behavioral_note(det)
            
            analyzed.append(det)
        
        return analyzed
    
    def _calculate_threat_score(self, detection: Dict, zone_type: str) -> float:
        """
        Calculate threat score (0-1) based on multiple factors
        """
        score = 0.0
        
        # 1. Object type score
        threat_type = detection.get('threat_type', 'unknown')
        object_score = self.object_scores.get(threat_type, 0.5)
        score += object_score * self.weights['object_type']
        
        # 2. Time factor (night = higher risk)
        time_score = self._get_time_factor()
        score += time_score * self.weights['time_factor']
        
        # 3. Zone factor
        zone_score = self._get_zone_factor(zone_type)
        score += zone_score * self.weights['zone_factor']
        
        # 4. Confidence factor
        confidence = detection.get('confidence', 0.5)
        score += confidence * self.weights['confidence']
        
        # 5. Behavior factor (simplified for now)
        behavior_score = 0.5  # Default neutral
        score += behavior_score * self.weights['behavior']
        
        return min(score, 1.0)
    
    def _get_time_factor(self) -> float:
        """Calculate risk factor based on time of day"""
        current_hour = datetime.now().hour
        
        # Night time is higher risk
        if self.night_hours[0] <= current_hour or current_hour < self.night_hours[1]:
            return 0.9  # Night
        elif 6 <= current_hour < 9 or 17 <= current_hour < 20:
            return 0.5  # Dawn/dusk
        else:
            return 0.3  # Day
    
    def _get_zone_factor(self, zone_type: str) -> float:
        """Calculate risk factor based on zone type"""
        zone_scores = {
            'restricted': 1.0,  # Highest risk - no access allowed
            'patrolled': 0.6,   # Medium risk - limited access
            'public': 0.2       # Low risk - normal access
        }
        return zone_scores.get(zone_type, 0.5)
    
    def _score_to_level(self, score: float) -> int:
        """Convert threat score to threat level"""
        if score >= 0.8:
            return self.CRITICAL
        elif score >= 0.6:
            return self.HIGH
        elif score >= 0.4:
            return self.MEDIUM
        else:
            return self.LOW
    
    def _get_behavioral_note(self, detection: Dict) -> str:
        """Generate behavioral context note"""
        threat_type = detection.get('threat_type', 'unknown')
        threat_level = detection.get('threat_level', self.LOW)
        current_hour = datetime.now().hour
        
        notes = []
        
        # Time-based notes
        if self.night_hours[0] <= current_hour or current_hour < self.night_hours[1]:
            notes.append("Night-time detection")
        
        # Object-specific notes
        if threat_type == 'human':
            if threat_level >= self.HIGH:
                notes.append("Unauthorized personnel")
            else:
                notes.append("Person detected")
        elif threat_type == 'vehicle':
            if threat_level >= self.HIGH:
                notes.append("Suspicious vehicle activity")
            else:
                notes.append("Vehicle in area")
        elif threat_type == 'weapon':
            notes.append("WEAPON DETECTED - IMMEDIATE ACTION REQUIRED")
        elif threat_type == 'animal':
            notes.append("Wildlife - low threat")
        
        return "; ".join(notes) if notes else "Standard detection"
    
    def generate_alert_message(self, detection: Dict) -> str:
        """Generate human-readable alert message"""
        threat_label = detection.get('threat_label', 'UNKNOWN')
        class_name = detection.get('class', 'object')
        confidence = detection.get('confidence', 0) * 100
        note = detection.get('behavioral_note', '')
        
        message = f"[{threat_label} ALERT] {class_name.upper()} detected "
        message += f"(Confidence: {confidence:.1f}%) - {note}"
        
        return message
    
    def filter_by_threat_level(self, analyzed_detections: List[Dict], min_level: int) -> List[Dict]:
        """Filter detections by minimum threat level"""
        return [d for d in analyzed_detections if d.get('threat_level', 0) >= min_level]
    
    def get_summary(self, analyzed_detections: List[Dict]) -> Dict:
        """Get threat summary statistics"""
        if not analyzed_detections:
            return {
                'total': 0,
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
                'highest_threat': None
            }
        
        summary = {
            'total': len(analyzed_detections),
            'critical': sum(1 for d in analyzed_detections if d.get('threat_level') == self.CRITICAL),
            'high': sum(1 for d in analyzed_detections if d.get('threat_level') == self.HIGH),
            'medium': sum(1 for d in analyzed_detections if d.get('threat_level') == self.MEDIUM),
            'low': sum(1 for d in analyzed_detections if d.get('threat_level') == self.LOW),
            'highest_threat': max(analyzed_detections, key=lambda x: x.get('threat_score', 0))
        }
        
        return summary


if __name__ == "__main__":
    # Test threat analyzer
    print("Testing Threat Analyzer...\n")
    
    analyzer = ThreatAnalyzer()
    
    # Sample detections
    test_detections = [
        {
            'class': 'person',
            'threat_type': 'human',
            'confidence': 0.92,
            'bbox': [100, 100, 200, 300]
        },
        {
            'class': 'car',
            'threat_type': 'vehicle',
            'confidence': 0.88,
            'bbox': [300, 150, 500, 350]
        },
        {
            'class': 'dog',
            'threat_type': 'animal',
            'confidence': 0.75,
            'bbox': [50, 200, 150, 300]
        }
    ]
    
    # Analyze in restricted zone
    print("=== Analysis in RESTRICTED zone ===")
    analyzed = analyzer.analyze(test_detections, zone_type="restricted")
    
    for det in analyzed:
        print(f"\nObject: {det['class']}")
        print(f"Threat Level: {det['threat_label']} (Score: {det['threat_score']:.2f})")
        print(f"Alert: {analyzer.generate_alert_message(det)}")
    
    # Get summary
    print("\n=== Threat Summary ===")
    summary = analyzer.get_summary(analyzed)
    print(f"Total detections: {summary['total']}")
    print(f"Critical: {summary['critical']}, High: {summary['high']}, Medium: {summary['medium']}, Low: {summary['low']}")
    
    # Filter high threats
    high_threats = analyzer.filter_by_threat_level(analyzed, analyzer.HIGH)
    print(f"\n=== High Priority Threats: {len(high_threats)} ===")
    for threat in high_threats:
        print(f"- {threat['class']}: {threat['threat_label']}")
