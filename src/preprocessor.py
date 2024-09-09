from statistics import median, variance, mean

def is_const_err(window_vals, limit):
    if variance(window_vals) < limit:
        return True
    return False


def med_filter(window_vals, med_window):
    med_arr = window_vals[:med_window]
    mid = med_window // 2

    if (med_arr[mid] != median(med_arr)):
        med_arr[mid] = median(med_arr)

    window_vals = med_arr + window_vals[med_window:]
    return window_vals


def range_check(window_vals, UL, LL, all_vals):
    if all_vals:
        for i in range(len(window_vals)):
            if (window_vals[i] > UL) or (window_vals[i] < LL):
                temp = window_vals[:i] + window_vals[i+1:]
                window_vals[i] = mean(temp)
    else:
        if (window_vals[-1] > UL) or (window_vals[-1] < LL):
            window_vals.pop()
            window_vals.append(mean(window_vals))

    return window_vals


def get_excluder_arr(arr, index):
    excluded = []
    excluded += arr[:index]
    excluded += arr[index+1:]
    return excluded



def main():
    window = [10,9,10,100,13,14,10]
    print(range_check(window, 75, -12, True))



if __name__ == "__main__":
    main()
