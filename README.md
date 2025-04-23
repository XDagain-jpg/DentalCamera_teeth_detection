# AI-Enhanced Camera System for Future Teeth Cleaning Robot 

This project is a **software prototype** developed as part of a semester-long medical device software engineering course. The goal was to simulate the vision of a semi-autonomous **dental cleaning robot**, focusing on the **AI-enhanced camera system** responsible for **real-time plaque detection** and **interactive edge enhancement** using live video.

We follow both **IEC 62304 software life cycle principles** and **Agile Scrum** for structured, testable development.

---

## Features

- Real-time **tooth, gum, and plaque detection** using a trained segmentation model.
- Interactive video processing: **pause, overlay, and edge detection**.
- GUI-based launcher to **start, pause, and log** pipeline executions.
- Compliant with **medical software traceability and modularity standards**.

---

## File Structure

| File | Description |
|------|-------------|
| `launcher.py` | A `tkinter`-based GUI to launch and monitor the software pipelines. |
| `self-trained.py` | Core AI pipeline using a self-trained Roboflow segmentation model to detect teeth and apply edge overlays upon user request (`p` key). |
| `self-trained_test.py` | Test-mode version of the AI pipeline with extended timing metrics. |
| `workflow.py` | A simplified pipeline using Roboflow workflows that cooperates with 2 models and provides basic visualization. |
| `workflow_test.py` | Same as `workflow.py` but with timing metrics included. |

---

## Model

The project uses a **self-trained** model hosted on Roboflow:
- `model_id = "dental-2uuam-ex2sf/2"`
- It segments **tooth**, **gum**, and **plaque** from live webcam frames.

To enhance performace, the user can also choose to use another pre-trained model hosted on Roboflow:
- `model_id = "dentalai2/1"`
- It also segments **tooth**, **gum**, and **plaque** from live webcam frames.

---

## How to Run

### Prerequisites
- Python 3.8+
- Dependencies: `opencv-python`, `supervision`, `shapely`, `roboflow inference SDK`, etc.
- A Roboflow API Key (already embedded as `api_key="sDX8QYVWEXhrucll3F4R"`)

### Steps

1. Clone the repo.
2. Install dependencies (consider `pip install -r requirements.txt` if available).
3. Run the launcher:
   ```bash
   python launcher.py
   ```
4. In the GUI:
   - Select a script: `workflow.py` or `self-trained.py`
      - `self-trained.py` is designed for camera and machine with more limited performance, it runs smoother and requires less resources;
      -  `workflow.py` is designed for camera and machine with better performance, it only works better than `self-trained.py` when your camera supports 1080p HD video recording example will be the built-in camera for MacBook Air;
   - (Optional) Toggle **Test Mode** to activate the `_test.py` variants with detailed timing
   - Click **Start**
   - Use `p` key in the window to pause and apply Canny edge overlay
   - Press `q` to quit the video stream

---

## Functional Flow

```
[Live Video Feed]
       ↓
[Teeth Detection Model]
       ↓
[Real-Time Annotated Frame] <---- User can press 'p' ----
                                       ↓
                        [Polygon Mask + Canny Edge Detection]
                                       ↓
                        [Overlayed Output with Edge Highlight]
```

---

## Example Controls

- **`p`** → Pause current frame and apply edge overlay
- **`q`** → Quit video window

---

## Performance Logging

In test mode (`self-trained_test.py` or `workflow_test.py`), logs will output:
- Detection time
- Visualization time
- Total frame processing time
- Frame rate analysis

---

## Development Process

We followed **IEC 62304** to guide:
- Requirements analysis (based on a survey with dentists)
- Software architecture design
- Unit implementation and testing
- System integration and traceability validation

Scrum was used for:
- Sprint planning and retrospectives
- Task management (via Jira)
- Iterative prototyping

---

## Future Work

- Enhance model for **subgingival plaque detection**
- Integrate with a robotic manipulator for physical cleaning
- Improve UI for dentist interaction
- Add force feedback & safety systems for real deployment

---

## References

- [IEC 62304: Medical device software – life cycle processes](https://www.iso.org/standard/38421.html)
- Roboflow Inference SDK
- OpenCV, Shapely, Supervision
