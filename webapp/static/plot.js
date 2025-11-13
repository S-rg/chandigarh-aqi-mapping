let autoUpdate = true;
let updateIntervalId = null;
let sensorData = {};
let maxDataPoints = 50;
let measurements = []; 

for (let i = 1; i <= 20; i++) {
    sensorData[i] = {
        timestamps: [],
        values: [],
        active: false
    };
}

document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    
    const intervalSelect = document.getElementById('updateIntervalSelect');
    if (intervalSelect) {
        intervalSelect.addEventListener('change', function() {
            const interval = parseInt(this.value);
            setupAutoUpdate(interval);
        });
    }
    
    setupAutoUpdate(5000);
});

async function initializeDashboard() {
    try {
        showLoading(true);
        const response = await fetch(`/api/get_sensor_mapping/${node_id}`);
        const data = await response.json();
        const mapping_ = data.mapping;

        const mapping = {};
        for (const [key, values] of Object.entries(mapping_)) {
            const [sensorId, measurementId] = key.split(",");
            if (!mapping[sensorId]) mapping[sensorId] = {};
            mapping[sensorId][measurementId] = values;
        }

        const nodeResponse = await fetch(`/api/node/${nodeId}`);
        const nodeData = await nodeResponse.json();
        
        if (!nodeData.sensors || !Array.isArray(nodeData.sensors)) {
            showError('No sensors found for node 1');
            return;
        }
        
        // Fetch measurements for each sensor
        const measurementPromises = nodeData.sensors.map(async (sensorId) => {
            try {
                const sensorResponse = await fetch(`/api/sensor/${nodeId}/${sensorId}`);
                const sensorData = await sensorResponse.json();
                
                // API returns {measurements: [id1, id2, id3, ...]}
                if (sensorData.measurements && Array.isArray(sensorData.measurements)) {
                    return sensorData.measurements.map(measurementId => ({
                        nodeId: nodeId,
                        sensorId: sensorId,
                        measurementId: measurementId,
                        measurementName: mapping[sensorId][measurementId][0] || '',
                        unit: mapping[sensorId][measurementId][1] || ''
                    }));
                }
                return [];
            } catch (error) {
                console.error(`Error fetching measurements for sensor ${sensorId}:`, error);
                return [];
            }
        });
        
        const allMeasurements = await Promise.all(measurementPromises);
        measurements = allMeasurements.flat();
        
        console.log('Total measurements found:', measurements.length);
        
        createGraphs();
        
        await loadAllMeasurementData();
        
        showLoading(false);
        updateGlobalLastUpdate();
        
    } catch (error) {
        console.error('Error initializing dashboard:', error);
        showError('Failed to initialize dashboard: ' + error.message);
        showLoading(false);
    }
}

function createGraphs() {
    const container = document.getElementById('sensorGrid');
    if (!container) return;
    
    // Clear existing content
    container.innerHTML = '';
    
    // Create a card for each measurement
    measurements.forEach((measurement, index) => {
        const card = createMeasurementCard(measurement, index);
        container.appendChild(card);
    });
}

function createMeasurementCard(measurement, index) {
    const col = document.createElement('div');
    col.className = 'col-xl-6 col-lg-12 col-md-12 mb-4';
    
    const card = document.createElement('div');
    card.className = 'sensor-card';
    card.id = `measurement-card-${index}`;
    
    const cardHeader = document.createElement('div');
    cardHeader.className = 'sensor-header';
    cardHeader.innerHTML = `
        <div class="sensor-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M3 17v2a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-2" stroke="currentColor" stroke-width="2" fill="none"/>
                <path d="M7 17V7a5 5 0 0 1 10 0v10" stroke="currentColor" stroke-width="2" fill="none"/>
            </svg>
        </div>
        <div class="sensor-info-header">
            <span class="sensor-name">${measurement.measurementName}</span>
            <span class="sensor-subtitle">Node ${measurement.nodeId} - Sensor ${measurement.sensorId}</span>
        </div>
        <div class="sensor-value-container" id="value-container-${index}">
            <span class="sensor-value" id="current-value-${index}">--</span>
            <span class="sensor-unit">${measurement.unit}</span>
        </div>
    `;
    
    const plotDiv = document.createElement('div');
    plotDiv.id = `plot-${index}`;
    plotDiv.className = 'plot-container';
    plotDiv.style.width = '100%';
    plotDiv.style.height = '300px';
    
    card.appendChild(cardHeader);
    card.appendChild(plotDiv);
    col.appendChild(card);
    
    return col;
}

