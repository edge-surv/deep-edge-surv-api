import cv2
import supervision as sv
from fastapi import APIRouter, status, Response
from starlette.responses import StreamingResponse
from ultralytics import YOLO
import random

from broker import MQTTBroker
from db import camera_table, DBQuery
from utils import generate_stream_url

broker = MQTTBroker()

streaming_router = APIRouter()


@streaming_router.get("/{camera_id}/surveillance")
async def live_ai_surveillance(camera_id: str):
    allowed_detection_objects = ["person", "door", "bag", "chair"]

    model = YOLO("ai/yolov8n.pt")
    model.fuse()
    box_annotator = sv.BoxAnnotator()
    label_annotator = sv.LabelAnnotator()
    cameras = camera_table.search(DBQuery.id == camera_id)

    if not cameras:
        response = {
            'found': False
        }
        return Response(response, status_code=404)
    camera = next(camera for camera in cameras)
    camera_url = generate_stream_url(camera)

    cap = cv2.VideoCapture(camera_url)

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    if not cap.isOpened():
        response = {
            'found': False
        }
        return Response(response, status_code=status.HTTP_404_NOT_FOUND)
    # start the video recording

    video_info = sv.VideoInfo(frame_width, frame_height, fps, 1800)
    with sv.VideoSink(f"output/{random.randint(0, 100)}.mp4", video_info) as sink:

        def generate():

            while True:

                ret, frame = cap.read()
                # Break the loop if the video ends or cannot fetch the frame
                if not ret:
                    print("End of video or cannot fetch frame.")
                    break
                # Run YOLO detection on the frame
                results = model(frame)[0]
                detections = sv.Detections.from_ultralytics(results)

                filtered_mask = [
                    class_name in allowed_detection_objects
                    for class_name in detections["class_name"]
                ]

                filtered_detections = detections[filtered_mask]

                if len(filtered_detections.class_id) > 0:
                    # publish when an object is detected

                    broker.publish("realtime-notifications", "person detected")

                labels = [
                    f"{class_name} {confidence:.2f}"
                    for class_name, confidence
                    in zip(filtered_detections['class_name'], filtered_detections.confidence)
                ]
                annotated_frame = box_annotator.annotate(
                    scene=frame, detections=filtered_detections)
                labelled_frame = label_annotator.annotate(
                    scene=annotated_frame, detections=filtered_detections, labels=labels)

                # save the file

                sink.write_frame(labelled_frame)

                ret, jpeg = cv2.imencode(".jpg", labelled_frame)
                if ret:
                    # Yield each JPEG frame as part of the stream
                    yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpeg.tobytes() + b"\r\n\r\n"

    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")
