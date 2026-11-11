import { PresenceEngine } from '../src/services/presence.engine';
import { PresenceState, MovementState } from '../src/constants/enums';

describe('Phase 8: Presence Confidence Engine & Privacy Tests', () => {
  it('should compute 100% confidence for full corroborating evidence', () => {
    const result = PresenceEngine.calculateConfidence({
      hasValidDynamicQr: true,      // 30
      hasTeacherScan: true,         // 25
      isTimetableEnrolled: true,    // 15
      dwellPingsCount: 6,           // 15 (60 mins class -> 6 pings)
      totalSessionMinutes: 60,
      peerProximityCount: 3,        // 10
      movementState: MovementState.STATIONARY // 5
    });

    expect(result.confidenceScore).toBe(100);
    expect(result.presenceState).toBe(PresenceState.HIGH_CONFIDENCE);
    expect(result.stateLabel).toBe('Present in scheduled classroom');
  });

  it('should compute partial confidence and appropriate non-accusatory states', () => {
    // Only dynamic QR + Timetable (30 + 15 = 45 -> UNCERTAIN)
    const uncertainResult = PresenceEngine.calculateConfidence({
      hasValidDynamicQr: true,
      hasTeacherScan: false,
      isTimetableEnrolled: true,
      dwellPingsCount: 0,
      totalSessionMinutes: 60,
      peerProximityCount: 0
    });

    expect(uncertainResult.confidenceScore).toBe(45);
    expect(uncertainResult.presenceState).toBe(PresenceState.UNCERTAIN);
    expect(uncertainResult.stateLabel).toBe('Presence could not be definitively verified');

    // No signals (< 20 -> NOT_DETECTED, strictly non-accusatory)
    const notDetectedResult = PresenceEngine.calculateConfidence({
      hasValidDynamicQr: false,
      hasTeacherScan: false,
      isTimetableEnrolled: false,
      dwellPingsCount: 0,
      totalSessionMinutes: 60,
      peerProximityCount: 0
    });

    expect(notDetectedResult.confidenceScore).toBe(0);
    expect(notDetectedResult.presenceState).toBe(PresenceState.NOT_DETECTED);
    expect(notDetectedResult.stateLabel).toBe('Not detected in scheduled classroom');
    expect(notDetectedResult.stateLabel).not.toContain('bunking');
  });

  it('should flag schedule mismatch without accusatory accusations', () => {
    const mismatch = PresenceEngine.checkScheduleMismatch('204', '305', 88);

    expect(mismatch.isMismatch).toBe(true);
    expect(mismatch.alert).toContain('Expected in Room 204, presence detected in Room 305 (88% confidence)');
    expect(mismatch.alert).not.toContain('misconduct');
  });
});
