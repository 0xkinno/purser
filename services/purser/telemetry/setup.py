"""
Purser Telemetry Setup
Initializes neatlogs tracing and wraps the Google Gemini client.
Strict requirement: genai.Client() is instantiated only AFTER neatlogs.init().
"""
import os
import neatlogs
from google import genai
from typing import Dict, Any, Optional


def redact_customer_pii(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Neatlogs mask callback.
    Receives span/event dict and returns sanitized dict or None.
    """
    if not isinstance(event, dict):
        return event

    attributes = event.get("attributes")
    if isinstance(attributes, dict):
        for k, v in list(attributes.items()):
            if isinstance(v, str) and "@" in v and "." in v:
                parts = v.split("@")
                attributes[k] = f"{parts[0][:2]}***@{parts[1]}"
    return event


def init_telemetry(role: str = "agent", mask_pii: bool = True) -> genai.Client:
    """
    Initialize neatlogs OpenTelemetry exporter and return wrapped Gemini client.
    """
    api_key = os.environ.get("NEATLOGS_API_KEY")
    if not api_key:
        raise ValueError("NEATLOGS_API_KEY environment variable is not set")

    git_sha = os.environ.get("GIT_SHA", "dev")[:7]
    flush_interval = float(os.environ.get("NEATLOGS_FLUSH_INTERVAL", "1.0"))

    neatlogs.init(
        api_key=api_key,
        workflow_name=f"purser-{role}",
        tags=[f"role:{role}", f"commit:{git_sha}"],
        flush_interval=flush_interval,
        mask=redact_customer_pii if mask_pii else None,
        capture_logs=True,
    )

    gemini_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=gemini_key)
    return neatlogs.wrap(client)


@neatlogs.span(kind="WORKFLOW", name="purser.ticket")
def execute_ticket_trace(ticket_id: str, action_summary: str = "ticket_review") -> dict:
    """Wrapper entry point creating a single WORKFLOW trace per ticket."""
    return {
        "ticket_id": ticket_id,
        "action_summary": action_summary,
        "status": "initialized",
    }
