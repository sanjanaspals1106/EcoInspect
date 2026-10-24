
import io

import pandas as pd
import streamlit as st
from PIL import Image

from detector import detect_objects
from severity import assess_severity
from summarizer import generate_report


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="EcoInspect | Environmental AI",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# Styling
# --------------------------------------------------

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .main-title {
        font-size: 2.6rem;
        font-weight: 750;
        color: #245c45;
        margin-bottom: 0;
    }

    .subtitle {
        font-size: 1rem;
        color: #64748b;
        margin-top: 0.3rem;
        margin-bottom: 1.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Header
# --------------------------------------------------

st.markdown(
    '<div class="main-title">🌿 EcoInspect</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    'Environmental Issue Detection, Severity Assessment '
    'and AI-Assisted Reporting'
    '</div>',
    unsafe_allow_html=True,
)

st.divider()


# --------------------------------------------------
# Sidebar: model selection
# --------------------------------------------------

with st.sidebar:
    st.header("Inspection Settings")

    category = st.selectbox(
        "Select the detection model",
        options=["Pothole", "Garbage", "Flood"],
        index=0,
        key="selected_category",
    )

    confidence = st.slider(
        "Confidence threshold",
        min_value=0.10,
        max_value=0.90,
        value=0.25,
        step=0.05,
    )

    st.divider()

    st.markdown("### Model mapping")

    st.write("**Pothole:** `pothole_best.pt`")
    st.write("**Garbage:** `garbage_best.pt`")
    st.write("**Flood:** `flood_best.pt`")

    st.caption(
        "Choose the model that matches the image. "
        "The app does not automatically classify image categories."
    )


# --------------------------------------------------
# Upload image
# --------------------------------------------------

st.header("1. Upload an Environmental Image")

uploaded_file = st.file_uploader(
    "Choose an image to inspect",
    type=["jpg", "jpeg", "png", "webp"],
    key="image_upload",
)

if uploaded_file is None:
    st.info(
        "Upload an image, select its category in the sidebar, "
        "and click Analyze Image."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Computer Vision")
        st.write(
            "Detect potholes, garbage, or flood-related objects "
            "using your trained YOLO models."
        )

    with col2:
        st.subheader("Severity Assessment")
        st.write(
            "Estimate visual severity using transparent, "
            "preliminary rules."
        )

    with col3:
        st.subheader("AI Report")
        st.write(
            "Generate a concise environmental inspection report "
            "using Groq."
        )


# --------------------------------------------------
# Process uploaded image
# --------------------------------------------------

if uploaded_file is not None:
    try:
        image_bytes = uploaded_file.getvalue()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        preview_col, info_col = st.columns(2)

        with preview_col:
            st.subheader("Uploaded Image")
            st.image(image, use_container_width=True)

        with info_col:
            st.subheader("Current Configuration")
            st.write(f"**Selected model:** {category}")
            st.write(f"**Confidence threshold:** {confidence:.2f}")
            st.write(
                f"**Image dimensions:** {image.width} × {image.height}"
            )
            st.write(f"**Filename:** {uploaded_file.name}")

        st.divider()

        # Explicitly analyze using the selected category.
        if st.button(
            f"Analyze Image with {category} Model",
            type="primary",
            use_container_width=True,
        ):
            with st.spinner(f"Running the {category} model..."):
                detection_result = detect_objects(
                    image=image,
                    category=category,
                    confidence=confidence,
                )

                severity_result = assess_severity(
                    category,
                    detection_result["detections"],
                )

            st.session_state["ecoinspect_result"] = {
                "image_bytes": image_bytes,
                "category": category,
                "confidence": confidence,
                "detection": detection_result,
                "severity": severity_result,
            }

            # Clear a report belonging to an older analysis.
            st.session_state.pop("ecoinspect_report", None)

        # Display only results matching the current image and settings.
        inspection = st.session_state.get("ecoinspect_result")

        if inspection is not None:
            is_current_inspection = (
                inspection["image_bytes"] == image_bytes
                and inspection["category"] == category
                and inspection["confidence"] == confidence
            )

            if not is_current_inspection:
                st.info(
                    "The image or settings have changed. Click "
                    "Analyze Image to update the results."
                )

            else:
                result = inspection["detection"]
                severity = inspection["severity"]

                st.divider()
                st.header("2. Detection Results")

                metric1, metric2, metric3 = st.columns(3)

                metric1.metric(
                    "Objects Detected",
                    result["object_count"],
                )

                metric2.metric(
                    "Visual Severity Estimate",
                    severity["severity"],
                )

                metric3.metric(
                    "Inference Time",
                    f'{result["inference_time"]:.3f} seconds',
                )

                annotated_col, severity_col = st.columns([1.2, 1])

                with annotated_col:
                    st.subheader("Annotated Image")

                    st.image(
                        result["annotated_image"],
                        channels="RGB",
                        use_container_width=True,
                    )

                    output_buffer = io.BytesIO()

                    Image.fromarray(
                        result["annotated_image"]
                    ).save(
                        output_buffer,
                        format="JPEG",
                    )

                    st.download_button(
                        "Download Annotated Image",
                        data=output_buffer.getvalue(),
                        file_name="ecoinspect_annotated.jpg",
                        mime="image/jpeg",
                    )

                with severity_col:
                    st.subheader("Severity Assessment")
                    st.write(f"**Estimate:** {severity['severity']}")
                    st.write(severity["explanation"])

                    st.caption(
                        "This is a preliminary heuristic estimate, "
                        "not a verified measure of real-world danger."
                    )

                # ------------------------------------------
                # Detection table
                # ------------------------------------------

                st.subheader("3. Individual Detections")

                if result["detections"]:
                    rows = []

                    for index, detection in enumerate(
                        result["detections"],
                        start=1,
                    ):
                        x1, y1, x2, y2 = detection["bbox"]

                        rows.append(
                            {
                                "Detection": index,
                                "Class": detection["class"],
                                "Confidence": round(
                                    detection["confidence"], 4
                                ),
                                "X1": round(x1, 2),
                                "Y1": round(y1, 2),
                                "X2": round(x2, 2),
                                "Y2": round(y2, 2),
                                "Image Area Ratio": round(
                                    detection["area_ratio"], 4
                                ),
                            }
                        )

                    st.dataframe(
                        pd.DataFrame(rows),
                        use_container_width=True,
                        hide_index=True,
                    )

                else:
                    st.warning(
                        "No objects were detected at this confidence "
                        "threshold. This does not prove the scene "
                        "is free of environmental issues."
                    )

                # ------------------------------------------
                # AI report generation
                # ------------------------------------------

                st.divider()
                st.header("4. AI-Generated Inspection Report")

                st.write(
                    "Generate a report grounded in the detections "
                    "and the rule-based severity estimate."
                )

                if st.button(
                    "Generate Inspection Report",
                    use_container_width=True,
                ):
                    with st.spinner("Generating report with Groq..."):
                        report = generate_report(
                            inspection["category"],
                            result["detections"],
                            severity,
                        )

                    st.session_state["ecoinspect_report"] = report

                report = st.session_state.get("ecoinspect_report")

                if report:
                    st.markdown(report)

                    st.download_button(
                        "Download Inspection Report",
                        data=report,
                        file_name="ecoinspect_report.txt",
                        mime="text/plain",
                    )

    except Exception as error:
        st.error(f"Image processing failed: {error}")
        st.exception(error)


# --------------------------------------------------
# Footer
# --------------------------------------------------

st.divider()

st.caption(
    "EcoInspect | Hybrid Computer Vision and NLP Framework | "
    "AI-assisted environmental inspection"
)
