1. Run sudo usermod -a -G dialout <username> to add your user to the "dialout" group.
2. Open a terminal and run ls /dev/tty* to list available serial ports. 
Note the port name, usually starting with /dev/ttyACM or /dev/ttyUSB. 
3. Use the screen command: screen /dev/ttyACM0 9600
Replace /dev/ttyACM0 with the correct serial port from your system.
Replace "9600" with the baud rate set on your Arduino.