async function loadAllMeasurementData() {
    const promises = measurements.map((measurement, index) => 
        loadMeasurementData(measurement, index)
    );
    
    await Promise.all(promises);
}

async function loadMeasurementData(measurement, index) {
    try {
        const response = await fetch(
            `/api/measurement/${measurement.nodeId}/${measurement.sensorId}/${measurement.measurementId}`
        );
        const result = await response.json();
        
        if (result.data && Array.isArray(result.data)) {
            const timestamps = result.data.map(d => new Date(d.timestamp));
            const values = result.data.map(d => d.value);
            
            // Keep only last maxDataPoints
            const startIdx = Math.max(0, timestamps.length - maxDataPoints);
            const slicedTimestamps = timestamps.slice(startIdx);
            const slicedValues = values.slice(startIdx);
            
            updatePlot(index, slicedTimestamps, slicedValues, measurement);
            
            // Update current value display
            if (values.length > 0) {
                const currentValue = values[values.length - 1];
                const valueElement = document.getElementById(`current-value-${index}`);
                if (valueElement) {
                    valueElement.textContent = currentValue.toFixed(2);
                }
            }
        }
        
    } catch (error) {
        console.error(`Error loading data for measurement ${measurement.measurementId}:`, error);
    }
}

function updatePlot(index, timestamps, values, measurement) {
    const plotDiv = document.getElementById(`plot-${index}`);
    if (!plotDiv) return;
    
    const trace = {
        x: timestamps,
        y: values,
        type: 'scatter',
        mode: 'lines+markers',
        name: measurement.measurementName,
        line: {
            color: '#4A90E2',
            width: 2
        },
        marker: {
            size: 4,
            color: '#4A90E2'
        }
    };
    
    const layout = {
        margin: { t: 20, r: 20, b: 40, l: 50 },
        xaxis: {
            title: 'Time',
            type: 'date',
            gridcolor: '#e0e0e0'
        },
        yaxis: {
            title: `${measurement.measurementName} (${measurement.unit})`,
            gridcolor: '#e0e0e0'
        },
        plot_bgcolor: '#ffffff',
        paper_bgcolor: '#ffffff',
        font: {
            family: 'Inter, system-ui, -apple-system, sans-serif',
            size: 11
        }
    };
    
    const config = {
        responsive: true,
        displayModeBar: false
    };
    
    Plotly.newPlot(plotDiv, [trace], layout, config);
}

function setupAutoUpdate(interval) {
    // Clear existing interval
    if (updateIntervalId) {
        clearInterval(updateIntervalId);
    }
    
    // Set up new interval if auto-update is enabled
    if (autoUpdate) {
        updateIntervalId = setInterval(() => {
            loadAllMeasurementData();
            updateGlobalLastUpdate();
        }, interval);
    }
}

function toggleAutoUpdate() {
    autoUpdate = !autoUpdate;
    const btn = document.getElementById('autoUpdateBtn');
    
    if (autoUpdate) {
        btn.textContent = 'Pause';
        const interval = parseInt(document.getElementById('updateIntervalSelect').value);
        setupAutoUpdate(interval);
    } else {
        btn.textContent = 'Resume';
        if (updateIntervalId) {
            clearInterval(updateIntervalId);
            updateIntervalId = null;
        }
    }
}

function refreshAllSensors() {
    loadAllMeasurementData();
    updateGlobalLastUpdate();
}

function updateGlobalLastUpdate() {
    const element = document.getElementById('globalLastUpdate');
    if (element) {
        const now = new Date();
        element.textContent = now.toLocaleTimeString();
    }
}

function showLoading(show) {
    const spinner = document.getElementById('loadingSpinner');
    if (spinner) {
        spinner.style.display = show ? 'block' : 'none';
    }
}

function showError(message) {
    const errorAlert = document.getElementById('errorAlert');
    const errorMessage = document.getElementById('errorMessage');
    
    if (errorAlert && errorMessage) {
        errorMessage.textContent = message;
        errorAlert.style.display = 'block';
    }
}

function hideError() {
    const errorAlert = document.getElementById('errorAlert');
    if (errorAlert) {
        errorAlert.style.display = 'none';
    }
}