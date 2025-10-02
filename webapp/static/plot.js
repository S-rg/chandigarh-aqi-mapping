let autoUpdate = true;
let updateIntervalId = null;
let sensorData = {};
let maxDataPoints = 50;

// NEW: Sensor mapping moved to frontend
const sensorMappings = {
    1: {table: "winsen1", gas: "pm25"},
    2: {table: "winsen1", gas: "pm10"},
    3: {table: "winsen1", gas: "co2"},
    4: {table: "winsen1", gas: "temp"},
    5: {table: "winsen1", gas: "humidity"},
    6: {table: "winsen1", gas: "voc"},
    7: {table: "winsen2", gas: "pm25"},
    8: {table: "winsen2", gas: "pm10"},
    9: {table: "winsen2", gas: "co2"},
    10: {table: "winsen2", gas: "temp"},
    11: {table: "winsen2", gas: "humidity"},
    12: {table: "winsen2", gas: "voc"},
    13: {table: "winsen1", gas: "pm1"},
    14: {table: "winsen1", gas: "ch2o"},
    15: {table: "winsen1", gas: "co"},
    16: {table: "winsen1", gas: "o3"},
    17: {table: "winsen1", gas: "no2"},
    18: {table: "winsen2", gas: "pm1"},
    19: {table: "winsen2", gas: "ch2o"},
    20: {table: "winsen2", gas: "co"}
};

for (let i = 1; i <= 20; i++) {
    sensorData[i] = {
        timestamps: [],
        values: [],
        active: false
    };
}

document.addEventListener('DOMContentLoaded', function() {
    initializePlots();
    startAutoUpdate();
    
    document.getElementById('updateInterval').addEventListener('change', function() {
        if (autoUpdate) {
            stopAutoUpdate();
            startAutoUpdate();
        }
    });
});

function initializePlots() {
    for (let i = 1; i <= 20; i++) {
        const layout = {
            margin: { t: 10, r: 10, b: 30, l: 40 },
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            xaxis: {
                type: 'date',
                gridcolor: 'rgba(255,255,255,0.1)',
                tickfont: { color: 'rgba(236, 240, 241, 0.5)', size: 10 }
            },
            yaxis: {
                gridcolor: 'rgba(255,255,255,0.1)',
                tickfont: { color: 'rgba(236, 240, 241, 0.5)', size: 10 }
            },
            showlegend: false,
            height: 250
        };
        
        const data = [{
            x: [],
            y: [],
            type: 'scatter',
            mode: 'lines+markers',
            line: { color: '#3498db', width: 2 },
            marker: { color: '#3498db', size: 4 }
        }];
        
        Plotly.newPlot(`plot-${i}`, data, layout, {responsive: true});
    }
}

// NEW: Updated fetch function to use gas endpoints
async function fetchSensorData(sensorId) {
    try {
        // Get mapping from frontend
        const mapping = sensorMappings[sensorId];
        if (!mapping) {
            throw new Error(`Sensor ${sensorId} not configured`);
        }
        
        // Call new gas-specific endpoint
        const response = await fetch(`/api/gas/${mapping.table}/${mapping.gas}/latest`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const data = await response.json();
        updateSensorDisplay(sensorId, data);
        return data;
    } catch (error) {
        console.error(`Error fetching sensor ${sensorId}:`, error);
        updateSensorStatus(sensorId, 'error');
        return null;
    }
}

function updateSensorDisplay(sensorId, data) {
    if (!data) return;
    
    const statusElement = document.getElementById(`status-${sensorId}`);
    statusElement.classList.remove('status-inactive', 'status-warning');
    statusElement.classList.add('status-active');
    
    const valueElement = document.getElementById(`value-${sensorId}`);
    const unitElement = document.getElementById(`unit-${sensorId}`);
    valueElement.textContent = data.value !== undefined ? data.value.toFixed(2) : '--';
    unitElement.textContent = data.unit || '';
    
    const now = new Date();
    document.getElementById(`updated-${sensorId}`).textContent = 
        `Updated: ${now.toLocaleTimeString()}`;
    
    sensorData[sensorId].timestamps.push(now);
    sensorData[sensorId].values.push(data.value || 0);
    sensorData[sensorId].active = true;
    
    if (sensorData[sensorId].timestamps.length > maxDataPoints) {
        sensorData[sensorId].timestamps.shift();
        sensorData[sensorId].values.shift();
    }
    
    updatePlot(sensorId);
}

function updatePlot(sensorId) {
    const data = sensorData[sensorId];
    if (!data.active) return;
    
    const update = {
        x: [data.timestamps],
        y: [data.values]
    };
    
    Plotly.update(`plot-${sensorId}`, update, {}, [0]);
}

function updateSensorStatus(sensorId, status) {
    const statusElement = document.getElementById(`status-${sensorId}`);
    statusElement.classList.remove('status-active', 'status-inactive', 'status-warning');
    
    switch(status) {
        case 'active':
            statusElement.classList.add('status-active');
            break;
        case 'error':
            statusElement.classList.add('status-inactive');
            break;
        case 'warning':
            statusElement.classList.add('status-warning');
            break;
    }
}

async function refreshAllSensors() {
    document.getElementById('loadingSpinner').style.display = 'inline-block';
    
    const promises = [];
    for (let i = 1; i <= 20; i++) {
        promises.push(fetchSensorData(i));
    }
    
    await Promise.allSettled(promises);
    
    document.getElementById('globalLastUpdate').textContent = new Date().toLocaleTimeString();
    document.getElementById('loadingSpinner').style.display = 'none';
}

// Start auto update
function startAutoUpdate() {
    if (updateIntervalId) clearInterval(updateIntervalId);
    
    const interval = parseInt(document.getElementById('updateInterval').value);
    refreshAllSensors(); // Initial fetch
    
    updateIntervalId = setInterval(() => {
        if (autoUpdate) {
            refreshAllSensors();
        }
    }, interval);
}

// Stop auto update
function stopAutoUpdate() {
    if (updateIntervalId) {
        clearInterval(updateIntervalId);
        updateIntervalId = null;
    }
}

// Toggle auto update
function toggleAutoUpdate() {
    autoUpdate = !autoUpdate;
    const btn = document.getElementById('autoUpdateBtn');
    
    if (autoUpdate) {
        btn.textContent = '⏸ Pause Updates';
        startAutoUpdate();
        document.getElementById('connectionStatus').textContent = 'Connected';
        document.getElementById('connectionStatus').className = 'badge bg-success';
    } else {
        btn.textContent = '▶ Resume Updates';
        stopAutoUpdate();
        document.getElementById('connectionStatus').textContent = 'Paused';
        document.getElementById('connectionStatus').className = 'badge bg-warning';
    }
}

// Show error message
function showError(message) {
    document.getElementById('errorMessage').textContent = message;
    document.getElementById('errorAlert').style.display = 'block';
    
    setTimeout(hideError, 5000);
}

// Hide error message
function hideError() {
    document.getElementById('errorAlert').style.display = 'none';
}