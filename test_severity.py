
from severity import assess_severity

detections = [
    {"class": "pothole", "confidence": 0.777, "area_ratio": 0.0602},
    {"class": "pothole", "confidence": 0.532, "area_ratio": 0.0081},
    {"class": "pothole", "confidence": 0.395, "area_ratio": 0.0461},
]

result = assess_severity("Pothole", detections)

print("Severity:", result["severity"])
print("Explanation:", result["explanation"])
print("Details:", result)
