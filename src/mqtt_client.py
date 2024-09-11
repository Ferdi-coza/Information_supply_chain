import paho.mqtt.client as mqtt
import json
from dateutil import parser

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
        print(f"Connected successfully")
        client.subscribe(self.topic)


    def on_message(self, client, userdata, msg):
        try:
            # Decode the payload
            payload = json.loads(msg.payload.decode())
            
            # Extract relevant information
            value = float(payload['state'])
            data = payload.get('data', {})
            
            # Extract additional information from the 'data' field
            device_class = data.get('device_class', 'unknown')
            unit_of_measurement = data.get('unit_of_measurement', 'unknown')
            last_changed = data.get('last_changed', None)
            # Parse the last_changed timestamp if available
            if last_changed:
                timestamp = parser.isoparse(last_changed)
                human_time = timestamp.strftime('%H:%M:%S')
            else:
                timestamp = None
                human_time = None
            
            # Log the reading and metadata
            reading = (value, human_time, device_class, unit_of_measurement)
            # Store the reading
            self.readings.append(reading)

        except (ValueError, KeyError) as e:
            print(f"Failed to decode message: {e}")

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