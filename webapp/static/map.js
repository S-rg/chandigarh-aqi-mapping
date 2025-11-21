// Map initialization and AQI location management
const MAP_CONFIG = window.MAP_CONFIG || {};
const API_URL = MAP_CONFIG.apiUrl || '/api/get_latest_aqi_data';
const DEFAULT_CENTER = MAP_CONFIG.defaultCenter || [27.7, 85.3];
const DEFAULT_ZOOM = MAP_CONFIG.defaultZoom || 11;
const USE_CLUSTERING = MAP_CONFIG.useClustering !== false;
const SHOW_NUMERIC_MARKERS = MAP_CONFIG.showNumericMarkers === true;
const COUNT_LABEL = MAP_CONFIG.countLabel || 'locations';

let map;
let markerCluster = null;
let markers = [];
let locationData = [];
let selectedMarker = null;
let nodeModal;

// AQI color coding based on AQI_IN (Indian AQI standards)
function getAQIColor(aqi) {
    if (aqi === null || aqi === undefined) return '#808080'; // Gray for no data
    
    if (aqi <= 50) return '#00E400';      // Good - Green
    if (aqi <= 100) return '#FFFF00';     // Satisfactory - Yellow
    if (aqi <= 200) return '#FF7E00';      // Moderate - Orange
    if (aqi <= 300) return '#FF0000';     // Poor - Red
    if (aqi <= 400) return '#8F3F97';     // Very Poor - Purple
    return '#7E0023';                     // Severe - Dark Red
}

// Get AQI category text
function getAQICategory(aqi) {
    if (aqi === null || aqi === undefined) return 'No Data';
    
    if (aqi <= 50) return 'Good';
    if (aqi <= 100) return 'Satisfactory';
    if (aqi <= 200) return 'Moderate';
    if (aqi <= 300) return 'Poor';
    if (aqi <= 400) return 'Very Poor';
    return 'Severe';
}

// Initialize map when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeMap();
    loadAQIData();
    setupEventListeners();
    
    // Initialize Bootstrap modal
    nodeModal = new bootstrap.Modal(document.getElementById('nodeModal'));
});

// Initialize Leaflet map
function initializeMap() {
    // Create map
    map = L.map('map', {
        center: DEFAULT_CENTER,
        zoom: DEFAULT_ZOOM,
        zoomControl: true
    });

    // Add OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);

    // Add custom controls
    L.control.scale({ imperial: false }).addTo(map);
    
    // Initialize marker cluster group if enabled
    if (USE_CLUSTERING) {
        markerCluster = L.markerClusterGroup({
            chunkedLoading: true,
            maxClusterRadius: 50
        });
        map.addLayer(markerCluster);
    }
}

// Load AQI data from API
async function loadAQIData() {
    const nodeList = document.getElementById('nodeList');
    const nodeCount = document.getElementById('nodeCount');
    
    try {
        nodeList.innerHTML = '<div class="loading-message">Loading AQI data...</div>';
        
        const response = await fetch(API_URL);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        locationData = data.locations || [];
        
        if (locationData.length === 0) {
        nodeList.innerHTML = '<div class="empty-message">No AQI data found in database</div>';
        nodeCount.textContent = `0 ${COUNT_LABEL}`;
            return;
        }
        
        // Update location count
        let label = COUNT_LABEL;
        if (locationData.length === 1 && COUNT_LABEL.endsWith('s')) {
            label = COUNT_LABEL.slice(0, -1);
        }
        nodeCount.textContent = `${locationData.length} ${label}`;
        
        // Clear existing markers
        clearMarkers();
        
        // Add markers and populate sidebar
        locationData.forEach(location => {
            addMarker(location);
            addLocationToList(location);
        });
        
        // Fit map to show all markers
        if (markers.length > 0) {
            fitMapToMarkers();
        }
        
    } catch (error) {
        console.error('Error loading AQI data:', error);
        nodeList.innerHTML = `<div class="error-message">Error loading AQI data: ${error.message}</div>`;
        nodeCount.textContent = 'Error';
    }
}

