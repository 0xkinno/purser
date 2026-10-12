-- Purser Supabase Postgres Schema Migration
-- Defines the immutable write-ahead Log, batches, tickets, ledger, muster, escalations, and receipts

CREATE TABLE IF NOT EXISTS batches (
    batch_id TEXT PRIMARY KEY,
    status TEXT NOT NULL DEFAULT 'ACTIVE', -- ACTIVE, CLOSED, FAILED
    policy_version TEXT NOT NULL,
    policy_hash TEXT NOT NULL,
    planner_model TEXT NOT NULL,
    writer_model TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    closed_at TIMESTAMPTZ,
    manifest_hash TEXT,
    summary JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tickets (
    ticket_id TEXT PRIMARY KEY,
    batch_id TEXT REFERENCES batches(batch_id),
    customer_id TEXT,
    customer_email TEXT NOT NULL,
    customer_name TEXT,
    subject TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'NEW', -- NEW, LEASED, IN_PROGRESS, AWAITING_CUSTOMER, ESCALATED, RESOLVED, DECLINED
    claimed_reason TEXT,
    order_ref TEXT,
    leased_by TEXT,
    leased_at TIMESTAMPTZ,
    lease_expires_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,
    resolution_type TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ticket_messages (
    message_id TEXT PRIMARY KEY,
    ticket_id TEXT NOT NULL REFERENCES tickets(ticket_id) ON DELETE CASCADE,
    sender_type TEXT NOT NULL, -- customer, agent, operator
    sender_name TEXT,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS customers_cache (
    customer_id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS log_records (
    id BIGSERIAL PRIMARY KEY,
    batch_id TEXT NOT NULL,
    action_id TEXT NOT NULL,
    seq INTEGER NOT NULL,
    state TEXT NOT NULL, -- INTENDED, DISPATCHED, ACCEPTED, SETTLED, UNCERTAIN, ABANDONED, DENIED, RECKONING
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    prev_hash TEXT NOT NULL,
    hash TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_batch_seq UNIQUE (batch_id, seq)
);

CREATE INDEX IF NOT EXISTS idx_log_records_action_id ON log_records(action_id);
CREATE INDEX IF NOT EXISTS idx_log_records_batch_id ON log_records(batch_id);

CREATE TABLE IF NOT EXISTS refund_actions (
    action_id TEXT PRIMARY KEY,
    ticket_id TEXT NOT NULL REFERENCES tickets(ticket_id),
    payment_id TEXT NOT NULL,
    amount_minor INTEGER NOT NULL,
    rule_id TEXT NOT NULL,
    policy_version TEXT NOT NULL,
    state TEXT NOT NULL DEFAULT 'INTENDED',
    attempt INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS receipts (
    receipt_id TEXT PRIMARY KEY,
    action_id TEXT NOT NULL REFERENCES refund_actions(action_id),
    ticket_id TEXT NOT NULL REFERENCES tickets(ticket_id),
    payment_id TEXT NOT NULL,
    refund_id TEXT, -- Dodo refund id ref_*
    amount_minor INTEGER NOT NULL,
    currency TEXT NOT NULL DEFAULT 'USD',
    rule_id TEXT NOT NULL,
    rule_source_sha TEXT,
    checkpoint_id TEXT,
    status TEXT NOT NULL, -- ACCEPTED, SETTLED_SUCCEEDED, SETTLED_FAILED
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    settled_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS escalations (
    escalation_id TEXT PRIMARY KEY,
    ticket_id TEXT NOT NULL REFERENCES tickets(ticket_id),
    action_id TEXT,
    reason TEXT NOT NULL,
    evidence_packet JSONB NOT NULL DEFAULT '{}'::jsonb,
    status TEXT NOT NULL DEFAULT 'PENDING', -- PENDING, APPROVED, DECLINED
    decided_by TEXT,
    decided_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS muster_rows (
    id BIGSERIAL PRIMARY KEY,
    batch_id TEXT NOT NULL REFERENCES batches(batch_id),
    ticket_id TEXT NOT NULL REFERENCES tickets(ticket_id),
    payment_id TEXT NOT NULL,
    refund_id TEXT,
    log_amount INTEGER NOT NULL,
    processor_amount INTEGER NOT NULL,
    status TEXT NOT NULL,
    matched BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS drill_runs (
    drill_id TEXT PRIMARY KEY,
    drill_name TEXT NOT NULL,
    fault_type TEXT NOT NULL,
    agent_version TEXT NOT NULL, -- v1-naive, v2-purser
    status TEXT NOT NULL, -- PASSED, FAILED
    metrics JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS witness_statements (
    statement_id TEXT PRIMARY KEY,
    batch_id TEXT NOT NULL REFERENCES batches(batch_id),
    crashed_trace_id TEXT,
    witness_trace_id TEXT NOT NULL,
    spans_count INTEGER NOT NULL,
    reconstructed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS incidents (
    incident_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL,
    resolved_at TIMESTAMPTZ NOT NULL,
    credit_percentage INTEGER NOT NULL DEFAULT 100,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS provenance (
    rule_id TEXT PRIMARY KEY,
    rule_name TEXT NOT NULL,
    source_sha TEXT NOT NULL,
    checkpoint_id TEXT NOT NULL,
    intent_summary TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
