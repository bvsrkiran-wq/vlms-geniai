import json, datetime, os

def generate_report(metrics_path='metrics.json', out_dir='reports'):
    os.makedirs(out_dir, exist_ok=True)
    metrics = {}
    if os.path.exists(metrics_path):
        with open(metrics_path) as f:
            metrics = json.load(f)

    summary = {
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "kpis": {
            "total_violations": metrics.get("violations", 0),
            "compliance_percent": metrics.get("compliance", 100),
            "violation_rate_per_hour": metrics.get("violations_per_hour", 0)
        }
    }
    fname = os.path.join(out_dir, f"report_{datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.json")
    with open(fname, 'w') as f:
        json.dump(summary, f, indent=2)
    print("✅ Report saved to", fname)

if __name__ == "__main__":
    generate_report()
