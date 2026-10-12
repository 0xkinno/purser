"""
Resolves runtime provenance mapping rule -> commit -> Entire checkpoint.
Reads actual git commit history for each rule function via git log -L.
If no Entire-Checkpoint trailer exists, sets checkpoint_id to None and displays 'No checkpoint'.
"""

import os
import subprocess
import re
from typing import Dict, Any, List, Optional

RULES_CATALOG = [
    {"rule_id": "R1_full_within_14_days", "name": "Full refund within 14 days", "file": "policy/rules.py", "symbol": "R1_full_within_14_days"},
    {"rule_id": "R2_prorata_annual_cancel", "name": "Pro-rata annual cancellation", "file": "policy/rules.py", "symbol": "R2_prorata_annual_cancel"},
    {"rule_id": "R3_downtime_credit", "name": "Service downtime credit", "file": "policy/rules.py", "symbol": "R3_downtime_credit"},
    {"rule_id": "R4_duplicate_charge", "name": "Duplicate transaction refund", "file": "policy/rules.py", "symbol": "R4_duplicate_charge"},
    {"rule_id": "R5_no_refund_after_usage_cap", "name": "Usage cap refund decline", "file": "policy/rules.py", "symbol": "R5_no_refund_after_usage_cap"},
    {"rule_id": "R6_chargeback_risk_escalate", "name": "Chargeback dispute escalation", "file": "policy/rules.py", "symbol": "R6_chargeback_risk_escalate"}
]

def resolve_rule_provenance() -> List[Dict[str, Any]]:
    provenance_map = []

    for rule in RULES_CATALOG:
        commit_sha = None
        checkpoint_id = None

        try:
            cmd = ["git", "log", f"-L:{rule['symbol']}:{rule['file']}", "--format=%H%n%B", "-1"]
            output = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
            lines = output.strip().splitlines()
            if lines:
                commit_sha = lines[0].strip()
                # Check for Entire-Checkpoint trailer
                for line in lines[1:]:
                    if "Entire-Checkpoint:" in line:
                        checkpoint_id = line.split("Entire-Checkpoint:")[-1].strip()
                        break
        except Exception:
            try:
                commit_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
            except Exception:
                commit_sha = None

        entry = {
            "rule_id": rule["rule_id"],
            "rule_name": rule["name"],
            "source_file": rule["file"],
            "commit_sha": commit_sha,
            "checkpoint_id": checkpoint_id,
            "checkpoint_display": checkpoint_id if checkpoint_id else "No checkpoint",
            "entire_url": f"https://entire.io/gh/0xkinno/purser/commit/{commit_sha}" if commit_sha else None,
            "intent": f"Founder policy rule codified in {rule['file']}"
        }
        provenance_map.append(entry)

    return provenance_map

if __name__ == "__main__":
    records = resolve_rule_provenance()
    for r in records:
        print(f"{r['rule_id']} -> commit {r['commit_sha'][:7] if r['commit_sha'] else 'None'} -> {r['checkpoint_display']}")
