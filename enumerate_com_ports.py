import serial.tools.list_ports



if __name__ == "__main__":
    # Print out list of available serial ports.
    # Note that you can't send serial messages
    # when the serial monitor is open in the Arduino IDE.
    print("Available serial ports:")
    for p in serial.tools.list_ports.comports():
        print(f"{p.name}: {p.description}")
