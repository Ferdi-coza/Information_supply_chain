import time
from datetime import datetime, timezone
import pytz
import numpy as np
import matplotlib.pyplot as plt
import csv
from mqtt_client import MQTTClient
from buffer import Buffer
from data_point import DataPoint

################################### MQTT SETUP ###################################
# Configuration for the MQTT broker
broker_address = "smartdigitalsystems.duckdns.org"
broker_port = 1883
topic = "aquaponicsvertical/sensor/illuminance[lux]/json"

# Create an instance of the MQTTClient
mqtt_client = MQTTClient(broker_address, broker_port, topic)

# Connect to the MQTT broker and start the client
mqtt_client.connect()
mqtt_client.start()



################################### PLOT SETUP ###################################
fig, ax = plt.subplots()
ax.set_title('Sensor Data')
ax.set_xlabel('Time')
ax.set_ylabel('Measurement Value')
plt.ion()  # Interactive mode on


def main():
    buffer = Buffer()
    val_reads = []
    outliers = []

    try:
        while True:
            ################### retrieve and format new reading ###################
            latest_reading = None
            readings_list = mqtt_client.get_readings()
            if readings_list:
                raw_reading = readings_list[0]
                local_tz = pytz.timezone('Africa/Johannesburg')
                dt_object = datetime.fromtimestamp(int(raw_reading[1]), tz=pytz.utc).astimezone(local_tz)
                read_time = dt_object.strftime('%H:%M:%S')
                latest_reading = DataPoint(raw_reading[0], read_time)
                print(f"Latest reading: {latest_reading.get_val()}  |  {latest_reading.get_time()}")
                



            ###################### Preprocess new readings ######################

               



            

            ########################## Data Validation ##########################
            valid_reading = None
            outlier = None

            if buffer.buffer_full() and latest_reading:
                has_outlier , out_idx = buffer.is_iqr_outlier()
                if not(has_outlier):
                    valid_reading = buffer.buff_through(latest_reading)
                else:
                    outlier = buffer.remove_idx(out_idx)
                    buffer.add_reading(latest_reading)

            elif latest_reading: 
                buffer.add_reading(latest_reading)

            
            

            if valid_reading:
                val_reads.append(valid_reading)
                print(f"list of valid outputs: {get_list_vals(val_reads)}")

            if outlier:
                outliers.append(outlier)
                print(f"OUTLIER: {outlier}")
                print(f"list of outliers: {get_list_vals(outliers)}")
                print("|||||||||||||||||||||||||||||||||||||||||||||||||||||")


            print(f"buffer {buffer.get_buffer()}" )

            
            #plot the buffer
            #update_plot(buffer)

            #reset values
            mqtt_client.clear_readings()
            # Add a delay to avoid flooding the output
            time.sleep(1)

    except KeyboardInterrupt:
        # Stop the MQTT client correctly
        mqtt_client.stop()
        print("MQTT client stopped.")


def get_list_vals(list):
    new_list = []
    for i in range(len(list)):
        new_list.append(list[i].get_val())
    return new_list


def update_plot(buffer):
    values = buffer.get_buf_vals()
    if not values:
        return

    # Clear the plot
    ax.clear()

    # Generate simple indices for the x-axis
    indices = list(range(len(values)))

    # Plot the data using scatter plot
    ax.lines(indices, values, c='g', s=50, edgecolor='black', alpha=0.75)

    # Adjust plot limits with margin
    if len(indices) > 1:
        ax.set_xlim(-1, len(values))  # Add margin to the left and right
    else:
        ax.set_xlim(-1, 1)  # Set default limits when there is only one data point

    if len(values) > 1:
        y_margin = (max(values) - min(values)) * 0.1  # 10% margin
        ax.set_ylim(min(values) - y_margin, max(values) + y_margin)
    else:
        ax.set_ylim(values[0] - 1, values[0] + 1)  # Set default limits for a single value

    # Enhance plot appearance
    ax.grid(True)
    ax.set_facecolor('#f5f5f5')
    ax.set_title('Sensor Data', fontsize=14)
    ax.set_xlabel('Index', fontsize=12)
    ax.set_ylabel('Measurement Value', fontsize=12)
    ax.tick_params(axis='both', which='major', labelsize=10)

    # Redraw the figure
    fig.canvas.draw()
    fig.canvas.flush_events()
    plt.show()


def write_to_csv(file_name, data_points):
    # Create and write to the CSV file
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write header
        writer.writerow(['Value', 'Time_Stamp'])
        # Write data
        for dp in data_points:
            writer.writerow([dp.get_val(), dp.get_time()])



if __name__ == '__main__' :
    main()