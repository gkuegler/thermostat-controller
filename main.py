""" 
Warning:
I use null terminated strings in my messages to the teensy.
Be very careful.
"""

import threading
import platform

import http_client
import control
from database import Database
import cmd_shell
import arduino
import flask_app
from sql import SQL

# TODO: need single parameter definitions to ensure type safety carried over to web interface
# e.g. {"sp":74, "sp.type":float, "sp.min":68, "sp.max":80, "sp.step":0.5}
# make a database verify types on database construction

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
    sample_count=db["sample_count"],
    cb_above=lambda: http.request("POST", "/api/cooling/status", "enable"),
    cb_below=lambda: http.request("POST", "/api/cooling/status", "disable"),
    sql=sql)

device = arduino.Arduino(PORT, BAUD_RATE, ctrl)
device.start()

shell = cmd_shell.CommandShell(db)

flask_app.set_database(db)
app = flask_app.create_app()
t = threading.Thread(target=flask_app.run_app,
                     args=(app, FLASK_LAN_ENABLED, FLASK_NO_RELOAD),
                     daemon=True)
t.start()

shell.cmdloop()
