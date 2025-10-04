// Auto-generate graph when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Add event listeners to radio buttons for auto-update
    const tableInputs = document.querySelectorAll('input[name="table"]');
    const sensorInputs = document.querySelectorAll('input[name="sensor"]');
    
    tableInputs.forEach(input => {
        input.addEventListener('change', make_graph);
    });
    
    sensorInputs.forEach(input => {
        input.addEventListener('change', make_graph);
    });
    
    // Generate initial graph
    make_graph();
});

function make_graph() {
    const table = document.querySelector('input[name="table"]:checked').value;
    const sensor = document.querySelector('input[name="sensor"]:checked').value;
    plotSensorData(table, sensor);
}

function plotSensorData(table, sensor) {
    fetch(`/api/${table}/${sensor}`)
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error(data.error);
            return;
        }

        const timestamps = data.data.map(row => row.timestamp).reverse();
        const values = data.data.map(row => row.sensor_value).reverse();

        const trace = {
            x: timestamps,
            y: values,
            type: 'scatter',
            mode: 'lines+markers',
            name: sensor
        };

        const layout = {
            title: `${sensor.toUpperCase()} Data from ${table}`,
            xaxis: { title: 'Timestamp' },
            yaxis: { title: 'Sensor Value' }
        };

        Plotly.newPlot('chart', [trace], layout);
    })
    .catch(error => console.error('Error fetching data:', error));
}