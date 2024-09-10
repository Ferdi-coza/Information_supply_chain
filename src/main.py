from mqtt_client import MQTTClient
from sliding_window import SlidingWindow
from data_point import DataPoint
from preprocessor import preprocess()
import sys

def main():
    if sys.argv[1] == "mqtt":
        # Set up and start the MQTT client
        broker_address = "smartdigitalsystems.duckdns.org"
        broker_port = 1883
        topic = "dl30-solar/sensor/panel_voltage/state1"
        mqtt_client = MQTTClient(broker_address, broker_port, topic)
        mqtt_client.connect()
        mqtt_client.start()
        client = mqtt_client
    
    window = SlidingWindow(10)
    clean_vals = []
    

    try:
        while True:
            ################### retrieve and format new reading ###################
            reading = None
            readings_list = client.get_readings()
            if readings_list:
                raw_reading = readings_list[0]
                print(f"Latest reading: {raw_reading}")
                reading = DataPoint(raw_reading[0], raw_reading[1], raw_reading[2], raw_reading[3])
                
            if reading and window.is_full():
                clean_vals.append(window.slide_next(reading))
                
            elif reading:
                window.add_reading(reading)
                
            
            ###################### Preprocess new readings #####################
            preprocess(window)
            
            
            client.clear_readings()


    except KeyboardInterrupt:
        # Stop the MQTT client correctly
        mqtt_client.stop()



if __name__ == '__main__' :
    main()