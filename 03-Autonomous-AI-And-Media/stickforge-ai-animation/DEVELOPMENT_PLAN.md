# StickForge AI — Development Plan & Roadmap

This development plan breaks down the mission into 11 well-defined, executable phases. Each phase concludes with unit/integration testing and verification against explicit acceptance criteria before marking complete.

---

## Phase Matrix

| Phase | Title | Scope & Deliverables | Status |
|---|---|---|---|
| **Phase 1** | Audit & Core Foundation | Base directories, SQLite schema & migrations, config, event bus, task queue, logging, PySide6 main shell, bootstrap pre-flight checks. | IN PROGRESS |
| **Phase 2** | Visible Chromium & DeepSeek | Dedicated persistent user profile, visible Playwright browser controller, session detection, guided login, prompt submission, automated `Continue` handler with duplicate-click protection. | QUEUED |
| **Phase 3** | AI Script & Story Engine | Provider-independent AI interface (DeepSeek browser & API adapter), structured prompt templates, Hindi/English/Hinglish script generator, schema validation, versioning. | QUEUED |
| **Phase 4** | Storyboard & Timing Engine | Scene decomposition, action mapping, camera specs, audio duration computation, timeline continuity validator. | QUEUED |
| **Phase 5** | 2D Stickman Skeletal Engine | 14-joint skeletal model, procedural keyframing, motion library (walk, run, jump, fall, sit, wave, fight), camera pan/zoom, deterministic frame rendering. | QUEUED |
| **Phase 6** | Voice, Audio & Subtitles | Edge TTS & pyttsx3 providers, voice profiles, duration calculator, SRT generator, multi-track audio mixing with music ducking. | QUEUED |
| **Phase 7** | Video Compositing & Export | Subprocess FFmpeg pipeline, export profiles (Shorts 9:16, Reels, Landscape 16:9), progress tracking, stream verification & quality checker. | QUEUED |
| **Phase 8** | Full Desktop UI & Editor | Dashboard, Project Wizard, Story Studio, Storyboard Editor, Character Studio, Animation Editor, Voice Studio, Timeline, Video Preview, Settings, Diagnostics. | QUEUED |
| **Phase 9** | Publishing Hub (YouTube/IG) | Official OAuth YouTube Data API v3 & Instagram Graph API publishers, upload progress, metadata manager, mock-verified test harness. | QUEUED |
| **Phase 10** | Scheduler & Smart Repurposing | Background cron scheduler, Shorts/Reels aspect-ratio adaptation, hook variations, retry policies. | QUEUED |
| **Phase 11** | Packaging, Verification & Release | PyInstaller spec, `launch_setup.bat`, `launch_app.bat`, complete test suite execution, E2E acceptance validation. | QUEUED |
