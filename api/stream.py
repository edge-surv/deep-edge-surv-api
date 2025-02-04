import cv2
import supervision as sv
from fastapi import APIRouter, Response
from starlette.responses import StreamingResponse, JSONResponse
from supervision.geometry.core import Point

from broker import MQTTBroker
from db import camera_table, DBQuery
from utils import generate_stream_url, generate_trackers, save_footage_details, model, save_frame

broker = MQTTBroker()

streaming_router = APIRouter()

VIDEO_SRC_PATH_1 = "src_videos/vehicles.mp4"
VIDEO_SRC_PATH_2 = "src_videos/people-walking.mp4"
# VIDEO_SRC_PATH = 0
VIDEO_SRCS = [VIDEO_SRC_PATH_1,VIDEO_SRC_PATH_2]
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

    # settings = settings_table.all()[0]

    # detection_objects = settings["detection_objects"]
    # minimum_conf = settings["minimum_confidence"]
    # counting_enabled = settings["enable_counting"]
    # segmentation_enabled = settings["enable_segmentation"]
    # tracking_enabled = settings["enable_tracking"]
    # save_footage = settings["save_footage"]

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

    model.fuse()
    # annotations
    box_annotator = sv.BoxAnnotator()
    label_annotator = sv.LabelAnnotator()
    line_zone_annotator = sv.LineZoneAnnotator(
        thickness=4,
        text_thickness=4,
        text_scale=2, )
    # tracking
    tracker = sv.ByteTrack()
    tracker.reset()

    # counting
    line_zone = sv.LineZone(start=LINE_START, end=LINE_END)

    # start the video capturing
    cap = cv2.VideoCapture(VIDEO_SRC_PATH_1)
    # get video info

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # generate the filename and save it to the database
    footage_saved, output_file_path = save_footage_details(camera)

    if not footage_saved and output_file_path is None:
        response = {
            "storage": False,
            "message": "Could not save footage",
        }
        return JSONResponse(response, status_code=400)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    video_writer = cv2.VideoWriter(f"output/{output_file_path}", fourcc, fps, (frame_width, frame_height))

    # the function to yield streams

    def generate():
        frame_count = 0

        while True:
            ret, frame = cap.read()

            if not ret:
                break

            results = model.predict(frame, conf=minimum_conf, iou=0.45)[0]

            detections = sv.Detections.from_ultralytics(results)

            filtered_mask = [
                class_name in detection_objects
                for class_name in detections["class_name"]
            ]

            filtered_detections = detections[filtered_mask]

            # classes for saving in the logs table

            detected_classes = [class_name for class_name in filtered_detections["class_name"]]

            # generate labels based on whether tracking is enabled
            labels, tracked_detections = generate_trackers(filtered_detections, tracking_enabled, tracker)

            # set to hold tracked detections
            # tracked_objects = set()
            #
            # # handle the logs logic
            # for tracked_detection in tracked_detections:
            #
            #     if not tracked_detection in tracked_objects:
            #         tracked_objects.add(tracked_detection)

            # extract labels and annotate frames

            frame_count += 1

            annotated_frame = box_annotator.annotate(
                scene=frame, detections=tracked_detections)

            labelled_frame = label_annotator.annotate(
                scene=annotated_frame, detections=tracked_detections, labels=labels)

            # save the labelled frames for logs

            save_frame(True, labelled_frame, detected_classes, camera_id, frame_count)

            # trigger the detections for counting

            line_zone.trigger(tracked_detections)

            # write frames to video

            if save_footage:
                video_writer.write(labelled_frame)

            ret, jpeg = cv2.imencode(".jpg", labelled_frame)
            if ret:
                # Yield each JPEG frame as part of the stream
                yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpeg.tobytes() + b"\r\n\r\n"

    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")
