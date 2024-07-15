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
import input

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

http = http_client.Client(config["host"], config["port"], mock=False)

ctrl = control.SlidingWindowAverageCooling(
    sp=config["host"],
    threshold=config["threshold"],
    sample_count=config["sample_count"],
    cb_above=lambda: http.request("POST", "/api/cooling/status", "enable"),
    cb_below=lambda: http.request("POST", "/api/cooling/status", "disable"),
)

input.start_command_shell(ctrl.set_sp, ctrl.set_threshold, http.set_timeout,
                          http.set_host, http.set_port)

http.set_timeout(30)

with serial.Serial(PORT, BAUD_RATE, write_timeout=1, timeout=15) as s:
    while True:
        s.flush()
        try:
            msg = s.readline()
            # print(f"msg: {msg}")

            data = json.loads(msg)

            print(data["tempF"])

            ctrl.update(data["tempF"])

        except json.JSONDecodeError as ex:
            print("Message not valid json.")
            ctrl.clear_buf()
