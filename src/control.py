import time
from threading import Lock
from sql import SQL


class Ramp:
    """
    Sample taken from heating.
    (70.7 - 68.3)/(60*2)  # deg/s -> 2.4 deg/m
    I measured a lag time of ~2.6 minutes before hot air actuall
    starting raising the room temp at a fairly linear rate.
    """
    def __init__(self) -> None:
        self.check_period = 60  # seconds
        self.min_temp_change = 1.5/60  # 1.5 deg/min to deg/s
        # Time it takes for room to start raising temp after a call for heating or cooling.
        self.lag_time = 60*3  # seconds

    def check(self):
        """
        I need to put in a timer based check system?
        So a multithreaded individual check that wakes up when cycle time is engaged?
        Like FreeRTOS?

        I need error conditions and a log system.


        """
        pass


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
        elif value > (sp + threshold):
            print("Heating Off")
            self.mode = "off"
            self.database.set("cooling_status", "off")
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

