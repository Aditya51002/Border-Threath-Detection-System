// Dashboard JavaScript

// Initialize Socket.IO connection
const socket = io();

// Global state
let map = null;
let markers = [];
let processingActive = false;

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    updateClock();
    setInterval(updateClock, 1000);
    
    loadStatistics();
    loadRecentAlerts();
    
    // Refresh stats every 10 seconds
    setInterval(loadStatistics, 10000);
});

// Update clock
function updateClock() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', { 
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    const dateString = now.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
    document.getElementById('current-time').textContent = `${dateString} ${timeString}`;
}

// Initialize Google Map
function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: 28.6139, lng: 77.2090 }, // Default: New Delhi
        zoom: 12,
        styles: [
            {
                featureType: 'poi',
                stylers: [{ visibility: 'off' }]
            }
        ]
    });
}

// Add marker to map
function addMarker(lat, lng, threatLevel, message) {
    const colors = {
        'CRITICAL': 'red',
        'HIGH': 'orange',
        'MEDIUM': 'yellow',
        'LOW': 'green'
    };
    
    const marker = new google.maps.Marker({
        position: { lat: lat, lng: lng },
        map: map,
        title: message,
        icon: {
            path: google.maps.SymbolPath.CIRCLE,
            scale: 10,
            fillColor: colors[threatLevel] || 'gray',
            fillOpacity: 0.8,
            strokeColor: 'white',
            strokeWeight: 2
        }
    });
    
    const infowindow = new google.maps.InfoWindow({
        content: `<strong>${threatLevel} ALERT</strong><br>${message}`
    });
    
    marker.addListener('click', function() {
        infowindow.open(map, marker);
    });
    
    markers.push(marker);
}

// Load statistics
async function loadStatistics() {
    try {
        const response = await fetch('/api/statistics');
        const data = await response.json();
        
        // Update stat cards
        document.getElementById('total-detections').textContent = 
            data.database.total_detections || 0;
        document.getElementById('critical-alerts').textContent = 
            data.alerts.critical || 0;
        document.getElementById('high-alerts').textContent = 
            data.alerts.high || 0;
        document.getElementById('active-cameras').textContent = 
            data.database.active_cameras || 0;
            
    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

// Load recent alerts
async function loadRecentAlerts() {
    try {
        const response = await fetch('/api/alerts/recent?limit=20');
        const alerts = await response.json();
        
        const container = document.getElementById('alerts-container');
        
        if (alerts.length === 0) {
            container.innerHTML = `
                <div class="p-3 text-muted text-center">
                    <i class="fas fa-shield-alt fa-2x mb-2"></i>
                    <p class="mb-0">No alerts</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = '';
        
        alerts.forEach(alert => {
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert-item alert-${alert.threat_label.toLowerCase()}`;
            alertDiv.innerHTML = `
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <strong class="text-uppercase">${alert.threat_label}</strong>
                        <small class="d-block text-muted">${formatTime(alert.timestamp)}</small>
                        <p class="mb-1 mt-1">${alert.message || 'Threat detected'}</p>
                    </div>
                    <span class="badge bg-secondary">${alert.alert_id}</span>
                </div>
            `;
            container.appendChild(alertDiv);
        });
        
        document.getElementById('alert-count').textContent = alerts.length;
        
    } catch (error) {
        console.error('Error loading alerts:', error);
    }
}

// Format timestamp
function formatTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Start video processing
async function startProcessing() {
    try {
        const response = await fetch('/api/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ source: 0 }) // 0 = webcam
        });
        
        const data = await response.json();
        
        if (data.success) {
            processingActive = true;
            document.getElementById('no-video').style.display = 'none';
            document.getElementById('video-stream').style.display = 'block';
            showNotification('Processing started', 'success');
        } else {
            showNotification(data.message || 'Failed to start', 'error');
        }
    } catch (error) {
        console.error('Error starting processing:', error);
        showNotification('Error starting processing', 'error');
    }
}

