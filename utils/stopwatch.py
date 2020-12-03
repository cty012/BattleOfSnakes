import time

import utils.functions as utils


class Stopwatch:
    def __init__(self, start_time=0):
        self.start_time = None
        self.end_time = None
        self.speed = 1
        self.interval = start_time

    def start(self, speed=None):
        if self.start_time is not None and self.end_time is not None:
            self.interval += self.speed * (self.end_time - self.start_time)
            self.start_time = self.end_time = None
        if self.start_time is None:
            self.start_time = time.time()
            if speed is not None:
                self.speed = speed

    def set_speed(self, speed):
        if self.start_time is not None and self.end_time is not None:
            self.interval += self.speed * (self.end_time - self.start_time)
        elif self.start_time is not None and self.end_time is None:
            current = time.time()
            self.interval += self.speed * (current - self.start_time)
            self.start_time = current
        self.speed = speed

    def stop(self):
        if self.start_time is None:
            return
        self.end_time = time.time()

    def is_running(self):
        return self.start_time is not None and self.end_time is None

    def get_time(self):
        """return the passed time in seconds"""
        if self.start_time is None:
            return self.interval
        elif self.end_time is None:
            return self.speed * (time.time() - self.start_time) + self.interval
        return self.speed * (self.end_time - self.start_time) + self.interval

    def get_str_time(self):
        """MINUTE:SECOND:1/100SECOND"""
        return utils.to_str_time(int(self.get_time() * 100))

    def clear(self):
        self.start_time = None
        self.end_time = None
        self.interval = 0
