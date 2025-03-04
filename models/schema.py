from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel


# user model
class UserData(BaseModel):
    id: str = str(uuid4())
    username: str
    password: str


class Agent(BaseModel):
    id: str = str(uuid4())
    name: str
    running: bool = False
    max_cameras: int = 4


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


#  camera settings model
class CameraSettings(BaseModel):
    id: str = str(uuid4())
    camera_id: str
    detection_objects: List[str]
    enabled: bool
    minimum_confidence: int | float
    enable_tracking: bool
    enable_counting: bool
    enable_zone: bool
    save_footage: bool


# camera zone config
class CameraZoneConfig(BaseModel):
    id: str = str(uuid4())
    camera_id: str
    coordinates: List[List[int]]


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

class User(BaseModel):
    id: Optional[str] = str(uuid4())
    username: str
    password: str
