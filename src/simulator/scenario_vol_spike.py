def vol_schedule(t:int)->float:
    # Low vol then sudden spike
    if t < 1500: return 0.0003
    if t < 2500: return 0.0015
    return 0.0006
