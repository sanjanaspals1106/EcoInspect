# EcoInspect

A hybrid Computer Vision and Natural Language Processing application
for environmental issue detection, severity assessment, and
automated inspection summaries.

## Models
- Flood detection: YOLOv8s
- Garbage detection: YOLOv8s
- Pothole detection: YOLOv8n

## Technology Stack
- Python
- Ultralytics YOLO
- Streamlit
- Groq API
- OpenCV
- Plotly

## Setup
1. Create and activate a Python virtual environment.
2. Install dependencies from requirements.txt.
3. Configure GROQ_API_KEY in .env.
4. Place the trained model weights in models/.
5. Run the application with streamlit run app.py.
