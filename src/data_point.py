class DataPoint:

    def __init__(self, value, time_stamp):
        self.value = value
        self.time_stamp = time_stamp

    def get_val(self):
        return self.value
    
    def get_time(self):
        return self.time_stamp