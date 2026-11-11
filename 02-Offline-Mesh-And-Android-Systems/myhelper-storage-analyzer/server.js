const express = require('express');
const fs = require('fs');
const app = express();

app.use(express.json());
const LOG_FILE = 'phone_logs.json';

app.post('/api/log', (req, res) => {
    const apiKey = req.headers['x-api-key'] || '';
    const data = req.body || {};

    const device = data.device || 'Unknown Device';
    const logType = data.type || 'GENERAL';
    const content = data.content || '';
    const timestamp = data.timestamp || new Date().toISOString();

    console.log('\n==================================================');
    console.log('📩 [NEW LIVE LOG RECEIVED FROM PHONE]');
    console.log(`🕒 Time:      ${timestamp}`);
    console.log(`📱 Device:    ${device}`);
    console.log(`🏷️ Type:      ${logType}`);
    console.log(`💬 Content:   ${content}`);
    console.log('==================================================');

    const logEntry = { timestamp, device, type: logType, content, apiKey };

    let logs = [];
    if (fs.existsSync(LOG_FILE)) {
        try {
            logs = JSON.parse(fs.readFileSync(LOG_FILE, 'utf8'));
        } catch (e) {
            logs = [];
        }
    }

    logs.unshift(logEntry);
    fs.writeFileSync(LOG_FILE, JSON.stringify(logs, null, 2));

    res.json({ status: 'success', message: 'Log received on Localhost!' });
});

app.listen(5000, () => {
    console.log('🚀 Cloudflare Tunnel Localhost Receiver running on http://localhost:5000');
    console.log('👉 Expose it via Cloudflare: cloudflared tunnel --url http://localhost:5000\n');
});
