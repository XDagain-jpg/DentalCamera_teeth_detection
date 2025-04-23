from inference import InferencePipeline
import cv2
from inference.core.interfaces.camera.entities import VideoFrame
import time, threading


_total_wf_ms = 0.0
_last_frame = 0.0
_between_frames = 0.0
_wf_frames = 0
_lock = threading.Lock()


def my_sink(result, video_frame):
    global _total_wf_ms, _wf_frames, _last_frame, _between_frames
    
    capture_ts = getattr(video_frame, "frame_timestamp", None)
    if _wf_frames > 0:
        # _between_frames += (capture_ts -_last_frame) * 1000
        _between_frames += (capture_ts.timestamp() - _last_frame) * 1000 ###########################
    
    
    if result.get("model_comparison_visualization"):
        cv2.imshow("Workflow Image", result["model_comparison_visualization"].numpy_image)
        t_done = time.time()
        cv2.waitKey(1)
        # elapsed_ms = (t_done - capture_ts) * 1000
        elapsed_ms = (t_done - capture_ts.timestamp()) * 1000 #################################

        with _lock:
            _total_wf_ms += elapsed_ms
            _wf_frames += 1
            # _last_frame = capture_ts

            _last_frame = capture_ts.timestamp() ###############################################
    
        if _wf_frames % 10 == 0:
            # print(f"Avg after {_wf_frames} frames, process time: {_total_wf_ms/_wf_frames:.1f} ms")
            # print(f"Between each frame captured: {_between_frames/_wf_frames:.1f} ms")

            print(f"Avg after {_wf_frames} frames, process time: {_total_wf_ms/_wf_frames:.1f} ms", flush=True)
            print(f"Between each frame captured: {_between_frames/_wf_frames:.1f} ms", flush=True)
    


# initialize a pipeline object
pipeline = InferencePipeline.init_with_workflow(
    api_key="sDX8QYVWEXhrucll3F4R",
    workspace_name="xd-pnva5",
    workflow_id="custom-workflow-2",
    video_reference=0, # Path to video, device id (int, usually 0 for built in webcams), or RTSP stream url
    max_fps=30,
    on_prediction=my_sink
)
pipeline.start() #start the pipeline
pipeline.join() #wait for the pipeline thread to finish