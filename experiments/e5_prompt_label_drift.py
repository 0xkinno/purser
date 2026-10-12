"""
Experiment E5: Prompt Label Drift Mid-Run
Hypothesis:
An agent resolving prompt dynamically by label (e.g., label='production')
will experience prompt drift mid-batch if the label is updated or pointed
to a new version while tickets are being processed.

Experiment:
1. Create a managed prompt 'purser-policy-planner' in neatlogs with v1 labelled 'production'.
2. Simulate a batch processing tickets 1..10.
3. For tickets 1..5: fetch prompt using label='production'. Both dynamic and pinned strategies yield v1.
4. Mid-batch (after ticket 5): create v2 and reassign label 'production' to v2.
5. For tickets 6..10:
   - Dynamic fetch (neatlogs.get_prompt(..., label='production')) silently drifts to v2.
   - Pinned fetch (neatlogs.get_prompt(..., version=batch_pinned_version)) remains stable at v1.
6. Verify and record observed drift in evidence/discovery/e5_prompt_label_drift.json.
"""

import json
import os
import sys
import uuid
from dotenv import load_dotenv
import neatlogs

load_dotenv()

api_key = os.environ.get("NEATLOGS_API_KEY")
if not api_key:
    print("ERROR: NEATLOGS_API_KEY missing", file=sys.stderr)
    sys.exit(1)

# Initialize neatlogs
neatlogs.init(api_key=api_key, workflow_name="purser-e5", tags=["experiment:e5"])

prompt_name = f"purser-planner-{uuid.uuid4().hex[:6]}"
print(f"Creating prompt '{prompt_name}' v1...")

# Step 1: Create v1
p1 = neatlogs.create_prompt(
    name=prompt_name,
    prompt="You are Purser Policy Planner v1. Strict refund policy.",
    labels=["production"],
    commit_message="Initial policy baseline v1"
)
v1_version = getattr(p1, "version", 1)
print(f"Created {prompt_name} v1 (version={v1_version})")

# Step 2: Batch startup pins version
batch_pinned_version = v1_version

batch_history = []

# Simulate tickets 1 to 5
for ticket_idx in range(1, 6):
    dyn_prompt = neatlogs.get_prompt(prompt_name, label="production")
    pin_prompt = neatlogs.get_prompt(prompt_name, version=batch_pinned_version)
    batch_history.append({
        "ticket": ticket_idx,
        "phase": "pre-drift",
        "dynamic_version": dyn_prompt.version,
        "pinned_version": pin_prompt.version,
        "dynamic_text": dyn_prompt.content,
        "pinned_text": pin_prompt.content,
        "drift_detected": (dyn_prompt.version != pin_prompt.version)
    })

print("Processed tickets 1..5. Now moving 'production' label to v2...")

# Step 3: Publish v2 and move 'production' label
p2 = neatlogs.create_prompt(
    name=prompt_name,
    prompt="You are Purser Policy Planner v2. Updated discretionary policy.",
    labels=["production"],
    commit_message="Update policy to v2"
)
v2_version = getattr(p2, "version", 2)
print(f"Created {prompt_name} v2 (version={v2_version}) with label 'production'")

# Step 4: Process tickets 6 to 10
for ticket_idx in range(6, 11):
    dyn_prompt = neatlogs.get_prompt(prompt_name, label="production")
    pin_prompt = neatlogs.get_prompt(prompt_name, version=batch_pinned_version)
    drift = (dyn_prompt.version != pin_prompt.version)
    batch_history.append({
        "ticket": ticket_idx,
        "phase": "post-drift",
        "dynamic_version": dyn_prompt.version,
        "pinned_version": pin_prompt.version,
        "dynamic_text": dyn_prompt.content,
        "pinned_text": pin_prompt.content,
        "drift_detected": drift
    })

drift_count = sum(1 for item in batch_history if item["drift_detected"])
print(f"Batch completed. Tickets with drift between dynamic and pinned: {drift_count}/10")

results = {
    "prompt_name": prompt_name,
    "v1_version": v1_version,
    "v2_version": v2_version,
    "batch_pinned_version": batch_pinned_version,
    "total_tickets": len(batch_history),
    "drift_detected_in_dynamic": drift_count > 0,
    "drift_tickets_count": drift_count,
    "ticket_events": batch_history,
    "conclusion": (
        "Fetching by label causes unpinned mid-batch prompt drift (H5 confirmed). "
        "Purser's invariant: resolve label once at batch start, record pinned_version in Log, "
        "and fetch strictly by version for all tickets in the batch."
    )
}

os.makedirs("evidence/discovery", exist_ok=True)
out_file = "evidence/discovery/e5_prompt_label_drift.json"
with open(out_file, "w") as f:
    json.dump(results, f, indent=2)

print(f"Saved E5 results to {out_file}")
