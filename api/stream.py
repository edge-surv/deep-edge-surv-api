import cv2
from fastapi import APIRouter, Response
from starlette.responses import StreamingResponse
from supervision.geometry.core import Point
import supervision as sv

from broker import MQTTBroker
from db import camera_table, DBQuery
from utils import generate_stream_url, save_frame
from agents import AIProcessor

broker = MQTTBroker()

streaming_router = APIRouter()

VIDEO_SRC_PATH_1 = "src_videos/vehicles.mp4"
VIDEO_SRC_PATH_2 = "src_videos/people-walking.mp4"
# VIDEO_SRC_PATH = 0
VIDEO_SRCS = [VIDEO_SRC_PATH_1, VIDEO_SRC_PATH_2]
LINE_START = Point(10, 500)
LINE_END = Point(2000, 500)


# VIDEO_SRC_PATH = 0


@streaming_router.get("/{camera_id}/surveillance")
async def live_ai_surveillance(camera_id: str):
    # get the settings
    detection_objects = ["person", "car", "truck"]
    minimum_conf = 0.25
    counting_enabled = True
    tracking_enabled = True
    save_footage = True
    box_annotator = sv.BoxAnnotator()
    label_annotator = sv.LabelAnnotator()

    # settings = settings_table.all()[0]

    # detection_objects = settings["detection_objects"]
    # minimum_conf = settings["minimum_confidence"]
    # counting_enabled = settings["enable_counting"]
    # segmentation_enabled = settings["enable_segmentation"]
    # tracking_enabled = settings["enable_tracking"]
    # save_footage = settings["save_footage"]

    # get the cameras and extract the RTSP url
    # cameras = camera_table.search(DBQuery.id == camera_id)
    #
    # if not cameras:
    #     response = {
    #         'found': False
    #     }
    #     return Response(response, status_code=404)
    # camera = next(camera for camera in cameras)
    # camera_url = generate_stream_url(camera)

    # initialize the AIProcessor class
    ai_processor = AIProcessor(detection_objects, running=True, minimum_conf=0.25, tracking_enabled=True)

    cap = cv2.VideoCapture(VIDEO_SRC_PATH_1)

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

            # save the labelled frames for logs

            save_frame(True, labelled_frame, results["detected_classes"], camera_id, frame_count)

            ret, jpeg = cv2.imencode(".jpg", labelled_frame)
            if ret:
                # Yield each JPEG frame as part of the stream
                yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpeg.tobytes() + b"\r\n\r\n"

    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")
