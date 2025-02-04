import threading
import platform
import os
import time
import queue
import logging

import http_client
import control
import filters
from database import Database
import cmd_shell
import arduino
import flask_app
from sql import SQL
import event
import log
from threads import ThreadWithExceptionLogging, log_traceback_to_file
import data


def control_loop(controller, db, eventq):
    # TODO: enforce explicit description of http hold-relay-closed messages and required
    # timing.
    # Report a fault if device could not be contacted.
    # Rreport a fault if time between messages exceded (with a buffer period).
    BAUD_RATE = 9600
    PORT = ("COM5") if (s := platform.system()) == "Windows" else (
        "/dev/ttyACM0" if s == "Linux" else None)
    SAMPLE_PERIOD_UPPER_WARNING_S = 15  # seconds
    LOGGER = logging.getLogger("CtrlLoop")

    filter = filters.SlidingAverage(3)
    sensor = arduino.Arduino(PORT, BAUD_RATE)
    safety = control.RampProtection(db, eventq)
    sql = None

    try:
        sql = SQL("test1", use_creds=True)
    except Exception as ex:
        LOGGER.error("No SQL")
        db["fault_condition"] += "No SQL. See traceback logs.\n"
        log_traceback_to_file(ex, "sql")

    while True:
        start = time.time()
        # Blocks for temp read.
        t, rh = sensor.sample()
        if t == None or rh == None:
            # Tell filter that pipelined data
            # is no longer valid.
            filter.clear_buf()
            time.sleep(0.1)
            continue

        # TODO: make average handler work with datapoints as it gets them.
        mode = controller.update(filter.update(t))

        # Update for webpage.
        data.data["current_temp"] = t
        data.data["current_humidity"] = rh

        # Only record when actual trigger is sent to turn on heat/ac.
        # TODO: convert to 1's and 0's for averages in grafana to work
        mode = 'true' if mode == 'on' else 'false'

        if isinstance(sql, SQL):
            sql.insert("test2", t, rh, sp=db["sp"], mode=mode)

        # Gaurd against event handlers generating an infinite
        # circular chain of events.
        max_event_cnt = 50

        # Handle all queued events.
        while True:
            max_event_cnt -= 1
            if max_event_cnt < 0:
                LOGGER.critical("Max number of event handle limit reached. "
                                "Possible circular logic error in code.")
                db["fault_condition"] += "Too many events handled."
                break
            # Python std queue.qsize() is not garunteed to be accurate.
            # Try until exception to ensure handling of all queued events.
            try:
                match eventq.get_nowait():
                    case event.ON:
                        data.data["cooling_status"] = "on"
                        safety.start()
                    case event.OFF:
                        data.data["cooling_status"] = "off"
                        safety.stop()
                    case event.FAULT:
                        LOGGER.error(
                            "FAULT: temp rise not fast enough, dissabling http.")
                        db["fault_condition"] += "Error: Temp rise fault. Disabling HTTP.\n"
                        controller.mode = "off"
                        controller.cb_above()
                        db["http_enabled"] = False
            except queue.Empty:
                break

        if (t := (time.time() - start)) > SAMPLE_PERIOD_UPPER_WARNING_S:
            LOGGER.warning(f"Control loop exceded time limit. Took {t:.2f}s")
            db["fault_condition"] += "Sample Period Exceded.\n"

    LOGGER.critical("Nonreachable Code: Control Loop Exited.")
    db["fault_condition"] += "Control loop exited.\n"


def main():
    CLEAR_FAULTS_ON_START = False
    FLASK_LAN_ENABLED = True

    # When set to false, Flask will continuously scan my
    # repository and auto reload on code change.
    FLASK_NO_RELOAD = True

    log.set_up_main_logger(
        os.path.splitext(__file__)[0] + ".log", logging.DEBUG, logging.DEBUG)
    """
    I use no spaces in database names so that my 'cmd' interface can parse variabe names.
    """
    # TODO: make a persistent and non-persistent section and getter & setter &
    # publisher/subscriber interfaces. Use native attribs instead of dictionary
    # interface?
    db = Database(
        name="data",
        sample_data={
            # User controlled parameters.
            "host": "10.0.0.10",
            "port": 80,
            "sp": 67,
            "threshold": 3,
            "sample_period": 10,  # FUTURE
            "sample_count": 3,  # no. of smaples to average
            "http_enabled": False,  # master enable/disable
            "controller_enabled": False,
            "min_runtime": 5,  # min
            "max_runtime": 25,  # min TODO: rename to 'limit'
            "fault_condition": "none",
        })

    # Clear faults on startup.;
    if CLEAR_FAULTS_ON_START:
        db["fault_condition"] = ""

    http = http_client.Client(db)

    # This is the keep-alive timeout for the furnace microcontroller.
    # The furnace microcontroller disables itself if an
    # enable POST isn't continuously sent faster than the timeout.
    db["http_enabled"] = True
    http.set_timeout(30)

    # Always disable on boot. This may change in future.
    db["http_enabled"] = False

    eventq = queue.SimpleQueue()
    controller = control.Heating(
        database=db,
        eventq=eventq,
        cb_on=lambda: http.request("POST", "/api/cooling/status", "enable"),
        cb_off=lambda: http.request("POST", "/api/cooling/status", "disable"))

    cthread = ThreadWithExceptionLogging(target=control_loop,
                                         args=(controller, db, eventq),
                                         daemon=True)
    cthread.start()

    # Start Flask webserver.
    flask_app.set_database(db)
    app = flask_app.create_app()
    t = ThreadWithExceptionLogging(target=flask_app.run_app,
                                   args=(app, FLASK_LAN_ENABLED, FLASK_NO_RELOAD),
                                   daemon=True)
    t.start()

    # Main thread for controlling through shell.
    shell = cmd_shell.CommandShell(db)
    shell.cmdloop()


if __name__ == "__main__":
    main()
