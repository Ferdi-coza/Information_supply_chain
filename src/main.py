from mqtt_client import MQTTClient
from sliding_window import SlidingWindow
from data_point import DataPoint
from preprocessor import is_const_err, range_check, med_filter, do_EMA
from datetime import timedelta
from dotenv import load_dotenv
import os
import sys
import time
import csv

def main():
    """
    Main function that initiates the MQTT client or CSV processing based on command-line arguments.
    
    For "mqtt" DYNAMIC mode:
        Connects to the MQTT broker, retrieves readings, processes them, and logs to CSV.

    For "csv" STATIC mode:
        Cleans data from the specified CSV file and writes it back to a new cleaned CSV file.

    Args:
        None (but uses command-line arguments for "mqtt" or "csv" mode).

    Returns:
        None
    """
    window = SlidingWindow(10)
    clean_vals = []
    num_reads = 1
    last_changed = [0, 0]  #value, timestamp
    last_EMA = 0
    
    if (len(sys.argv) != 2) or (sys.argv[1] not in ("params", "mqtt", "csv")):
        print("Invalid program arguments")
        print("Run <python/python3 main.py params> to see parameter options")
        return
        
    
    if sys.argv[1] == "params":
        print("For Dynamic sensor readings: argv 1 = mqtt:")
        print("         argv 2 = panel_voltage | battery_voltage | water_temp | illuminance | ph")
        print()
        print("For Static data from csv file: argv 1 = csv")
        print("         argv 2 = csv file path eg ../Data/<csv_filename.csv>")
        return
    
    elif sys.argv[1] == "mqtt":
        #load environment variables
        load_dotenv()
        # Set up and start the MQTT client
        broker_address = os.getenv("MQTT_BROKER")
        broker_port = int(os.getenv("MQTT_PORT"))
        topic = os.getenv(sys.argv[2])
        mqtt_client = MQTTClient(broker_address, broker_port, topic)
        mqtt_client.connect()
        mqtt_client.start()
        client = mqtt_client
        
    elif sys.argv[1] == "csv":
        cleaned_data = run_csv(sys.argv[2], last_changed, last_EMA)
        datapoints_to_csv(cleaned_data, "clean", True)
        print("new cleaned data csv made")
        return
    
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
                    last_EMA = reading.value
                else: datapoints_to_csv([reading], "raw", False)
                num_reads += 1
                
            if reading and window.is_full():
                clean_vals.append(window.slide_next(reading))
                
            elif reading:
                window.add_reading(reading)
                
            
            ###################### Preprocess new readings #####################
            if window.is_full() and reading:
                #print(f"window before PP: {window.get_win_vals()}")
                
                if num_reads == 10:
                    last_changed[0] = window.get_win_vals()[-1]
                    last_changed[1] = window.get_win_times()[-1]
            
                #check for constant error sensor fault
                if is_const_err(window, last_changed, get_max_time(window)):
                    print("CONSTANT ERROR DETECTED")

                #perform range check on current window
                if num_reads == 10:
                    range_check(window, get_UL(window), get_LL(window), True)
                else:
                    range_check(window, get_UL(window), get_LL(window), False)

                #perform median filtering to smooth data
                med_filter(window, 3)

                #print(f"window after PP : {window.get_win_vals()}")
            
            
            client.clear_readings()
            time.sleep(1)


    except KeyboardInterrupt:
        # Stop the MQTT client correctly
        mqtt_client.stop()


def get_UL(window):
    """
    Get the upper limit (UL) for a sensor based on its type.

    Args:
        window (SlidingWindow): The sliding window object containing sensor readings.

    Returns:
        float: The upper limit for the specified sensor type.
    """
    sensor_type = window.get_sensor_type()
    if sensor_type == "voltage_sensor":
        UL = 300

    return UL


def get_LL(window):
    """
    Get the lower limit (LL) for a sensor based on its type.

    Args:
        window (SlidingWindow): The sliding window object containing sensor readings.

    Returns:
        float: The lower limit for the specified sensor type.
    """
    sensor_type = window.get_sensor_type()
    if sensor_type == "voltage_sensor":
        LL = -1

    return LL


def get_max_time(window):
    """
    Retrieve the maximum allowed time for readings based on the sensor type.

    Args:
        window (SlidingWindow): The sliding window object containing sensor readings.

    Returns:
        timedelta: The maximum time allowed for readings from the sensor.
    """
    sensor_type = window.get_sensor_type()
    max_time = 0
    
    if sensor_type == "voltage_sensor":
        max_time = timedelta(minutes=30)
    
    return max_time

def run_csv(file_path, last_changed, last_EMA):
    """
    Clean data from a CSV file by processing sensor readings and applying filters.

    Args:
        file_path (str): The path to the CSV file containing raw data.

    Returns:
        list: A list of cleaned DataPoint objects.
    """
    data_points = csv_to_datapoints(file_path)
    cleaned_data = []
    window = SlidingWindow(10)
    
    while not window.is_full():
        window.add_reading(data_points.pop(0))
        first_window = True
    
    while data_points:
        if first_window:
            last_changed[0] = window.get_win_vals()[-1]
            last_changed[1] = window.get_win_times()[-1]
            last_EMA = window.get_win_vals()[-1]

        #check for constant error sensor fault
        if is_const_err(window, last_changed, get_max_time(window)):
            print("CONSTANT ERROR DETECTED")

        #perform range check on current window
        if first_window:
            first_window = False
            range_check(window, get_UL(window), get_LL(window), True)
        else:
            range_check(window, get_UL(window), get_LL(window), False)
            
        #perform EMA smoothing
        last_EMA = do_EMA(window, last_EMA, 0.4)

        #perform median filtering to smooth data
        med_filter(window, 3)

        cleaned_val = window.slide_next(data_points.pop(0))
        cleaned_data.append(cleaned_val)
    
    cleaned_data += window.as_list()
    return cleaned_data
        

def csv_to_datapoints(file_path):
    """
    Convert data from a CSV file into a list of DataPoint objects.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        list: A list of DataPoint objects created from the CSV rows.
    """
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
    """
    Write a list of DataPoint objects to a CSV file.

    Args:
        data_points (list): The list of DataPoint objects to write.
        file_type (str): The type of file being written ("raw" or "clean").
        write_all (bool): Whether to overwrite the file (True) or append to it (False).

    Returns:
        None
    """
    file_path = "../data/" + file_type + "_" + data_points[0].sensor_type + ".csv"
    
    mode = 'w' if write_all else 'a'
    
    with open(file_path, mode=mode, newline='') as file:
        csv_writer = csv.writer(file)

        # Write the header
        if write_all:
            csv_writer.writerow(['State', 'Time', 'Device', 'Unit'])

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