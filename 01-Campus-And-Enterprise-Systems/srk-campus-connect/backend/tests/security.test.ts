import { CryptoUtil } from '../src/security/crypto.util';

describe('Phase 1: Cryptographic Utilities & QR Protocol Tests', () => {
  it('should generate a valid Ed25519 keypair, sign a presence event payload, and verify signature', () => {
    const keyPair = CryptoUtil.generateEd25519KeyPair();
    expect(keyPair.publicKey).toBeDefined();
    expect(keyPair.secretKey).toBeDefined();

    const sampleEventPayload = JSON.stringify({
      eventId: 'evt-12345',
      userId: 'usr-9876',
      sessionId: 'sess-abc',
      timestamp: 1725244800000,
      source: 'DYNAMIC_QR'
    });

    const signature = CryptoUtil.signMessage(sampleEventPayload, keyPair.secretKey);
    expect(signature).toBeDefined();

    const isValid = CryptoUtil.verifySignature(sampleEventPayload, signature, keyPair.publicKey);
    expect(isValid).toBe(true);

    // Tampering test
    const tamperedPayload = sampleEventPayload.replace('usr-9876', 'usr-hacker');
    const isTamperedValid = CryptoUtil.verifySignature(tamperedPayload, signature, keyPair.publicKey);
    expect(isTamperedValid).toBe(false);
  });

  it('should generate and validate dynamic rolling session QR codes with HMAC', () => {
    const sessionId = 'DBMS-204-20260902-1000';
    const qrData = CryptoUtil.generateDynamicSessionQr(sessionId);

    expect(qrData.qrString).toContain('CAMPUS_SESSION_V1:DBMS-204-20260902-1000:');
    expect(qrData.nonce).toBeDefined();
    expect(qrData.expiresAt.getTime()).toBeGreaterThan(Date.now());

    // Validate QR
    const validationResult = CryptoUtil.validateDynamicSessionQr(qrData.qrString);
    expect(validationResult.isValid).toBe(true);
    expect(validationResult.sessionId).toBe(sessionId);
    expect(validationResult.nonce).toBe(qrData.nonce);

    // Tampering test on QR signature
    const tamperedQr = qrData.qrString.slice(0, -4) + 'ffff';
    const tamperedResult = CryptoUtil.validateDynamicSessionQr(tamperedQr);
    expect(tamperedResult.isValid).toBe(false);
  });
});
