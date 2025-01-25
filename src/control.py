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
    def __init__(self, database, cb_above, cb_below, sql=None):
        self.database = database
        self.cb_above = cb_above  # callback
        self.cb_below = cb_below  # callback
        self.sql = sql

        self.mode = "off"

    def update(self, sample, humidity):
        # Get current control parameters.
        sp = self.database["sp"]
        threshold = self.database["threshold"]

        if sample == None:
            return

        if sample < sp:
            print("Heating Needed")
            self.mode = "on"
            self.database.set("cooling_status", "on")
        elif sample > (sp + threshold):
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
            self.sql.insert("test2", t=sample, rh=humidity, sp=sp, mode=mode)
