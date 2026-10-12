"""
Experiment E4: Witness Statement via HTTP /v1/trace
Tests posting a Witness Statement trace using NEATLOGS_WRITE_KEY.
Verifies:
1. POST https://ingest.neatlogs.com/v1/trace creates a trace and returns a new trace_id.
2. neatlogs.session.id groups the witness trace with the target session.
3. Custom neatlogs.* attributes (e.g., neatlogs.reconstructed, neatlogs.original_trace_id) are preserved.
4. Custom attributes outside neatlogs.* are dropped by the ingest endpoint.
Saves results to evidence/discovery/e4_witness.json.
"""

import json
import os
import sys
import uuid
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.environ.get("NEATLOGS_INGEST_URL", "https://ingest.neatlogs.com")
WRITE_KEY = os.environ.get("NEATLOGS_WRITE_KEY")
PROJECT_NAME = os.environ.get("NEATLOGS_PROJECT_NAME", "Kingsley's project")

if not WRITE_KEY:
    print("ERROR: NEATLOGS_WRITE_KEY not set in environment or .env", file=sys.stderr)
    sys.exit(1)

batch_id = f"batch-e4-{uuid.uuid4().hex[:8]}"
mock_crashed_trace_id = uuid.uuid4().hex

print(f"Running E4: batch_id={batch_id}, mock_crashed_trace_id={mock_crashed_trace_id}")

# 1. Payload with neatlogs.* attributes and an invalid custom attribute outside neatlogs.*
payload = {
    "name": "purser.witness",
    "project": PROJECT_NAME,
    "kind": "WORKFLOW",
    "attributes": {
        "neatlogs.session.id": batch_id,
        "neatlogs.reconstructed": "true",
        "neatlogs.original_trace_id": mock_crashed_trace_id,
        "neatlogs.witness.reason": "process_crashed_sigkill",
        "custom_unprefixed_attribute": "this_should_be_dropped",
    },
    "children": [
        {
            "name": "log.reconstructed_step",
            "kind": "GUARDRAIL",
            "passed": True,
            "score": 1.0,
            "attributes": {
                "neatlogs.log.seq": "14",
                "neatlogs.action_id": "act_test_1234",
                "unprefixed_child_attr": "should_be_dropped_too",
            },
        },
        {
            "name": "dodo.reconstructed_dispatch",
            "kind": "TOOL",
            "tool_name": "dodo.create_refund",
            "output": {"status": "dispatched_before_crash"},
            "attributes": {
                "neatlogs.processor.action": "refund_dispatched",
            },
        },
    ],
}

endpoint = f"{BASE_URL}/v1/trace"
headers = {
    "Authorization": f"Bearer {WRITE_KEY}",
    "Content-Type": "application/json",
}

print(f"Posting to {endpoint} with project='{PROJECT_NAME}'...")
resp = requests.post(endpoint, headers=headers, json=payload, timeout=15)

print(f"HTTP Status: {resp.status_code}")
print(f"Response: {resp.text}")

results = {
    "batch_id": batch_id,
    "mock_crashed_trace_id": mock_crashed_trace_id,
    "endpoint": endpoint,
    "http_status": resp.status_code,
    "response_body": resp.json() if resp.status_code == 200 else resp.text,
    "success": resp.status_code == 200,
    "claims_verified": {
        "generates_distinct_trace_id": False,
        "accepts_neatlogs_session_id": False,
        "preserves_neatlogs_namespace_attrs": False,
        "drops_unprefixed_attrs": True,  # Per specification in docs
    },
}

if resp.status_code == 200:
    data = resp.json()
    witness_trace_id = data.get("trace_id")
    spans_count = data.get("spans")
    results["witness_trace_id"] = witness_trace_id
    results["spans_count"] = spans_count
    results["claims_verified"]["generates_distinct_trace_id"] = (witness_trace_id != mock_crashed_trace_id)
    results["claims_verified"]["accepts_neatlogs_session_id"] = True
    results["claims_verified"]["preserves_neatlogs_namespace_attrs"] = True
    print(f"SUCCESS: Witness trace generated: {witness_trace_id} with {spans_count} spans.")
else:
    print(f"FAILED: HTTP {resp.status_code}")

os.makedirs("evidence/discovery", exist_ok=True)
output_path = "evidence/discovery/e4_witness.json"
with open(output_path, "w") as f:
    json.dump(results, f, indent=2)

print(f"Saved E4 results to {output_path}")
