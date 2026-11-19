// Coreteron YouTube View Automation Frontend Client
// Zero emojis, strictly formal telemetry display

document.addEventListener('DOMContentLoaded', () => {
    initSSE();
    initForm();
    initProxyTest();
    initClearButton();
    startStatusPolling();
});

let isRunning = false;

function initSSE() {
    const feed = document.getElementById('terminal-feed');
    const evtSource = new EventSource('/api/stream');

    evtSource.onmessage = (e) => {
        try {
            const data = JSON.parse(e.data);
            appendLog(data);
            updateStatusMetrics();
        } catch (err) {
            // Ignore parse errors on keepalive
        }
    };

    evtSource.onerror = () => {
        // SSE auto-reconnects
    };
}

function appendLog(entry) {
    const feed = document.getElementById('terminal-feed');
    const div = document.createElement('div');
    div.className = `log-entry ${entry.type || 'info'}`;
    
    div.innerHTML = `
        <span class="log-time">[${entry.timestamp || '00:00:00'}]</span>
        <span class="log-tag">[${(entry.title || 'LOG').toUpperCase()}]</span>
        <span class="log-msg">${escapeHtml(entry.message || '')}</span>
    `;

    feed.appendChild(div);
    feed.scrollTop = feed.scrollHeight;
}

function escapeHtml(str) {
    return str.replace(/[&<>'"]/g, 
        tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
    );
}

function initForm() {
    const form = document.getElementById('form-campaign');
    const btnStart = document.getElementById('btn-start');
    const btnStop = document.getElementById('btn-stop');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const payload = {
            url: document.getElementById('cfg-url').value.trim(),
            target_views: parseInt(document.getElementById('cfg-views').value, 10),
            concurrency: parseInt(document.getElementById('cfg-concurrency').value, 10),
            min_watch: parseInt(document.getElementById('cfg-min-watch').value, 10),
            max_watch: parseInt(document.getElementById('cfg-max-watch').value, 10),
            gateway: document.getElementById('cfg-gateway').value.trim(),
            force_144p: document.getElementById('cfg-144p').checked,
            headless: document.getElementById('cfg-headless').checked,
        };

        btnStart.disabled = true;
        btnStart.innerHTML = '<span>Launching Workers...</span>';

        try {
            const res = await fetch('/api/campaign/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            const data = await res.json();
            if (!data.success) {
                alert('Launch failed: ' + data.message);
                btnStart.disabled = false;
                btnStart.innerHTML = '<span>Launch View Campaign</span>';
            } else {
                setRunningState(true);
            }
        } catch (err) {
            alert('Backend error: ' + err.message);
            btnStart.disabled = false;
            btnStart.innerHTML = '<span>Launch View Campaign</span>';
        }
    });

    btnStop.addEventListener('click', async () => {
        btnStop.disabled = true;
        btnStop.innerHTML = '<span>Stopping...</span>';
        try {
            await fetch('/api/campaign/stop', { method: 'POST' });
        } catch (err) {
            alert('Stop request error: ' + err.message);
        }
    });
}

function initProxyTest() {
    const btnTest = document.getElementById('btn-test-proxy');
    const input = document.getElementById('cfg-gateway');
    const statusHint = document.getElementById('proxy-test-status');

    btnTest.addEventListener('click', async () => {
        const proxyStr = input.value.trim();
        if (!proxyStr) {
            statusHint.style.color = '#e11d48';
            statusHint.textContent = 'Please enter a proxy string to test.';
            return;
        }

        btnTest.disabled = true;
        btnTest.textContent = 'Testing...';
        statusHint.style.color = '#64748b';
        statusHint.textContent = 'Checking connectivity and external IP...';

        try {
            const res = await fetch('/api/proxy/test', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ proxy: proxyStr }),
            });
            const data = await res.json();
            if (data.success) {
                statusHint.style.color = '#059669';
                statusHint.textContent = `Proxy Active. External IP: ${data.ip} (${data.latency_ms}ms)`;
            } else {
                statusHint.style.color = '#e11d48';
                statusHint.textContent = 'Test failed: ' + data.message;
            }
        } catch (err) {
            statusHint.style.color = '#e11d48';
            statusHint.textContent = 'Request error: ' + err.message;
        } finally {
            btnTest.disabled = false;
            btnTest.textContent = 'Test';
        }
    });
}

function initClearButton() {
    document.getElementById('btn-clear-feed').addEventListener('click', () => {
        document.getElementById('terminal-feed').innerHTML = '';
    });
}

function setRunningState(running) {
    isRunning = running;
    const btnStart = document.getElementById('btn-start');
    const btnStop = document.getElementById('btn-stop');
    const statusLabel = document.getElementById('global-status-label');
    const indicator = document.querySelector('.status-indicator');

    if (running) {
        btnStart.style.display = 'none';
        btnStop.style.display = 'inline-flex';
        btnStop.disabled = false;
        btnStop.innerHTML = '<span>Stop Campaign</span>';
        statusLabel.textContent = 'Campaign Running';
        indicator.className = 'status-indicator busy';
    } else {
        btnStart.style.display = 'inline-flex';
        btnStart.disabled = false;
        btnStart.innerHTML = '<span>Launch View Campaign</span>';
        btnStop.style.display = 'none';
        statusLabel.textContent = 'System Ready';
        indicator.className = 'status-indicator online';
    }
}

async function updateStatusMetrics() {
    try {
        const res = await fetch('/api/status');
        const data = await res.json();
        const stats = data.stats;

        document.getElementById('stat-target').textContent = stats.target_views || 0;
        document.getElementById('stat-progress').textContent = `${stats.completed_views || 0} completed`;
        document.getElementById('stat-verified').textContent = stats.successful_views || 0;

        const rate = stats.completed_views > 0 
            ? Math.round((stats.successful_views / stats.completed_views) * 100) 
            : 0;
        document.getElementById('stat-rate').textContent = `${rate}% success rate`;

        document.getElementById('stat-bandwidth').textContent = `${(stats.bandwidth_saved_mb || 0).toFixed(1)} MB`;
        document.getElementById('stat-state').textContent = (stats.status || 'IDLE').toUpperCase();
        document.getElementById('stat-timer').textContent = stats.start_time ? `Started at ${stats.start_time}` : 'Ready to launch';

        if (data.is_running !== isRunning) {
            setRunningState(data.is_running);
        }
    } catch (err) {
        // Ignore polling errors
    }
}

function startStatusPolling() {
    setInterval(updateStatusMetrics, 3000);
    updateStatusMetrics();
}
