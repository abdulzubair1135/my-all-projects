# StickForge AI — Architecture Specification

## Overview

StickForge AI is an integrated desktop studio built on PySide6 and Python 3.10+, designed to run on Windows with local CPU/GPU acceleration. It implements a layered, decoupled architecture with strong separation of concerns.

```
+-------------------------------------------------------------------+
|                        PySide6 Desktop UI                         |
| (Dashboard, Wizard, StoryStudio, Storyboard, Timeline, Publishing)|
+---------------------------------+---------------------------------+
                                  | Event Bus / Qt Signals
+---------------------------------v---------------------------------+
|                           Core Services                           |
|  - TaskManager (State Machine)   - ConfigManager                  |
|  - CheckpointManager             - Logging & Diagnostics          |
|  - Database (SQLite)             - Resource & Cache Manager       |
+------------------+------------------------------+-----------------+
                   |                              |
+------------------v--------------+ +-------------v-----------------+
|       AI & Browser Layer        | |      Multimedia Pipeline      |
| - AIProvider (DeepSeek / API)   | | - Stickman Skeletal Engine    |
| - BrowserManager (Playwright)   | | - TTSManager (Edge/Pyttsx3)   |
| - PageStateDetector             | | - AudioMixer & Subtitles      |
| - LongResponseManager (Continue)| | - FFmpeg Compositor           |
+---------------------------------+ +-------------------------------+
                                                  |
                                    +-------------v-----------------+
                                    |     Publishing & Scheduler    |
                                    | - YouTube Data API v3         |
                                    | - Instagram Graph API         |
                                    | - Background Job Scheduler    |
                                    +-------------------------------+
```

---

## 1. Directory Structure

