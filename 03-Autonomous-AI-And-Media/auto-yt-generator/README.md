# 🎬 AUTO YT GENERATOR — AI-Powered Automated YouTube Studio

An automated 2D video production engine designed to create full 1080p animated YouTube videos from a single prompt or topic.

---

## 🌟 Key Features

- **🧠 16-Layer AI Video Director**:
  - **`SemanticDirector`**: Sentiment, emotion, narrative intent & key metric analysis.
  - **`ActingDirector`**: Expressive character staging, rule-of-thirds positioning, eye gaze tracking, and dynamic gestures.
  - **`CameraDirector`**: Cinematic framing (Wide, Medium, Close-Up, Extreme Close-Up, Reaction), cubic ease-in-out zoom curves, and 5-layer parallax depth.
- **🎭 2D Articulated Puppet Rig**:
  - Modular puppet hierarchy (Torso, Head, Eyes, Eyebrows, Viseme Mouth, Limbs).
  - Autonomous natural blinking cycle & pupil gaze tracking.
  - 14-Viseme acoustic lip-synchronization (`REST`, `A`, `E`, `O`, `U`, `MBP`, `FV`, `TH`, `L`, `SZ`, `SHCH`, `KG`, `NDT`).
- **📊 Motion Graphics & Procedural B-Roll**:
  - Animated stats counter cards, progress bars, and glowing neon metrics.
  - Procedural science cutaways (Neural Synapse Networks, Deep Space Vortex, Perspective 3D Grids).
  - Cinematic scene transitions (Zoom Punch, Glitch Flash, Crossfade).
- **🎙️ Studio Audio Pipeline**:
  - Multilingual neural voices via Microsoft EdgeTTS (Free, no token required).
  - Optional ElevenLabs voice cloning support.
  - Lossless FFmpeg PCM audio decoder with master voice boost (1.35x) and automatic voice ducking (-16dB music attenuation).
- **🔤 Dynamic Mobile Karaoke Captions**:
  - Word-by-word bouncing captions with active word yellow/cyan pop highlights and 3D stroke outline for 100% mobile readability.
  - Supports 16:9 Landscape and 9:16 Vertical (Shorts / Reels / TikTok).
- **🖼️ 3D High-CTR Thumbnails & Metadata**:
  - High-CTR 3D YouTube thumbnails with expressive character poses.
  - Automated SEO titles, descriptions, and chapter timestamps.
- **🖥️ Desktop GUI Studio**:
  - Dark-themed PyQt5 application with 1-Click Generator, Video Gallery & Player, and Project Manager.

---

## 🚀 Quick Start

### 1. Requirements
- Python 3.10+
- FFmpeg (automatically provided via `imageio-ffmpeg` or system PATH)

### 2. Installation
```bash
git clone https://github.com/<your-username>/auto-yt-generator.git
cd auto-yt-generator
pip install -r requirements.txt
```

### 3. Configuration (Optional)
Copy `.env.example` to `.env` and configure your API keys (the system runs with free EdgeTTS and built-in fallbacks out of the box):
```bash
cp .env.example .env
```

### 4. Launch Studio
Double click **`run.bat`** or run:
```bash
# Launch GUI Studio
python app/main.py gui

# Or generate via CLI
python app/main.py new-project --topic "What happens if you stop sleeping?" --duration 60
python app/main.py render-video <PROJECT_ID>
```

---

## 🧪 Testing

Run the comprehensive unit test suite (44 unit tests):
```bash
python -m unittest discover -s tests
```

---

## 📜 License
MIT License
