import { JwtUtil, JwtPayload } from '../src/security/jwt.util';
import { UserRole } from '../src/constants/enums';

describe('Phase 1: JWT & RBAC Protocol Tests', () => {
  const samplePayload: JwtPayload = {
    sub: '507f1f77bcf86cd799439011',
    role: UserRole.FACULTY,
    email: 'arjun@campus.edu',
    departmentId: '507f1f77bcf86cd799439012',
    deviceId: 'dev_iphone_15'
  };

  it('should generate valid access and refresh JWTs and verify payload integrity', () => {
    const accessToken = JwtUtil.generateAccessToken(samplePayload);
    const refreshToken = JwtUtil.generateRefreshToken(samplePayload);

    expect(accessToken).toBeDefined();
    expect(refreshToken).toBeDefined();

    const decodedAccess = JwtUtil.verifyAccessToken(accessToken);
    expect(decodedAccess.sub).toBe(samplePayload.sub);
    expect(decodedAccess.role).toBe(UserRole.FACULTY);
    expect(decodedAccess.email).toBe(samplePayload.email);

    const decodedRefresh = JwtUtil.verifyRefreshToken(refreshToken);
    expect(decodedRefresh.sub).toBe(samplePayload.sub);
  });

  it('should reject invalid or tampered tokens', () => {
    const accessToken = JwtUtil.generateAccessToken(samplePayload);
    const tamperedToken = accessToken.slice(0, -5) + 'abcde';

    expect(() => {
      JwtUtil.verifyAccessToken(tamperedToken);
    }).toThrow();
  });
});
