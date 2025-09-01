import cv2, json, sys, os
from ultralytics import YOLO

MODEL_PATH = "yolov8n.pt"
if not os.path.exists(MODEL_PATH):
    !wget -O yolov8n.pt https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt

model = YOLO(MODEL_PATH)

def evaluate(video_path):
    if not os.path.exists(video_path):
        print(f"❌ File not found: {video_path}")
        return

    cap = cv2.VideoCapture(video_path)
    frame_count, events = 0, 0

    while True:
        ret, frame = cap.read()
        if not ret: break
        frame_count += 1

        results = model(frame, verbose=False)[0]
        people = sum(1 for c in results.boxes.cls if int(c) == 0)  # class 0 = person

        # Example rule: hazard if > 5 people detected
        if people > 5:
            events += 1

    cap.release()

    results = {
        "frames": frame_count,
        "hazard_events": events,
        "avg_events_per_min": round(events / (frame_count/30/60), 2) if frame_count else 0
    }

    with open("metrics.json", "w") as f: json.dump(results, f, indent=2)
    with open("metrics.txt", "w") as f: f.write(str(results))

    print("✅ Geni AI Video Analytics complete. Results saved.")
    print(results)

if __name__ == "__main__":
    video_path = sys.argv[1] if len(sys.argv) > 1 else "sample_analytics_video.mp4"
    evaluate(video_path)