```
StickForgeAI/
├── app/
│   ├── main.py                     # Entry point
│   ├── bootstrap.py                # Environment initialization & pre-flight checks
│   ├── core/                       # Core engine services
│   │   ├── config.py               # Application configuration
│   │   ├── event_bus.py            # Global publish-subscribe event bus
│   │   ├── task_manager.py         # Persistent task queue & state machine
│   │   ├── checkpoint_manager.py   # Job checkpoint recovery
│   │   ├── logging_manager.py      # Structured file & UI logging with redaction
│   │   └── resource_manager.py     # Memory & disk cache governance
│   ├── ui/                         # PySide6 desktop views & components
│   │   ├── main_window.py          # Shell container with navigation bar
│   │   ├── dashboard.py            # Recent projects, status overview
│   │   ├── project_wizard.py       # New project configuration modal
│   │   ├── story_studio.py         # Script generation & editing
│   │   ├── storyboard_editor.py    # Timed scenes, actions, backgrounds
│   │   ├── character_studio.py     # Stickman customization & pose tester
│   │   ├── animation_editor.py     # Skeletal preview & motion parameters
│   │   ├── voice_studio.py         # TTS voice preview & speech generator
│   │   ├── timeline_editor.py      # Multi-track audio/video visual timeline
│   │   ├── video_preview.py        # Real-time player / frame scrubber
│   │   ├── publishing_hub.py       # YouTube & Instagram integration
│   │   ├── render_queue.py         # Active rendering jobs & export progress
│   │   ├── diagnostics.py          # System health, browser logs & debugging
│   │   └── settings.py             # User preferences & API credentials
│   ├── ai/                         # AI generation & browser coordination
│   │   ├── ai_provider.py          # Unified AI interface
│   │   ├── deepseek_controller.py  # Playwright browser automation for DeepSeek
│   │   ├── deepseek_api_adapter.py # Direct API client for supported endpoints
│   │   ├── long_response_manager.py# Automatic Continue handling & assembly
│   │   ├── prompt_templates.py     # Structured story & storyboard prompts
│   │   ├── schema_validator.py     # Output JSON validation against schemas
│   │   └── output_parser.py        # Robust recovery of fragmented JSON
│   ├── browser/                    # Playwright browser session management
│   │   ├── browser_manager.py      # Visible persistent Chromium controller
│   │   ├── page_state_detector.py  # Detects generating, continue, login, error
│   │   └── browser_diagnostics.py  # Screenshot capture & session inspection
│   ├── story/                      # Story & storyboard generation logic
│   │   ├── script_generator.py     # High-level story creator
│   │   ├── storyboard_generator.py # Script-to-scenes decomposition
│   │   └── continuity_checker.py   # Timing & character continuity validator
│   ├── animation/                  # Deterministic 2D stickman engine
│   │   ├── character.py            # Stickman character model & attributes
│   │   ├── skeleton.py             # Kinematic joint hierarchy
│   │   ├── pose.py                 # Keyframe poses (stand, sit, run, etc.)
│   │   ├── motion_library.py       # Procedural movement interpolators
│   │   ├── action_registry.py      # Registry of supported animation actions
│   │   ├── camera.py               # Deterministic 2D virtual camera
│   │   ├── background_renderer.py  # Procedural & image background renderer
│   │   └── scene_renderer.py       # Frame-by-frame scene rasterizer
│   ├── audio/                      # Speech synthesis & audio processing
│   │   ├── tts_provider.py         # Abstract TTS provider
│   │   ├── edge_tts_provider.py    # Edge TTS (multilingual, natural voices)
│   │   ├── pyttsx3_provider.py     # Offline fallback TTS engine
│   │   ├── tts_manager.py          # Voice selection, synthesis & caching
│   │   ├── subtitle_generator.py   # Synchronized SRT & text segmenter
│   │   └── audio_mixer.py          # FFmpeg multi-track mixer with ducking
│   ├── video/                      # Video rendering & validation
│   │   ├── ffmpeg_manager.py       # Safe subprocess FFmpeg/probe wrapper
│   │   ├── compositor.py           # Frame assembly & audio binding
│   │   ├── thumbnail_generator.py  # Cover art & title card generator
│   │   └── quality_checker.py      # FFprobe stream verification
│   ├── publishing/                 # Social media uploaders & scheduler
│   │   ├── base_publisher.py       # Unified publisher interface
│   │   ├── youtube_publisher.py    # YouTube Data API v3 uploader
│   │   ├── instagram_publisher.py  # Instagram Graph API Reels uploader
│   │   ├── publishing_scheduler.py # Background publish cron/scheduler
│   │   └── publishing_status.py    # Job progress & error tracking
│   └── storage/                    # Persistence layer
│       ├── database.py             # SQLite connection & schema migrations
│       ├── repositories.py         # CRUD repository for projects, scenes
│       ├── project_manager.py      # Project bundle save/load (.sfproj)
│       └── asset_manager.py        # Backgrounds, fonts, music metadata
├── tests/
├── assets/
├── projects/
└── output/
```

---

## 2. Key Subsystems & Design Choices

### Visible Chromium & DeepSeek Automation
- Standard automated agents often run headless, which triggers anti-bot hurdles and prevents users from handling manual logins or CAPTCHAs.
- StickForge AI runs a **visible persistent Chromium profile** (`browser/user_data/`).
- Users log in once interactively; subsequent runs reuse the authenticated cookies and local storage directly without extracting plaintext credentials.
- `LongResponseManager` detects when DeepSeek indicates more text is available (`Continue` button), verifies page state to prevent duplicate clicks, and stitches output segments safely.

### Deterministic Stickman Animation Engine
- Built with Python, NumPy, Pillow, and OpenCV/PySide drawing primitives.
- Renders at fixed target framerates (24, 30, 60 FPS) directly to disk frames or video pipes without unpredictable timing jitter.
- Skeletal model defines 14 joints with hierarchical FK (Forward Kinematics), allowing smooth procedural interpolation between keyframe poses.

### Safe Subprocess Video Rendering
- Audio and video encoding are isolated into managed worker processes executing `ffmpeg.exe` via explicit argument lists (no shell string concatenation).
- Renders intermediate scenes incrementally into cache so that a change in scene 3 does not force re-rendering scenes 1 and 2.
