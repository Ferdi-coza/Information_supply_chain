class DataPoint:

    def __init__(self, value, time_stamp, sensor_type, unit_of_measurement):
        self.value = value
        self.time_stamp = time_stamp
        self.sensor_type = sensor_type
        self.unit_of_measurement = unit_of_measurement

    def get_val(self):
        return self.value
    
    def get_time(self):
        return self.time_stamp