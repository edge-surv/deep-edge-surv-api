import threading
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from fastapi import APIRouter, BackgroundTasks
from starlette.responses import JSONResponse

from agents.processor import AIProcessor
from agents.tasks import monitor_camera_stream
from db import (
    agents_table,
    DBQuery,
    camera_table,
    camera_settings_table,
    camera_zones_table,
)
from models import Agent

agents_router = APIRouter()

executor = ThreadPoolExecutor(max_workers=10)

active_agents = {}


@agents_router.get("/")
def get_agents():
    agents = agents_table.all()

    if len(agents) == 0:
        response = {"agents": []}

        return JSONResponse(response, status_code=200)

    response = {"agents": agents}

    return JSONResponse(response, status_code=200)


@agents_router.post("/")
def create_agent(agent_data: Agent):
    if agent_data:
        agents_table.insert(agent_data.model_dump())

        response = {"created": True}

        return JSONResponse(response, status_code=201)

    else:

        response = {"created": False}

        return JSONResponse(response, status_code=400)


@agents_router.delete("/{agent_id}")
def delete_agent(agent_id: str):
    agents_table.remove(DBQuery.id == agent_id)

    response = {
        "deleted": True,
    }

    return JSONResponse(response, status_code=200)


@agents_router.put("/{agent_id}")
def update_agent(agent_id: str, agent_data: Agent):
    if agent_data:
        agents_table.update(agent_data, DBQuery.id == agent_id)

        response = {
            "updated": True,
        }

        return JSONResponse(response, status_code=200)

    else:

        response = {"updated": False}

        return JSONResponse(response, status_code=400)


# start agent
@agents_router.post("/{agent_id}/start")
def start_agent(agent_id: str, background_tasks: BackgroundTasks):
    global active_agents

    # update agent status to true
    agents_table.update({"running": True}, DBQuery.id == agent_id)

    if agent_id in active_agents:
        return JSONResponse({"running": True}, status_code=400)
    # get cameras for that agent
    cameras = camera_table.search(DBQuery.agent_id == agent_id)

    if not cameras:
        return JSONResponse({"started": False}, status_code=400)

    # add the agent to the active agents

    active_agents[agent_id] = []

    for camera in cameras:
        # create a stop flag
        stop_flag = threading.Event()

        # camera_url = generate_stream_url(camera)
        camera_url = 0
        # Retrieve camera settings.
        cameras_settings = camera_settings_table.get(DBQuery.camera_id == camera["id"])
        detection_objects = cameras_settings["detection_objects"]
        minimum_conf = cameras_settings["minimum_confidence"]
        surveillance_enabled = cameras_settings["enabled"]
        tracking_enabled = cameras_settings["enable_tracking"]
        save_footage = cameras_settings["save_footage"]
        zone_enabled = cameras_settings["enable_zone"]

        # Retrieve zone coordinates for the camera.
        zone = camera_zones_table.get(DBQuery.camera_id == camera["id"])
        polygon_coordinates = np.array(zone["coordinates"])

        # Initialize the AI processor using your existing logic.
        ai_processor = AIProcessor(
            detection_objects,
            polygon_coordinates,
            surveillance_enabled,
            minimum_conf=minimum_conf,
            tracking_enabled=tracking_enabled,
            zone_enabled=zone_enabled,
        )

        # Schedule each camera stream as a background task.
        future = executor.submit(
            monitor_camera_stream,
            camera,
            ai_processor,
            camera_url,
            cameras_settings["save_footage"],
            agent_id,
        )

        # add the task to the list of active agent

        active_agents[agent_id].append((future, stop_flag))

    return JSONResponse({"started": True}, status_code=200)


# stop the agent
@agents_router.post("/{agent_id}/stop")
def stop_agent(agent_id: str):
    global active_agents

    # update agent status to false
    agents_table.update({"running": False}, DBQuery.id == agent_id)
    if agent_id not in active_agents:
        return JSONResponse({"message": "Agent not running"}, status_code=400)

    for future, stop_flag in active_agents[agent_id]:
        # stop the thread
        stop_flag.set()

        # cancel the future
        future.cancel()

    del active_agents[agent_id]

    return JSONResponse({"stopped": True}, status_code=200)
