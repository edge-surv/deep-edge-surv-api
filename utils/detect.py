import cv2
import supervision as sv
from ultralytics import YOLOWorld
import io


def detect_objects(prompt: str, video_path: str, confidence: float = 0.25):
    """
    Detect objects in video based on prompt and return detected frames

    Returns:
        dict: Contains detection results and frame timestamps
    """
    # Initialize YOLO and annotators
    model = YOLOWorld("yolov8s-worldv2.pt")
    model.set_classes([prompt])
    box_annotator = sv.BoxAnnotator()

    # Setup video processing
    frame_generator = sv.get_video_frames_generator(source_path=video_path)
    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)

    frames = []
    timestamps = []
    total_detections = 0

    for frame_idx, frame in enumerate(frame_generator):
        # Process every 30th frame
        if frame_idx % 30 != 0:
            continue

        # Run detection
        results = model.predict(frame, conf=confidence)[0]
        detections = sv.Detections.from_ultralytics(results)

        if len(detections) > 0:
            # Annotate frame
            annotated_frame = frame.copy()
            annotated_frame = box_annotator.annotate(annotated_frame, detections)

            # Convert frame to bytes
            success, buffer = cv2.imencode(".jpg", annotated_frame)
            frame_bytes = io.BytesIO(buffer).getvalue()

            frames.append({"name": f"frame_{frame_idx}.jpg", "data": frame_bytes})
            timestamps.append(frame_idx / fps)
            total_detections += len(detections)

    return {
        "frames": frames,
        "timestamps": timestamps,
        "total_detections": total_detections,
    }
