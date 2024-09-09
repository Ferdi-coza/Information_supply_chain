from numpy import isnan

def valid_ph(reading):
    if isnan(reading):
        return False
    
    if (reading < 2) or (reading > 12):
        return False
    
    return True

def valid_illuminance(reading):
    if isnan(reading):
        return False
    
    if (reading < 0) or (reading > 100_000):
        return False
    
    return True
    

def valid_water_temp(reading):
    if isnan(reading):
        return False
    
    if (reading < 0) or (reading > 40):
        return False
    
    return True


def valid_ec(reading):
    if isnan(reading):
        return False
    
    if (reading < 0) or (reading > 20):
        return False
    
    return True
    