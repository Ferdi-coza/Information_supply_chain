"""
Module containing all functions needed to Preprocess the data:
    is_const_err(window_vals, limit)
    med_filter(window, med_window)
    range_check(window, UL, LL, all_vals)
"""
from statistics import median, mean
from datetime import datetime


def do_EMA(window, last_EMA, alpha):
    window_vals = window.get_win_vals()
    latest_val = window_vals[-1]
    
    #determine new EMA value
    new_EMA = alpha * latest_val + ((1 - alpha) * last_EMA)
    
    #update last reading to new EMA value
    window.change_val(-1, new_EMA)
    
    #update last EMA
    last_EMA = new_EMA
    return last_EMA
    

def is_const_err(window, last_changed, max_time):
    """
    Check if the sensor is experiencing a constant error, where the latest value
    matches the previously recorded value for a time exceeding the allowed maximum.

    Args:
        window (SlidingWindow): The sliding window object containing sensor readings.
        last_changed (list): A list containing the last recorded value and its timestamp
                             in the format [value, timestamp].
        max_time (timedelta): The maximum allowed time between value changes before
                              it is considered a constant error.

    Returns:
        bool: True if a constant error is detected (value unchanged for too long), 
              False otherwise.
    """
    window_times = window.get_win_times()
    window_vals = window.get_win_vals()
    
    if window_vals[-1] == last_changed[0]:
        #new value == last changed value
        time_diff = time_difference(last_changed[1], window_times[-1])
        if time_diff > max_time:
            return True
        
    else:
        #new value != last changed value
        last_changed[0] = window_vals[-1]
        last_changed[1] = window_times[-1]
    
    return False
    


def med_filter(window, med_window):
    """
    Apply a median filter to the window values and update the window if necessary.

    Args:
        window (SlidingWindow): The sliding window object containing sensor readings.
        med_window (int): The size of the sub-window to apply the median filter to.

    Returns:
        None
    """
    window_vals = window.get_win_vals()
    med_arr = window_vals[:med_window]
    mid = med_window // 2

    if (med_arr[mid] != median(med_arr)):
        window.change_val(mid, median(med_arr))



def range_check(window, UL, LL, all_vals):
    """
    Check if values in the window are within a specified range and adjust if necessary.

    Args:
        window (SlidingWindow): The sliding window object containing sensor readings.
        UL (float): The upper limit for acceptable values.
        LL (float): The lower limit for acceptable values.
        all_vals (bool): Whether to check and adjust all values or only the latest one.

    Returns:
        None
    """
    window_vals = window.get_win_vals()
    if all_vals:
        for i in range(window.size):
            if (window_vals[i] > UL) or (window_vals[i] < LL):
                temp = window_vals[:i] + window_vals[i+1:]
                window.change_val(i, mean(temp))
    else:
        if (window_vals[-1] > UL) or (window_vals[-1] < LL):
            window_vals.pop()
            window.change_val(-1, mean(window_vals))
            
            
def time_difference(time1, time2):
    """
    Calculate the difference between two timestamps in the format "%H:%M:%S".

    Args:
        time1 (str): The first timestamp as a string.
        time2 (str): The second timestamp as a string.

    Returns:
        timedelta: The difference between the two times as a timedelta object.
    """
    time_format = "%H:%M:%S"

    t1 = datetime.strptime(time1, time_format)
    t2 = datetime.strptime(time2, time_format)
    
    # Calculate the difference (this will be a timedelta object)
    time_diff = t2 - t1
    
    return time_diff


def main():
    window = [10,9,10,100,13,14,10]
    print(range_check(window, 75, -12, True))


if __name__ == "__main__":
    main()
