import logging
import time
import datetime
from threading import Lock, Thread
from sql import SQL
import event
from math import exp

import data


def minutes(s):
    return s*60.0


# TODO: Disable min-temp rate check after 1st check and let duration handle it?
# or make the checks follow the min curve, so 1st measurement needs to be above 0.5°F
# and the subsequent need to follow the exponential decay? I like this idea. Need the
# formula from excel trendline though or run a bunch of sql querries when the call for heat was 'on'?
# Find deviation from curve and require 90% adherrance?
# TODO: timed ramp protection => dT = 0.5 * e^(-0.2*t)
# 0.25°F/min has been observed with the vent closed
class RampProtection:
    """
    Sample taken from heating.
    I measured a lag time of ~2.6 minutes before hot air actually
    starting raising the room temp at a fairly linear rate.
    """
    def __init__(self, db, eventq) -> None:
        self.eventq = eventq
        self.db = db
        self.check_period = 2*60  # seconds
        self.min_temp_rate = 0.1  # °F/min
        # Time it takes for room to start raising temp after a call for heating.
        self.lag_time = 3*60 + 30
        self.rate_violation_limit = 3

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

    def calc_req_temp_rise_rate_from_curve(self, t: float):
        return 0.5*exp(-0.25*t)

    def start_temp_monitor(self):
        """
        I need to put in a timer based check system? So a multithreaded
        individual check that wakes up when cycle time is engaged? Like
        FreeRTOS?

        I need error conditions and a log system.
        """
        with self.mutex:
            self._allowed_to_run = True

        rate_violations = 0

        self.LOGGER.debug("starting")
        self.LOGGER.debug("pausing for lag phase")

        start = time.time()

        time.sleep(self.lag_time)

        self.LOGGER.debug("resumed; lag phase ended")
        now = time.time()

        # Hack
        time_start_checking = now + self.check_period

        self.previous_time = now
        self.previous_temp = data.data["current_temp"]

        # TODO: remove sleeps because i can't restart quickly
        if not self.allowed_to_run():
            return

        time.sleep(self.check_period)

        while self.allowed_to_run():
            now = time.time()
            # TODO: add global filtering to current temperature
            t = data.data["current_temp"]
            rate = ((t - self.previous_temp)*60)/(now - self.previous_time)
            self.previous_time = now
            self.previous_temp = t

            delta = (now - time_start_checking)/60.0
            req_rate = self.calc_req_temp_rise_rate_from_curve(delta)
            self.LOGGER.info(
                f"temp change rate = {delta:.1f}min {rate:.3f}°F/min > {req_rate:.3f}°F/min"
            )

            if rate < req_rate:
                rate_violations += 1
                self.LOGGER.error(
                    f"FAULT: a temp change rate of '{req_rate:.3f}°F/min' was not met.\n"
                    f"Measured a rate of '{rate:.3f}°F/min'; violation #{rate_violations}"
                )

            if rate_violations >= self.rate_violation_limit:
                self.LOGGER.error(f"Max number of rate violations reached.")
                self.eventq.put(event.FAULT)
                return

            if ((now - start)/60) > self.db["max_runtime"]:
                self.LOGGER.error("FAULT: max runtime exceeded")
                self.eventq.put(event.FAULT)
                return

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
            self.db["fault_condition"] += f"Warning: Short Cycle: {duration_formatted}"

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
