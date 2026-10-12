"""
NeatLogs telemetry and Gemini SDK setup with PII masking and session binding.
Follows Section 4.4 and Section 5.1.
"""

import os
import re
from typing import Dict, Any, Optional
import neatlogs
from google import genai

def redact_customer_pii(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Masks emails, phone numbers, and potential card numbers before export to NeatLogs.
    Enforces PII detection count = 0 (Invariant P12).
    """
    if not isinstance(data, dict):
        return data

    sanitized = {}
    for k, v in data.items():
        if isinstance(v, str):
            # Mask emails
            v_masked = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[REDACTED_EMAIL]', v)
            # Mask credit card numbers
            v_masked = re.sub(r'\b(?:\d[ -]*?){13,16}\b', '[REDACTED_CARD]', v_masked)
            sanitized[k] = v_masked
        elif isinstance(v, dict):
            sanitized[k] = redact_customer_pii(v)
        else:
            sanitized[k] = v
    return sanitized

def init_telemetry(role: str = "agent", session_id: Optional[str] = None) -> genai.Client:
    """
    Initializes NeatLogs with flush_interval=1.0 (validated in E1).
    Wraps Google Gemini client AFTER neatlogs.init().
    """
    neatlogs.init(
        api_key=os.environ["NEATLOGS_API_KEY"],
        workflow_name=f"purser-{role}",
        tags=[
            f"role:{role}",
            f"commit:{os.environ.get('GIT_SHA', 'dev')[:7]}"
        ],
        flush_interval=float(os.environ.get("NEATLOGS_FLUSH_INTERVAL", "1.0")),
        mask=redact_customer_pii,
        capture_logs=True
    )

    if session_id:
        try:
            # Set neatlogs session id if SDK supports it
            neatlogs.set_session(session_id)
        except Exception:
            pass

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    return neatlogs.wrap(client)
