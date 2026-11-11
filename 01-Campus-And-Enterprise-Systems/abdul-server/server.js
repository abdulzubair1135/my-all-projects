const http = require('http');
const url = require('url');

const PORT = 80;
const messages = [
    { sender: 'System', text: 'Welcome to the decentralised offline mesh portal!' }
];

const renderPage = () => `
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Abdul Dream Mesh Node</title>
  <style>
    body { font-family: system-ui, sans-serif; background: #0d1117; color: #c9d1d9; padding: 20px; text-align: center; }
    .card { background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 24px; max-width: 520px; margin: 20px auto; box-shadow: 0 10px 30px rgba(0,0,0,0.6); }
    h1 { color: #58a6ff; font-size: 24px; margin-bottom: 6px; }
    .badge { background: #238636; color: #fff; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: bold; }
    p { color: #8b949e; line-height: 1.5; font-size: 14px; }
    .chat-box { background: #0d1117; border: 1px solid #30363d; border-radius: 8px; padding: 12px; text-align: left; max-height: 180px; overflow-y: auto; margin: 16px 0; }
    .msg { font-size: 13px; margin-bottom: 8px; border-bottom: 1px solid #21262d; padding-bottom: 4px; }
    .msg strong { color: #58a6ff; }
    form { display: flex; gap: 8px; margin-top: 10px; }
    input[type='text'] { flex: 1; padding: 10px; border-radius: 6px; border: 1px solid #30363d; background: #21262d; color: white; outline: none; }
    button { background: #238636; color: white; border: none; padding: 10px 16px; border-radius: 6px; cursor: pointer; font-weight: bold; }
    .footer { margin-top: 24px; font-size: 11px; color: #484f58; }
  </style>
</head>
<body>
  <div class="card">
    <span class="badge">OFFLINE LOCAL SERVER</span>
    <h1>www.abdul.dream</h1>
    <p>Decentralized Mesh Gateway hosted live from Abdul's Laptop.</p>

    <div class="chat-box">
      ${messages.map(m => `<div class="msg"><strong>${m.sender}:</strong> ${m.text}</div>`).join('')}
    </div>

    <form method="GET" action="/send">
      <input type="text" name="msg" placeholder="Drop a note on this node..." required />
      <button type="submit">Post</button>
    </form>
  </div>
  <div class="footer">NearMesh System Node • Active Loop</div>
</body>
</html>
`;

const server = http.createServer((req, res) => {
    const parsedUrl = url.parse(req.url, true);

    if (parsedUrl.pathname === '/send') {
        const text = parsedUrl.query.msg;
        if (text) {
            messages.push({ sender: 'Guest Node', text: text });
        }
        res.writeHead(302, { Location: '/' });
        res.end();
        return;
    }

    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end(renderPage());
});

server.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running on port ${PORT}`);
});