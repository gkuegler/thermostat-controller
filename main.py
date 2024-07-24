""" 
Warning:
I use null terminated strings in my messages to the teensy.
Be very careful.
"""

import threading

import http_client
import control
from database import Database
import cmd_shell
import arduino
import flask_app

# TODO: need single parameter definitions
# e.g. {"sp":74, "sp.min":68, "sp.max":80, "sp.step":0.5}

FK_LAN_ENABLED = True
FK_NO_RELOAD = True
BAUD_RATE = 9600
PORT = "COM5"

db = Database(
    name="data",
    sample_data={
        # User controlled parameters.
        "host": "10.0.0.10",
        "port": 80,
        "sp": 74,
        "threshold": 1.5,
        "sample_count": 3,
        "http_enabled": True,
        # Status parameters set by the running program.
        "current_temp": 0.0,
        "cooling_status": "off",
    })

http = http_client.Client(db)
http.set_timeout(30)
db["http_enabled"] = False

ctrl = control.SlidingWindowAverageCooling(
    database=db,
    sample_count=db["sample_count"],
    cb_above=lambda: http.request("POST", "/api/cooling/status", "enable"),
    cb_below=lambda: http.request("POST", "/api/cooling/status", "disable"),
)

device = arduino.Arduino(PORT, BAUD_RATE, ctrl)
device.start()

shell = cmd_shell.CommandShell(db)

flask_app.set_database(db)
app = flask_app.create_app()
t = threading.Thread(target=flask_app.run_app,
                     args=(app, FK_LAN_ENABLED, FK_NO_RELOAD),
                     daemon=True)
t.start()

shell.cmdloop()
