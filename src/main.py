""" 
Warning:
I use null terminated strings in my messages to the teensy.
Be very careful.
"""

import http
import threading
import platform
import traceback
import os
import time
import queue

import http_client
import control
import filters
from database import Database
import cmd_shell
import arduino
import flask_app
from sql import SQL
import event


def control_loop(sensor, ctrl, db, eventq, safety):
    filter = filters.SlidingAverage(3)

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

        # Event handler.
        while True:
            try:
                evt = eventq.get_nowait()
                if evt == event.ON and db["http_enabled"]:
                    safety.start()
                if evt == event.OFF:
                    safety.stop()
                if evt == event.FAULT:
                    print("FAULT: temp rise not fast enough.")
                    db["fault_condition"] = "Error: Temp rise fault. Disabled HTTP."
                    ctrl.mode = "off"
                    ctrl.cb_above()
                    db["http_enabled"] = False
            except queue.Empty:
                break
    print("Control Loop Exited.")


# TODO: need single parameter definitions to ensure type safety carried over to web interface
# e.g. {"sp":74, "sp.type":float, "sp.min":68, "sp.max":80, "sp.step":0.5}
# make a database verify types on database construction
try:
    FLASK_LAN_ENABLED = True

    # When set to false, Flask will continuously scan my
    # repository and auto reload on code change.
    FLASK_NO_RELOAD = True

    BAUD_RATE = 9600

    PORT = ("COM5") if (s := platform.system()) == "Windows" else (
        "/dev/ttyACM0" if s == "Linux" else None)
    """
    I use no spaces in database names so that my 'cmd' interface can parse variabe names.
    """
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
            "min_runtime": 5,  # min; for safety
            "max_runtime": 20,  # min; for safety

            # Status parameters set by the running program.
            "current_temp": 0.0,  # sentinel value of 0.0
            "current_humidity": 111,  # sentinel value of 111
            "cooling_status": "off",
            "fault_condition": "none",
        })

    try:
        sql = SQL("test1", use_creds=True)
    except:
        sql = None

    http = http_client.Client(db)
    http.set_timeout(30)
    db["http_enabled"] = False

    eventq = queue.SimpleQueue()
    ctrl = control.Heating(
        database=db,
        eventq=eventq,
        cb_above=lambda: http.request("POST", "/api/cooling/status", "enable"),
        cb_below=lambda: http.request("POST", "/api/cooling/status", "disable"),
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
except Exception as ex:
    dir_path = os.path.dirname(os.path.realpath(__file__))

    def format_traceback(ex):
        s = "-------- start exception traceback --------\n"
        s += "".join(traceback.format_exception(ex))
        s += "-------- end exception traceback --------\n"
        return s

    with open(os.path.join(dir_path, 'traceback.log'), 'wt') as f:
        f.write(format_traceback(ex))
