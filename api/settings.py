from fastapi import APIRouter, status
from starlette.responses import JSONResponse
from models import Settings

from db import settings_table

settings_router = APIRouter()


# save the settings
@settings_router.post("/")
def save_settings(settings_data: Settings):
    if settings_data:

        # clear the settings table first
        settings_table.truncate()

        # save the new settings
        settings_table.insert(settings_data.model_dump())

        response = {
            "created": True,
        }

        return JSONResponse(response, status_code=status.HTTP_201_CREATED)

    else:

        response = {
            "created": False,
        }

        return JSONResponse(response, status_code=status.HTTP_400_BAD_REQUEST)


# get the settings
@settings_router.get("/")
def get_settings():
    settings = settings_table.all()

    if len(settings) == 0:
        response = {
            "settings": None,
        }

        return JSONResponse(response, status_code=status.HTTP_200_OK)

    else:
        response = {
            "settings": settings[0],
        }

        return JSONResponse(response, status_code=status.HTTP_200_OK)


# update the settings
@settings_router.put("/")
def update_settings(settings_data: Settings):
    if settings_data:

        settings_table.truncate()

        settings_table.insert(settings_data.model_dump())

        response = {
            "updated": True,
        }

        return JSONResponse(response, status_code=status.HTTP_200_OK)


    else:

        response = {
            "created": False,
        }

        return JSONResponse(response, status_code=status.HTTP_400_BAD_REQUEST)
