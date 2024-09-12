from datetime import datetime
from numpy import std, mean
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


def CUSUM(CT_plus_win, CT_min_win, window_vals):
    """
    Compute the next values for the CUSUM control chart.

    Args:
        CT_plus_win (SlidingWindow): A deque holding previous positive cumulative sums (CUSUM+).
        CT_min_win (SlidingWindow): A deque holding previous negative cumulative sums (CUSUM-).
        slack (float): The slack value or allowable deviation from the target.
        control_lim (float): The control limit for detecting an out-of-control process.

    Returns:
        boolean: a boolean indicating if the process is in control.
    """
    target = get_target(window_vals)
    slack = get_slack(window_vals)
    control_lim = get_control_lim(window_vals)
    
    # Compute the deviation from the target
    dev_plus = max(0, window_vals[0] - target - slack)
    dev_minus = min(0, window_vals[0] - target + slack)
    
    if CT_plus_win.is_full():
        CT_plus_win.slide_next(float(dev_plus))
        CT_min_win.slide_next(float(dev_minus))
    else:
        CT_plus_win.add_reading(float(dev_plus))
        CT_min_win.add_reading(float(dev_minus))
        
    CT_plus_sum = sum(CT_plus_win.as_list())
    CT_minus_sum = sum(CT_min_win.as_list())
    
    if CT_plus_sum > control_lim:
        return False
    
    if CT_minus_sum < control_lim:
        return False
    
    return True


def get_slack(sensor_readings, k=2):
    
    """
    Calculate slack based on the standard deviation of sensor readings.
    
    Args:
        sensor_readings (list): A list of sensor readings in the sliding window.
        k (float): Multiplier to adjust the slack level. Default is 2.
        
    Returns:
        float: The calculated slack based on the standard deviation.
    """
    return k * std(sensor_readings)

def get_control_lim(sensor_readings, k=5):
    
    return k * std(sensor_readings)

def get_target(window_vals):
    return mean(window_vals)