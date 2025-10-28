from collections import deque
import math

class VolEstimator:
    def __init__(self, window:int=50):
        self.window = window
        self.q = deque(maxlen=window)
    def update(self, mid: float):
        if self.q and mid>0:
            ret = math.log(mid/self.q[-1])
            self.q.append(mid)
            return abs(ret)
        self.q.append(mid)
        return 0.0
    def realized(self)->float:
        if len(self.q)<2: return 0.0
        diffs = [abs(math.log(self.q[i]/self.q[i-1])) for i in range(1,len(self.q))]
        return sum(diffs)/len(diffs)
