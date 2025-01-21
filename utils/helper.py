import ipaddress
import socket

import nmap
import psutil


# generate camera urls
def generate_stream_url(camera):
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
    for interface, address in psutil.net_if_addrs().items():
        for addr in address:
            if addr.family == socket.AF_INET:  # IPv4 addresses
                ip = addr.address
                netmask = addr.netmask
                if ip and netmask and ip != "127.0.0.1":
                    subnet = ipaddress.IPv4Network(f"{ip}/{netmask}", strict=False)
                    return str(subnet)
    return None


# generate labels
def generate_labels(filtered_detections, tracking_enabled: bool, tracker):
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
