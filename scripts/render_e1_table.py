import json

def generate_e1_table():
    with open('evidence/discovery/e1_results.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    lines = [
        "| Kill Signal | flush_interval | Step Killed | Spans Executed | Spans Received | Root Present? | Last Step Visible | Trace ID |",
        "|:---|:---|:---|:---|:---|:---|:---|:---|"
    ]
    for r in data:
        t = r.get("trace_id")
        tid = f"`{t[:10]}...`" if t else "None"
        lines.append(
            f"| {r['kill_signal']} | {r['flush_interval']}s | {r['killed_at_step']} | "
            f"{r['spans_executed']} | {r['spans_received']} | {r['root_present']} | "
            f"{r['last_step_visible']} | {tid} |"
        )
    return "\n".join(lines)

if __name__ == "__main__":
    print(generate_e1_table())
