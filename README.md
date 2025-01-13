# System Architecture
Flask = controller interface
postgresql = logged temp data
arduino = get temp data through serial port

Temp & humidity data is read from arduino through serial port.
A sliding window filter averages temperatures.
An http put request is sent to esp32 based microcontroller acting as a relay.
Continuous enable messages must keep relay enabled as a safety.

Flask web interface is used to control temperature setpoint settings and display current measurements.
A cmd line utility also controls & displays the same.



(3) Services:
1. flask based thermostat
2. postgresql database
3. grafana web dashboard (gets info from postgresql)