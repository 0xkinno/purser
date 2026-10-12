#!/usr/bin/env python3
"""
Experiment E1: Crash Truncation Analysis for neatlogs Python SDK.
Measures the loss of spans and root truncation when a traced process
terminates abnormally (SIGKILL vs SIGTERM) across various flush intervals.
"""
import sys
import os
import time
import json
import signal
import subprocess
import argparse
from pathlib import Path

PROJECT_ID = "66e14d91-d72a-4337-b327-1030c9057892"


def run_child(flush_interval: float, run_id: str):
    """Child worker process running inside WSL/Linux."""
    # Load .env if present
    env_file = Path(__file__).resolve().parent.parent / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    k, v = line.strip().split("=", 1)
                    os.environ.setdefault(k, v)

    import neatlogs

    neatlogs.init(
        api_key=os.environ["NEATLOGS_API_KEY"],
        workflow_name="purser-e1",
        tags=["experiment:e1", f"run:{run_id}"],
        flush_interval=flush_interval,
        capture_logs=True,
    )

    print(f"CHILD_READY PID:{os.getpid()}", flush=True)

    with neatlogs.trace("purser.e1.root", kind="WORKFLOW"):
        for step in range(1, 21):
            print(f"STEP:{step}", flush=True)
            with neatlogs.trace(f"step_{step}", kind="TOOL", step=step):
                time.sleep(0.3)
            print(f"STEP_DONE:{step}", flush=True)

    print("CHILD_COMPLETED", flush=True)


def readback_trace_cli(run_id: str) -> dict:
    """Reads back trace and spans for a specific run_id using neatlogs CLI."""
    cmd = [
        "neatlogs",
        "--project",
        PROJECT_ID,
        "traces",
        "list",
        "--limit",
        "20",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        return {"error": res.stderr}

    try:
        data = json.loads(res.stdout)
    except Exception as e:
        return {"error": f"json parse error: {e}"}

    matched_trace = None
    for tr in data.get("data", {}).get("traces", []):
        tags = tr.get("tags", [])
        if f"run:{run_id}" in tags:
            matched_trace = tr
            break

    if not matched_trace:
        return {"found": False}

    trace_id = matched_trace.get("traceId")
    spans_cmd = [
        "neatlogs",
        "--project",
        PROJECT_ID,
        "traces",
        "spans",
        "list",
        trace_id,
    ]
    spans_res = subprocess.run(spans_cmd, capture_output=True, text=True)
    spans = []
    if spans_res.returncode == 0:
        try:
            spans_data = json.loads(spans_res.stdout)
            spans = spans_data.get("data", {}).get("spans", [])
        except Exception:
            pass

    root_present = any(
        s.get("spanName") == "purser.e1.root" or s.get("spanType") == "WORKFLOW"
        for s in spans
    )

    last_step = 0
    for s in spans:
        name = s.get("spanName", "")
        if name.startswith("step_"):
            try:
                num = int(name.split("_")[1])
                if num > last_step:
                    last_step = num
            except Exception:
                pass

    return {
        "found": True,
        "trace_id": trace_id,
        "spans_received": len(spans),
        "root_present": root_present,
        "last_step_visible": last_step,
        "raw_trace": matched_trace,
    }


def run_harness():
    """Parent harness orchestrating the kill matrix inside WSL."""
    test_matrix = [
        # SIGKILL runs
        {"signal": "SIGKILL", "flush_interval": 5.0, "kill_step": 3},
        {"signal": "SIGKILL", "flush_interval": 5.0, "kill_step": 12},
        {"signal": "SIGKILL", "flush_interval": 5.0, "kill_step": 19},
        {"signal": "SIGKILL", "flush_interval": 1.0, "kill_step": 3},
        {"signal": "SIGKILL", "flush_interval": 1.0, "kill_step": 12},
        {"signal": "SIGKILL", "flush_interval": 1.0, "kill_step": 19},
        {"signal": "SIGKILL", "flush_interval": 0.2, "kill_step": 3},
        {"signal": "SIGKILL", "flush_interval": 0.2, "kill_step": 12},
        {"signal": "SIGKILL", "flush_interval": 0.2, "kill_step": 19},
        # SIGTERM runs
        {"signal": "SIGTERM", "flush_interval": 5.0, "kill_step": 12},
        {"signal": "SIGTERM", "flush_interval": 1.0, "kill_step": 12},
        {"signal": "SIGTERM", "flush_interval": 0.2, "kill_step": 12},
    ]

    results = []
    script_path = "/mnt/c/Users/hp/Downloads/PURSER/experiments/e1_crash_truncation.py"
    python_bin = "/tmp/purser_wsl_venv/bin/python3"

    for i, test in enumerate(test_matrix, 1):
        sig_name = test["signal"]
        flush_int = test["flush_interval"]
        kill_step = test["kill_step"]
        run_id = f"e1-{sig_name.lower()}-step{kill_step}-flush{flush_int}-{int(time.time())}"

        print(f"\n[{i}/{len(test_matrix)}] Running {sig_name} at step {kill_step} (flush_interval={flush_int}s)...")

        cmd = [
            python_bin,
            script_path,
            "--child",
            "--flush-interval",
            str(flush_int),
            "--run-id",
            run_id,
        ]

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        child_pid = None
        executed_step = 0
        killed = False

        while True:
            line = proc.stdout.readline()
            if not line:
                break
            line_str = line.strip()
            if line_str.startswith("CHILD_READY PID:"):
                child_pid = int(line_str.split("CHILD_READY PID:")[1])
            elif line_str.startswith("STEP:"):
                current_step = int(line_str.split("STEP:")[1])
                executed_step = current_step
                if current_step == kill_step and child_pid:
                    time.sleep(0.15)  # Kill midway through the 0.3s span
                    sig = signal.SIGKILL if sig_name == "SIGKILL" else signal.SIGTERM
                    os.kill(child_pid, sig)
                    killed = True
                    print(f" -> Sent {sig_name} to PID {child_pid} at step {current_step}")
                    break

        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            print(" -> Timed out waiting after SIGTERM, killing process forcefully")
            proc.kill()
            proc.wait()

        results.append({
            "kill_signal": sig_name,
            "flush_interval": flush_int,
            "killed_at_step": kill_step,
            "spans_executed": executed_step,
            "run_id": run_id,
        })

    print("\nAll runs complete. Waiting 35 seconds for neatlogs backend ingestion and finalization...")
    time.sleep(35)

    print("\nReading back traces from neatlogs...")
    final_table = []
    for row in results:
        run_id = row["run_id"]
        readback = readback_trace_cli(run_id)
        row["spans_received"] = readback.get("spans_received", 0)
        row["root_present"] = readback.get("root_present", False)
        row["last_step_visible"] = readback.get("last_step_visible", 0)
        row["trace_id"] = readback.get("trace_id")
        final_table.append(row)
        print(f"Run {run_id}: received={row['spans_received']} spans, root={row['root_present']}, last_step={row['last_step_visible']}")

    # Save to evidence/discovery/e1_results.json
    out_dir = Path("/mnt/c/Users/hp/Downloads/PURSER/evidence/discovery")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "e1_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(final_table, f, indent=2)

    print(f"\nSaved raw results to {out_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--child", action="store_true")
    parser.add_argument("--flush-interval", type=float, default=5.0)
    parser.add_argument("--run-id", type=str, default="test")
    args = parser.parse_args()

    if args.child:
        run_child(args.flush_interval, args.run_id)
    else:
        run_harness()
