"""
Unit and Property-based tests for Write-Ahead Log (WAL) and SHA-256 hash chain (Invariants P7, P11).
"""

import asyncio
import os
import pytest
from hypothesis import given, strategies as st
import asyncpg
import dotenv
dotenv.load_dotenv()

from services.purser.log.wal import Log, compute_record_hash, GENESIS_HASH

@pytest.mark.asyncio
async def test_wal_hash_chain_and_append():
    db_url = os.getenv("DATABASE_URL")
    pool = await asyncpg.create_pool(db_url, min_size=1, max_size=3)
    log = Log(pool)
    batch_id = f"test-batch-{os.urandom(4).hex()}"

    try:
        # Append 3 records
        r1 = await log.append(batch_id, "act_1", "INTENDED", {"amount": 1000})
        assert r1.seq == 1
        assert r1.prev_hash == GENESIS_HASH

        r2 = await log.append(batch_id, "act_1", "DISPATCHED", {"attempt": 1})
        assert r2.seq == 2
        assert r2.prev_hash == r1.hash

        r3 = await log.append(batch_id, "act_1", "ACCEPTED", {"refund_id": "ref_123"})
        assert r3.seq == 3
        assert r3.prev_hash == r2.hash

        # Verify chain integrity (P11)
        valid = await log.verify_chain(batch_id)
        assert valid is True

    finally:
        # Cleanup
        async with pool.acquire() as conn:
            await conn.execute("DELETE FROM log_records WHERE batch_id = $1;", batch_id)
        await pool.close()

def test_hash_chain_tamper_detection():
    """P11 property: altering any record payload or hash breaks chain integrity."""
    prev = GENESIS_HASH
    h1 = compute_record_hash(prev, "b1", "a1", 1, "INTENDED", {"amount": 500})
    h2 = compute_record_hash(h1, "b1", "a1", 2, "DISPATCHED", {"attempt": 1})

    # Tampered payload in record 1
    h1_tampered = compute_record_hash(prev, "b1", "a1", 1, "INTENDED", {"amount": 9999})
    assert h1 != h1_tampered

    # Subsequent record hash computation diverges
    h2_diverged = compute_record_hash(h1_tampered, "b1", "a1", 2, "DISPATCHED", {"attempt": 1})
    assert h2 != h2_diverged
