"""
Print out list of available serial ports.

Note: You can't send/receive serial messages from another
terminal when the serial monitor is open in the Arduino IDE.

Arduino UNO shows up as 'ttyACM...'.
"""

import serial.tools.list_ports

print("Available serial ports:")
for p in serial.tools.list_ports.comports():
    print(f"{p.device}: {p.subsystem}")
