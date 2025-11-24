// Auto-refresh stats every 3 seconds
function updateStats() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            document.getElementById('total-requests').textContent = data.total_requests;
            document.getElementById('blocked-requests').textContent = data.blocked_requests;
            document.getElementById('cached-items').textContent = data.cached_items;
            document.getElementById('blocked-sites-count').textContent = data.blocked_sites_count;
            
            // Update server status
            const statusIndicator = document.querySelector('.status-indicator');
            const statusText = document.querySelector('.status-text');
            if (data.server_running) {
                statusIndicator.classList.add('running');
                statusIndicator.classList.remove('stopped');
                statusText.textContent = 'RUNNING';
            } else {
                statusIndicator.classList.add('stopped');
                statusIndicator.classList.remove('running');
                statusText.textContent = 'STOPPED';
            }
        })
        .catch(error => console.error('Error updating stats:', error));
}

// Start auto-refresh
setInterval(updateStats, 3000);

// Show toast notification
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast show ${type}`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Start server
function startServer() {
    fetch('/api/start', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showToast(data.message, 'success');
                setTimeout(() => location.reload(), 1500);
            } else {
                showToast(data.message, 'error');
            }
        })
        .catch(error => {
            showToast('Failed to start server', 'error');
            console.error('Error:', error);
        });
}

// Stop server
function stopServer() {
    fetch('/api/stop', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showToast(data.message, 'success');
                setTimeout(() => location.reload(), 1500);
            } else {
                showToast(data.message, 'error');
            }
        })
        .catch(error => {
            showToast('Failed to stop server', 'error');
            console.error('Error:', error);
        });
}

// Block site
function blockSite() {
    const input = document.getElementById('blockInput');
    const pattern = input.value.trim();
    
    if (!pattern) {
        showToast('Please enter a website URL', 'error');
        return;
    }
    
    fetch('/api/block-site', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pattern: pattern })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showToast(data.message, 'success');
            input.value = '';
            setTimeout(() => location.reload(), 1500);
        } else {
            showToast(data.message, 'error');
        }
    })
    .catch(error => {
        showToast('Failed to block site', 'error');
        console.error('Error:', error);
    });
}

// Unblock site
function unblockSite(pattern) {
    fetch('/api/unblock-site', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pattern: pattern })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showToast(data.message, 'success');
            setTimeout(() => location.reload(), 1500);
        } else {
            showToast(data.message, 'error');
        }
    })
    .catch(error => {
        showToast('Failed to unblock site', 'error');
        console.error('Error:', error);
    });
}

// Quick block
function quickBlock(site) {
    fetch('/api/quick-block', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ site: site })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showToast(data.message, 'success');
            setTimeout(() => location.reload(), 1500);
        } else {
            showToast(data.message, 'error');
        }
    })
    .catch(error => {
        showToast('Failed to block site', 'error');
        console.error('Error:', error);
    });
}

// Clear cache
function clearCache() {
    if (!confirm('Are you sure you want to clear the cache?')) return;
    
    fetch('/api/clear-cache', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            showToast(data.message, data.status);
            updateStats();
        })
        .catch(error => {
            showToast('Failed to clear cache', 'error');
            console.error('Error:', error);
        });
}

// Clear logs
function clearLogs() {
    if (!confirm('Are you sure you want to clear all logs?')) return;
    
    fetch('/api/clear-logs', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            showToast(data.message, data.status);
            updateStats();
        })
        .catch(error => {
            showToast('Failed to clear logs', 'error');
            console.error('Error:', error);
        });
}