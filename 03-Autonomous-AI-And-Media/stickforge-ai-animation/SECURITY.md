# StickForge AI — Security & Privacy Policy

StickForge AI is engineered with strict local-first security principles.

---

## 1. Credentials & Secrets Management
- **Zero Hardcoded Secrets**: No API keys, OAuth client secrets, or private passwords exist in source files, batch scripts, or default configs.
- **Dedicated Persistent Profile**: Playwright browser runs with a sandboxed user-data profile in `browser/user_data/`. The user's personal browser profiles (Chrome, Edge, Brave) are never accessed or copied.
- **Local SQLite Database**: Stores only application metadata and non-sensitive project definitions. No plaintext credentials or browser cookies are saved into the database.
- **Environment & Keyring Integration**: API tokens (YouTube OAuth, Instagram access tokens) are stored in secure local configuration files with strict OS file permissions or Windows Credential Locker.

## 2. Browser Automation Safety
- **Visible Execution**: Browser automation runs visibly by default so the user is in full control of all interactions.
- **No CAPTCHA Bypassing**: CAPTCHAs, MFA prompts, and Cloudflare challenges are never automated. The application enters `WAITING_FOR_USER` state and prompts the user to resolve them manually in the browser.
- **Bounded Requests**: All browser interactions feature hard timeouts, state verification, and exponential backoff retry caps.

## 3. Subprocess & Media Safety
- **No Shell Injection**: Subprocess execution for FFmpeg uses structured argument lists (`subprocess.Popen(["ffmpeg", "-i", ...])`), completely bypassing shell string interpolation.
- **Path Sanitization**: All user-supplied filenames and project names are sanitized against directory traversal attacks (`../`, `..\`).

## 4. Log Redaction
- All loggers run through a sanitization filter that masks authorization headers, bearer tokens, API keys, and sensitive paths before writing to disk.
