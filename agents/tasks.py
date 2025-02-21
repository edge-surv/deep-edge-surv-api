import logging

import cv2

from db import agents_table, DBQuery
from utils import save_frame


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
                logging.warning(f"No frame received from camera {camera['id']}. Exiting loop.")
                break

            frame_count += 1
            # run the frame processing
            results = ai_processor.process_frame(frame)

            if save_footage:
                save_frame(True, results["annotated_frame"], results["detected_classes"], camera["id"], frame_count)
    except Exception as e:
        logging.exception(f"Error in camera {camera['id']} stream: {e}")
    finally:
        cap.release()
