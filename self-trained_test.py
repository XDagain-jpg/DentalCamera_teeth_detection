from inference import InferencePipeline
from inference.core.interfaces.camera.entities import VideoFrame
import cv2
import supervision as sv
import numpy as np
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
import time, threading


_total_wf_ms = 0.0 #total processing time
_outline = 0.0 #record how long it takes to provide visualization
_detect = 0.0 #record how long it takes to detect
_last_frame = 0.0
_between_frames = 0.0
_wf_frames = 0
_lock = threading.Lock()


def create_instance_segmentation_polygon(points):
    """Convert instance segmentation points into a Shapely polygon."""
    polygon_coords = [(p["x"], p["y"]) for p in points]
    return Polygon(polygon_coords)

def get_combined_tooth_polygon(predictions):
    polygons = []
    for pred in predictions["predictions"]:
        if pred["class"] == "Tooth" and "points" in pred:
            polygon = create_instance_segmentation_polygon(pred["points"])
            if polygon.is_valid and not polygon.is_empty:
                polygons.append(polygon)

    if not polygons:
        return None  # No valid teeth polygons found

    combined_polygon = unary_union(polygons)  # Union of all polygons
    return combined_polygon

def create_binary_mask_from_polygon(image_shape, polygon):
    mask = np.zeros(image_shape[:2], dtype=np.uint8)
    height, width = mask.shape

    for y in range(height):
        for x in range(width):
            if polygon.contains(Point(x, y)):
                mask[y, x] = 255

    return mask

def preprocess_image(image, mask):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8)).apply(gray)
    blurred = cv2.GaussianBlur(clahe, (5, 5), 0)
    edges = cv2.Canny(blurred, 40, 70)
    return cv2.bitwise_and(edges, edges, mask=mask)

def overlay_edges_on_image(image, edges, color=(0, 0, 255)):
    if len(image.shape) == 2 or image.shape[2] == 1:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    overlay = image.copy()
    edge_mask = edges > 0
    overlay[edge_mask] = color  
    return overlay



def my_custom_sink(predictions: dict, video_frame: VideoFrame):
    global _total_wf_ms, _wf_frames, _last_frame, _between_frames, _outline, _detect
    
    capture_ts_attr = getattr(video_frame, "frame_timestamp", None)
    capture_ts = capture_ts_attr.timestamp()
    if _wf_frames > 0:
        _between_frames += (capture_ts -_last_frame) * 1000
    
    t_callback = time.time()

    #print(f"[Frame] capture from last time: {t_callback - capture_ts:.3f}s")
    # (A) If VideoFrame has a capture ts, grab it (attribute name may vary)

    labels = [p["class"] for p in predictions["predictions"]]
    # load our predictions into the Supervision Detections api
    detections = sv.Detections.from_inference(predictions)
    # annotate the frame using our supervision annotator, the video_frame, the predictions (as supervision Detections), and the prediction labels
    polygon_annotator = sv.PolygonAnnotator()

    image = label_annotator.annotate(
        scene=video_frame.image.copy(), detections=detections, labels=labels
    )
    annotated_frame = polygon_annotator.annotate(
        image,
        detections=detections
    )

    cv2.imshow("Predictions", annotated_frame)
    
    t_done = time.time()

    key = cv2.waitKey(10) & 0xFF
    if key == ord('q'):
       cv2.destroyAllWindows()
    elif key == ord('p'):
        t_pause = time.time()
        image = video_frame.image
        polygon = get_combined_tooth_polygon(predictions)
        if polygon:
            mask = create_binary_mask_from_polygon(image.shape, polygon)
            edges = preprocess_image(image, mask)
    
        overlay = overlay_edges_on_image(image, edges)

        image = label_annotator.annotate(
            scene=overlay, detections=detections, labels=labels
        )
        annotated_frame = polygon_annotator.annotate(
            image,
            detections=detections
        )
        t_pause_done = time.time()
        print(f"For this paused frames, process time: {t_pause_done-t_pause:.3f} s")
        cv2.imshow("Predictions", annotated_frame)
        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == ord('p'):
                break
    
    outline_ms = (t_done - t_callback) * 1000
    detect_ms = (t_callback - capture_ts) * 1000
    total_ms = (t_done - capture_ts) * 1000

    with _lock:
        _outline += outline_ms
        _detect += detect_ms
        _total_wf_ms += total_ms
        _wf_frames += 1
        _last_frame = capture_ts
    
    if _wf_frames % 10 == 0:
        print(f"Avg after {_wf_frames} frames, detect time: {_detect/_wf_frames:.1f} ms")
        print(f"Outline time: {_outline/_wf_frames:.1f} ms")
        print(f"Total Processing time: {_total_wf_ms/_wf_frames:.1f} ms")
        print(f"Between each frame captured: {_between_frames/_wf_frames:.1f} ms")



# create a bounding box annotator and label annotator to use in our custom sink
label_annotator = sv.LabelAnnotator()

def my_custom_sink_example(predictions: dict, video_frame: VideoFrame):
    # get the text labels for each prediction
    #print(predictions)
    labels = [p["class"] for p in predictions["predictions"]]
    # load our predictions into the Supervision Detections api
    detections = sv.Detections.from_inference(predictions)
    # annotate the frame using our supervision annotator, the video_frame, the predictions (as supervision Detections), and the prediction labels
    polygon_annotator = sv.PolygonAnnotator()
    
    image = label_annotator.annotate(
        scene=video_frame.image.copy(), detections=detections, labels=labels
    )
    annotated_frame = polygon_annotator.annotate(
        image,
        detections=detections
    )
    #image = box_annotator.annotate(image, detections=detections)
    # display the annotated image
    cv2.imshow("Predictions", annotated_frame)
    cv2.waitKey(1)


api_key = "sDX8QYVWEXhrucll3F4R"
# initialize a pipeline object

pipeline = InferencePipeline.init(
    model_id= "dental-2uuam-ex2sf/2", # Roboflow model to use "tooth_gums/2",
    video_reference=0, # Path to video, device id (int, usually 0 for built in webcams), or RTSP stream url
    on_prediction= my_custom_sink,  #my_custom_sink_example ,   # Function to run after each prediction
    api_key = api_key
)


pipeline.start()
pipeline.join()

