import cv2, json, sys, os, subprocess
from ultralytics import YOLO

MODEL_PATH = "ppe_yolov8.pt"

if not os.path.exists(MODEL_PATH):
    url = "https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n-helmet.pt"
    print(f"📥 Downloading YOLOv8 PPE model from {url}...")
    subprocess.run(["wget", "-O", MODEL_PATH, url], check=True)

# Load YOLOv8 model
model = YOLO(MODEL_PATH)

# Define expected PPE classes for compliance
REQUIRED = {"helmet", "vest", "mask", "gloves", "glasses", "boots"}

def evaluate(video_path):
    if not os.path.exists(video_path):
        print(f"❌ File not found: {video_path}")
        return

    cap = cv2.VideoCapture(video_path)
    frame_count, violations = 0, 0

    while True:
        ret, frame = cap.read()
        if not ret: break
        frame_count += 1

        results = model(frame, verbose=False)[0]
        detected = {model.names[int(c)] for c in results.boxes.cls}

        # Rule: person present but missing PPE
        if "person" in detected and not REQUIRED.issubset(detected):
            violations += 1

    cap.release()

    compliance = 100 - ((violations / frame_count) * 100 if frame_count else 0)
    metrics = {
        "frames": frame_count,
        "ppe_violations": violations,
        "compliance_percent": round(compliance, 2),
        "violations_per_hour": round(violations / (frame_count/30/3600), 2) if frame_count else 0
    }

    with open("metrics.json", "w") as f: json.dump(metrics, f, indent=2)
    with open("metrics.txt", "w") as f: f.write(str(metrics))

    print("✅ PPE Evaluation complete:", metrics)

if __name__ == "__main__":
    video = sys.argv[1] if len(sys.argv) > 1 else "sample_ppe_video.mp4"
    evaluate(video)
