import json, datetime, os, time, smtplib, requests, schedule
from email.message import EmailMessage

CONFIG_PATH = "alerts_config.json"

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {"email": {"enabled": False}, "webhook": {"enabled": False}}

def send_email(subject, body, attachment_path=None):
    cfg = load_config().get("email", {})
    if not cfg.get("enabled"): return
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = cfg["user"]
    msg["To"] = ",".join(cfg["recipients"])
    msg.set_content(body)
    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, "rb") as f:
            msg.add_attachment(f.read(), maintype="application", subtype="json", filename=os.path.basename(attachment_path))
    with smtplib.SMTP(cfg["smtp_host"], cfg["smtp_port"]) as server:
        server.starttls()
        server.login(cfg["user"], os.getenv(cfg["password_env"], ""))
        server.send_message(msg)
    print("📧 Email sent")

def send_webhook(payload):
    cfg = load_config().get("webhook", {})
    if not cfg.get("enabled"): return
    r = requests.post(cfg["url"], json=payload, timeout=5)
    print("🔗 Webhook sent:", r.status_code)

def generate_report(metrics_path="metrics.json", out_dir="reports"):
    os.makedirs(out_dir, exist_ok=True)
    metrics = {}
    if os.path.exists(metrics_path):
        with open(metrics_path) as f: metrics = json.load(f)

    summary = {
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "kpis": {
            "frames": metrics.get("frames", 0),
            "ppe_violations": metrics.get("ppe_violations", metrics.get("hazard_events", 0)),
            "compliance_percent": metrics.get("compliance_percent", 100)
        }
    }
    fname = os.path.join(out_dir, f"report_{datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.json")
    with open(fname, "w") as f: json.dump(summary, f, indent=2)
    print("✅ Report saved:", fname)

    send_email("Daily Compliance Report", "Please find attached the daily compliance report.", fname)
    send_webhook(summary)

# Schedule daily run at 06:00 UTC
schedule.every().day.at("06:00").do(generate_report)

if __name__ == "__main__":
    print("⏳ Scheduler started. Running immediate test report...")
    generate_report()
    print("Will auto-run daily at 06:00 UTC...")
    while True:
        schedule.run_pending()
        time.sleep(30)
