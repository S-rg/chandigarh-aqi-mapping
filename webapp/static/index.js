async function loadNodes() {
    try {
        const response = await fetch("/api/get_all_nodes");
        if (!response.ok) {
            throw new Error(`HTTP error ${response.status}`);
        }

        const data = await response.json();
        const container = document.getElementById("node-links");

        data.nodes.forEach(nodeId => {
            const link = document.createElement("a");
            link.href = `/plot/${nodeId}`;
            link.textContent = `Node ${nodeId}`;
            link.style.display = "block";
            container.appendChild(link);
        });

    } catch (error) {
        console.error("Error loading nodes:", error);
    }
}
document.addEventListener("DOMContentLoaded", loadNodes);