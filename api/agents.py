import asyncio
import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from fastapi import APIRouter, BackgroundTasks
from starlette.responses import JSONResponse

from agents.processor import AIProcessor
from agents.tasks import monitor_camera_stream
from db import DBQuery, camera_settings_table, camera_table, camera_zones_table

agents_router = APIRouter()

AGENT_STATUS_FILE = "agents/status.json"
active_tasks = []
executor = ThreadPoolExecutor(max_workers=4)


def get_agent_status():
    if not os.path.exists(AGENT_STATUS_FILE):
        return {"running": False}
    with open(AGENT_STATUS_FILE, "r") as f:
        return json.load(f)


def set_agent_status(running: bool):
    with open(AGENT_STATUS_FILE, "w") as f:
        json.dump({"running": running}, f)


@agents_router.post("/start")
async def start_agent(background_tasks: BackgroundTasks):
    global active_tasks

    status = get_agent_status()
    if status["running"]:
        return JSONResponse(
            status_code=400,
            content={"message": "Process already running", "running": True},
        )

    # Get all cameras
    cameras = camera_table.all()

    if not cameras:
        return JSONResponse(
            content={"started": False},
            status_code=400,
        )

    set_agent_status(True)

    print("Started the agent")

    for camera in cameras:
        # create a stop flag
        stop_flag = threading.Event()

        # Retrieve camera settings
        cameras_settings = camera_settings_table.get(DBQuery.camera_id == camera["id"])
        if not cameras_settings:
            continue

        detection_objects = cameras_settings["detection_objects"]
        minimum_conf = cameras_settings["minimum_confidence"]
        surveillance_enabled = cameras_settings["enabled"]
        tracking_enabled = cameras_settings["enable_tracking"]
        save_footage = cameras_settings["save_footage"]
        zone_enabled = cameras_settings["enable_zone"]

        # Retrieve zone coordinates for the camera
        zone = camera_zones_table.get(DBQuery.camera_id == camera["id"])
        if not zone:
            continue

        polygon_coordinates = np.array(zone["coordinates"])

        # Initialize the AI processor
        ai_processor = AIProcessor(
            detection_objects,
            polygon_coordinates,
            surveillance_enabled,
            minimum_conf=minimum_conf,
            tracking_enabled=tracking_enabled,
            zone_enabled=zone_enabled,
        )

        camera_url = 0  # Replace with actual camera URL generation logic

        # Schedule camera stream processing
        future = executor.submit(
            monitor_camera_stream,
            camera,
            ai_processor,
            camera_url,
            save_footage,
            stop_flag,
        )

        active_tasks.append((future, stop_flag))

    return JSONResponse(
        {
            "started": True,
            "cameras": len(cameras),
        },
        status_code=200,
    )


@agents_router.post("/stop")
async def stop_agent():
    global active_tasks, executor

    status = get_agent_status()
    if not status["running"]:
        return JSONResponse(
            status_code=400,
            content={"message": "Process is not running", "running": False},
        )

    set_agent_status(False)

    # Stop all running tasks
    for future, stop_flag in active_tasks:
        stop_flag.set()
        future.cancel()

    # Clear the tasks list
    active_tasks.clear()

    # Shutdown the current executor and create a new one
    executor.shutdown(wait=False)
    executor = ThreadPoolExecutor(max_workers=4)

    return JSONResponse(
        {
            "stopped": True,
        },
        status_code=200,
    )
