from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel


# user model
class UserData(BaseModel):
    id: str = str(uuid4())
    username: str
    password: str


# camera model
class Camera(BaseModel):
    id: str = str(uuid4())
    agent_id: str
    host: str
    port: int
    name: str
    username: str
    password: str
    provider: str


class Agent(BaseModel):
    id: str = str(uuid4())
    name: str
    max_cameras: int = 4


# settings model
class Settings(BaseModel):
    id: str = str(uuid4())
    agent_id: Optional[str] = None
    detection_objects: List[str]
    enabled: bool
    minimum_confidence: int | float
    enable_tracking: bool
    enable_counting: bool
    save_footage: bool


class Storage(BaseModel):
    id: str = str(uuid4())
    camera_id: str
    camera_name: str
    filename: str
    date: str
    time: str


class Logs(BaseModel):
    id: str = str(uuid4())
    camera_id: str
    filename: str
    objects_detected: List[str | int]
    date: str
    time: str


class CameraZoneConfig(BaseModel):
    id: str = str(uuid4())
    camera_id: str
    coordinates: List[List[int]]
