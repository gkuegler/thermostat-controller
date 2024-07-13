"""
Warning:
I use null terminated strings in my messages to the teensy.
Be very careful.
"""

import serial
import json

import http_client
import control

BAUD_RATE = 9600
PORT = "COM5"
TEMPERATURE_SETPOINT = 73

previous_time = 0

ctrl = control.SlidingWindowAverageCooling(76, 1, http_client.enable_cooling,
                                           http_client.disable_cooling, 5)

http_client.set_timeout(10)

with serial.Serial(PORT, BAUD_RATE, write_timeout=1, timeout=4) as s:
    while True:
        s.flush()
        try:
            msg = s.readline()
            # print(f"msg: {msg}")
            data = json.loads(msg)
            print(data["tempF"])

            # t = data["time"]

            # if previous_time == t:
            #     print("Sensor reading is stale.")
            #     continue

            # previous_time = t

            ctrl.update(data["tempF"])

        except json.JSONDecodeError as ex:
            print("Message not valid json.")
            ctrl.clear_buf()

