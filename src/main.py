""" 
Warning:
I use null terminated strings in my messages to the teensy.
Be very careful.
"""

import threading
import platform
import traceback
import os
import time

import http_client
import control
import filters
from database import Database
import cmd_shell
import arduino
import flask_app
from sql import SQL


def control_loop(device, ctrl, db):
    filter = filters.SlidingAverage(3)

    while (True):
        # Blocks for temp read.
        t, rh = device.sample()
        if t == None or rh == None:
            # Tell filter that pipelined data
            # is no longer valid.
            filter.clear_buf()
            time.sleep(2)

        # Update for webpage.
        db["current_temp"] = t
        db["current_humidity"] = rh

        ctrl.update(filter.update(t), rh)


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

    db = Database(
        name="data",
        sample_data={
            # User controlled parameters.
            "host": "10.0.0.10",
            "port": 80,
            "sp": 65,
            "threshold": 1.5,
            "sample_count": 3,
            "http_enabled": True,

            # Status parameters set by the running program.
            "current_temp": 0.0,
            "cooling_status": "off",
            "current_humidity": 111
        })

    try:
        sql = SQL("test1", use_creds=True)
    except:
        sql = None

    http = http_client.Client(db)
    http.set_timeout(30)
    db["http_enabled"] = False

    ctrl = control.SlidingWindowAverageHeating(
        database=db,
        cb_above=lambda: http.request("POST", "/api/cooling/status", "enable"),
        cb_below=lambda: http.request("POST", "/api/cooling/status", "disable"),
        sql=sql)

    device = arduino.Arduino(PORT, BAUD_RATE)

    cthread = threading.Thread(target=control_loop,
                               args=(device, ctrl, db),
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
