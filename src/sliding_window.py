from collections import deque

class SlidingWindow:
    
    def __init__(self, size):
        self.size = size
        self.max_size = 40                             # Max size of window queue
        self.window = deque(maxlen=self.max_size)      # create a queue object


    def add_reading(self, reading):
        self.window.append(reading)
    
    
    def slide_next(self, reading):
        self.window.append(reading)
        return self.window.popleft()


    def remove_idx(self, idx):
        buf_list = list(self.window)
        removed = buf_list.pop(idx)
        self.window = deque(buf_list, maxlen=self.max_size)
        return removed

    
    def buf_as_list(self):
        return list(self.window)


    def get_win_vals(self):
        obj_list = list(self.window)
        vals_list = []

        for i in range(len(self.window)):
            vals_list.append(obj_list[i].get_val())
        
        return vals_list
    

    def get_win_times(self):
        obj_list = list(self.window)
        times_list = []

        for i in range(len(self.window)):
            times_list.append(obj_list[i].get_time())
        
        return times_list
    

    def get_sensor_type(self):
        readings = list(self.window)
        return readings[0].sensor_type
    

    def change_val(self, index, new_val):
        readings = list(self.window)
        readings[index].value = new_val
        

    def is_full(self):
        return len(self.window) >= self.size
    

    
    
    
def main():
    pass


if __name__ == '__main__' :
    main()