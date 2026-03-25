import os
import random
from datetime import datetime

class StrategicAIAgent:
    """
    Strategic AI Agent for Border Security operations.
    Processes detection logs to generate tactical insights and response protocols.
    """
    
    def __init__(self):
        self.persona = "Border Security Strategic Intelligence"
        self.last_analysis = None
        
    def analyze_threats(self, alerts, detections):
        """
        Analyzes recent activity and generates strategic advice.
        Utilizes rule-based generative logic to synthesize situational awareness.
        """
        if not alerts and not detections:
            return "Sector currently stable. Maintain standard surveillance protocols."
        
        critical_count = len([a for a in alerts if a.get('threat_label') == 'CRITICAL'])
        high_count = len([a for a in alerts if a.get('threat_label') == 'HIGH'])
        human_detections = len([d for d in detections if d.get('class') == 'person'])
        
        insights = []
        
        if critical_count > 0:
            insights.append(f"CRITICAL BREACH ATTEMPT: {critical_count} high-intensity events detected.")
            insights.append("TACTICAL RESPONSE: Deploy Rapid Response Teams to Sector Zulu-1 immediately.")
        elif high_count > 2:
            insights.append(f"PREDICTIVE ALERT: Multiple high-risk detections ({high_count}) suggest perimeter probing.")
            insights.append("STRATEGIC SUGGESTION: Increase drone patrol frequency in the northern corridor.")
        elif human_detections > 5:
            insights.append(f"CROWD ANOMALY: {human_detections} humanoid signatures identified.")
            insights.append("ADVICE: Activate thermal searchlights and initiate audio warnings.")
        else:
            insights.append("SECTOR UPDATE: Minor activity detected. Low probability of immediate threat.")
            
        current_hour = datetime.now().hour
        if 20 <= current_hour or current_hour <= 5:
            insights.append("NIGHT OPS NOTE: Low-light performance optimization active.")
            
        self.last_analysis = " ".join(insights)
        return self.last_analysis

    def get_tactical_summary(self):
        return self.last_analysis if self.last_analysis else "System standby."

    def chat(self, query):
        query = query.lower()
        if "status" in query:
            return "Sector Alpha is at Alert Level Green."
        elif "threat" in query:
            return self.get_tactical_summary()
        elif "help" in query:
            return "Available: tactical summaries, threat analysis, and patrol optimization."
        else:
            return "Strategic Command analyzing query..."
