from collections import deque
import numpy as np

class Buffer:
    
    def __init__(self):
        self.max_size = 40                             # Max size of buffer queue
        self.buffer = deque(maxlen=self.max_size)      # create a queue object


    def add_reading(self, reading):
        self.buffer.append(reading)                    # add element to the right end of the queue


    def remove_idx(self, idx):
        buf_list = list(self.buffer)
        removed = buf_list.pop(idx)
        self.buffer = deque(buf_list, maxlen=self.max_size)
        return removed


    def get_buffer(self):
        buf_list = []
        obj_list = list(self.buffer)

        for i in range(len(self.buffer)):
            buf_list.append((obj_list[i].get_val(), obj_list[i].get_time()))
        
        return buf_list
    
    def buf_as_list(self):
        return list(self.buffer)


    def get_buf_vals(self):
        obj_list = list(self.buffer)
        vals_list = []

        for i in range(len(self.buffer)):
            vals_list.append(obj_list[i].get_val())
        
        return vals_list
    

    def get_buf_times(self):
        obj_list = list(self.buffer)
        times_list = []

        for i in range(len(self.buffer)):
            times_list.append(obj_list[i].get_time())
        
        return times_list
        


    def buffer_full(self):
        return len(self.buffer) >= 10
    

    def buff_through(self, reading):
        self.buffer.append(reading)
        return self.buffer.popleft()                    # remove leftmost element
    
    
    def is_iqr_outlier(self):
        np_buf_arr = np.array(self.get_buf_vals())     #self.get_buf_vals()
        Q1 = np.percentile(np_buf_arr, 25)
        Q3 = np.percentile(np_buf_arr, 75)
        IQR = Q3 - Q1

        if IQR == 0.0:
            return False, None
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        mid_idx = len(np_buf_arr) // 2 -1
        if np_buf_arr[mid_idx] <= lower_bound or np_buf_arr[mid_idx] >= upper_bound:
            return True, mid_idx
        else:
            return False, None

        
    


        


    

def main():
    buffer = Buffer()

    buffer.add_reading(43.61)
    buffer.add_reading(43.59)
    buffer.add_reading(43.59)
    buffer.add_reading(43.58)
    buffer.add_reading(43.59)

    print(buffer.is_iqr_outlier())




if __name__ == '__main__' :
    main()