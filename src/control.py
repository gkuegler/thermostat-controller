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
        self.min_temp_rate = 0.2  # 1.5 deg/min to deg/s
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
            rate = ((t - self.previous_temp)*60)/(k - self.previous_time)
            self.previous_time = k
            self.previous_temp = t

            self.LOGGER.debug(f"rate abs(°F/m): {rate:.3f}")

            if rate < self.min_temp_rate:
                self.LOGGER.error("FAULT: temp rise rate not met")
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
                 cb_on=None,
                 cb_off=None,
                 sql=None):
        self.db = database
        self.eventq = eventq
        self.cb_on = cb_on  # callback to turn heating on
        self.cb_off = cb_off  # callback to turn heating off
        self.sql = sql

        self.mode = "off"

        self.LOGGER = logging.getLogger("CtrlHeating")

    def update(self, sample, humidity):
        # Get current control parameters.
        sp = self.db["sp"]
        threshold = self.db["threshold"]

        if sample == None:
            return

        # Only turn on unless it was off before.
        if sample < sp and self.db["http_enabled"] and self.mode == "off":
            self.mode = "on"
            self.db.set("cooling_status", "on")  # only for web UI
            if self.eventq:
                self.eventq.put(event.ON)
        # Explicitly not requre heater to be on to turn it off.
        elif sample > (sp + threshold):
            self.LOGGER.info("call for off")
            self.mode = "off"
            self.db.set("cooling_status", "off")
            if self.mode == "on" and self.eventq:
                self.eventq.put(event.OFF)
        else:
            print("Threshold")

        # Hold relay open or closed.
        if self.mode == "on" and self.cb_on:
            self.cb_on()

        elif self.mode == "off" and self.cb_off:
            self.cb_off()

        # Only record when actual trigger is sent to turn on heat/ac.
        # TODO: convert to 1's and 0's for averages in grafana to work
        mode = 'true' if self.db[
            "http_enabled"] and self.mode == 'on' else 'false'

        if isinstance(self.sql, SQL):
            self.sql.insert("test2", t=sample, rh=humidity, sp=sp, mode=mode)
