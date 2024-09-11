from mqtt_client import MQTTClient
from sliding_window import SlidingWindow
from data_point import DataPoint
from preprocessor import is_const_err, range_check, med_filter
import sys
import time
import csv

def main():
    if sys.argv[1] == "mqtt":
        # Set up and start the MQTT client
        broker_address = "smartdigitalsystems.duckdns.org"
        broker_port = 1883
        topic = "dl30-solar/sensor/panel_voltage/state_REG"
        mqtt_client = MQTTClient(broker_address, broker_port, topic)
        mqtt_client.connect()
        mqtt_client.start()
        client = mqtt_client
        
    if sys.argv[1] == "csv":
        cleaned_data = run_csv(sys.argv[2])
        datapoints_to_csv(cleaned_data, "clean", True)
        print("new cleaned data csv made")
        
    
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
                
                if num_reads == 1:
                    datapoints_to_csv([reading], "raw", True)
                else: datapoints_to_csv([reading], "raw", False)
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


def run_csv(file_path):
    data_points = csv_to_datapoints(file_path)
    cleaned_data = []
    window = SlidingWindow(10)
    
    while not window.is_full():
        window.add_reading(data_points.pop(0))
        first_window = True
    
    while data_points:
        #check for constant error sensor fault
        if is_const_err(window.get_win_vals(), 0.00001):
            print("CONSTANT ERROR DETECTED")

        #perform range check on current window
        if first_window:
            first_window = False
            range_check(window, get_UL(window), get_LL(window), True)
        else:
            range_check(window, get_UL(window), get_LL(window), False)

        #perform median filtering to smooth data
        med_filter(window, 3)

        cleaned_val = window.slide_next(data_points.pop(0))
        cleaned_data.append(cleaned_val)
    
    return cleaned_data
        
        
        
    

def csv_to_datapoints(file_path):
    data_points = []

    with open(file_path, mode='r') as file:
        csv_reader = csv.reader(file)

        # Skip the header if present
        next(csv_reader, None)

        # Iterate through each row in the CSV
        for row in csv_reader:
            # Extract data from each row
            state = float(row[0])  
            time = row[1]
            device = row[2]
            unit = row[3]

            # Create a DataPoint object from the CSV row
            data_point = DataPoint(state, time, device, unit)

            # Append the DataPoint object to the list
            data_points.append(data_point)

    return data_points


def datapoints_to_csv(data_points, file_type, write_all):
    
    file_path = "../data/" + file_type + "_" + data_points[0].sensor_type + ".csv"
    
    mode = 'w' if write_all else 'a'
    
    with open(file_path, mode=mode, newline='') as file:
        csv_writer = csv.writer(file)

        # Write the header
        if write_all:
            csv_writer.writerow(['state', 'time', 'device', 'unit'])

        # Iterate through the DataPoint objects and write each to a row
        for data_point in data_points:
            # Create a row from the DataPoint attributes
            row = [
                data_point.get_val(),  # state
                data_point.get_time(),  # time
                data_point.sensor_type,  # device
                data_point.unit_of_measurement  # unit
            ]

            # Write the row to the CSV file
            csv_writer.writerow(row)

if __name__ == '__main__' :
    main()