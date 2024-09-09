import paho.mqtt.client as mqtt
import json

class MQTTClient:

    def __init__(self, broker_address, broker_port, topic):
        self.broker_address = broker_address
        self.broker_port = broker_port
        self.topic = topic
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.readings = []


    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        client.subscribe(self.topic)


    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            value = float(payload['value'])
            timestamp = payload['time']
            reading = (value, timestamp)
            print(f"MQTT received reading: {reading}")
            self.readings.append(reading)
        except ValueError:
            print("Failed to decode message")


    def connect(self):
        self.client.connect(self.broker_address, self.broker_port, 60)


    def start(self):
        self.client.loop_start()


    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()


    def get_readings(self):
        return self.readings


    def clear_readings(self):
        self.readings = []