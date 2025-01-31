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


def control_loop(sensor, ctrl, db, eventq, safety):
    # TODO: enforce explicit description of http hold-relay-closed messages and required
    # timing.
    # Report a fault if device could not be contacted.
    # Rreport a fault if time between messages exceded (with a buffer period).
    filter = filters.SlidingAverage(3)
    LOGGER = logging.getLogger("CtrlLoop")

    while True:
        # Blocks for temp read.
        t, rh = sensor.sample()
        if t == None or rh == None:
            # Tell filter that pipelined data
            # is no longer valid.
            filter.clear_buf()
            time.sleep(2)

        # Update for webpage.
        db["current_temp"] = t
        db["current_humidity"] = rh

        ctrl.update(filter.update(t), rh)

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
            # To ensure handling of all queued events, try until exception.
            try:
                evt = eventq.get_nowait()

                # TODO: This doesn't trigger safety if http is enabled after event.ON generated.
                if evt == event.ON and db["http_enabled"]:
                    safety.start()
                if evt == event.OFF:
                    safety.stop()
                if evt == event.FAULT:
                    LOGGER.error("FAULT: temp rise not fast enough, dissabling http.")
                    db["fault_condition"] += "Error: Temp rise fault. Disabling HTTP.\n"
                    ctrl.mode = "off"
                    ctrl.cb_above()
                    db["http_enabled"] = False
            except queue.Empty:
                break

    LOGGER.critical("Nonreachable Code: Control Loop Exited.")


def main():
    CLEAR_FAULTS_ON_START = False
    FLASK_LAN_ENABLED = True

    # When set to false, Flask will continuously scan my
    # repository and auto reload on code change.
    FLASK_NO_RELOAD = True

    BAUD_RATE = 9600

    PORT = ("COM5") if (s := platform.system()) == "Windows" else (
        "/dev/ttyACM0" if s == "Linux" else None)

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
            "http_enabled": True,  # master enable/disable
            "min_runtime": 5,  # min
            "max_runtime": 25,  # min TODO: rename to 'limit'

            # Status parameters set by the running program.
            "current_temp": 0.0,  # sentinel value of 0.0
            "current_humidity": 111,  # sentinel value of 111
            "cooling_status": "off",
            "fault_condition": "none",
        })

    # Clear faults on startup.;
    if CLEAR_FAULTS_ON_START:
        db["fault_condition"] = ""

    try:
        sql = SQL("test1", use_creds=True)
    except:
        sql = None

    http = http_client.Client(db)

    # This is the keep-alive timeout for the furnace microcontroller.
    # The furnace microcontroller disables itself if an
    # enable POST isn't continuously sent faster than the timeout.
    db["http_enabled"] = True
    http.set_timeout(30)

    # Always disable on boot. This may change in future.
    db["http_enabled"] = False

    eventq = queue.SimpleQueue()
    ctrl = control.Heating(
        database=db,
        eventq=eventq,
        cb_on=lambda: http.request("POST", "/api/cooling/status", "enable"),
        cb_off=lambda: http.request("POST", "/api/cooling/status", "disable"),
        sql=sql)

    sensor = arduino.Arduino(PORT, BAUD_RATE)
    safety = control.RampProtection(db, eventq)

    cthread = threading.Thread(target=control_loop,
                               args=(sensor, ctrl, db, eventq, safety),
                               daemon=True)
    cthread.start()

    # Start Flask webserver.
    flask_app.set_database(db)
    app = flask_app.create_app()
    t = threading.Thread(target=flask_app.run_app,
                         args=(app, FLASK_LAN_ENABLED, FLASK_NO_RELOAD),
                         daemon=True)
    t.start()

    # Main thread for controlling through shell.
    shell = cmd_shell.CommandShell(db)
    shell.cmdloop()


if __name__ == "__main__":
    main()
