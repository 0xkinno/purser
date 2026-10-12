"""
Witness Statement builder via NeatLogs HTTP trace ingestion (POST /v1/trace).
Implements Section 4.4 and Task 1.8.
Reconstructs truncated spans from the durable WAL with honest audit attributes.
"""

import os
import requests
from datetime import datetime, timezone
from typing import Dict, Any, List

class WitnessStatementBuilder:
    def __init__(self, write_key: Optional[str] = None):
        self.write_key = write_key or os.getenv("NEATLOGS_WRITE_KEY")
        self.ingest_url = "https://ingest.neatlogs.com/v1/trace"

    def submit_statement(
        self,
        batch_id: str,
        crashed_trace_id: str,
        reconstructed_spans: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Submits a Witness Statement trace linked to the batch session and original trace.
        """
        headers = {
            "Authorization": f"Bearer {self.write_key}",
            "Content-Type": "application/json"
        }

        root_span = {
            "name": "purser.witness",
            "kind": "WORKFLOW",
            "status": "STATUS_CODE_OK",
            "start_time_unix_nano": int(datetime.now(timezone.utc).timestamp() * 1e9),
            "end_time_unix_nano": int((datetime.now(timezone.utc).timestamp() + 0.1) * 1e9),
            "attributes": {
                "neatlogs.session.id": batch_id,
                "neatlogs.audit.crashed_trace_id": crashed_trace_id,
                "neatlogs.audit.reconstructed": "true"
            }
        }

        spans_payload = [root_span] + reconstructed_spans

        payload = {
            "spans": spans_payload
        }

        resp = requests.post(self.ingest_url, headers=headers, json=payload, timeout=10)
        resp.raise_for_status()
        return resp.json()
