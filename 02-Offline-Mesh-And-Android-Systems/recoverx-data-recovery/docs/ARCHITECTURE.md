# RecoverX — System Architecture

## Architecture Pattern
RecoverX implements the recommended Android Architecture guidelines: **Clean Architecture + Unidirectional Data Flow (UDF) + MVVM**.

```
+--------------------------------------------------------------+
|                        UI Layer                              |
|   Jetpack Compose + Material 3 + Navigation Destinations     |
|   (ViewModels emitting StateFlow, receiving User Intents)   |
+--------------------------------------------------------------+
                               |
                               v
+--------------------------------------------------------------+
|                       Domain Layer                           |
|   UseCases: ScanFilesUseCase, ClassifyFileUseCase,           |
|   RestoreCandidateUseCase, DetectDuplicatesUseCase           |
+--------------------------------------------------------------+
                               |
                               v
+--------------------------------------------------------------+
|                        Data Layer                            |
|   Repositories: StorageRepository, RecoveryRepository,       |
|                 HistoryRepository, SettingsRepository        |
|                                                              |
|   Data Sources:                                              |
|   - MediaStoreSource (Android ContentResolver)               |
|   - SAFDocumentSource (DocumentFile / Tree API)              |
|   - BinarySignatureSource (Header/Footer stream parser)      |
|   - RoomDatabase (Local metadata, sessions, recovery logs)  |
+--------------------------------------------------------------+
```

## Core Modules & Packages (`com.recoverx`)
- `com.recoverx.app`: Application class, initialization, dependency provider.
- `com.recoverx.core.permissions`: PermissionCoordinator handling Android 7 through 16 storage permissions.
- `com.recoverx.core.storage`: Volume inspector, SAF helpers, ContentResolver streamers.
- `com.recoverx.core.errors`: Unified AppError and Diagnostics reporting.
- `com.recoverx.data.database`: Room Database, DAOs (`ScanSessionDao`, `DiscoveredItemDao`, `RecoveryRecordDao`, `ScanErrorDao`).
- `com.recoverx.data.entities`: Persistent entity data classes.
- `com.recoverx.scanner`: ScanCoordinator, QuickScanEngine, DeepScanEngine.
- `com.recoverx.discovery`: Discovery sources (Media, Folder, Trash, AlternateCopy, Thumbnail, Signature).
- `com.recoverx.recovery`: RecoveryManager, StreamingRestorer, CollisionResolver, IntegrityValidator.
- `com.recoverx.preview`: Media preview coordinators for Images (Coil) and Videos (Media3 ExoPlayer).
- `com.recoverx.navigation`: App navigation graph, destination routes, argument passing.
- `com.recoverx.ui`: Compose screens, components, theme, typography, dialogs, bottom sheets.
