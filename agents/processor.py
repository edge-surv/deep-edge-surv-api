# from uuid import uuid4
# import supervision as sv
# from ultralytics import YOLO
# import time
# from datetime import datetime
# from db.db import notifications_table


# class AIProcessor:
#     """
#     A class that processes frames using a given model and detects objects.
#     """

#     def __init__(
#         self,
#         detection_objects,
#         running=True,
#         minimum_conf=0.25,
#         tracking_enabled=True,
#     ):
#         self.model = YOLO("yolov8n.pt")
#         self.model.fuse()
#         self.detection_objects = detection_objects
#         self.minimum_conf = minimum_conf
#         self.tracking_enabled = tracking_enabled
#         self.running = running
#         self.tracker = sv.ByteTrack()
#         self.box_annotator = sv.BoxAnnotator()
#         self.label_annotator = sv.LabelAnnotator()
#         self.last_notification_time = 0

#     def process_frame(self, frame):
#         """

#         :param frame:
#         :return: dict
#         """
#         results = self.model.predict(frame, conf=self.minimum_conf, iou=0.45)[0]
#         detections = sv.Detections.from_ultralytics(results)

#         # filter detections based on the detection objects
#         filtered_mask = [
#             class_name in self.detection_objects
#             for class_name in detections["class_name"]
#         ]

#         filtered_detections = detections[filtered_mask]

#         labels, tracked_detections = self.generate_trackers(
#             filtered_detections, self.tracker
#         )

#         #  notify whenever there is a detection
#         current_time = time.time()
#         if (
#             len(filtered_detections) > 0
#             and (current_time - self.last_notification_time) >= 60
#         ):
#             detected_objects = [
#                 class_name for class_name in filtered_detections["class_name"]
#             ]
#             notification = {
#                 "id": str(uuid4()),
#                 "objects": detected_objects,
#                 "date": datetime.now().strftime("%Y-%m-%d"),
#                 "time": datetime.now().strftime("%H:%M:%S"),
#             }
#             notifications_table.insert(notification)
#             self.last_notification_time = current_time

#         annotated_frame = self.box_annotator.annotate(
#             frame, detections=tracked_detections
#         )
#         annotated_frame = self.label_annotator.annotate(
#             annotated_frame, detections=tracked_detections, labels=labels
#         )

#         return {
#             "detections": tracked_detections,
#             "labels": labels,
#             "detected_classes": [
#                 class_name for class_name in filtered_detections["class_name"]
#             ],
#             "annotated_frame": annotated_frame,
#         }

#     def generate_trackers(self, filtered_detections, tracker):
#         """

#         :param filtered_detections:Detections
#         :param tracker:ByteTrack object
#         :return:
#         """
#         # check if there are detections
#         if len(filtered_detections) == 0:
#             return [], filtered_detections

#         # check if tracking is enabled and update detections with tracker
#         if self.tracking_enabled:
#             tracked_detections = tracker.update_with_detections(filtered_detections)

#             # check if there are no tracked detections
#             if tracked_detections is None or len(tracked_detections.class_id) == 0:
#                 # return the filtered detections with no labels
#                 labels = [
#                     f"{class_name}"
#                     for class_name, confidence in zip(
#                         filtered_detections["class_name"],
#                         filtered_detections.confidence,
#                     )
#                 ]
#                 return labels, filtered_detections

#             # return the tracked detections with labels
#             labels = [
#                 f"{class_name} #{tracker_id}"
#                 for class_name, tracker_id in zip(
#                     tracked_detections["class_name"], tracked_detections.tracker_id
#                 )
#             ]

#             return labels, tracked_detections

#         else:
#             # return the filtered detections with labels if tracking is disabled
#             labels = [
#                 f"{class_name}"
#                 for class_name, confidence in zip(
#                     filtered_detections["class_name"], filtered_detections.confidence
#                 )
#             ]

#             return labels, filtered_detections
