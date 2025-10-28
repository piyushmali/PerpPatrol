class LoopDetector:
    def __init__(self, min_ms:int): self.min_ms = min_ms
    def ok(self, last_fill_ms:int, now_ms:int)->bool:
        return (now_ms - last_fill_ms) >= self.min_ms
