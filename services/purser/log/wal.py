"""
Write-Ahead Log (WAL) with SHA-256 hash chaining and durable ledger view.
Implements Section 4.3 and 4.6 (Invariants P1, P2, P7, P11).
"""

import hashlib
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
import asyncpg

GENESIS_HASH = "0" * 64

def compute_record_hash(prev_hash: str, batch_id: str, action_id: str, seq: int, state: str, payload: dict) -> str:
    serialized = json.dumps(payload, sort_keys=True, default=str)
    raw = f"{prev_hash}|{batch_id}|{action_id}|{seq}|{state}|{serialized}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

@dataclass
class LogRecord:
    id: Optional[int]
    batch_id: str
    action_id: str
    seq: int
    state: str
    payload: Dict[str, Any]
    prev_hash: str
    hash: str
    created_at: Optional[datetime] = None

@dataclass
class LedgerView:
    payment_id: str
    total_amount_minor: int
    refunded_minor: int
    remaining_minor: int
    actions_count: int

class Log:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def get_latest_hash(self, batch_id: str) -> str:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT hash FROM log_records WHERE batch_id = $1 ORDER BY seq DESC LIMIT 1;",
                batch_id
            )
            return row["hash"] if row else GENESIS_HASH

    async def get_next_seq(self, batch_id: str) -> int:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT COALESCE(MAX(seq), 0) + 1 AS next_seq FROM log_records WHERE batch_id = $1;",
                batch_id
            )
            return row["next_seq"]

    async def append(self, batch_id: str, action_id: str, state: str, payload: Dict[str, Any]) -> LogRecord:
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # Acquire advisory or table level lock for batch sequencing
                row_last = await conn.fetchrow(
                    "SELECT seq, hash FROM log_records WHERE batch_id = $1 ORDER BY seq DESC LIMIT 1 FOR UPDATE;",
                    batch_id
                )
                if row_last:
                    seq = row_last["seq"] + 1
                    prev_hash = row_last["hash"]
                else:
                    seq = 1
                    prev_hash = GENESIS_HASH

                rec_hash = compute_record_hash(prev_hash, batch_id, action_id, seq, state, payload)

                inserted = await conn.fetchrow(
                    """
                    INSERT INTO log_records (batch_id, action_id, seq, state, payload, prev_hash, hash)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    RETURNING id, batch_id, action_id, seq, state, payload, prev_hash, hash, created_at;
                    """,
                    batch_id, action_id, seq, state, json.dumps(payload), prev_hash, rec_hash
                )

                return LogRecord(
                    id=inserted["id"],
                    batch_id=inserted["batch_id"],
                    action_id=inserted["action_id"],
                    seq=inserted["seq"],
                    state=inserted["state"],
                    payload=json.loads(inserted["payload"]) if isinstance(inserted["payload"], str) else inserted["payload"],
                    prev_hash=inserted["prev_hash"],
                    hash=inserted["hash"],
                    created_at=inserted["created_at"]
                )

    async def receipt_for(self, action_id: str) -> Optional[Dict[str, Any]]:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM receipts WHERE action_id = $1;",
                action_id
            )
            return dict(row) if row else None

    async def ledger_view(self, payment_id: str, payment_total_minor: int) -> LedgerView:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT amount_minor FROM receipts 
                WHERE payment_id = $1 AND status IN ('ACCEPTED', 'SETTLED_SUCCEEDED');
                """,
                payment_id
            )
            refunded = sum(r["amount_minor"] for r in rows)
            remaining = max(0, payment_total_minor - refunded)
            return LedgerView(
                payment_id=payment_id,
                total_amount_minor=payment_total_minor,
                refunded_minor=refunded,
                remaining_minor=remaining,
                actions_count=len(rows)
            )

    async def verify_chain(self, batch_id: str) -> bool:
        """Verifies P11 hash chain integrity for the batch."""
        async with self.pool.acquire() as conn:
            records = await conn.fetch(
                "SELECT * FROM log_records WHERE batch_id = $1 ORDER BY seq ASC;",
                batch_id
            )
            expected_prev = GENESIS_HASH
            for r in records:
                if r["prev_hash"] != expected_prev:
                    return False
                payload = json.loads(r["payload"]) if isinstance(r["payload"], str) else r["payload"]
                expected_hash = compute_record_hash(
                    r["prev_hash"], r["batch_id"], r["action_id"], r["seq"], r["state"], payload
                )
                if r["hash"] != expected_hash:
                    return False
                expected_prev = r["hash"]
            return True
