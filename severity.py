
def assess_severity(category, detections):
    """
    Estimate visual severity using category-specific heuristics.

    This is a preliminary visual estimate, not a verified
    assessment of physical danger or environmental impact.
    """

    category = category.strip().lower()
    count = len(detections)

    if count == 0:
        return {
            "severity": "Unavailable",
            "explanation": (
                "No objects were detected at the selected confidence "
                "threshold. This does not confirm that the scene is safe."
            ),
            "assessment_type": "Heuristic visual estimate",
        }

    max_area = max(
        (d.get("area_ratio", 0) for d in detections),
        default=0,
    )

    total_area = min(
        1.0,
        sum(d.get("area_ratio", 0) for d in detections),
    )

    if category == "pothole":
        if count >= 3 or max_area >= 0.05:
            level = "High"
            reason = (
                "Multiple pothole detections or a large relative "
                "bounding-box area."
            )
        elif count >= 2 or max_area >= 0.02:
            level = "Medium"
            reason = (
                "Multiple detections or a moderately sized "
                "bounding-box region."
            )
        else:
            level = "Low"
            reason = "Few detections with relatively small bounding boxes."

    elif category == "garbage":
        if count >= 10 or max_area >= 0.18:
            level = "High"
            reason = (
                "A large garbage detection region or many detected "
                "garbage objects."
            )
        elif count >= 4 or max_area >= 0.08:
            level = "Medium"
            reason = (
                "Several detections or a moderately sized garbage region."
            )
        else:
            level = "Low"
            reason = (
                "Few detections with relatively small bounding-box areas."
            )

    elif category == "flood":
        if count >= 3 or max_area >= 0.35:
            level = "High"
            reason = (
                "Multiple detected regions or a large relative "
                "bounding-box area."
            )
        elif count >= 2 or max_area >= 0.15:
            level = "Medium"
            reason = (
                "Multiple detections or a moderately large "
                "bounding-box region."
            )
        else:
            level = "Low"
            reason = (
                "Few detections with a relatively small detected region."
            )

    else:
        raise ValueError(f"Unsupported category: {category}")

    return {
        "severity": level,
        "explanation": reason,
        "object_count": count,
        "largest_bbox_area_ratio": round(max_area, 4),
        "total_bbox_area_ratio_capped": round(total_area, 4),
        "assessment_type": "Heuristic visual estimate",
    }
