# RecoverX — Testing Strategy

## Test Levels
1. **Unit Testing (JUnit 4 + MockK/Coroutines Test)**:
   - File signature recognition (`SignatureRegistryTest`).
   - Extension & MIME categorization (`FileCategorizerTest`).
   - Destination collision resolution (`CollisionResolverTest`).
   - Integrity validation (`IntegrityValidatorTest`).
   - Duplicate detection hashing logic (`DuplicateDetectorTest`).
   - Room DAO operations with in-memory SQLite database.
2. **Integration Testing**:
   - ContentResolver query adapters against Android MediaStore.
   - Storage Access Framework (SAF) tree parsing.
   - Streaming restorer buffer and cancellation tests.
3. **Physical Device Validation**:
   - Continuous verification on attached physical device (Android 15, API 35).
   - Real permission grants, MediaStore scans, file restoration to actual device storage.
