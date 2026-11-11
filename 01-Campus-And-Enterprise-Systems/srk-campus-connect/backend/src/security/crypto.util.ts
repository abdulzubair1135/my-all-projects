import nacl from 'tweetnacl';
import naclUtil from 'tweetnacl-util';
import crypto from 'crypto';
import { envConfig } from '../config/env.config';

export class CryptoUtil {
  /**
   * Generates a new Ed25519 keypair encoded in Base64
   */
  static generateEd25519KeyPair(): { publicKey: string; secretKey: string } {
    const keyPair = nacl.sign.keyPair();
    return {
      publicKey: naclUtil.encodeBase64(keyPair.publicKey),
      secretKey: naclUtil.encodeBase64(keyPair.secretKey)
    };
  }

  /**
   * Signs a string message with an Ed25519 secret key (Base64)
   */
  static signMessage(message: string, secretKeyBase64: string): string {
    const messageBytes = naclUtil.decodeUTF8(message);
    const secretKeyBytes = naclUtil.decodeBase64(secretKeyBase64);
    const signature = nacl.sign.detached(messageBytes, secretKeyBytes);
    return naclUtil.encodeBase64(signature);
  }

  /**
   * Verifies an Ed25519 detached signature given message, signatureBase64, and publicKeyBase64
   */
  static verifySignature(message: string, signatureBase64: string, publicKeyBase64: string): boolean {
    try {
      const messageBytes = naclUtil.decodeUTF8(message);
      const signatureBytes = naclUtil.decodeBase64(signatureBase64);
      const publicKeyBytes = naclUtil.decodeBase64(publicKeyBase64);
      return nacl.sign.detached.verify(messageBytes, signatureBytes, publicKeyBytes);
    } catch (error) {
      return false;
    }
  }

  /**
   * Generates a dynamic rolling QR token for a class session
   * Format: CAMPUS_SESSION_V1:{sessionId}:{nonce}:{timestamp}:{hmacSignature}
   */
  static generateDynamicSessionQr(sessionId: string): { qrString: string; nonce: string; timestamp: number; expiresAt: Date } {
    const nonce = crypto.randomBytes(12).toString('hex');
    const timestamp = Date.now();
    const expiresAt = new Date(timestamp + envConfig.qrNonceTtlSeconds * 1000);
    
    const messageToSign = `${sessionId}:${nonce}:${timestamp}`;
    const hmac = crypto
      .createHmac('sha256', envConfig.qrHmacSecret)
      .update(messageToSign)
      .digest('hex');
      
    const qrString = `CAMPUS_SESSION_V1:${sessionId}:${nonce}:${timestamp}:${hmac}`;
    return { qrString, nonce, timestamp, expiresAt };
  }

  /**
   * Validates a dynamic rolling QR string
   */
  static validateDynamicSessionQr(qrString: string, allowedDriftSeconds = 60): { isValid: boolean; sessionId?: string; nonce?: string; timestamp?: number; error?: string } {
    try {
      const parts = qrString.split(':');
      if (parts.length !== 5 || parts[0] !== 'CAMPUS_SESSION_V1') {
        return { isValid: false, error: 'Invalid QR format' };
      }

      const [, sessionId, nonce, timestampStr, signature] = parts;
      const timestamp = parseInt(timestampStr, 10);
      if (isNaN(timestamp)) {
        return { isValid: false, error: 'Invalid timestamp in QR' };
      }

      // Check time expiry window
      const now = Date.now();
      const ageSeconds = (now - timestamp) / 1000;
      if (ageSeconds < -10 || ageSeconds > (envConfig.qrNonceTtlSeconds + allowedDriftSeconds)) {
        return { isValid: false, error: 'QR Code has expired' };
      }

      // Verify HMAC
      const messageToSign = `${sessionId}:${nonce}:${timestampStr}`;
      const expectedHmac = crypto
        .createHmac('sha256', envConfig.qrHmacSecret)
        .update(messageToSign)
        .digest('hex');

      if (expectedHmac !== signature) {
        return { isValid: false, error: 'Cryptographic signature mismatch in QR' };
      }

      return { isValid: true, sessionId, nonce, timestamp };
    } catch (err: any) {
      return { isValid: false, error: err.message || 'QR validation failure' };
    }
  }
}
