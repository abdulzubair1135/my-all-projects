const { spawn, exec, execSync } = require('child_process');
const path = require('path');
const http = require('http');

console.log('====================================================================');
console.log('        AUTONOMOUS WEB-AGENT IDE - INITIALIZING ALL SERVICES');
console.log('====================================================================\n');

const isWindows = process.platform === 'win32';
const rootDir = __dirname;
const backendDir = path.join(rootDir, 'backend');
const frontendDir = path.join(rootDir, 'frontend');
const viteBin = path.join(frontendDir, 'node_modules', 'vite', 'bin', 'vite.js');

// 1. Free up ports 3001 & 5173 if previously held
if (isWindows) {
  try {
    execSync('powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 3001,5173 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"', { stdio: 'ignore' });
  } catch {}
}

// 2. Start Backend directly via Node (Zero npm / cmd.exe Unicode path issues)
console.log('[1/3] Starting Backend Controller on port 3001...');
const backendProc = spawn(process.execPath, [path.join(backendDir, 'src', 'server.js')], {
  cwd: backendDir,
  stdio: 'inherit',
  env: { ...process.env, FORCE_COLOR: '1' }
});

backendProc.on('error', (err) => {
  console.error('[Backend Error]:', err);
});

// 3. Start Frontend directly via Vite JS entrypoint
console.log('[2/3] Starting Frontend Dev Server on port 5173...');
const frontendProc = spawn(process.execPath, [viteBin, '--port', '5173', '--host'], {
  cwd: frontendDir,
  stdio: 'inherit',
  env: { ...process.env, FORCE_COLOR: '1' }
});

frontendProc.on('error', (err) => {
  console.error('[Frontend Error]:', err);
});

// 4. Wait for Frontend to be ready, then open browser
function openBrowser() {
  const url = 'http://localhost:5173';
  console.log(`\n[3/3] Launching browser at ${url}...`);
  console.log('====================================================================');
  console.log('          LIVE EXECUTION STREAM - WATCHING AGENT ACTIONS');
  console.log('====================================================================\n');
  if (isWindows) {
    exec(`start "" "${url}"`);
  } else if (process.platform === 'darwin') {
    exec(`open "${url}"`);
  } else {
    exec(`xdg-open "${url}"`);
  }
}

let attempts = 0;
const checkInterval = setInterval(() => {
  attempts++;
  http.get('http://localhost:5173', (res) => {
    clearInterval(checkInterval);
    openBrowser();
  }).on('error', () => {
    if (attempts > 30) {
      clearInterval(checkInterval);
      openBrowser();
    }
  });
}, 1000);

function cleanup() {
  console.log('\nShutting down Autonomous IDE...');
  try { backendProc.kill(); } catch {}
  try { frontendProc.kill(); } catch {}
  process.exit(0);
}

process.on('SIGINT', cleanup);
process.on('SIGTERM', cleanup);
