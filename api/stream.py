import cv2
import supervision as sv
from fastapi import APIRouter, Response
from starlette.responses import StreamingResponse

from agents import AIProcessor
from broker import MQTTBroker
from db import camera_table, DBQuery, settings_table
from utils import generate_stream_url, save_frame

broker = MQTTBroker()

streaming_router = APIRouter()


@streaming_router.get("/{agent_id}/cameras/{camera_id}/surveillance")
async def live_ai_surveillance(camera_id: str, agent_id: str):
    box_annotator = sv.BoxAnnotator()
    label_annotator = sv.LabelAnnotator()

    # get the settings for an agent
    settings = settings_table.get(DBQuery.agent_id == agent_id)

    detection_objects = settings["detection_objects"]
    minimum_conf = settings["minimum_confidence"]
    surveillance_enabled = settings["enabled"]
    # counting_enabled = settings["enable_counting"]
    tracking_enabled = settings["enable_tracking"]
    save_footage = settings["save_footage"]

    # get the cameras and extract the RTSP url
    cameras = camera_table.search(DBQuery.id == camera_id)

    if not cameras:
        response = {
            'cameras': []
        }
        return Response(response, status_code=200)

    camera = next(camera for camera in cameras)

    # camera_url = generate_stream_url(camera)
    camera_url = 0

    # initialize the AIProcessor class
    ai_processor = AIProcessor(detection_objects, running=surveillance_enabled, minimum_conf=minimum_conf,
                               tracking_enabled=tracking_enabled)

    cap = cv2.VideoCapture(camera_url)

    def generate():
        frame_count = 0

        while True:
            ret, frame = cap.read()

            if not ret:
                break
            # process the frame
            frame_count += 1

            results = ai_processor.process_frame(frame)

            annotated_frame = box_annotator.annotate(
                scene=frame, detections=results["detections"])

            labelled_frame = label_annotator.annotate(
                scene=annotated_frame, detections=results["detections"], labels=results["labels"])

            if save_footage:
                # save the labelled frames for logs

                save_frame(True, labelled_frame, results["detected_classes"], camera_id, frame_count)

            ret, jpeg = cv2.imencode(".jpg", labelled_frame)
            if ret:
                # Yield each JPEG frame as part of the stream
                yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpeg.tobytes() + b"\r\n\r\n"

    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")
