// Map initialization and node management
let map;
let markers = [];
let nodeData = [];
let selectedMarker = null;
let nodeModal;

// Initialize map when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeMap();
    loadNodes();
    setupEventListeners();
    
    // Initialize Bootstrap modal
    nodeModal = new bootstrap.Modal(document.getElementById('nodeModal'));
});

// Initialize Leaflet map
function initializeMap() {
    // Default center (Chandigarh, India)
    const defaultCenter = [30.7333, 76.7794];
    const defaultZoom = 12;

    // Create map
    map = L.map('map', {
        center: defaultCenter,
        zoom: defaultZoom,
        zoomControl: true
    });

    // Add OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);

    // Add custom controls
    L.control.scale({ imperial: false }).addTo(map);
}

// Load nodes from API
async function loadNodes() {
    const nodeList = document.getElementById('nodeList');
    const nodeCount = document.getElementById('nodeCount');
    
    try {
        nodeList.innerHTML = '<div class="loading-message">Loading nodes...</div>';
        
        const response = await fetch('/api/get_all_nodes_with_locations');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        nodeData = data.nodes || [];
        
        if (nodeData.length === 0) {
            nodeList.innerHTML = '<div class="empty-message">No nodes found in database</div>';
            nodeCount.textContent = '0 nodes';
            return;
        }
        
        // Update node count
        nodeCount.textContent = `${nodeData.length} ${nodeData.length === 1 ? 'node' : 'nodes'}`;
        
        // Clear existing markers
        clearMarkers();
        
        // Add markers and populate sidebar
        nodeData.forEach(node => {
            addMarker(node);
            addNodeToList(node);
        });
        
        // Fit map to show all markers
        if (markers.length > 0) {
            fitMapToMarkers();
        }
        
    } catch (error) {
        console.error('Error loading nodes:', error);
        nodeList.innerHTML = `<div class="error-message">Error loading nodes: ${error.message}</div>`;
        nodeCount.textContent = 'Error';
    }
}

// Add marker to map
function addMarker(node) {
    const marker = L.marker([node.latitude, node.longitude], {
        icon: createCustomIcon()
    }).addTo(map);
    
    // Create popup content
    const popupContent = `
        <div class="popup-header">Node ${node.node_id}</div>
        <div class="popup-location">${node.location || 'Unknown Location'}</div>
        <div class="popup-coords">${node.latitude.toFixed(6)}, ${node.longitude.toFixed(6)}</div>
        <a href="/plot/${node.node_id}" class="popup-link">View Details</a>
    `;
    
    marker.bindPopup(popupContent);
    
    // Add click event
    marker.on('click', function() {
        selectNode(node.node_id);
        showNodeModal(node);
    });
    
    // Store marker with node data
    marker.nodeData = node;
    markers.push(marker);
}

// Create custom marker icon
function createCustomIcon() {
    return L.divIcon({
        className: 'custom-marker',
        html: '<div class="custom-marker-icon"></div>',
        iconSize: [20, 20],
        iconAnchor: [10, 10],
        popupAnchor: [0, -10]
    });
}

// Add node to sidebar list
function addNodeToList(node) {
    const nodeList = document.getElementById('nodeList');
    
    // Remove loading message if present
    const loadingMsg = nodeList.querySelector('.loading-message');
    if (loadingMsg) {
        loadingMsg.remove();
    }
    
    const nodeItem = document.createElement('div');
    nodeItem.className = 'node-item';
    nodeItem.dataset.nodeId = node.node_id;
    
    nodeItem.innerHTML = `
        <div class="node-item-header">
            <div class="node-item-name">${node.location || 'Unknown Location'}</div>
            <div class="node-item-id">${node.node_id}</div>
        </div>
        <div class="node-item-location">${node.location || 'No location specified'}</div>
        <div class="node-item-coords">${node.latitude.toFixed(6)}, ${node.longitude.toFixed(6)}</div>
    `;
    
    // Add click event
    nodeItem.addEventListener('click', function() {
        selectNode(node.node_id);
        const marker = markers.find(m => m.nodeData.node_id === node.node_id);
        if (marker) {
            map.setView([node.latitude, node.longitude], 15);
            marker.openPopup();
            showNodeModal(node);
        }
    });
    
    nodeList.appendChild(nodeItem);
}

// Select a node (highlight in sidebar and map)
function selectNode(nodeId) {
    // Remove active class from all items
    document.querySelectorAll('.node-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Add active class to selected item
    const nodeItem = document.querySelector(`.node-item[data-node-id="${nodeId}"]`);
    if (nodeItem) {
        nodeItem.classList.add('active');
        nodeItem.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
    // Highlight marker
    markers.forEach(marker => {
        if (marker.nodeData.node_id === nodeId) {
            selectedMarker = marker;
            // You can add custom styling here if needed
        }
    });
}

// Show node modal
function showNodeModal(node) {
    const modalTitle = document.getElementById('nodeModalTitle');
    const modalBody = document.getElementById('nodeModalBody');
    const viewDetailsLink = document.getElementById('viewDetailsLink');
    
    modalTitle.textContent = `Node ${node.node_id}`;
    viewDetailsLink.href = `/plot/${node.node_id}`;
    
    modalBody.innerHTML = `
        <div class="node-info-item">
            <div class="info-label">Location</div>
            <div class="info-value">${node.location || 'Unknown Location'}</div>
        </div>
        <div class="node-info-item">
            <div class="info-label">Node ID</div>
            <div class="info-value">${node.node_id}</div>
        </div>
        <div class="node-info-item">
            <div class="info-label">Coordinates</div>
            <div class="info-value">${node.latitude.toFixed(6)}, ${node.longitude.toFixed(6)}</div>
        </div>
    `;
    
    nodeModal.show();
}

// Clear all markers
function clearMarkers() {
    markers.forEach(marker => {
        map.removeLayer(marker);
    });
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
        loadNodes();
    });
    
    // Fit bounds button
    document.getElementById('fitBoundsBtn').addEventListener('click', function() {
        fitMapToMarkers();
    });
    
    // Search functionality
    const searchInput = document.getElementById('nodeSearch');
    searchInput.addEventListener('input', function(e) {
        const searchTerm = e.target.value.toLowerCase();
        filterNodes(searchTerm);
    });
}

// Filter nodes in sidebar
function filterNodes(searchTerm) {
    const nodeItems = document.querySelectorAll('.node-item');
    
    nodeItems.forEach(item => {
        const nodeId = item.dataset.nodeId;
        const node = nodeData.find(n => n.node_id === nodeId);
        
        if (!node) return;
        
        const searchableText = `${node.node_id} ${node.location || ''} ${node.latitude} ${node.longitude}`.toLowerCase();
        
        if (searchableText.includes(searchTerm)) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

