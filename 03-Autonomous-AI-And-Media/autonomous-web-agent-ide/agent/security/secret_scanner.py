import re
from typing import List, Tuple

# Regex rules for detecting credentials and sensitive tokens
SECRET_PATTERNS = [
    # Private keys
    (re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----[\s\S]*?-----END (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----", re.MULTILINE), "[REDACTED_PRIVATE_KEY]"),
    # AWS Access Key ID
    (re.compile(r"\b(AKIA[0-9A-Z]{16})\b"), "[REDACTED_AWS_KEY]"),
    # AWS Secret Key
    (re.compile(r"(?i)aws_secret_access_key\s*[:=]\s*['\"]?([A-Za-z0-9/+=]{40})['\"]?"), "aws_secret_access_key = [REDACTED_SECRET]"),
    # GitHub Tokens
    (re.compile(r"\b(ghp_[0-9a-zA-Z]{36}|github_pat_[0-9a-zA-Z_]{82})\b"), "[REDACTED_GITHUB_TOKEN]"),
    # Generic API Keys (OpenAI, Anthropic, DeepSeek, etc.)
    (re.compile(r"\b(sk-[a-zA-Z0-9_-]{20,})\b"), "[REDACTED_API_KEY]"),
    # JWT Tokens
    (re.compile(r"\beyJ[a-zA-Z0-9_-]{10,}\.eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\b"), "[REDACTED_JWT]"),
    # Database Connection Strings with Passwords
    (re.compile(r"(mongodb(?:\+srv)?|postgres|postgresql|mysql|redis)://(?:[^:]+):([^@]+)@"), r"\1://[USER]:[REDACTED_PASSWORD]@"),
    # Generic password assignments
    (re.compile(r"(?i)(?:password|passwd|secret|api_key|token|auth_token)\s*[:=]\s*['\"]([^'\"\s]{6,})['\"]"), r"password = [REDACTED_SECRET]")
]

FORBIDDEN_FILENAMES = {
    ".env",
    ".env.local",
    ".env.production",
    "id_rsa",
    "id_ed25519",
    "credentials.json",
    ".npmrc",
    ".pypirc"
}

class SecretScanner:
    @classmethod
    def scan_and_redact(cls, text: str) -> Tuple[str, int]:
        """
        Scans text and replaces any detected sensitive data with redaction markers.
        Returns (redacted_text, count_of_redactions).
        """
        if not text or not isinstance(text, str):
            return text, 0

        redacted = text
        total_redactions = 0

        for pattern, replacement in SECRET_PATTERNS:
            matches = pattern.findall(redacted)
            if matches:
                total_redactions += len(matches)
                redacted = pattern.sub(replacement, redacted)

        return redacted, total_redactions

    @classmethod
    def is_forbidden_file(cls, filename: str) -> bool:
        """
        Returns True if the filename is sensitive and should never be sent to LLM.
        """
        base = filename.split("/")[-1].split("\\")[-1]
        if base in FORBIDDEN_FILENAMES or base.endswith((".pem", ".key", ".pfx", ".p12")):
            return True
        return False