// Add marker to map with clustering
function addMarker(location) {
    const aqi = location.AQI_IN || location.AQI_US;
    const color = getAQIColor(aqi);
    
    // Create custom colored marker icon
    const icon = SHOW_NUMERIC_MARKERS ? createNumericBadgeIcon(aqi) : createColoredIcon(color, aqi);
    
    const marker = L.marker([location.lat, location.lon], {
        icon: icon
    });
    
    // Create popup content with AQI information
    const popupContent = createPopupContent(location);
    marker.bindPopup(popupContent);
    
    // Add click event
    marker.on('click', function() {
        selectLocation(location.locationId);
        showLocationModal(location);
    });
    
    // Store marker with location data
    marker.locationData = location;
    markers.push(marker);
    
    // Add to cluster group or directly to map
    if (USE_CLUSTERING && markerCluster) {
        markerCluster.addLayer(marker);
    } else {
        marker.addTo(map);
    }
}

// Create colored marker icon
function createColoredIcon(color, aqi) {
    const size = 20;
    const html = `
        <div style="
            background-color: ${color};
            width: ${size}px;
            height: ${size}px;
            border: 3px solid white;
            border-radius: 50%;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        "></div>
    `;
    
    return L.divIcon({
        className: 'aqi-marker',
        html: html,
        iconSize: [size, size],
        iconAnchor: [size/2, size/2],
        popupAnchor: [0, -size/2]
    });
}

function createNumericBadgeIcon(aqi) {
    const color = getAQIColor(aqi);
    const text = (aqi !== null && aqi !== undefined) ? aqi : 'NA';
    const html = `
        <div class="aqi-badge-marker" style="background-color: ${color};">
            <span>${text}</span>
        </div>
    `;
    return L.divIcon({
        className: 'aqi-badge-wrapper',
        html: html,
        iconSize: [42, 42],
        iconAnchor: [21, 21],
        popupAnchor: [0, -21]
    });
}

// Create popup content
function createPopupContent(location) {
    const aqi = location.AQI_IN || location.AQI_US;
    const aqiCategory = getAQICategory(aqi);
    const aqiColor = getAQIColor(aqi);
    
    const locationName = location.city || location.locationId || 'Unknown Location';
    const stateCountry = [location.state, location.country].filter(Boolean).join(', ');
    
    let content = `
        <div class="popup-header" style="margin-bottom: 0.5rem;">
            <strong>${locationName}</strong>
        </div>
    `;
    
    if (stateCountry) {
        content += `<div class="popup-location" style="margin-bottom: 0.5rem;">${stateCountry}</div>`;
    }
    
    if (aqi !== null && aqi !== undefined) {
        content += `
            <div style="margin-bottom: 0.75rem;">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
                    <div style="width: 16px; height: 16px; background-color: ${aqiColor}; border-radius: 50%; border: 2px solid white; box-shadow: 0 1px 2px rgba(0,0,0,0.2);"></div>
                    <strong>AQI: ${aqi} (${aqiCategory})</strong>
                </div>
        `;
        
        if (location.PM2_5_UGM3 !== null && location.PM2_5_UGM3 !== undefined) {
            content += `<div style="font-size: 0.85em; color: #666;">PM2.5: ${location.PM2_5_UGM3.toFixed(1)} µg/m³</div>`;
        }
        if (location.PM10_UGM3 !== null && location.PM10_UGM3 !== undefined) {
            content += `<div style="font-size: 0.85em; color: #666;">PM10: ${location.PM10_UGM3.toFixed(1)} µg/m³</div>`;
        }
        if (location.T_C !== null && location.T_C !== undefined) {
            content += `<div style="font-size: 0.85em; color: #666;">Temp: ${location.T_C.toFixed(1)}°C</div>`;
        }
        
        content += `</div>`;
    }
    
    if (location.last_updated) {
        const date = new Date(location.last_updated);
        content += `<div style="font-size: 0.75em; color: #999; margin-top: 0.5rem;">Updated: ${date.toLocaleString()}</div>`;
    }
    
    return content;
}

