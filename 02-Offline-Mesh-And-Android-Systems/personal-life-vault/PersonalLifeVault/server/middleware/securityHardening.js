const logger = require('../utils/logger');

// In-memory IP Ban Store (IP -> failed count & ban timestamp)
const failedAttemptsMap = new Map();
const bannedIPsSet = new Set();

/**
 * 10-Layer Security Hardening Middleware
 */
function securityHardening(req, res, next) {
  const clientIP = req.ip || req.socket.remoteAddress || 'unknown';

  // 1. IP Ban Enforcement Check (Expires after 15 minutes)
  if (bannedIPsSet.has(clientIP)) {
    const banTime = failedAttemptsMap.get(clientIP)?.bannedAt || 0;
    if (Date.now() - banTime < 15 * 60 * 1000) {
      logger.warn('SECURITY', `Blocked request from banned IP: ${clientIP}`);
      return res.status(403).json({
        success: false,
        error: 'Access Denied: Your IP has been temporarily flagged and blocked due to multiple suspicious attempts. Please wait 15 minutes.'
      });
    } else {
      bannedIPsSet.delete(clientIP);
      failedAttemptsMap.delete(clientIP);
    }
  }

  // 2. Malicious Bot & Vulnerability Scanner Blocking
  const userAgent = (req.headers['user-agent'] || '').toLowerCase();
  const suspiciousBots = ['nmap', 'sqlmap', 'nikto', 'dirbuster', 'gobuster', 'wpscan', 'masscan', 'zgrab', 'python-requests'];
  if (suspiciousBots.some(bot => userAgent.includes(bot))) {
    logger.warn('SECURITY', `Blocked malicious scanner/bot attempt from ${clientIP} (UA: ${userAgent})`);
    return res.status(403).json({ success: false, error: 'Forbidden: Automated security scanner detected' });
  }

  // 3. Security Response Headers
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-XSS-Protection', '1; mode=block');
  res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains; preload');
  res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');

  next();
}

/**
 * Records a failed security/auth attempt for an IP address.
 * Automatically bans the IP if failures exceed 10 within 10 minutes.
 */
function recordFailedAttempt(ip) {
  if (!ip) return;
  const now = Date.now();
  const record = failedAttemptsMap.get(ip) || { count: 0, firstAttempt: now };

  // Reset if window expired (10 minutes)
  if (now - record.firstAttempt > 600000) {
    record.count = 1;
    record.firstAttempt = now;
  } else {
    record.count += 1;
  }

  failedAttemptsMap.set(ip, record);

  if (record.count >= 25) {
    record.bannedAt = now;
    bannedIPsSet.add(ip);
    logger.error('SECURITY', `🚨 SECURITY ALERT: IP ${ip} temporarily banned after ${record.count} failed attempts!`);
  }
}

module.exports = {
  securityHardening,
  recordFailedAttempt
};
