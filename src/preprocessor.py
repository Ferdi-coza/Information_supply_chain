from statistics import median, variance, mean

def is_const_err(window_vals, limit):
    if variance(window_vals) < limit:
        return True
    return False


def med_filter(window, med_window):
    window_vals = window.get_win_vals()
    med_arr = window_vals[:med_window]
    mid = med_window // 2

    if (med_arr[mid] != median(med_arr)):
        window.change_val(mid, median(med_arr))



def range_check(window, UL, LL, all_vals):
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


def main():
    window = [10,9,10,100,13,14,10]
    print(range_check(window, 75, -12, True))



if __name__ == "__main__":
    main()