// Stop video processing
async function stopProcessing() {
    try {
        const response = await fetch('/api/stop', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            processingActive = false;
            document.getElementById('no-video').style.display = 'block';
            document.getElementById('video-stream').style.display = 'none';
            showNotification('Processing stopped', 'info');
        }
    } catch (error) {
        console.error('Error stopping processing:', error);
    }
}

// Upload video
async function uploadVideo(input) {
    const file = input.files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('video', file);
    
    try {
        showNotification('Uploading video...', 'info');
        
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Video uploaded successfully', 'success');
            // Start processing with uploaded video
            // You can extend this to process uploaded videos
        } else {
            showNotification(data.message || 'Upload failed', 'error');
        }
    } catch (error) {
        console.error('Error uploading video:', error);
        showNotification('Error uploading video', 'error');
    }
}

// Show notification
function showNotification(message, type = 'info') {
    // Simple alert for now - can be enhanced with toast notifications
    const colors = {
        'success': '#28a745',
        'error': '#dc3545',
        'info': '#17a2b8',
        'warning': '#ffc107'
    };
    
    console.log(`[${type.toUpperCase()}] ${message}`);
    // You can add a toast notification library here
}

// Socket.IO event handlers
socket.on('connect', function() {
    console.log('Connected to server');
    document.getElementById('system-status').textContent = 'ONLINE';
    document.getElementById('system-status').className = 'badge bg-success me-3';
});

socket.on('disconnect', function() {
    console.log('Disconnected from server');
    document.getElementById('system-status').textContent = 'OFFLINE';
    document.getElementById('system-status').className = 'badge bg-danger me-3';
});

socket.on('video_frame', function(data) {
    // Update video stream
    const img = document.getElementById('video-stream');
    img.src = 'data:image/jpeg;base64,' + data.frame;
    
    // Update counters
    document.getElementById('fps-counter').textContent = `FPS: ${data.fps.toFixed(1)}`;
    document.getElementById('detection-counter').textContent = `Detections: ${data.detections}`;
});

socket.on('new_alert', function(data) {
    console.log('New alert:', data);
    
    // Play sound (optional)
    playAlertSound();
    
    // Add to alerts list
    const container = document.getElementById('alerts-container');
    const alertDiv = document.createElement('div');
    const detection = data.detection;
    
    alertDiv.className = `alert-item alert-${detection.threat_label.toLowerCase()}`;
    alertDiv.innerHTML = `
        <div class="d-flex justify-content-between align-items-start">
            <div>
                <strong class="text-uppercase">${detection.threat_label}</strong>
                <small class="d-block text-muted">${formatTime(data.timestamp)}</small>
                <p class="mb-1 mt-1">${detection.behavioral_note}</p>
                <small class="text-muted">${detection.class} - ${(detection.confidence * 100).toFixed(1)}%</small>
            </div>
        </div>
    `;
    
    // Add to top of list
    if (container.firstChild) {
        container.insertBefore(alertDiv, container.firstChild);
    } else {
        container.innerHTML = '';
        container.appendChild(alertDiv);
    }
    
    // Keep only last 20 alerts
    while (container.children.length > 20) {
        container.removeChild(container.lastChild);
    }
    
    // Update counter
    document.getElementById('alert-count').textContent = container.children.length;
    
    // Add marker to map if location available
    if (map && data.location) {
        addMarker(
            data.location.lat || 28.6139,
            data.location.lon || 77.2090,
            detection.threat_label,
            detection.behavioral_note
        );
    }
    
    // Reload statistics
    loadStatistics();
});

// Play alert sound (optional)
function playAlertSound() {
    // You can add an audio element and play it here
    // const audio = new Audio('/static/alert.mp3');
    // audio.play();
}

// Initialize map if Google Maps is not loaded yet
if (typeof google === 'undefined') {
    window.initMap = function() {
        map = new google.maps.Map(document.getElementById('map'), {
            center: { lat: 28.6139, lng: 77.2090 },
            zoom: 12
        });
    };
}
