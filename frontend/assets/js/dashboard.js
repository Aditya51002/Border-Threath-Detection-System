// 🛡️ BorderShield AI - Next-Gen Command & Control JS Logic

// Initialize Socket.IO connection
const socket = io();

// Global state
let map = null;
let markers = [];
let processingActive = false;
let criticalAlertCount = 0;

// Initialization
document.addEventListener('DOMContentLoaded', function() {
    updateClock();
    setInterval(updateClock, 1000);
    loadStatistics();
    loadRecentAlerts();
    setInterval(loadStatistics, 5000);
    document.getElementById('video-stream').style.display = 'none';
});

function updateClock() {
    const now = new Date();
    document.getElementById('current-time').textContent = now.toLocaleTimeString('en-US', { 
        hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit'
    });
}

function initMap() {
    const center = { lat: 28.6139, lng: 77.2090 };
    map = new google.maps.Map(document.getElementById('map'), {
        center: center,
        zoom: 13,
        disableDefaultUI: true,
        styles: [
            { "elementType": "geometry", "stylers": [{ "color": "#212121" }] },
            { "elementType": "labels.icon", "stylers": [{ "visibility": "off" }] },
            { "elementType": "labels.text.fill", "stylers": [{ "color": "#757575" }] },
            { "elementType": "labels.text.stroke", "stylers": [{ "color": "#212121" }] },
            { "featureType": "administrative", "elementType": "geometry", "stylers": [{ "color": "#757575" }] },
            { "featureType": "poi", "elementType": "geometry", "stylers": [{ "color": "#181818" }] },
            { "featureType": "road", "elementType": "geometry.fill", "stylers": [{ "color": "#2c2c2c" }] },
            { "featureType": "water", "elementType": "geometry", "stylers": [{ "color": "#000000" }] }
        ]
    });
    
    new google.maps.Circle({
        strokeColor: "#00d2ff",
        strokeOpacity: 0.8,
        strokeWeight: 2,
        fillColor: "#00d2ff",
        fillOpacity: 0.1,
        map: map,
        center: center,
        radius: 2000
    });
}

async function getAIAdvice() {
    const summaryEl = document.getElementById('ai-summary');
    summaryEl.innerHTML = '<i class="fas fa-circle-notch fa-spin me-2"></i> Formulating tactical response...';
    
    try {
        const response = await fetch('/api/ai/analyze');
        const data = await response.json();
        summaryEl.innerHTML = data.success ? 
            `<span class="text-primary font-weight-bold">STRATEGIC COMMAND:</span> ${data.analysis}` :
            "AI Command evaluating sector.";
    } catch (error) {
        summaryEl.textContent = "Strategic AI connection offline.";
    }
}

async function loadStatistics() {
    try {
        const response = await fetch('/api/statistics');
        const data = await response.json();
        
        animateCounter('total-detections', data.database.total_detections || 0);
        animateCounter('critical-alerts', data.alerts.critical || 0);
        animateCounter('high-alerts', data.alerts.high || 0);
        animateCounter('active-cameras', data.database.active_cameras || 0);
        
        if (data.alerts.critical > criticalAlertCount) triggerCriticalAlert();
        criticalAlertCount = data.alerts.critical;
    } catch (error) {
        console.error('Stats Sync Error:', error);
    }
}

function animateCounter(id, target) {
    const el = document.getElementById(id);
    const current = parseInt(el.textContent) || 0;
    if (current === target) return;
    
    const step = Math.ceil(Math.abs(target - current) / 10);
    let val = current;
    const interval = setInterval(() => {
        val = (val < target) ? Math.min(val + step, target) : Math.max(val - step, target);
        el.textContent = val;
        if (val === target) clearInterval(interval);
    }, 30);
}

async function loadRecentAlerts() {
    try {
        const [alertsRes, detectionsRes] = await Promise.all([
            fetch('/api/alerts/recent?limit=15'),
            fetch('/api/detections/recent?limit=30')
        ]);
        renderAlerts(await alertsRes.json());
        renderDetections(await detectionsRes.json());
    } catch (error) {
        console.error('Log Load Error:', error);
    }
}

function renderAlerts(alerts) {
    const container = document.getElementById('alerts-container');
    if (!alerts.length) return;
    
    container.innerHTML = '';
    alerts.forEach(alert => {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert-item alert-${alert.threat_label.toLowerCase()} glass-panel`;
        alertDiv.innerHTML = `
            <div class="d-flex justify-content-between align-items-start mb-2">
                <div>
                    <span class="badge bg-${getSeverityClass(alert.threat_label)} mb-2 text-uppercase font-weight-bold">${alert.threat_label}</span>
                    <p class="mb-1 font-weight-bold text-main">${alert.message || 'Intrusion Detected'}</p>
                </div>
                <small class="text-dim">${formatTime(alert.timestamp)}</small>
            </div>
            <div class="ai-insights">
                <i class="fas fa-microchip me-1 opacity-70"></i> AI INSIGHT: Sector ${alert.camera_id || 'Alpha'} monitored.
            </div>
        `;
        container.appendChild(alertDiv);
    });
}

function renderDetections(detections) {
    const container = document.getElementById('detections-container');
    container.innerHTML = detections.map(det => `
        <div class="detection-log-item">
            <div class="d-flex justify-content-between">
                <span class="text-main">${det.object_class || det.class || 'Object'} detected</span>
                <span class="text-dim small">${formatTime(det.timestamp)}</span>
            </div>
            <div class="progress mt-1" style="height: 2px; background: rgba(255,255,255,0.05);">
                <div class="progress-bar bg-primary" role="progressbar" style="width: ${det.confidence * 100}%"></div>
            </div>
        </div>
    `).join('');
}

function getSeverityClass(label) {
    const map = { 'CRITICAL': 'danger', 'HIGH': 'warning', 'MEDIUM': 'primary', 'LOW': 'success' };
    return map[label] || 'secondary';
}

async function startProcessing() {
    setSystemLoading(true);
    try {
        const response = await fetch('/api/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ source: 0 })
        });
        if ((await response.json()).success) {
            processingActive = true;
            document.getElementById('no-video').style.display = 'none';
            document.getElementById('video-stream').style.display = 'block';
            getAIAdvice();
        }
    } finally {
        setSystemLoading(false);
    }
}

function setSystemLoading(loading) {
    const btn = document.querySelector('.btn-glow');
    btn.innerHTML = loading ? '<i class="fas fa-spinner fa-spin me-2"></i> CONNECTING...' : '<i class="fas fa-power-off me-2"></i> INITIALIZE SYSTEM';
    btn.disabled = loading;
}

socket.on('video_frame', function(data) {
    document.getElementById('video-stream').src = 'data:image/jpeg;base64,' + data.frame;
    document.getElementById('fps-counter').textContent = `${data.fps.toFixed(1)} FPS`;
    document.getElementById('detection-counter').textContent = `${data.detections} DETECTIONS`;
});

socket.on('new_alert', function(data) {
    loadRecentAlerts();
    loadStatistics();
    if (data.detection.threat_label === 'CRITICAL') triggerCriticalAlert();
});

function triggerCriticalAlert() {
    document.body.style.boxShadow = 'inset 0 0 100px rgba(255,75,43,0.3)';
    setTimeout(() => document.body.style.boxShadow = 'none', 1000);
}

function formatTime(timestamp) {
    return new Date(timestamp).toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

