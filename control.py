import time
from threading import Lock


class CycleTimeLogger:

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

    def __init__(self, database, sample_count, cb_above, cb_below):
        self.database = database
        self.sample_count = sample_count
        self.cb_above = cb_above  # callback
        self.cb_below = cb_below  # callback

        self.samples = [None] * sample_count
        self.index = 0
        self.mode = "off"
        self.cycle_logger = CycleTimeLogger()
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

    def filter(self, sample):
        """
        Return the average temperature across the last (3) samples.
        """
        self.samples[self.index] = sample
        self.increment_index()
        sum = 0
        for x in self.samples:
            if isinstance(x, (int, float)):
                sum += x
            else:
                return None
        return sum / float(len(self.samples))

    def update(self, sample):
        if isinstance(sample, (int, float)):
            self.database["current_temp"] = sample

        # Get current control parameters.
        sp = self.database["sp"]
        threshold = self.database["threshold"]

        value = self.filter(sample)

        if value > sp:
            print("Cooling Needed")
            self.mode = "on"
            self.database["cooling_mode"] = "on"
            self.cycle_logger.log_on()
        elif value < (sp - threshold):
            print("Cooling Off")
            self.mode = "off"
            self.database["cooling_mode"] = "off"
            self.cycle_logger.log_off()
        else:
            print("Threshold")

        if self.mode == "on":
            self.cb_above()

        elif self.mode == "off":
            self.cb_below()


if __name__ == '__main__':
    d = CycleTimeLogger()
    d.log_on()
    time.sleep(6)
    d.log_off()
