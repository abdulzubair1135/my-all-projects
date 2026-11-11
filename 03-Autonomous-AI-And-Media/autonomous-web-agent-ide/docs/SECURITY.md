# Security Architecture & Threat Model

The Autonomous Web-Agent IDE is built upon the fundamental principle: **The AI is not trusted.**

```
AI proposes WHAT it wants to do
       ↓
Policy Engine decides WHETHER it is allowed
       ↓
PathGuard & Sandbox decide HOW it is safely executed
       ↓
Verification Engine decides WHETHER it actually worked
```

---

## 1. Filesystem Sandbox (`PathGuard`)

All file read, write, edit, and delete operations must pass through canonical path validation:

1. **Path Traversal Protection**: Rejects `../`, `..\\`, `/../`, and nested traversal attempts.
2. **Canonical Realpath Check**: Resolves all symlinks and parent directory links. If the resolved path does not start with the project's canonical root directory, execution raises a `SecurityException`.
3. **Windows Device Path Blocking**: Rejects reserved DOS device names: `CON`, `PRN`, `AUX`, `NUL`, `COM1-9`, `LPT1-9`.
4. **UNC Path Blocking**: Rejects network share paths (`\\\\server\\share`).
5. **Atomic Writes**: Writes changes to `.tmp_<filename>_<pid>` before renaming to prevent partial write corruption.
6. **Conflict Detection**: Verifies SHA256 hashes before modifying files to protect against overwriting manual developer edits.

---

## 2. Command Policy Engine

Commands are evaluated into four distinct tiers:

| Tier | Behavior | Examples |
|---|---|---|
| **SAFE** | Executed automatically in `SAFE` mode | `npm install`, `npm test`, `npm run build`, `python -m pytest`, `node app.js`, `git status`, `git add`, `git commit` |
| **CAUTION** | Requires user approval in `SAFE` & `ASK` modes | `curl`, `wget`, `docker`, `git push`, `git reset`, commands with chaining operators (`&&`, `||`, `;`, `\|`) |
| **DANGEROUS** | Always requires explicit interactive confirmation | `npm publish`, `pip install --system`, `kill`, `taskkill`, modifying environment variables |
| **BLOCKED** | Immediately rejected and never executed | `format`, `diskpart`, `mkfs`, `dd`, `rm -rf /`, `del /s C:\`, `powershell -ExecutionPolicy Bypass`, reading `~/.ssh` or `.aws` credentials |

---

## 3. Secret Protection & Scanning (`SecretScanner`)

Before any context, code, or command log is transmitted to the web-based LLM, the `SecretScanner` executes automated scrubbing:
- Private Keys (`-----BEGIN RSA PRIVATE KEY-----`)
- AWS Access Keys & Secret Keys
- GitHub Personal Access Tokens (`ghp_...`, `github_pat_...`)
- OpenAI / Anthropic / DeepSeek API Keys (`sk-...`)
- JSON Web Tokens (`eyJ...`)
- Database Connection URIs with embedded passwords
- Sensitive files (`.env`, `.env.local`, `id_rsa`, `*.pem`, `*.key`) are completely excluded from LLM context previews.
