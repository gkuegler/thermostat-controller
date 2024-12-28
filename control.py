import time
from threading import Lock
from sql import SQL


class CycleTimeLoggerBase:
    def __init__(self):
        pass

    def log_on(self):
        pass

    def log_off(self):
        pass


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
            off_duration = (self.time_on - self.time_off)/60.0
            with open(self.fname, 'at') as f:
                f.write(f"duration off: {off_duration:.2f}\n")

    def log_off(self):
        if not self.mode == 'off':
            self.mode = 'off'
            self.time_off = time.time()
            on_duration = (self.time_off - self.time_on)/60.0
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

        self.samples = [None]*sample_count
        self.index = 0
        self.mode = "off"
        self.cycle_logger = CycleTimeLoggerBase()
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
        return sum/float(len(self.samples))

    def update(self, sample, humidity):
        if isinstance(sample, (int, float)):
            self.database["current_temp"] = sample
        if isinstance(humidity, (int, float)):
            self.database["current_humidity"] = humidity

        # Get current control parameters.
        sp = self.database["sp"]
        threshold = self.database["threshold"]

        value = self.filter(sample)

        if value == None:
            return

        if value > sp:
            print("Cooling Needed")
            self.mode = "on"
            self.database.set("cooling_status", "on")
            self.cycle_logger.log_on()
        elif value < (sp - threshold):
            print("Cooling Off")
            self.mode = "off"
            self.database.set("cooling_status", "off")
            self.cycle_logger.log_off()
        else:
            print("Threshold")

        if self.mode == "on":
            self.cb_above()

        elif self.mode == "off":
            self.cb_below()


class SlidingWindowAverageHeating(object):
    """
    docstring
    """
    def __init__(self, database, sample_count, cb_above, cb_below, sql=None):
        self.database = database
        self.sample_count = sample_count
        self.cb_above = cb_above  # callback
        self.cb_below = cb_below  # callback
        self.sql = sql

        self.samples = [None]*sample_count
        self.index = 0
        self.mode = "off"
        self.cycle_logger = CycleTimeLoggerBase()
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
        return sum/float(len(self.samples))

    def update(self, sample, humidity):
        if isinstance(sample, (int, float)):
            self.database["current_temp"] = sample
        if isinstance(humidity, (int, float)):
            self.database["current_humidity"] = humidity

        # Get current control parameters.
        sp = self.database["sp"]
        threshold = self.database["threshold"]

        value = self.filter(sample)

        if value == None:
            return

        if value < sp:
            print("Heating Needed")
            self.mode = "on"
            self.database.set("cooling_status", "on")
            self.cycle_logger.log_on()
        elif value > (sp + threshold):
            print("Heating Off")
            self.mode = "off"
            self.database.set("cooling_status", "off")
            self.cycle_logger.log_off()
        else:
            print("Threshold")

        if self.mode == "on":
            self.cb_above()

        elif self.mode == "off":
            self.cb_below()

        # Only record when actual trigger is sent to turn on heat/ac.

        mode = 'true' if self.database[
            "http_enabled"] and self.mode == 'on' else 'false'

        if isinstance(self.sql, SQL):
            self.sql.insert("test2", t=value, rh=humidity, sp=sp, mode=mode)


if __name__ == '__main__':
    d = CycleTimeLogger()
    d.log_on()
    time.sleep(6)
    d.log_off()
