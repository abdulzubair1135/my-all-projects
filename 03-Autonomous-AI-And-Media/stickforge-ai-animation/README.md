# StickForge AI 🎬🤖

**AI-Powered Stickman Animation, Video Creation, Editing, and Social Media Publishing Studio**

StickForge AI is a desktop application for Windows that transforms ideas and scripts into complete animated stickman videos ready for YouTube Shorts, Instagram Reels, and standard video formats.

---

## Key Features

1. **AI Story & Script Studio**: Story creation supporting Hindi, English, and Hinglish with customizable tone, duration, characters, and genre.
2. **Visible DeepSeek Browser Adapter**: Controlled Chromium automation with dedicated persistent profile, manual login, session detection, and guarded automatic Continue handling.
3. **Deterministic Stickman Animation Engine**: Skeletal 2D stickman animation engine with kinematic joints, procedural motion primitives (walk, run, jump, fall, sit, wave, fight, emotes), camera controls, and scene transitions.
4. **Voice & Audio Pipeline**: Provider-independent TTS architecture supporting Edge TTS (online) and PyTTSx3 (offline local), audio mixing with music ducking, and synchronized subtitles (.srt and burned-in).
5. **Compositing & Video Export**: Subprocess-isolated FFmpeg rendering with real-time progress tracking, probe inspection, and export presets (YouTube Shorts 1080x1920, Reels, Landscape 1920x1080).
6. **Timeline & Multi-Track Studio**: Interactive visual timeline with scene cards, animation tracks, narration clips, audio effects, and live scene preview.
7. **Social Media Publishing Hub**: Secure OAuth-based YouTube Data API v3 and Instagram Graph API publishing adapters with scheduling, metadata generation, and simulated verification testing.
8. **Checkpointed Persistent Job System**: SQLite-backed state machine for long-running AI generation, rendering, and publishing tasks with resume capability.

---

## Quick Start (Windows)

### 1. Environment Setup
Run the automated environment setup script:
```cmd
launch_setup.bat
```
This script will:
* Verify Python 3.10+
* Verify or configure virtual environment
* Install dependencies from `requirements.txt`
* Verify Playwright Chromium browser binary
* Verify FFmpeg and FFprobe
* Initialize the SQLite application database
* Create initial asset and template directories

### 2. Launch the Application
```cmd
launch_app.bat
```

---

## Documentation
* [Architecture Guide](ARCHITECTURE.md)
* [Development Plan](DEVELOPMENT_PLAN.md)
* [Implementation Status](IMPLEMENTATION_STATUS.md)
* [Testing Guide](TESTING.md)
* [Troubleshooting](TROUBLESHOOTING.md)
* [Security & Privacy](SECURITY.md)
* [Third-Party Licenses](THIRD_PARTY_LICENSES.md)
