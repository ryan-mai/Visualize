function refreshStatus() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            document.getElementById('status').textContent = data.status;
            document.getElementById('uptime').textContent = data.uptime;
            document.getElementById('guilds').textContent = data.guilds;
            document.getElementById('last-activity').textContent = data.last_activity;
            
            // Update status card class
            const statusCard = document.querySelector('.status-card');
            statusCard.className = 'status-card status-' + data.status.toLowerCase().replace(' ', '-');
        });
}

// Auto-refresh every 30 seconds
setInterval(refreshStatus, 30000);

// Refresh on page load
window.addEventListener('load', refreshStatus);