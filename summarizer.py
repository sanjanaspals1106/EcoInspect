
import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()


def generate_report(category, detections, severity_result):
    """Generate a factual report grounded in detector output."""

    if not detections:
        return (
            f"No {category.lower()} objects were detected at the "
            "selected confidence threshold. This does not establish "
            "that the scene is free of environmental issues."
        )

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return (
            f"Environmental Inspection Report\n\n"
            f"Category: {category}\n"
            f"Detected objects: {len(detections)}\n"
            f"Visual severity estimate: {severity_result['severity']}\n"
            f"Basis: {severity_result['explanation']}\n\n"
            "The Groq API key is not configured, so an AI-generated "
            "narrative is unavailable."
        )

    client = Groq(api_key=api_key)

    detection_summary = [
        {
            "class": item["class"],
            "confidence": round(item["confidence"], 3),
            "bbox_area_ratio": round(item.get("area_ratio", 0), 4),
        }
        for item in detections
    ]

    prompt = f"""
Write a concise environmental inspection report using only these facts.

Category: {category}
Detection count: {len(detections)}
Detections: {detection_summary}
Rule-based visual severity estimate: {severity_result['severity']}
Severity explanation: {severity_result['explanation']}

Requirements:
- Use a professional, neutral tone.
- Include a short heading, findings, and a recommended next step.
- Clearly call the severity a heuristic visual estimate.
- Do not claim to know the physical size, cause, location, or real-world
  danger of an issue unless explicitly provided.
- Do not invent weather conditions, people, property damage, or context.
- Do not change or override the supplied severity.
- Recommend human verification before operational decisions.
- Keep the report under 150 words.
"""

    try:
        
        response = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Write concise, factual environmental reports. "
                        "Never invent locations, dimensions, causes, or "
                        "conditions. Preserve the supplied severity."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            reasoning_effort="low",
            include_reasoning=False,
            temperature=0.2,
            max_completion_tokens=800,
        )

        choice = response.choices[0]
        report = (choice.message.content or "").strip()

        if not report:
            raise ValueError(
                f"Groq returned empty content. "
                f"Finish reason: {choice.finish_reason}"
            )

        if choice.finish_reason == "length":
            report += (
                "\n\nNote: The generated report may be incomplete."
            )

        return report


    except Exception as error:
        print(f"Groq report generation failed: {error}")

        return (
            f"Environmental Inspection Report\n\n"
            f"Category: {category}\n"
            f"Detected objects: {len(detections)}\n"
            f"Visual severity estimate: {severity_result['severity']}\n"
            f"Basis: {severity_result['explanation']}\n\n"
            "AI narrative generation failed. The factual summary above "
            "is available without the language model."
        )
