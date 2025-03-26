import logging
import os
import smtplib
import uuid
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import cv2
import supervision as sv
from ultralytics import YOLO

from config import ROOT_DIR
from utils import save_frame
from db import logs_table


# monitor cameras
def monitor_camera_stream(camera, ai_processor, camera_url, save_footage, stop_flag):
    """
    Continuously process the video stream from a single camera.
    """
    frame_count = 0
    cap = cv2.VideoCapture(camera_url)
    if not cap.isOpened():
        logging.error(f"Failed to open camera stream: {camera_url}")
        return

    try:
        while not stop_flag.is_set():
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


# video search task for the agent
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
        dict: Frames and timestamps where objects were detected
    """
    # Initialize annotators and trackers
    label_annotator = sv.LabelAnnotator()
    box_annotator = sv.BoxAnnotator()
    tracker = sv.ByteTrack()

    # Initialize YOLO World model
    model = YOLO("yolov8s-worldv2.pt")
    model.fuse()
    model.set_classes([prompt])

    # Setup video processing
    frame_generator = sv.get_video_frames_generator(source_path=source_video)
    video_info = sv.VideoInfo.from_video_path(source_video)

    # Calculate frame area for filtering
    width, height = video_info.resolution_wh
    frame_area = width * height

    detected_frames = []
    frame_timestamps = []
    output_files = []
    frame_skip = 15  # Process every 30th frame

    # Ensure output directory exists
    OUTPUT_DIR = f"{ROOT_DIR}/output/images"
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = f"{ROOT_DIR}/output/videos/{uuid.uuid4()}.mp4"

    with sv.VideoSink(target_path=output_path, video_info=video_info) as sink:

        for frame_idx, frame in enumerate(frame_generator):
            # Skip frames based on frame_skip
            if frame_idx % frame_skip != 0:
                continue

            # Run inference
            results = model.predict(frame, conf=confidence, iou=0.45)[0]
            detections = sv.Detections.from_ultralytics(results)

            # Filter out large detections (likely false positives)
            filtered_detections = detections[(detections.area / frame_area) < 0.10]

            if len(filtered_detections) > 0:
                # Generate labels
                labels = [prompt] * len(filtered_detections)

                # Annotate frame
                annotated_frame = frame.copy()
                annotated_frame = box_annotator.annotate(
                    annotated_frame, filtered_detections
                )
                annotated_frame = label_annotator.annotate(
                    annotated_frame, filtered_detections, labels=labels
                )

                # Store frame and timestamp
                detected_frames.append(annotated_frame)
                frame_timestamps.append(frame_idx / video_info.fps)

                # Save output if enabled
                if save_output:
                    frame_uuid = str(uuid.uuid4())
                    output_file = f"{frame_uuid}.jpg"
                    output_path = os.path.join(OUTPUT_DIR, output_file)

                    # save the video
                    sink.write_frame(annotated_frame)

                    try:
                        # Ensure the output directory exists
                        os.makedirs(os.path.dirname(output_path), exist_ok=True)
                        # write the frame to disk
                        success = cv2.imwrite(output_path, annotated_frame)

                        if success:
                            # append the files of the photos
                            output_files.append(output_path)
                        else:
                            return {
                                "search": False,
                            }
                    except Exception as e:
                        logging.error(f"Error saving frame: {e}")
                        return {
                            "search": False,
                        }

    return {
        "timestamps": frame_timestamps,
        "total_detections": len(detected_frames),
        "output_files": output_files,
        "search": True,
    }


def send_email(
    sender_email, sender_password, recipient_email, subject, body, attachment_path=None
):
    try:
        # Create message container
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject

        # Add body to email
        msg.attach(MIMEText(body, "plain"))

        # Attach image if provided
        if attachment_path:
            with open(attachment_path, "rb") as attachment:
                part = MIMEImage(attachment.read())
                part.add_header(
                    "Content-Disposition",
                    "attachment",
                    filename=os.path.basename(attachment_path),
                )
                msg.attach(part)

        # Create SMTP session
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()

        # Login to the server
        server.login(sender_email, sender_password)

        # Send email
        server.send_message(msg)
        server.quit()

        return True
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
    return False


# search the logs
def search_logs(prompt: str):
    """
    Search for specific objects/prompts in the logs using YOLOWorld model.
    Args:
        prompt (str): What to search for in the logs (e.g., "person wearing red", "blue car")
    """

    # Initialize YOLOWorld model and annotators
    model = YOLO("yolov8s-worldv2.pt")
    model.set_classes([prompt])
    box_annotator = sv.BoxAnnotator()
    label_annotator = sv.LabelAnnotator()
    SEARCH_OUTPUT_DIR = f"{ROOT_DIR}/output/images/search/logs"

    # Get all logs from database
    logs = logs_table.all()

    if len(logs) < 1:
        return {
            "search": False,
            "message": "No logs found",
        }

    # Extract image paths from logs
    image_paths = []
    for log in logs:
        image_path = os.path.join("output/images/logs", log["filename"])
        if os.path.exists(image_path):
            image_paths.append(image_path)

    detected_frames = []
    frame_timestamps = []
    output_files = []

    # Process each image with YOLOWorld
    for image_path in image_paths:
        # convert the image to a numpy array
        frame = cv2.imread(image_path)
        results = model.predict(frame, conf=0.25, iou=0.45)[0]
        # get detections from the results
        detections = sv.Detections.from_ultralytics(results)

        if len(detections) > 0:
            # Generate labels
            labels = [prompt] * len(detections)

            # Annotate frame
            annotated_frame = frame.copy()
            annotated_frame = box_annotator.annotate(annotated_frame, detections)
            annotated_frame = label_annotator.annotate(
                annotated_frame, detections, labels=labels
            )

            # Save annotated frame
            output_path = (
                f"output/images/search/logs/log_search_{os.path.basename(image_path)}"
            )

            # write the image to the path
            cv2.imwrite(output_path, annotated_frame)

            detected_frames.append(results)
            # get the exact files
            frame_timestamps.append(os.path.basename(image_path))
            output_files.append(os.path.basename(output_path))

    return {
        "timestamps": frame_timestamps,
        "total_detections": len(detected_frames),
        "output_files": output_files,
        "search": True,
    }
