from fastapi import APIRouter
from starlette.responses import JSONResponse

from db import agents_table, DBQuery
from models import Agent

agents_router = APIRouter()


@agents_router.get("/")
def get_agents():
    agents = agents_table.all()

    if len(agents) == 0:
        response = {
            "agents": []
        }

        return JSONResponse(response, status_code=200)

    response = {
        "agents": agents
    }

    return JSONResponse(response, status_code=200)


@agents_router.post("/")
def create_agent(agent_data: Agent):
    if agent_data:
        agents_table.insert(agent_data.model_dump())

        response = {
            "created": True
        }

        return JSONResponse(response, status_code=201)

    else:

        response = {
            "created": False
        }

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

        response = {
            "updated": False
        }

        return JSONResponse(response, status_code=400)
