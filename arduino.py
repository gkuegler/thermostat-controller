""" 
Warning:
I use null terminated strings in my messages to the teensy.
Be very careful.
"""

import serial
import json
import threading
import time


class Arduino:

    def __init__(self, port, baud_rate, controller):
        self.port = port
        self.baud_rate = baud_rate
        self.controller = controller
        self.thread = threading.Thread(target=self.loop, daemon=True)

    def start(self):
        self.thread.start()

    def sample(self, s):
        # s.flush()
        try:
            # Block for arduino to send serial communications.
            data = json.loads(s.readline())
            print(data["tempF"])
            self.controller.update(data["tempF"], data["humidity"])
        except json.JSONDecodeError:
            print("Message not valid json.")
            # Tell controller pipelined data is no longer
            # valid in filters, dsp, etc.
            self.controller.clear_buf()

    def loop(self):
        while True:
            try:
                with serial.Serial(self.port,
                                   self.baud_rate,
                                   write_timeout=1,
                                   timeout=15) as s:
                    while True:
                        # Sample rate controlled by arduino.
                        # This thread blocks until next temp reading available.
                        self.sample(s)
            except serial.SerialException as ex:
                if ex.errno == 2:
                    print(f"Error Arduino not connected.")
                else:
                    print(ex)
            except Exception as ex:
                print(ex)
            finally:
                self.controller.clear_buf()
                time.sleep(2)
                continue
