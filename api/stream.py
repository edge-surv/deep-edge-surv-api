import cv2
from fastapi import APIRouter, Response
from starlette.responses import StreamingResponse, JSONResponse

from agents.processor import AIProcessor
from db import camera_table, DBQuery, camera_settings_table, camera_zones_table
from utils import save_frame, generate_stream_url

streaming_router = APIRouter()


@streaming_router.get("/{camera_id}/surveillance")
async def live_ai_surveillance(camera_id: str):
    # get the settings for an agent
    cameras_settings = camera_settings_table.search(DBQuery.camera_id == camera_id)

    if len(cameras_settings) == 0:
        response = {
            "cameras_settings": None,
        }

        return JSONResponse(response, status_code=200)

    single_camera_settings = cameras_settings[0]

    detection_objects = single_camera_settings["detection_objects"]
    minimum_conf = single_camera_settings["minimum_confidence"]
    surveillance_enabled = single_camera_settings["enabled"]
    tracking_enabled = single_camera_settings["enable_tracking"]
    save_footage = single_camera_settings["save_footage"]

    # get the cameras and extract the RTSP url
    cameras = camera_table.search(DBQuery.id == camera_id)

    if not cameras:
        response = {
            "cameras": [],
        }
        return Response(response, status_code=200)

    camera = next(camera for camera in cameras)

    # camera_url = generate_stream_url(camera)
    camera_url = 0

    # initialize the AIProcessor class
    ai_processor = AIProcessor(
        detection_objects,
        running=surveillance_enabled,
        minimum_conf=minimum_conf,
        tracking_enabled=tracking_enabled,
    )
    cap = cv2.VideoCapture(camera_url)

    def generate():
        frame_count = 0

        try:
            while True:
                ret, frame = cap.read()

                if not ret:
                    if cap and cap.isOpened():
                        cap.release()
                    break
                # process the frame
                frame_count += 1

                results = ai_processor.process_frame(frame)

                if save_footage:
                    # save the labelled frames for logs

                    save_frame(
                        True,
                        results["annotated_frame"],
                        results["detected_classes"],
                        camera_id,
                        frame_count,
                    )

                ret, jpeg = cv2.imencode(".jpg", results["annotated_frame"])
                if ret:
                    # Yield each JPEG frame as part of the stream
                    yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpeg.tobytes() + b"\r\n\r\n"

        except Exception as e:
            if cap and cap.isOpened():
                cap.release()

                return Response(
                    {
                        "stream": False,
                    },
                    status_code=400,
                )
        finally:
            if cap and cap.isOpened():
                cap.release()

    return StreamingResponse(
        generate(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@streaming_router.get("/{camera_id}")
def stream_camera_feed(camera_id: str):
    cameras = camera_table.search(DBQuery.id == camera_id)

    if not cameras:
        response = {
            "cameras": [],
        }
        return JSONResponse(response, status_code=200)

    camera = next(camera for camera in cameras)

    camera_url = generate_stream_url(camera)

    cap = cv2.VideoCapture(camera_url)

    def generate():
        frame_count = 0

        try:

            while True:
                ret, frame = cap.read()

                if not ret:
                    break
                # process the frame
                frame_count += 1

                ret, jpeg = cv2.imencode(".jpg", frame)
                if ret:
                    # Yield each JPEG frame as part of the stream
                    yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpeg.tobytes() + b"\r\n\r\n"

        except Exception as e:

            if cap and cap.isOpened():
                cap.release()

                return JSONResponse(
                    {
                        "stream": 400,
                    },
                    status_code=500,
                )

    return StreamingResponse(
        generate(), media_type="multipart/x-mixed-replace; boundary=frame"
    )
