import random

import cv2
import supervision as sv
from supervision.geometry.core import Point
from fastapi import APIRouter, status, Response
from starlette.responses import StreamingResponse
from ultralytics import YOLO

from broker import MQTTBroker
from db import camera_table, DBQuery, settings_table
from utils import generate_stream_url, generate_trackers

broker = MQTTBroker()

streaming_router = APIRouter()

VIDEO_SRC_PATH = "src_videos/people-walking.mp4"

LINE_START = Point(50, 1500)
LINE_END = Point(3790, 1500)


# VIDEO_SRC_PATH = 0


@streaming_router.get("/{camera_id}/surveillance")
async def live_ai_surveillance(camera_id: str):
    # get the settings
    detection_objects = ["person", "car", "truck"]
    minimum_conf = 0.25
    counting_enabled = True
    tracking_enabled = True

    # settings = settings_table.all()[0]

    # detection_objects = settings["detection_objects"]
    # minimum_conf = settings["minimum_confidence"]
    # counting_enabled = settings["enable_counting"]
    # segmentation_enabled = settings["enable_segmentation"]
    # tracking_enabled = settings["enable_tracking"]

    # get the cameras and extract the RTSP url
    cameras = camera_table.search(DBQuery.id == camera_id)

    if not cameras:
        response = {
            'found': False
        }
        return Response(response, status_code=404)
    camera = next(camera for camera in cameras)
    camera_url = generate_stream_url(camera)

    # model configuration

    model = YOLO("ai/yolov8n.pt")
    model.fuse()
    # annotations
    box_annotator = sv.BoxAnnotator()
    label_annotator = sv.LabelAnnotator()
    line_zone_annotator = sv.LineZoneAnnotator(
        thickness=4,
        text_thickness=4,
        text_scale=2,)
    # tracking
    tracker = sv.ByteTrack()
    tracker.reset()

    # counting
    line_zone = sv.LineZone(start=LINE_START, end=LINE_END)

    # start the video capturing

    frames_generator = sv.get_video_frames_generator(VIDEO_SRC_PATH)

    # start the video recording

    video_info = sv.VideoInfo.from_video_path(VIDEO_SRC_PATH)

    def generate():
        # filename should match the camera_id and the dates to

        with sv.VideoSink(f"output/{random.randint(0, 100)}.mp4", video_info) as sink:
            # Run YOLO detection on the frame

            for frame in frames_generator:
                results = model.predict(frame, conf=minimum_conf, iou=0.45)[0]

                detections = sv.Detections.from_ultralytics(results)

                filtered_mask = [
                    class_name in detection_objects
                    for class_name in detections["class_name"]
                ]

                filtered_detections = detections[filtered_mask]

                # generate labels based on whether tracking is enabled
                labels, tracked_detections = generate_trackers(filtered_detections, tracking_enabled, tracker)

                # extract labels and annotate frames

                annotated_frame = box_annotator.annotate(
                    scene=frame, detections=tracked_detections)

                labelled_frame = label_annotator.annotate(
                    scene=annotated_frame, detections=tracked_detections, labels=labels)


                labelled_frame = line_zone_annotator.annotate(labelled_frame, line_counter=line_zone,)

                # trigger the detections for counting

                line_zone.trigger(tracked_detections)

                # save the file

                sink.write_frame(labelled_frame)

                ret, jpeg = cv2.imencode(".jpg", labelled_frame)
                if ret:
                    # Yield each JPEG frame as part of the stream
                    yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpeg.tobytes() + b"\r\n\r\n"

    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")
