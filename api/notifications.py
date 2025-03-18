from starlette.responses import JSONResponse
from fastapi import APIRouter, status
from db import notifications_table, DBQuery

notifications_router = APIRouter()


@notifications_router.get("/")
def get_all_notifications():
    notifications = notifications_table.all()

    if len(notifications) > 0:
        response = {
            "notifications": notifications,
        }
        return JSONResponse(response, status_code=status.HTTP_200_OK)
    else:
        response = {
            "notifications": [],
        }
        return JSONResponse(response, status_code=status.HTTP_200_OK)


@notifications_router.delete("/{notification_id}")
def delete_notification(notification_id: str):
    notifications_table.remove(DBQuery.id == notification_id)

    response = {
        "deleted": True,
    }

    return JSONResponse(response, status_code=status.HTTP_204_NO_CONTENT)
