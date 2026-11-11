# RecoverX — Architectural Decision Records (ADR)

## ADR 01: Language & Toolkit Selection
- **Decision**: Kotlin + Jetpack Compose with Material 3.
- **Rationale**: Declarative UI, state management via StateFlow, seamless integration with Modern Android development standards.

## ADR 02: Persistence Layer
- **Decision**: Room Database (SQLite).
- **Rationale**: Strongly typed, compile-time verified SQL queries, Flow observation, structured migration capabilities.

## ADR 03: Media Playback
- **Decision**: AndroidX Media3 ExoPlayer.
- **Rationale**: Google's modern standard for Android media playback replacing legacy MediaPlayer/standalone ExoPlayer.

## ADR 04: Storage Framework Integration
- **Decision**: Hybrid MediaStore + Storage Access Framework (SAF).
- **Rationale**: Complies with Android 10-16 Scoped Storage mandates while empowering users to select specific custom folders or SD cards.
