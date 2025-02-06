from fastapi import APIRouter, status
from starlette.responses import JSONResponse
from db import logs_table

analytics_router = APIRouter()


@analytics_router.get("/")
def get_analytics():
    logs = logs_table.all()

    if len(logs) < 1:
        response = {
            "logs": []
        }

        return JSONResponse(response, status_code=status.HTTP_200_OK)

    else:
        response = {
            "logs": logs
        }

        return JSONResponse(response, status_code=status.HTTP_200_OK)
