const { execSync, exec, spawn } = require('child_process');
const fs = require('fs');

class DockerService {
  constructor() {
    this.isStartingDaemon = false;
  }

  /**
   * Check if Docker CLI is installed and if the daemon is currently running.
   */
  getStatus() {
    let installed = false;
    let version = null;
    let daemonRunning = false;
    let desktopExePath = this.getDockerDesktopExePath();

    try {
      const verOutput = execSync('docker --version', { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'ignore'] });
      installed = true;
      version = verOutput.trim();
    } catch {
      installed = false;
    }

    if (installed) {
      try {
        execSync('docker ps', { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'ignore'], timeout: 3000 });
        daemonRunning = true;
      } catch {
        daemonRunning = false;
      }
    }

    return { 
      installed, 
      version, 
      daemonRunning, 
      desktopInstalled: !!desktopExePath, 
      desktopPath: desktopExePath,
      isStarting: this.isStartingDaemon
    };
  }

  /**
   * Find Docker Desktop executable path on Windows.
   */
  getDockerDesktopExePath() {
    const candidatePaths = [
      'C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe',
      'C:\\Program Files (x86)\\Docker\\Docker\\Docker Desktop.exe',
      process.env.LOCALAPPDATA ? `${process.env.LOCALAPPDATA}\\Programs\\Docker\\Docker\\Docker Desktop.exe` : null
    ].filter(Boolean);

    for (const p of candidatePaths) {
      if (fs.existsSync(p)) {
        return p;
      }
    }
    return null;
  }

  /**
   * Automatically launch Docker Desktop and wait until the daemon is active.
   */
  async startDockerDesktop(timeoutMs = 45000) {
    const desktopPath = this.getDockerDesktopExePath();
    if (!desktopPath) {
      return { success: false, reason: 'Docker Desktop executable not found on this computer.' };
    }

    if (this.getStatus().daemonRunning) {
      return { success: true, message: 'Docker daemon is already active.' };
    }

    this.isStartingDaemon = true;
    console.log(`[DockerService] Launching Docker Desktop from ${desktopPath}...`);

    // Launch Docker Desktop in background
    exec(`start "" "${desktopPath}"`, (err) => {
      if (err) {
        console.error('[DockerService] Error launching Docker Desktop:', err);
      }
    });

    // Poll until daemon is responsive
    const startTime = Date.now();
    while (Date.now() - startTime < timeoutMs) {
      await new Promise(res => setTimeout(res, 2500));
      try {
        execSync('docker ps', { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'ignore'], timeout: 3000 });
        this.isStartingDaemon = false;
        console.log('[DockerService] Docker daemon successfully activated!');
        return { success: true, message: 'Docker Desktop launched and daemon is active.' };
      } catch {
        // Still initializing
      }
    }

    this.isStartingDaemon = false;
    return { success: false, reason: `Docker Desktop launch timed out after ${timeoutMs / 1000}s. Falling back to embedded DB.` };
  }

  /**
   * Automatically spin up or start a database container (e.g. 'mongodb', 'postgres', 'redis').
   * If Docker is off, it launches Docker Desktop automatically!
   */
  async ensureDatabaseContainer(type = 'mongodb', port = 27017) {
    let status = this.getStatus();
    if (!status.installed) {
      return {
        success: false,
        reason: 'Docker is not installed on this machine. Using embedded zero-config database fallback.',
        mode: 'fallback'
      };
    }

    // If daemon is not running, autonomously launch Docker Desktop!
    if (!status.daemonRunning) {
      console.log('[DockerService] Daemon not running. Auto-launching Docker Desktop...');
      const launchResult = await this.startDockerDesktop(35000);
      status = this.getStatus();
      if (!status.daemonRunning) {
        return {
          success: false,
          reason: launchResult.reason || 'Docker Desktop could not finish starting in time. Using embedded database fallback.',
          mode: 'fallback'
        };
      }
    }

    const containerName = `auto-${type}`;
    const image = type === 'mongodb' ? 'mongo:latest' : type === 'postgres' ? 'postgres:alpine' : 'redis:alpine';

    return new Promise((resolve) => {
      exec(`docker ps -a --filter "name=^/${containerName}$" --format "{{.Names}}"`, (err, stdout) => {
        const exists = stdout && stdout.trim() === containerName;

        if (exists) {
          exec(`docker ps --filter "name=^/${containerName}$" --format "{{.Names}}"`, (err2, stdout2) => {
            if (stdout2 && stdout2.trim() === containerName) {
              return resolve({
                success: true,
                message: `Container ${containerName} is already running on port ${port}`,
                uri: type === 'mongodb' ? `mongodb://localhost:${port}` : `localhost:${port}`,
                containerName,
                mode: 'docker'
              });
            } else {
              exec(`docker start ${containerName}`, (err3) => {
                if (err3) {
                  return resolve({ success: false, reason: err3.message, mode: 'fallback' });
                }
                return resolve({
                  success: true,
                  message: `Started existing container ${containerName} on port ${port}`,
                  uri: type === 'mongodb' ? `mongodb://localhost:${port}` : `localhost:${port}`,
                  containerName,
                  mode: 'docker'
                });
              });
            }
          });
        } else {
          const runCmd = `docker run -d -p ${port}:${port} --name ${containerName} ${image}`;
          exec(runCmd, (errRun) => {
            if (errRun) {
              return resolve({ success: false, reason: errRun.message, mode: 'fallback' });
            }
            return resolve({
              success: true,
              message: `Created and started ${containerName} from ${image} on port ${port}`,
              uri: type === 'mongodb' ? `mongodb://localhost:${port}` : `localhost:${port}`,
              containerName,
              mode: 'docker'
            });
          });
        }
      });
    });
  }
}

module.exports = new DockerService();
