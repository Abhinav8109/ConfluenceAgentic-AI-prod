"""
Prompt Injection Defense and Content Isolation Guardrails
Treats Confluence retrieved text strictly as untrusted data.
Detects injection attempts and prevents system prompt / credential leakage.
"""

import re
import logging
from typing import Tuple

logger = logging.getLogger("cloudops.security")

# Known prompt injection signatures
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
    r"disregard\s+(all\s+)?(previous|prior)\s+instructions",
    r"reveal\s+(your\s+)?(api|system|credentials|token|secret|password)",
    r"print\s+(your\s+)?(system\s+prompt|instructions|secret|api\s+token)",
    r"output\s+initial\s+prompt",
    r"bypass\s+security\s+controls",
    r"you\s+are\s+now\s+in\s+developer\s+mode",
    r"jailbreak",
]

SECRET_PATTERNS = [
    r"AIza[0-9A-Za-z-_]{35}",                          # Google API Key
    r"ATATT[0-9A-Za-z\-_]{30,}",                       # Atlassian API Token
    r"ya29\.[0-9A-Za-z\-_]+",                          # GCP OAuth Access Token
    r"(?i)api[_-]?token\s*[:=]\s*['\"][^'\"]{10,}['\"]",
    r"(?i)password\s*[:=]\s*['\"][^'\"]{6,}['\"]",
]

def scan_for_prompt_injection(text: str) -> Tuple[bool, str]:
    """
    Scans text (user input or retrieved content) for prompt injection patterns.
    Returns (is_suspicious, reason).
    """
    for pattern in INJECTION_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            matched_text = match.group(0)
            logger.warning(f"Security Alert: Detected potential prompt injection pattern: '{matched_text}'")
            return True, f"Detected injection pattern: {matched_text}"
    return False, ""

def isolate_untrusted_content(page_title: str, page_url: str, content: str) -> str:
    """
    Encloses retrieved content in strict XML-style untrusted data fences.
    System prompt instructs the LLM that content inside these fences is purely reference data.
    """
    return (
        f'<confluence_untrusted_data title="{page_title}" url="{page_url}">\n'
        f"{content}\n"
        f"</confluence_untrusted_data>"
    )

def scrub_sensitive_secrets(text: str) -> str:
    """
    Scans text before rendering to user and redacts any leaked tokens or passwords.
    """
    scrubbed = text
    for pattern in SECRET_PATTERNS:
        scrubbed = re.sub(pattern, "[REDACTED_CREDENTIAL]", scrubbed)
    return scrubbed
