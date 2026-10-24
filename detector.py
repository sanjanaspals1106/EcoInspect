
import time
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO


# --------------------------------------------------
# Model configuration
# --------------------------------------------------

MODEL_PATHS = {
    "Flood": Path("models/flood_best.pt"),
    "Garbage": Path("models/garbage_best.pt"),
    "Pothole": Path("models/pothole_best.pt"),
}

COLORS = {
    "Flood": (255, 140, 0),
    "Garbage": (30, 180, 90),
    "Pothole": (60, 100, 255),
}

_loaded_models = {}


# --------------------------------------------------
# Load models once
# --------------------------------------------------

def get_model(category):
    if category not in MODEL_PATHS:
        raise ValueError(f"Unknown category: {category}")

    if category not in _loaded_models:
        model_path = MODEL_PATHS[category]

        if not model_path.is_absolute():
            model_path = Path(__file__).resolve().parent / model_path

        if not model_path.exists():
            raise FileNotFoundError(
                f"Model file not found: {model_path}"
            )

        print(f"Loading {category} model from: {model_path}")
        _loaded_models[category] = YOLO(str(model_path))

    return _loaded_models[category]


# --------------------------------------------------
# Custom annotation rendering
# --------------------------------------------------

def draw_annotations(image, detections, category):
    annotated = np.array(image.convert("RGB")).copy()
    height, width = annotated.shape[:2]

    color = COLORS.get(category, (40, 180, 100))
    thickness = max(2, round(min(height, width) / 350))
    font_scale = max(0.55, min(height, width) / 900)
    font_thickness = max(1, thickness - 1)

    for detection in detections:
        x1, y1, x2, y2 = map(int, detection["bbox"])

        x1 = max(0, min(x1, width - 1))
        x2 = max(0, min(x2, width - 1))
        y1 = max(0, min(y1, height - 1))
        y2 = max(0, min(y2, height - 1))

        if x2 <= x1 or y2 <= y1:
            continue

        label = (
            f'{detection["class"].capitalize()} '
            f'{detection["confidence"]:.2f}'
        )

        cv2.rectangle(
            annotated,
            (x1, y1),
            (x2, y2),
            color,
            thickness,
        )

        (text_width, text_height), baseline = cv2.getTextSize(
            label,
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            font_thickness,
        )

        label_top = max(0, y1 - text_height - baseline - 8)
        label_bottom = label_top + text_height + baseline + 8
        label_right = min(width - 1, x1 + text_width + 12)

        cv2.rectangle(
            annotated,
            (x1, label_top),
            (label_right, label_bottom),
            color,
            -1,
        )

        cv2.putText(
            annotated,
            label,
            (x1 + 6, label_bottom - baseline - 4),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            (255, 255, 255),
            font_thickness,
            cv2.LINE_AA,
        )

    return annotated


# --------------------------------------------------
# Object detection
# --------------------------------------------------

def detect_objects(image, category, confidence=0.25):
    """
    Run YOLO inference, print diagnostic information,
    filter detections by the requested threshold,
    and return annotations and detection details.
    """

    model = get_model(category)

    if image.mode != "RGB":
        image = image.convert("RGB")

    print("\n--- ECOINSPECT DETECTION DEBUG ---")
    print(f"Category: {category}")
    print(f"Model path: {MODEL_PATHS[category]}")
    print(f"Requested confidence: {confidence}")
    print(f"Image size: {image.size}")

    start_time = time.perf_counter()

    # Use a low inference threshold for diagnosis.
    # Filter against the user's actual threshold below.
    results = model.predict(
        source=image,
        conf=0.01,
        verbose=False,
    )

    inference_time = time.perf_counter() - start_time
    result = results[0]

    raw_boxes = result.boxes

    print(f"Raw detections at 0.01: {len(raw_boxes)}")

    detections = []

    image_area = image.width * image.height

    for box in raw_boxes:
        class_id = int(box.cls[0].item())
        score = float(box.conf[0].item())

        print(
            f"Raw prediction: {model.names[class_id]}, "
            f"confidence={score:.4f}"
        )

        # Apply the threshold selected in Streamlit.
        if score < confidence:
            continue

        x1, y1, x2, y2 = box.xyxy[0].tolist()

        area_ratio = (
            max(0, x2 - x1) * max(0, y2 - y1)
        ) / image_area

        detections.append({
            "class": model.names[class_id],
            "confidence": score,
            "bbox": [
                round(x1, 2),
                round(y1, 2),
                round(x2, 2),
                round(y2, 2),
            ],
            "area_ratio": area_ratio,
        })

    print(f"Detections above selected threshold: {len(detections)}")
    print("--- END DEBUG ---\n")

    annotated_image = draw_annotations(
        image,
        detections,
        category,
    )

    return {
        "annotated_image": annotated_image,
        "detections": detections,
        "object_count": len(detections),
        "inference_time": round(inference_time, 4),
    }
