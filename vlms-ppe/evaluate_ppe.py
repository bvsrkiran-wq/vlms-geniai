import cv2, json, sys, os, subprocess
from ultralytics import YOLO

MODEL_PATH = "yolov8n.pt"
if not os.path.exists(MODEL_PATH):
    url = "https://huggingface.co/Ultralytics/YOLOv8/resolve/main/yolov8n.pt"
    print(f"📥 Downloading model from {url}")
    subprocess.run(["wget", "-O", MODEL_PATH, url], check=True)

model = YOLO(MODEL_PATH)

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

        # Rule: if a person is detected but no helmet detected
        violations += 1 if "person" in detected and "helmet" not in detected else 0

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

    print("✅ PPE Eval completed:", metrics)

if __name__ == "__main__":
    evaluate(sys.argv[1] if len(sys.argv) > 1 else "sample_ppe_video.mp4")