// Add location to sidebar list
function addLocationToList(location) {
    const nodeList = document.getElementById('nodeList');
    
    // Remove loading message if present
    const loadingMsg = nodeList.querySelector('.loading-message');
    if (loadingMsg) {
        loadingMsg.remove();
    }
    
    const locationItem = document.createElement('div');
    locationItem.className = 'node-item';
    locationItem.dataset.locationId = location.locationId;
    
    const aqi = location.AQI_IN || location.AQI_US;
    const aqiColor = getAQIColor(aqi);
    const aqiCategory = getAQICategory(aqi);
    const locationName = location.city || `Location ${location.locationId}`;
    
    locationItem.innerHTML = `
        <div class="node-item-header">
            <div class="node-item-name">${locationName}</div>
            ${aqi !== null && aqi !== undefined ? `
                <div style="display: flex; align-items: center; gap: 0.25rem;">
                    <div style="width: 12px; height: 12px; background-color: ${aqiColor}; border-radius: 50%; border: 1px solid white; box-shadow: 0 1px 2px rgba(0,0,0,0.2);"></div>
                    <span style="font-size: 0.75rem; font-weight: 600; color: ${aqiColor};">${aqi}</span>
                </div>
            ` : ''}
        </div>
        <div class="node-item-location">${location.state || ''} ${location.country || ''}</div>
        ${aqi !== null && aqi !== undefined ? `
            <div style="font-size: 0.75rem; color: #666; margin-top: 0.25rem;">AQI: ${aqiCategory}</div>
        ` : ''}
        <div class="node-item-coords">${location.lat.toFixed(4)}, ${location.lon.toFixed(4)}</div>
    `;
    
    // Add click event
    locationItem.addEventListener('click', function() {
        selectLocation(location.locationId);
        const marker = markers.find(m => m.locationData.locationId === location.locationId);
        if (marker) {
            map.setView([location.lat, location.lon], 15);
            marker.openPopup();
            showLocationModal(location);
        }
    });
    
    nodeList.appendChild(locationItem);
}

