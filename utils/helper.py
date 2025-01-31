import ipaddress
import socket
import os

import nmap
import psutil
from datetime import datetime
from db import storage_table
import cv2
import uuid
from models import Storage
from ultralytics import YOLO

from settings import ROOT_DIR

model = YOLO("ai/yolov8n.pt")


# generate camera urls
def generate_stream_url(camera):
    """

    :param camera: Camera from models
    :return: camera_url:str
    """
    if camera['provider'] == 'dahua':
        return f"rtsp://{camera['username']}:{camera['password']}@{camera['host']}:{camera['port']}/cam/realmonitor?/channel=1&subtype=1"

    return None


# scan for the camera hosts
def scan_rtsp_ports(network_range, ports):
    scanner = nmap.PortScanner()

    scanner.scan(network_range, ports, arguments='-Pn -T4 --min-parallelism 10 -n')

    rtsp_cameras = []

    # loop through the scanned ports
    for host in scanner.all_hosts():
        # to replace with port 554
        if 'tcp' in scanner[host] and 554 in scanner[host]['tcp']:
            port_info = scanner[host]['tcp'][554]
            if port_info['state'] == 'open':
                rtsp_cameras.append({
                    'host': host,
                    'state': port_info['state'],
                    'port': 554
                })

    return rtsp_cameras


# get connected subnet
def get_connected_subnet():
    """

    :return subnet:str
    """
    for interface, address in psutil.net_if_addrs().items():
        for addr in address:
            if addr.family == socket.AF_INET:  # IPv4 addresses
                ip = addr.address
                netmask = addr.netmask
                if ip and netmask and ip != "127.0.0.1":
                    subnet = ipaddress.IPv4Network(f"{ip}/{netmask}", strict=False)
                    return str(subnet)
    return None


# generate trackers
def generate_trackers(filtered_detections, tracking_enabled: bool, tracker):
    """

    :param filtered_detections:Detections
    :param tracking_enabled:bool
    :param tracker:ByteTrack object
    :return:
    """
    # check if tracking is enabled and update detections with tracker
    if tracking_enabled:
        tracked_detections = tracker.update_with_detections(filtered_detections)

        labels = [f"{class_name} #{tracker_id}" for class_name, tracker_id in
                  zip(tracked_detections["class_name"], tracked_detections.tracker_id)]

        return labels, tracked_detections

    else:

        labels = [
            f"{class_name} {confidence:.2f}"
            for class_name, confidence
            in zip(filtered_detections['class_name'], filtered_detections.confidence)
        ]

        return labels, filtered_detections


# generate counts for objects detected in a frame
def generate_count():
    """

    :return:
    """

    pass


def save_footage(camera):
    """
    :param camera: Camera from models
    :return: Tuple[bool, str|None]
    """
    file_id = str(uuid.uuid4())
    filename = f"{file_id}_{datetime.now().date()}.mp4"

    storage = {
        "id": file_id,
        "camera_id": camera["id"],
        "camera_name": camera["name"],
        "filename": filename,
        "date": str(datetime.now().date()),
        "time": str(datetime.now().time())

    }

    storage_data = Storage(**storage)

    if storage_data:
        storage_table.insert(storage_data.model_dump())

        return True, filename

    else:

        return False, None


# save frames
def save_frame(frame, detections, camera_id):
    """

    :param frame:
    :param camera_id
    :param detections Tracked detections:
    :return bool
    """
    timestamp = f"{str(datetime.now().date())}__{str(datetime.now().time())}"

    # save the details in logs table

    # persist to file dir
    frame_name = os.path.join(ROOT_DIR, f"logs/images/{timestamp}.jpg")

    cv2.imwrite(frame_name, frame)

