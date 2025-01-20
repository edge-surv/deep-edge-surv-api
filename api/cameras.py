from db import camera_table
from models import Camera
from utils import get_connected_subnet, scan_rtsp_ports
from fastapi import APIRouter, status, Response

camera_router = APIRouter()


# add cameras to the database
@camera_router.post("/")
def add_camera(camera_data: Camera):
    if camera_data:
        camera_table.insert(camera_data.model_dump())

        response = {
            "created": True,
        }

        return Response(response, status_code=status.HTTP_201_CREATED)

    else:

        response = {
            "created": False,
        }

        return Response(response, status_code=status.HTTP_400_BAD_REQUEST)


# delete camera from the database
@camera_router.delete("/{camera_id}")
def delete_camera(camera_id: str):
    camera_table.remove(Camera.id == camera_id)

    response = {
        "deleted": True,
    }

    return Response(response, status_code=status.HTTP_204_NO_CONTENT)


# update camera
@camera_router.put("/{camera_id}")
def update_camera(camera_data: Camera, camera_id: str):
    if camera_data:
        camera_table.update(camera_data, Camera.id == camera_id)

        response = {
            "updated": True,
        }

        return Response(response, status_code=status.HTTP_200_OK)

    else:

        response = {
            "updated": False
        }

        return Response(response, status_code=status.HTTP_400_BAD_REQUEST)


# list cameras
@camera_router.get("/")
def get_all_cameras():
    cameras = camera_table.all()

    if len(cameras) > 0:

        response = {
            "cameras": cameras
        }

        return Response(response, status_code=status.HTTP_200_OK)

    else:

        response = {
            "cameras": None
        }

        return Response(response, status_code=status.HTTP_404_NOT_FOUND)


# scan for IP cameras on the connected network or subnet
@camera_router.get("/scan")
def discover_cameras():
    # get the current subnet
    connected_subnet = get_connected_subnet()

    # scan for available cameras
    available_cameras = scan_rtsp_ports(connected_subnet, "554")

    if len(available_cameras) > 0:

        response = {
            "cameras": available_cameras
        }

        return Response(response, status_code=status.HTTP_200_OK)

    else:

        response = {
            "cameras": None
        }

        return Response(response, status_code=status.HTTP_404_NOT_FOUND)
