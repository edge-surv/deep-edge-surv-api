import random

import cv2
import supervision as sv
from fastapi import APIRouter, status, Response
from starlette.responses import StreamingResponse
from ultralytics import YOLO

from broker import MQTTBroker
from db import camera_table, DBQuery, settings_table
from utils import generate_stream_url, generate_trackers

broker = MQTTBroker()

streaming_router = APIRouter()


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
    box_annotator = sv.BoxAnnotator()
    label_annotator = sv.LabelAnnotator()
    tracker = sv.ByteTrack()
    tracker.reset()

    # start the video capturing


    cap = cv2.VideoCapture("src_videos/people-walking.mp4")

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    if not cap.isOpened():
        response = {
            'found': False
        }
        return Response(response, status_code=status.HTTP_404_NOT_FOUND)
    # start the video recording

    video_info = sv.VideoInfo(frame_width, frame_height, fps)

    def generate():
        with sv.VideoSink(f"output/{random.randint(0, 100)}.mp4", video_info) as sink:
            while True:

                ret, frame = cap.read()
                # Break the loop if the video ends or cannot fetch the frame
                if not ret:
                    print("End of video or cannot fetch frame.")
                    cap.release()
                    break
                # Run YOLO detection on the frame
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

                # save the file

                sink.write_frame(labelled_frame)

                ret, jpeg = cv2.imencode(".jpg", labelled_frame)
                if ret:
                    # Yield each JPEG frame as part of the stream
                    yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpeg.tobytes() + b"\r\n\r\n"


    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")
