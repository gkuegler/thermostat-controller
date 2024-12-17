"""
Td = b * T + c * ln(RH/100)
Where
Td: is the dew point 
T: is the air temperature in degrees Celsius 
RH: is the relative humidity in percent 
b = 17.625 
c = 243.04°C
Need to convert to °C first.
"""

import math

ln = math.log

celsius = lambda T: (T - 32) * (5.0 / 9.0)
fahrenheit = lambda T: ((9.0 / 5.0) * T) + 32

a = 17.271
b = 237.7
dewpoint = lambda T, RH: (b * (ln(RH / 100.0) + (
    (a * T) / (b + T)))) / (a - ln(RH / 100.0) - ((a * T) / (b + T)))
"""
65, 20 => 24.0
65, 40 => 40.1
75, 20 => 31.3
75, 40 => 49.0
"""
for T, RH in [(65.0, 20.0), (65.0, 40.0), (75.0, 20.0), (75.0, 40.0)]:
    d = fahrenheit(dewpoint(celsius(T), RH))
    print(f"d: {d}")
