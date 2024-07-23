""" 
Warning:
I use null terminated strings in my messages to the teensy.
Be very careful.
"""

import serial
import json

import http_client
import control
from database import Database
import cmd_shell
import arduino

BAUD_RATE = 9600
PORT = "COM5"

db = Database(name="data",
                           sample_data={
                               "host": "10.0.0.10",
                               "port": 80,
                               "sp": 74,
                               "threshold": 1.5,
                               "sample_count": 3,
                               "http_enabled": True
                           })

http = http_client.Client(db)
http.set_timeout(30)
db["http_enabled"]=False

ctrl = control.SlidingWindowAverageCooling(
    database=db,
    sample_count=db["sample_count"],
    cb_above=lambda: http.request("POST", "/api/cooling/status", "enable"),
    cb_below=lambda: http.request("POST", "/api/cooling/status", "disable"),
)



device = arduino.Arduino(PORT, BAUD_RATE, ctrl)
device.start()

shell = cmd_shell.CommandShell(db)

shell.cmdloop()