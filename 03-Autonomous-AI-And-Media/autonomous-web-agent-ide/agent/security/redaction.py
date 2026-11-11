from typing import Dict, Any, List

try:
    from security.secret_scanner import SecretScanner
except ImportError:
    from .secret_scanner import SecretScanner

def redact_context_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively scans and redacts dictionary fields.
    """
    sanitized = {}
    for key, val in data.items():
        if isinstance(val, str):
            redacted, _ = SecretScanner.scan_and_redact(val)
            sanitized[key] = redacted
        elif isinstance(val, dict):
            sanitized[key] = redact_context_dict(val)
        elif isinstance(val, list):
            sanitized[key] = [
                redact_context_dict(item) if isinstance(item, dict)
                else (SecretScanner.scan_and_redact(item)[0] if isinstance(item, str) else item)
                for item in val
            ]
        else:
            sanitized[key] = val
    return sanitized
