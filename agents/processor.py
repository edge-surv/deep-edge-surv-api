import supervision as sv
from ultralytics import YOLO

from utils import generate_trackers


class AIProcessor:
    """
    A class that processes frames using a given model.
    """

    def __init__(self, detection_objects, running=True, minimum_conf=0.25, tracking_enabled=True):
        self.model = YOLO("ai/yolov8n.pt")
        self.model.fuse()
        self.detection_objects = detection_objects
        self.minimum_conf = minimum_conf
        self.tracking_enabled = tracking_enabled
        self.running = running
        self.tracker = sv.ByteTrack()
        self.box_annotator = sv.BoxAnnotator()
        self.label_annotator = sv.LabelAnnotator()

    def process_frame(self, frame):
        results = self.model.predict(frame, conf=self.minimum_conf, iou=0.45)[0]
        detections = sv.Detections.from_ultralytics(results)

        filtered_mask = [
            class_name in self.detection_objects
            for class_name in detections["class_name"]
        ]

        filtered_detections = detections[filtered_mask]
        labels, tracked_detections = generate_trackers(filtered_detections, self.tracking_enabled, self.tracker)

        return {
            'detections': tracked_detections,
            'labels': labels,
            'detected_classes': [class_name for class_name in filtered_detections["class_name"]]
        }
