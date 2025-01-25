import serial
import json


class Arduino:
    def __init__(self, port, baud_rate):
        self.serial = serial.Serial(port=port,
                                    baudrate=baud_rate,
                                    write_timeout=1,
                                    timeout=15)

    def sample(self):
        # Sample rate controlled by arduino.
        # This thread blocks until next temp reading available.
        # Block for arduino to send serial communications.
        try:
            if not self.serial.is_open:
                self.serial.open()

            raw = self.serial.readline().decode(encoding="ASCII").rstrip()
            data = json.loads(raw)

            tempF = _t if isinstance(_t := data["tempF"],
                                     (int, float)) else None
            rh = _rh if isinstance(_rh := data["humidity"],
                                   (int, float)) else None

            print(str(tempF) + "°F")
            return tempF, rh
        except json.JSONDecodeError:
            print("Message not valid json.")
        except serial.SerialException as ex:
            if ex.errno == 2:
                print(f"Error Arduino not connected.")
            else:
                print(ex)
        except Exception as ex:
            print(ex)
        return None, None
