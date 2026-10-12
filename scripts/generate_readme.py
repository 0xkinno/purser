import json
import os

def render_table(summary):
    v1 = summary["v1_baseline"]
    v2 = summary["v2_purser"]
    delta = summary["delta"]

    lines = [
        "| Metric | Baseline (v1-naive) | Purser (v2) | Delta / Protection |",
        "|:---|:---|:---|:---|",
        f"| Duplicate refunds | {v1['duplicate_refunds']} | {v2['duplicate_refunds']} | {delta['duplicate_refunds_prevented']} prevented (P1) |",
        f"| Over-refunds | {v1['over_refunds']} | {v2['over_refunds']} | {delta['over_refunds_prevented']} prevented (P2) |",
        f"| Wrong customer refunds | {v1['wrong_customer_refunds']} | {v2['wrong_customer_refunds']} | {delta['wrong_customer_prevented']} prevented (P4) |",
        f"| Unaccounted at muster | {v1['unaccounted_muster']} | {v2['unaccounted_muster']} | {delta['unaccounted_muster_eliminated']} eliminated (P9) |",
        f"| Crash recovery rate | {int(v1['recovery_success_rate']*100)}% | {int(v2['recovery_success_rate']*100)}% | +{int((v2['recovery_success_rate']-v1['recovery_success_rate'])*100)}% |",
        f"| Median latency | {v1['median_latency_ms']} ms | {v2['median_latency_ms']} ms | -{v1['median_latency_ms']-v2['median_latency_ms']} ms |",
        f"| Cost per ticket | ${v1['cost_per_ticket_usd']:.3f} | ${v2['cost_per_ticket_usd']:.3f} | {delta['cost_reduction_percent']}% reduction |"
    ]
    return "\n".join(lines)

def main():
    summary_path = os.path.join("evidence", "drills", "summary.json")
    if not os.path.exists(summary_path):
        print("Summary file does not exist.")
        return

    with open(summary_path, "r", encoding="utf-8") as f:
        summary = json.load(f)

    drills_table = render_table(summary)
    print("Generated Drills Table:\n")
    print(drills_table)

if __name__ == "__main__":
    main()
