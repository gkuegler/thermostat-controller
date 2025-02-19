import logging
import time
import datetime
from threading import Lock, Thread
from sql import SQL
import event

import data


# TODO: Disable min-temp rate check after 1st check and let duration handle it?
# or make the checks follow the min curve, so 1st measurement needs to be above 0.5°F
# and the subsequent need to follow the exponential decay? I like this idea. Need the
# formula from excel trendline though or run a bunch of sql querries when the call for heat was 'on'?
# Find deviation from curve and require 90% adherrance?
# TODO: timed ramp protection => dT = 0.5 * e^(-0.2*t)
class RampProtection:
    """
    Sample taken from heating.
    I measured a lag time of ~2.6 minutes before hot air actually
    starting raising the room temp at a fairly linear rate.
    """
    def __init__(self, db, eventq) -> None:
        self.eventq = eventq
        self.db = db
        self.check_period = 30  # seconds
        self.min_temp_rate = 0.1  # °F/min
        # Time it takes for room to start raising temp after a call for heating.
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
            return self._allowed_to_run

    def calc_req_temp_rise_from_curve(self):
        pass

    def start_temp_monitor(self):
        """
        I need to put in a timer based check system? So a multithreaded
        individual check that wakes up when cycle time is engaged? Like
        FreeRTOS?

        I need error conditions and a log system.
        """
        with self.mutex:
            self._allowed_to_run = True

        self.LOGGER.debug("starting")
        self.LOGGER.debug("pausing for lag phase")

        start = time.time()

        time.sleep(self.lag_time)

        self.LOGGER.debug("resumed; lag phase ended")

        self.previous_time = time.time()
        self.previous_temp = data.data["current_temp"]

        # TODO: remove sleeps because i can't restart quickly
        if not self.allowed_to_run():
            return

        time.sleep(self.check_period)

        while self.allowed_to_run():
            k = time.time()
            # TODO: add global filtering to current temperature
            t = data.data["current_temp"]
            rate = ((t - self.previous_temp)*60)/(k - self.previous_time)
            self.previous_time = k
            self.previous_temp = t

            self.LOGGER.info(f"temp change rate = {rate:.3f}°F/min")

            if rate < self.min_temp_rate:
                self.LOGGER.error(
                    f"FAULT: a temp change rate of '{self.min_temp_rate:.3f}°F/min' was not met.\n"
                    f"Measured a rate of '{rate:.3f}°F/min'")
                # self.eventq.put(event.FAULT)
                # self.stop()
                return

            if ((k - start)/60) > self.db["max_runtime"]:
                self.LOGGER.error("FAULT: max runtime exceeded")
                self.eventq.put(event.FAULT)
                self.stop()

            time.sleep(self.check_period)
        self.LOGGER.debug("exiting ramp protection")


class Heating(object):
    """
    docstring
    """

    # TODO: combine ramp control with this class to make a Furnace controller?
    def __init__(self, database, eventq=None, cb_on=None, cb_off=None):
        self.db = database
        self.eventq = eventq
        self.cb_on = cb_on  # callback to turn heating on
        self.cb_off = cb_off  # callback to turn heating off
        self.start_time = 0

        self.mode = "off"

        self.LOGGER = logging.getLogger("CtrlHeating")

    def _switch_on(self):
        self.mode = "on"
        self.LOGGER.info("call for on")
        self.start_time = time.time()
        if self.eventq:
            self.eventq.put(event.ON)

    def _switch_off(self):
        self.mode = "off"
        self.LOGGER.info("call for off")
        duration = time.time() - self.start_time
        duration_formatted = datetime.timedelta(seconds=duration)
        self.LOGGER.info(f"duration: {duration_formatted}")
        if duration < 10*60:
            self.LOGGER.warning(f"Short cycled, duration: {duration_formatted}")
            self.db["fault_condition"] += "Warning: Short Cycle: {duration_formatted}"

        if self.eventq:
            self.eventq.put(event.OFF)

    def safety_checks(self):
        # TODO: in thread or out of thread? or use ticks? or time?
        return

    def update(self, sample):
        if not self.db["controller_enabled"]:
            if self.mode == "on":
                self._switch_off()
            return None

        if sample == None:
            return None

        # Get current control parameters.
        sp = self.db["sp"]
        threshold = self.db["threshold"]

        # Only turn on unless it was off before.
        if sample < sp and self.mode == "off":
            self._switch_on()
        elif sample > (sp + threshold):
            if self.mode == "on":
                self._switch_off()
            # Redundant mode set to off.
            self.mode = "off"
        else:
            print("Threshold")

        # Hold relay open or closed.
        if self.mode == "on" and self.cb_on:
            self.cb_on()

        elif self.mode == "off" and self.cb_off:
            self.cb_off()

        return self.mode
