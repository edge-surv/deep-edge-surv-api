import threading

import paho.mqtt.client as mqtt


class MQTTBroker:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_message = self.on_message  # Set the on_message handler
        self.client.connect('localhost', 1883, keepalive=60)
        self.subscribed_topics = []

    # subscribe to a topic
    def subscribe(self, topic):
        self.client.subscribe(topic)

    # handle continuous listening
    def start_loop(self):
        mqtt_thread = threading.Thread(target=self.client.loop_forever, daemon=True)
        mqtt_thread.start()

    # handle topic publishing
    def publish(self, topic, message):
        self.client.publish(topic, message)

    # handle callback when a message is received
    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode('utf-8')
        print(f"Message received on topic {msg.topic}: {payload}")
