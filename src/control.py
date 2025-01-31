import logging
import time
from threading import Lock, Thread
from sql import SQL
import event


class RampProtection:
    """
    Sample taken from heating.
    (70.7 - 68.3)/(60*2)  # deg/s -> 2.4 deg/m
    I measured a lag time of ~2.6 minutes before hot air actuall
    starting raising the room temp at a fairly linear rate.
    """
    def __init__(self, db, eventq) -> None:
        self.eventq = eventq
        self.db = db
        self.check_period = 2*60  # seconds
        self.min_temp_change = 0.2  # 1.5 deg/min to deg/s
        # Time it takes for room to start raising temp after a call for heating or cooling.
        self.lag_time = 3*60

        self.thread = False
        self._allowed_to_run = False
        self.mutex = Lock()

        self.previous_time = 0
        self.previous_temp = 0

        self.LOGGER = logging.getLogger("RampProtection")

    def stop(self):
        with self.mutex:
            self._allowed_to_run = False

    def start(self):
        self.thread = Thread(target=self.start_temp_monitor, daemon=True)
        self.thread.start()

    def allowed_to_run(self):
        with self.mutex:
            return self._allowed_to_run and self.db["http_enabled"]

    def start_temp_monitor(self):
        """
        I need to put in a timer based check system?
        So a multithreaded individual check that wakes up when cycle time is engaged?
        Like FreeRTOS?

        I need error conditions and a log system.
        """
        with self.mutex:
            self._allowed_to_run = True

        self.LOGGER.debug("starting")
        self.LOGGER.debug("pausing for lag phase")

        time.sleep(self.lag_time)

        self.LOGGER.debug("resumed; lag phase ended")

        self.previous_time = time.time()
        self.previous_temp = self.db["current_temp"]

        # TODO: remove sleeps because i can't restart quickly
        time.sleep(self.check_period)

        while self.allowed_to_run():
            k = time.time()
            # TODO: add global filtering to temperature
            t = self.db["current_temp"]
            rate = (abs(t - self.previous_temp)*60)/(k - self.previous_time)
            self.previous_time = k
            self.previous_temp = t

            self.LOGGER.debug(f"rate abs(°F/m): {rate:.3f}")

            if rate < self.min_temp_change:
                self.LOGGER.error("generating fault event")
                self.eventq.put(event.FAULT)
                self.stop()
                return

            time.sleep(self.check_period)


class Heating(object):
    """
    docstring
    """
    def __init__(self,
                 database,
                 eventq=None,
                 cb_above=None,
                 cb_below=None,
                 sql=None):
        self.database = database
        self.eventq = eventq
        self.cb_above = cb_above  # callback
        self.cb_below = cb_below  # callback
        self.sql = sql

        self.mode = "off"

        self.LOGGER = logging.getLogger("CtrlHeating")

    def update(self, sample, humidity):
        # Get current control parameters.
        sp = self.database["sp"]
        threshold = self.database["threshold"]

        if sample == None:
            return

        if sample < sp:
            if self.mode == "off" and self.eventq:
                self.eventq.put(event.ON)
            self.mode = "on"
            self.database.set("cooling_status", "on")
        elif sample > (sp + threshold):
            if self.mode == "on" and self.eventq:
                self.eventq.put(event.OFF)
            self.mode = "off"
            self.database.set("cooling_status", "off")
        else:
            print("Threshold")

        # Hold relay open or closed.
        if self.mode == "on" and self.cb_above:
            self.cb_above()

        elif self.mode == "off" and self.cb_below:
            self.cb_below()

        # Only record when actual trigger is sent to turn on heat/ac.
        mode = 'true' if self.database[
            "http_enabled"] and self.mode == 'on' else 'false'

        if isinstance(self.sql, SQL):
            self.sql.insert("test2", t=sample, rh=humidity, sp=sp, mode=mode)
