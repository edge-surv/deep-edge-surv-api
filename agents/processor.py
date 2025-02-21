import supervision as sv
from ultralytics import YOLO


class AIProcessor:
    """
    A class that processes frames using a given model and detects objects within a specified zone.
    """

    def __init__(self, detection_objects, polygon_coordinates, running=True, minimum_conf=0.25, tracking_enabled=True,
                 zone_enabled=False):
        self.model = YOLO("ai/yolov8n.pt")
        self.zone_enabled = zone_enabled
        self.model.fuse()
        self.detection_objects = detection_objects
        self.minimum_conf = minimum_conf
        self.tracking_enabled = tracking_enabled
        self.polygon_zone = sv.PolygonZone(polygon=polygon_coordinates)
        self.running = running
        self.tracker = sv.ByteTrack()
        self.box_annotator = sv.BoxAnnotator()
        self.label_annotator = sv.LabelAnnotator()
        self.zone_annotator = sv.PolygonZoneAnnotator(zone=self.polygon_zone, color=sv.Color.ROBOFLOW,
                                                      display_in_zone_count=False)

    def process_frame(self, frame):
        """

        :param frame:
        :return: dict
        """
        results = self.model.predict(frame, conf=self.minimum_conf, iou=0.45)[0]
        detections = sv.Detections.from_ultralytics(results)

        # filter detections based on the detection objects

        filtered_mask = [
            class_name in self.detection_objects
            for class_name in detections["class_name"]
        ]

        filtered_detections = detections[filtered_mask]

        labels, tracked_detections = self.generate_trackers(filtered_detections, self.tracker)

        # handle when the zone is enabled

        if self.zone_enabled:
            # trigger the zone
            self.polygon_zone.trigger(detections=filtered_detections)

            # annotate frames with detections

            annotated_frame = self.box_annotator.annotate(frame, detections=tracked_detections)
            annotated_frame = self.label_annotator.annotate(annotated_frame, detections=tracked_detections,
                                                            labels=labels)
            annotated_frame = self.zone_annotator.annotate(annotated_frame)

            return {
                'detections': tracked_detections,
                'labels': labels,
                'detected_classes': [class_name for class_name in filtered_detections["class_name"]],
                'annotated_frame': annotated_frame
            }

        # handle no zone
        else:

            annotated_frame = self.box_annotator.annotate(frame, detections=tracked_detections)
            annotated_frame = self.label_annotator.annotate(annotated_frame, detections=tracked_detections,
                                                            labels=labels)

            return {
                'detections': tracked_detections,
                'labels': labels,
                'detected_classes': [class_name for class_name in filtered_detections["class_name"]],
                'annotated_frame': annotated_frame
            }

    def generate_trackers(self, filtered_detections, tracker):
        """

        :param filtered_detections:Detections
        :param tracker:ByteTrack object
        :return:
        """
        # check if there are detections
        if len(filtered_detections) == 0:
            return [], filtered_detections

        # check if tracking is enabled and update detections with tracker
        if self.tracking_enabled:
            tracked_detections = tracker.update_with_detections(filtered_detections)

            if tracked_detections is None:
                return [], filtered_detections

            labels = [f"{class_name} #{tracker_id}" for class_name, tracker_id in
                      zip(tracked_detections["class_name"], tracked_detections.tracker_id)]

            return labels, tracked_detections

        else:

            labels = [
                f"{class_name}"
                for class_name, confidence
                in zip(filtered_detections['class_name'], filtered_detections.confidence)
            ]

            return labels, filtered_detections
