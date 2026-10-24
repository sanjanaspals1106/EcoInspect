
from PIL import Image
from detector import detect_objects

image_path = input("Enter the path to a test image: ").strip()
category = input(
    "Select model (Flood / Garbage / Pothole): "
).strip().title()

image = Image.open(image_path).convert("RGB")

result = detect_objects(
    image=image,
    category=category,
    confidence=0.25,
)

print("\nDetection Results")
print("-----------------")
print("Category:", category)
print("Objects detected:", result["object_count"])
print("Inference time:", result["inference_time"], "seconds")
print("Detections:", result["detections"])

annotated = Image.fromarray(result["annotated_image"])
annotated.save("results/test_annotated.jpg")

print("\nAnnotated image saved to results/test_annotated.jpg")
