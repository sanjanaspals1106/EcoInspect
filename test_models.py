from ultralytics import YOLO
from pathlib import Path

models = {
    "Flood": "models/flood_best.pt",
    "Garbage": "models/garbage_best.pt",
    "Pothole": "models/pothole_best.pt",
}

for name, path in models.items():
    print(f"\nTesting {name} model...")

    try:
        model = YOLO(path)
        print("Classes:", model.names)
        print("Model loaded successfully.")

    except Exception as e:
        print(f"ERROR loading {name}: {e}")

print("\nModel loading tests complete.")
