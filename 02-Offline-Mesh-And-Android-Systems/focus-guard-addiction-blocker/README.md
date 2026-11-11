# P.RN Controller (Porn Controller)
### Offline Digital Addiction Prevention & Self-Control Android Application
**Branded and Built by projectX² (projectX2)**

---

## 1. Executive Summary & Vision

**P.RN Controller** is an offline-first digital self-control application engineered to break compulsive digital habits, eliminate exposure to adult content, and redirect compulsive search loops toward mindfulness and productivity.

Core Philosophy:
> *"Don't just block distractions. Help users build self-control."*

---

## 2. Key Modules & Technical Capabilities

### 🛡️ Module 1: Adult Content Protection (Local DNS Loopback)
- **Zero Cloud Leakage**: Uses Android's `VpnService` strictly locally. Does NOT connect to any external VPN server.
- **Pure DNS Sinkholing**: Captures outbound UDP port 53 DNS requests. Matches against an in-memory trie / Room database of 500+ curated adult hosts.
- **NXDOMAIN Loopback**: Blocked domains receive instant NXDOMAIN (`RCODE = 3`) or sinkhole replies. Safe domains are resolved via Cloudflare Family DNS (`1.1.1.3`).
- **Zero TLS Decryption**: Adheres to Android sandbox security. No root CAs installed; no TLS decryption attempted.
- **Offline Import / Export**: Users can manually import offline domain lists in bulk.

### 🔍 Module 2: Keyword & Repeated Search Blocker
- **Compulsive Pattern Detection**: Tracks repetitive searches (e.g. typing names or triggers repeatedly in search bars across Instagram, browsers, etc.).
- **Sliding Window & Cooldowns**: Evaluates search repetition frequency over a 10-minute sliding window with customizable sensitivity and cooldown periods to prevent intervention spam.
- **Strict Privacy**: Explicitly avoids password fields (`node.isPassword`), authentication screens, and private messengers.

### ⚡ Module 3: Smart Intervention System
- **Non-Shaming Redirection**: Prompts users with constructive, high-dopamine-breaking interventions.
- **4 Tone Categories**:
  - **Motivational**: Growth-mindset coaching.
  - **Strict**: Direct, firm interruptions.
  - **Funny**: Lighthearted humor to break compulsive trances.
  - **Friendly**: Gentle mindfulness and pacing.
- **Immediate Actions**: Return to Work, Take a Break, Complete a Task, or Dismiss.

### 🧘 Module 4: Task Assignment Engine
- **Habit Replacement**: Replaces compulsive urges with positive behavioral patterns:
  - *Drink Water* (1 min)
  - *Deep Box Breathing* (1 min)
  - *Walking* (2 min)
  - *Meditation* (3 min)
  - *Clean Desk* (3 min)
  - *Reading a Book* (5 min)
  - *Physical Exercises* (Optional: 5 Push-ups, 10 Squats, 30s Plank)
- **Interactive Countdown Timer**: Start, pause, resume, complete, and cancel with background service tracking.

### ⏱️ Module 5: Productivity Focus Mode
- **Pomodoro Presets**: 15m, 25m, 45m, 50m, or Mindful 5m Break.
- **Foreground Service**: Resilient notification countdown that survives application switching.

### 📊 Module 6: Local Habit Analytics
- **Pure On-Device Computation**: 100% computed inside Room Database.
- **Interactive Compose Charts**: Weekly focus trends, blocked loops, completion counts.
- **Dopamine Insight**: Treats interventions as prefrontal-cortex training rather than failure.

### 🎵 Module 7: Audio Intro & Custom Branding
- **Branding**: Premium charcoal (`#121214`), electric purple (`#8B5CF6`), and cyber blue (`#06B6D4`) UI with custom `projectX²` badge.
- **Intro Chime**: Futuristic Cmaj9 chord synthesis on application startup powered mathematically via `AudioTrack`.

---

## 3. Technology Stack

- **Language**: Kotlin 2.0
- **UI**: Jetpack Compose + Material 3
- **Architecture**: MVVM + Clean Architecture
- **Database**: Room Database 2.6.1 (9 Entities)
- **Preferences**: DataStore Preferences
- **Background Processing**: Android Foreground Services (`LocalVpnService`, `FocusService`, `TaskTimerService`)
- **UI Inspection**: Android `AccessibilityService` (Opt-in)
- **Target SDK**: Android 15 (API 35) | **Min SDK**: Android 10 (API 29)

---

## 4. Building the APK

```powershell
# Set JAVA_HOME to JDK 21
$env:JAVA_HOME = "C:\Program Files\Android\Android Studio\jbr"

# Build Release APK
.\gradlew.bat assembleRelease
```

Generated APK:
`app/build/outputs/apk/release/app-release-unsigned.apk` (or debug signed release).
