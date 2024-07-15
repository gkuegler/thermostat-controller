""" 
Warning:
I use null terminated strings in my messages to the teensy.
Be very careful.
"""

import serial
import json
import threading

import http_client
import control
import database
import cmd_shell

class Arduino:
    def __init__(self, port, baud_rate, controller):
        self.port = port
        self.baud_rate = baud_rate
        self.controller = controller
        self.thread = threading.Thread(target=self.loop, daemon=True)

    def start(self):
        self.thread.start()

    def loop(self):
        with serial.Serial(self.port, self.baud_rate, write_timeout=1, timeout=15) as s:
            while True:
                s.flush()
                try:
                    # Block for arduino to send serial communications.
                    msg = s.readline()
                    # print(f"msg: {msg}")

                    data = json.loads(msg)

                    print(data["tempF"])

                    # Update controller with sensor data.
                    self.controller.update(data["tempF"])

                except json.JSONDecodeError as ex:
                    print("Message not valid json.")
                    # Tell controller pipelined data is no longer
                    # valid in filters, dsp, etc.
                    self.controller.clear_buf()
