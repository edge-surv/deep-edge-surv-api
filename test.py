import os
import cv2
import supervision as sv
from ultralytics import YOLOWorld


def detect_and_save_frames(prompt: str, video_path: str, confidence: float = 0.25):
    """
    Detect objects in video based on prompt and save frames where objects are detected.

    Args:
        prompt (str): What to search for in the video
        video_path (str): Path to the video file
        confidence (float): Detection confidence threshold
    """
    # Create output directory
    output_dir = "./frames"
    os.makedirs(output_dir, exist_ok=True)

    # Initialize YOLO and annotators
    model = YOLOWorld("yolov8s-worldv2.pt")
    model.set_classes([prompt])
    box_annotator = sv.BoxAnnotator()

    # Setup video processing
    frame_generator = sv.get_video_frames_generator(source_path=video_path)

    for frame_idx, frame in enumerate(frame_generator):
        # Skip every 30th frame
        if frame_idx % 30 == 0:
            continue

        # Run detection
        results = model.predict(frame, conf=confidence)[0]
        detections = sv.Detections.from_ultralytics(results)

        if len(detections) > 0:
            # Annotate and save frame
            annotated_frame = frame.copy()
            annotated_frame = box_annotator.annotate(annotated_frame, detections)

            # Save the frame
            output_path = os.path.join(output_dir, f"frame_{frame_idx}.jpg")
            cv2.imwrite(output_path, annotated_frame)


# Example usage
prompt = "find me a white truck"
video_path = "./vehicles.mp4"
detect_and_save_frames(prompt, video_path)
