import logging

import cv2

from db import agents_table, DBQuery
from utils import save_frame
from ultralytics import YOLO
import supervision as sv
from config import ROOT_DIR


# monitor cameras
def monitor_camera_stream(camera, ai_processor, camera_url, save_footage, agent_id):
    """
    Continuously process the video stream from a single camera.
    """
    frame_count = 0
    cap = cv2.VideoCapture(camera_url)
    if not cap.isOpened():
        logging.error(f"Failed to open camera stream: {camera_url}")
        return

    try:
        while agents_table.get(DBQuery.id == agent_id)["running"]:
            ret, frame = cap.read()
            if not ret:
                logging.warning(
                    f"No frame received from camera {camera['id']}. Exiting loop."
                )
                break

            frame_count += 1
            # run the frame processing
            results = ai_processor.process_frame(frame)

            if save_footage:
                save_frame(
                    True,
                    results["annotated_frame"],
                    results["detected_classes"],
                    camera["id"],
                    frame_count,
                )
    except Exception as e:
        logging.exception(f"Error in camera {camera['id']} stream: {e}")
    finally:
        cap.release()


# video search of the items


def search_video(
    prompt: str, source_video: str, confidence: float = 0.25, save_output: bool = True
):
    """
    Search for specific objects/prompts in a video using YOLOWorld model.

    Args:
        prompt (str): What to search for in the video (e.g., "person wearing red", "blue car")
        source_video (str): Path to the source video
        confidence (float): Detection confidence threshold
        save_output (bool): Whether to save the annotated video

    Returns:
        list: Timestamps of detected objects matching the prompt
    """
    # Initialize annotators
    label_annotator = sv.LabelAnnotator()
    box_annotator = sv.BoxAnnotator()

    # Initialize YOLO World model
    model = YOLO("yolov8s-worldv2.pt")

    # Set the search prompt
    model.set_classes([prompt])

    # Setup video processing
    frame_generator = sv.get_video_frames_generator(source_path=source_video)
    video_info = sv.VideoInfo.from_video_path(source_video)

    # Calculate frame area for filtering
    width, height = video_info.resolution_wh
    frame_area = width * height

    # Prepare output video if saving is enabled
    if save_output:
        output_path = (
            f"{ROOT_DIR}/output/{prompt.replace(' ', '_')}_results.mp4"
        )
        with sv.VideoSink(target_path=output_path, video_info=video_info) as sink:
            for frame_idx, frame in enumerate(frame_generator):
                # Run inference
                results = model.predict(frame, conf=confidence)[0]
                detections = sv.Detections.from_ultralytics(results).with_nms(
                    threshold=0.1
                )

                # Filter out large detections (likely false positives)
                detections = detections[(detections.area / frame_area) < 0.10]

                if len(detections) > 0:
                    # Annotate frame with detections
                    annotated_frame = frame.copy()
                    annotated_frame = box_annotator.annotate(
                        annotated_frame, detections
                    )
                    annotated_frame = label_annotator.annotate(
                        annotated_frame, detections
                    )
                    sink.write_frame(annotated_frame)
    else:
        # Just process without saving
        detections_timestamps = []
        for frame_idx, frame in enumerate(frame_generator):
            results = model.infer(frame, confidence=confidence)
            detections = sv.Detections.from_inference(
                results).with_nms(threshold=0.1)
            detections = detections[(detections.area / frame_area) < 0.10]

            if len(detections) > 0:
                # Calculate timestamp
                timestamp = frame_idx / video_info.fps
                detections_timestamps.append(timestamp)

        return detections_timestamps