// Select a location (highlight in sidebar and map)
function selectLocation(locationId) {
    // Remove active class from all items
    document.querySelectorAll('.node-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Add active class to selected item
    const locationItem = document.querySelector(`.node-item[data-location-id="${locationId}"]`);
    if (locationItem) {
        locationItem.classList.add('active');
        locationItem.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
    // Highlight marker
    markers.forEach(marker => {
        if (marker.locationData.locationId === locationId) {
            selectedMarker = marker;
        }
    });
}

// Show location modal
function showLocationModal(location) {
    const modalTitle = document.getElementById('nodeModalTitle');
    const modalBody = document.getElementById('nodeModalBody');
    const viewDetailsLink = document.getElementById('viewDetailsLink');
    
    const locationName = location.city || `Location ${location.locationId}`;
    modalTitle.textContent = locationName;
    viewDetailsLink.style.display = 'none'; // Hide view details link for AQI data
    
    const aqi = location.AQI_IN || location.AQI_US;
    const aqiColor = getAQIColor(aqi);
    const aqiCategory = getAQICategory(aqi);
    
    let modalHTML = `
        <div class="node-info-item">
            <div class="info-label">Location</div>
            <div class="info-value">${locationName}</div>
        </div>
    `;
    
    if (location.state || location.country) {
        modalHTML += `
            <div class="node-info-item">
                <div class="info-label">State/Country</div>
                <div class="info-value">${[location.state, location.country].filter(Boolean).join(', ')}</div>
            </div>
        `;
    }
    
    if (location.locationId) {
        modalHTML += `
            <div class="node-info-item">
                <div class="info-label">Location ID</div>
                <div class="info-value">${location.locationId}</div>
            </div>
        `;
    }
    
    modalHTML += `
        <div class="node-info-item">
            <div class="info-label">Coordinates</div>
            <div class="info-value">${location.lat.toFixed(6)}, ${location.lon.toFixed(6)}</div>
        </div>
    `;
    
    if (aqi !== null && aqi !== undefined) {
        modalHTML += `
            <div class="node-info-item">
                <div class="info-label">Air Quality Index</div>
                <div class="info-value" style="display: flex; align-items: center; gap: 0.5rem;">
                    <div style="width: 20px; height: 20px; background-color: ${aqiColor}; border-radius: 50%; border: 2px solid white; box-shadow: 0 1px 2px rgba(0,0,0,0.2);"></div>
                    <strong>${aqi} (${aqiCategory})</strong>
                </div>
            </div>
        `;
    }
    
    // Add sensor readings
    const readings = [];
    if (location.PM2_5_UGM3 !== null && location.PM2_5_UGM3 !== undefined) {
        readings.push(`PM2.5: ${location.PM2_5_UGM3.toFixed(1)} µg/m³`);
    }
    if (location.PM10_UGM3 !== null && location.PM10_UGM3 !== undefined) {
        readings.push(`PM10: ${location.PM10_UGM3.toFixed(1)} µg/m³`);
    }
    if (location.PM1_UGM3 !== null && location.PM1_UGM3 !== undefined) {
        readings.push(`PM1: ${location.PM1_UGM3.toFixed(1)} µg/m³`);
    }
    if (location.CO_PPB !== null && location.CO_PPB !== undefined) {
        readings.push(`CO: ${location.CO_PPB.toFixed(1)} ppb`);
    }
    if (location.NO2_PPB !== null && location.NO2_PPB !== undefined) {
        readings.push(`NO₂: ${location.NO2_PPB.toFixed(1)} ppb`);
    }
    if (location.O3_PPB !== null && location.O3_PPB !== undefined) {
        readings.push(`O₃: ${location.O3_PPB.toFixed(1)} ppb`);
    }
    if (location.SO2_PPB !== null && location.SO2_PPB !== undefined) {
        readings.push(`SO₂: ${location.SO2_PPB.toFixed(1)} ppb`);
    }
    if (location.T_C !== null && location.T_C !== undefined) {
        readings.push(`Temperature: ${location.T_C.toFixed(1)}°C`);
    }
    if (location.H_PERCENT !== null && location.H_PERCENT !== undefined) {
        readings.push(`Humidity: ${location.H_PERCENT.toFixed(1)}%`);
    }
    if (location.TVOC_PPM !== null && location.TVOC_PPM !== undefined) {
        readings.push(`TVOC: ${location.TVOC_PPM.toFixed(2)} ppm`);
    }
    if (location.Noise_DB !== null && location.Noise_DB !== undefined) {
        readings.push(`Noise: ${location.Noise_DB.toFixed(1)} dB`);
    }
    
    if (readings.length > 0) {
        modalHTML += `
            <div class="node-info-item">
                <div class="info-label">Sensor Readings</div>
                <div class="info-value" style="font-size: 0.9em; line-height: 1.6;">
                    ${readings.join('<br>')}
                </div>
            </div>
        `;
    }
    
    if (location.last_updated) {
        const date = new Date(location.last_updated);
        modalHTML += `
            <div class="node-info-item">
                <div class="info-label">Last Updated</div>
                <div class="info-value">${date.toLocaleString()}</div>
            </div>
        `;
    }
    
    modalBody.innerHTML = modalHTML;
    nodeModal.show();
}

// Clear all markers
function clearMarkers() {
    if (USE_CLUSTERING && markerCluster) {
        markerCluster.clearLayers();
    } else {
        markers.forEach(marker => {
            if (map.hasLayer(marker)) {
                map.removeLayer(marker);
            }
        });
    }
    markers = [];
}

// Fit map to show all markers
function fitMapToMarkers() {
    if (markers.length === 0) return;
    
    const group = new L.featureGroup(markers);
    map.fitBounds(group.getBounds().pad(0.1));
}

// Setup event listeners
function setupEventListeners() {
    // Refresh button
    document.getElementById('refreshBtn').addEventListener('click', function() {
        loadAQIData();
    });
    
    // Fit bounds button
    document.getElementById('fitBoundsBtn').addEventListener('click', function() {
        fitMapToMarkers();
    });
    
    // Search functionality
    const searchInput = document.getElementById('nodeSearch');
    searchInput.addEventListener('input', function(e) {
        const searchTerm = e.target.value.toLowerCase();
        filterLocations(searchTerm);
    });
}

// Filter locations in sidebar
function filterLocations(searchTerm) {
    const locationItems = document.querySelectorAll('.node-item');
    
    locationItems.forEach(item => {
        const locationId = item.dataset.locationId;
        const location = locationData.find(l => l.locationId === locationId);
        
        if (!location) return;
        
        const searchableText = `
            ${location.locationId} 
            ${location.city || ''} 
            ${location.state || ''} 
            ${location.country || ''} 
            ${location.lat} 
            ${location.lon}
            ${location.AQI_IN || ''}
            ${location.AQI_US || ''}
        `.toLowerCase();
        
        if (searchableText.includes(searchTerm)) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}
