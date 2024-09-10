from mqtt_client import MQTTClient
from sliding_window import SlidingWindow
from data_point import DataPoint
from preprocessor import is_const_err, range_check, med_filter
import sys
import time

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
    num_reads = 1
    

    try:
        while True:
            ################### retrieve and format new reading ###################
            reading = None
            readings_list = client.get_readings()
            if readings_list:
                raw_reading = readings_list[0]
                print(f"Reading number {num_reads} is: {raw_reading}")
                reading = DataPoint(raw_reading[0], raw_reading[1], raw_reading[2], raw_reading[3])
                num_reads += 1
                
            if reading and window.is_full():
                clean_vals.append(window.slide_next(reading))
                
            elif reading:
                window.add_reading(reading)
                
            
            ###################### Preprocess new readings #####################
            if window.is_full() and reading:
                print(f"window before PP: {window.get_win_vals()}")
                #check for constant error sensor fault
                if is_const_err(window.get_win_vals(), 0.00001):
                    print("CONSTANT ERROR DETECTED")

                #perform range check on current window
                if num_reads == 10:
                    print("all vals getting checked")
                    range_check(window, get_UL(window), get_LL(window), True)
                else:
                    range_check(window, get_UL(window), get_LL(window), False)

                #perform median filtering to smooth data
                med_filter(window, 3)

                print(f"window after PP : {window.get_win_vals()}")
            
            
            client.clear_readings()
            time.sleep(1)


    except KeyboardInterrupt:
        # Stop the MQTT client correctly
        mqtt_client.stop()


def get_UL(window):
    sensor_type = window.get_sensor_type()

    if sensor_type == "voltage_sensor":
        UL = 300

    return UL


def get_LL(window):
    sensor_type = window.get_sensor_type()


    if sensor_type == "voltage_sensor":
        LL = -1

    return LL



if __name__ == '__main__' :
    main()