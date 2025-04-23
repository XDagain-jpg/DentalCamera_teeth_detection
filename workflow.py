from inference import InferencePipeline
import cv2
from inference.core.interfaces.camera.entities import VideoFrame



def my_sink(result, video_frame):
    if result.get("model_comparison_visualization"):
        cv2.imshow("Workflow Image", result["model_comparison_visualization"].numpy_image)
        cv2.waitKey(1)
    


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