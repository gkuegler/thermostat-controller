import time
from threading import Lock


class DataLogger:

    def __init__(self):
        self.time_on = 0
        self.time_off = 0
        self.fname = "cycle time data.txt"
        self.mode = 'off'

    def log_on(self):
        if not self.mode == 'on':
            self.mode = 'on'
            self.time_on = time.time()
            off_duration = (self.time_on - self.time_off) / 60.0
            with open(self.fname, 'at') as f:
                f.write(f"duration off: {off_duration:.2f}\n")

    def log_off(self):
        if not self.mode == 'off':
            self.mode = 'off'
            self.time_off = time.time()
            on_duration = (self.time_off - self.time_on) / 60.0
            with open(self.fname, 'at') as f:
                f.write(f"duration on: {on_duration:.2f}\n")


class SlidingWindowAverageCooling(object):
    """
    docstring
    """

    def __init__(self, sp, threshold, sample_count, cb_above, cb_below):
        self.sp = sp
        self.threshold = threshold
        self.sample_count = sample_count
        self.cb_above = cb_above
        self.cb_below = cb_below

        self.samples = [None] * sample_count
        self.index = 0

        self.mode = "off"

        self.data_logger = DataLogger()

        self.mutext = Lock()

    def increment_index(self):
        """
        Wrap the index around the circular buffer.
        """
        if self.index >= self.sample_count - 1:
            self.index = 0
        else:
            self.index += 1

    def clear_buf(self):
        for i in range(len(self.samples)):
            self.samples[i] = None

    def set_sp(self, sp):
        with self.mutext:
            self.sp = sp

    def set_threshold(self, threshold):
        with self.mutext:
            self.threshold = threshold

    def update(self, sample):
        with self.mutext:
            self.samples[self.index] = sample
            self.increment_index()

            sum = 0
            for x in self.samples:
                if isinstance(x, (int, float)):
                    sum += x
                else:
                    return None

            avg = sum / float(len(self.samples))

            if avg > self.sp:
                print("Cooling Needed")
                self.mode = "on"
                self.data_logger.log_on()
            elif avg < (self.sp - self.threshold):
                print("Cooling Off")
                self.mode = "off"
                self.data_logger.log_off()
            else:
                print("Threshold")

            if self.mode == "on":
                self.cb_above()

            elif self.mode == "off":
                self.cb_below()


if __name__ == '__main__':
    d = DataLogger()
    d.log_on()
    time.sleep(6)
    d.log_off()
