from fastapi import APIRouter, status
from starlette.responses import JSONResponse
from models import Settings

from db import settings_table, DBQuery

settings_router = APIRouter()


# configure agent
@settings_router.post("/{agent_id}")
def save_settings(agent_id: str, settings: Settings):
    if settings:

        settings_data = {
            **settings.model_dump(),
            "agent_id": agent_id
        }

        settings_table.insert(settings_data)

        response = {
            "created": True
        }

        return JSONResponse(response, status_code=200)


    else:
        response = {
            "created": False
        }

        return JSONResponse(response, status_code=400)


# get the settings
@settings_router.get("/{agent_id}")
def get_settings(agent_id: str):
    settings = settings_table.get(DBQuery.agent_id == agent_id)

    if len(settings) == 0:
        response = {
            "settings": None,
        }

        return JSONResponse(response, status_code=status.HTTP_200_OK)

    else:
        response = {
            "settings": settings,
        }

        return JSONResponse(response, status_code=status.HTTP_200_OK)


# update the settings
@settings_router.put("/{agent_id}")
def update_settings(settings_data: Settings, agent_id: str):
    if settings_data:

        settings_table.update(settings_data.model_dump(), DBQuery.agent_id == agent_id)

        response = {
            "updated": True,
        }

        return JSONResponse(response, status_code=status.HTTP_200_OK)


    else:

        response = {
            "created": False,
        }

        return JSONResponse(response, status_code=status.HTTP_400_BAD_REQUEST)
