
from summarizer import generate_report
from severity import assess_severity

category = "Pothole"

detections = [
    {"class": "pothole", "confidence": 0.777, "area_ratio": 0.0602},
    {"class": "pothole", "confidence": 0.532, "area_ratio": 0.0081},
    {"class": "pothole", "confidence": 0.395, "area_ratio": 0.0461},
]

severity_result = assess_severity(category, detections)
report = generate_report(category, detections, severity_result)

print("\n--- ECOINSPECT INCIDENT REPORT ---\n")
print(report)
