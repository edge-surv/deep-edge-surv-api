from fastapi import APIRouter, Response, status
from models import Settings

from db import settings_table

settings_router = APIRouter()


# save the settings
@settings_router.post("/")
def save_settings(settings_data: Settings):
    if settings_data:
        settings_table.insert(settings_data.model_dump())

        response = {
            "created": True,
        }

        return Response(response, status_code=status.HTTP_201_CREATED)

    else:

        response = {
            "created": False,
        }

        return Response(response, status_code=status.HTTP_400_BAD_REQUEST)


# get the settings
@settings_router.get("/")
def get_settings():
    settings = settings_table.all()

    if len(settings) == 0:
        response = {
            "found": False,
        }

        return Response(response, status_code=status.HTTP_404_BAD_REQUEST)

    else:
        response = {
            "settings": settings,
        }

        return Response(response, status_code=status.HTTP_200_OK)


# update the settings
@settings_router.put("/")
def update_settings(settings_data: Settings):
    if settings_data:

        settings_table.truncate()

        settings_table.insert(settings_data.model_dump())

        response = {
            "updated": True,
        }

        return Response(response, status_code=status.HTTP_200_OK)


    else:

        response = {
            "created": False,
        }

        return Response(response, status_code=status.HTTP_400_BAD_REQUEST)
