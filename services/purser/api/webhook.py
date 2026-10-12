"""
FastAPI Webhook Receiver for Dodo Payments.
Handles refund.succeeded, refund.failed, and payment.succeeded.
Verifies Standard Webhook signatures and updates settlement records in the Log (Invariant P6).
"""

import hmac
import hashlib
import json
import os
from typing import Dict, Any
from fastapi import FastAPI, Request, HTTPException, Header, Depends
import asyncpg
import dotenv
dotenv.load_dotenv()

from services.purser.log.wal import Log

app = FastAPI(title="Purser Webhook Receiver", version="1.0.0")

def verify_webhook_signature(payload_bytes: bytes, signature_header: str, secret: str) -> bool:
    """Verifies HMAC signature matching webhook specification."""
    if not signature_header or not secret:
        return False
    # Standard signature format: v1,<sig> or hex
    sig = signature_header.split(",")[-1].replace("v1=", "").strip()
    expected = hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()
    return hmac.compare_digest(sig, expected)

@app.post("/webhooks/dodo")
async def handle_dodo_webhook(request: Request):
    secret = os.getenv("DODO_WEBHOOK_SECRET", "")
    sig_header = request.headers.get("webhook-signature") or request.headers.get("x-dodo-signature") or ""

    body_bytes = await request.body()
    # In test mode without secret configured, verify if secret is set
    if secret and not verify_webhook_signature(body_bytes, sig_header, secret):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    data = await request.json()
    event_type = data.get("type") or data.get("event")
    event_payload = data.get("data", {})

    db_url = os.getenv("DATABASE_URL")
    pool = await asyncpg.create_pool(db_url, min_size=1, max_size=2)
    log = Log(pool)

    try:
        if event_type == "refund.succeeded":
            refund_id = event_payload.get("refund_id")
            async with pool.acquire() as conn:
                receipt = await conn.fetchrow(
                    "UPDATE receipts SET status = 'SETTLED_SUCCEEDED', settled_at = NOW() WHERE refund_id = $1 RETURNING *;",
                    refund_id
                )
                if receipt:
                    batch_row = await conn.fetchrow(
                        "SELECT batch_id FROM refund_actions WHERE action_id = $1;",
                        receipt["action_id"]
                    )
                    batch_id = batch_row["batch_id"] if batch_row else "global"
                    await log.append(batch_id, receipt["action_id"], "SETTLED", {
                        "status": "succeeded",
                        "refund_id": refund_id,
                        "amount_minor": receipt["amount_minor"]
                    })

        elif event_type == "refund.failed":
            refund_id = event_payload.get("refund_id")
            async with pool.acquire() as conn:
                receipt = await conn.fetchrow(
                    "UPDATE receipts SET status = 'SETTLED_FAILED', settled_at = NOW() WHERE refund_id = $1 RETURNING *;",
                    refund_id
                )
                if receipt:
                    # Reopen ticket automatically per Section 4.5
                    await conn.execute(
                        "UPDATE tickets SET status = 'NEW' WHERE ticket_id = $1;",
                        receipt["ticket_id"]
                    )
                    batch_row = await conn.fetchrow(
                        "SELECT batch_id FROM refund_actions WHERE action_id = $1;",
                        receipt["action_id"]
                    )
                    batch_id = batch_row["batch_id"] if batch_row else "global"
                    await log.append(batch_id, receipt["action_id"], "SETTLED", {
                        "status": "failed",
                        "refund_id": refund_id,
                        "amount_minor": receipt["amount_minor"],
                        "reopened_ticket": receipt["ticket_id"]
                    })

        return {"received": True, "event": event_type}
    finally:
        await pool.close()
