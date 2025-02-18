import cv2
import supervision as sv
from fastapi import APIRouter, Response
from starlette.responses import StreamingResponse

from agents import AIProcessor
from broker import MQTTBroker
from db import camera_table, DBQuery, settings_table, camera_zones_table
from utils import generate_stream_url, save_frame
import numpy as np

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

    # extract the zones for the camera
    zone = camera_zones_table.get(DBQuery.camera_id == camera_id)

    coordinates = zone["coordinates"]

    polygone = np.array(coordinates)
    polygone_zone = sv.PolygonZone(polygon=polygone)
    zone_annotator = sv.PolygonZoneAnnotator(
        zone=polygone_zone, color=sv.Color.YELLOW, thickness=2, text_thickness=2, text_scale=1,
        display_in_zone_count=False)

    # create a polygone

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
    ai_processor = AIProcessor(detection_objects, polygone_zone, surveillance_enabled,
                               minimum_conf=minimum_conf,
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

            # annotate the zone in the screen

            annotated_frame = box_annotator.annotate(
                scene=frame, detections=results["detections"])

            labelled_frame = label_annotator.annotate(
                scene=annotated_frame, detections=results["detections"], labels=results["labels"])

            zoned_frame = zone_annotator.annotate(scene=labelled_frame)

            if save_footage:
                # save the labelled frames for logs

                save_frame(True, zoned_frame, results["detected_classes"], camera_id, frame_count)

            ret, jpeg = cv2.imencode(".jpg", zoned_frame)
            if ret:
                # Yield each JPEG frame as part of the stream
                yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpeg.tobytes() + b"\r\n\r\n"

    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")
