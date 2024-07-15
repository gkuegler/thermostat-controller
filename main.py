""" 
Warning:
I use null terminated strings in my messages to the teensy.
Be very careful.
"""

import serial
import json

import http_client
import control
import database
import cmd_shell
import arduino

BAUD_RATE = 9600
PORT = "COM5"

config = database.Database(name="data",
                           sample_data={
                               "host": "10.0.0.83",
                               "port": 80,
                               "sp": 76,
                               "threshold": 1.5,
                               "sample_count": 3

                           })

http = http_client.Client(config["host"], config["port"], enabled=True)
http.set_timeout(30)
http.enable()

ctrl = control.SlidingWindowAverageCooling(
    sp=config["sp"],
    threshold=config["threshold"],
    sample_count=config["sample_count"],
    cb_above=lambda: http.request("POST", "/api/cooling/status", "enable"),
    cb_below=lambda: http.request("POST", "/api/cooling/status", "disable"),
)



device = arduino.Arduino(PORT, BAUD_RATE, ctrl)
device.start()

shell = cmd_shell.CommandShell(ctrl.set_sp, ctrl.set_threshold, http.set_timeout,
                          http.set_host, http.set_port, http.enable)

shell.cmdloop()