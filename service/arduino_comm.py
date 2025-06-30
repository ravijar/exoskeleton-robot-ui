import serial
import serial.tools.list_ports
import threading
import time

arduino_ser = None  # Global serial object

def list_serial_ports():
    """Return a list of available COM ports."""
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def connect_to_arduino(port, baud=9600):
    """Connect to the specified Arduino port."""
    global arduino_ser
    try:
        arduino_ser = serial.Serial(port, baud, timeout=1)
        time.sleep(2)
        return True
    except Exception as e:
        print("Failed to connect to Arduino:", e)
        arduino_ser = None
        return False

def send_to_arduino(command):
    if arduino_ser and arduino_ser.is_open:
        try:
            arduino_ser.write((command + "\n").encode())
        except Exception as e:
            print("Failed to send to Arduino:", e)

def read_xyz_loop(callback):
    def loop():
        while True:
            if arduino_ser and arduino_ser.in_waiting:
                try:
                    line = arduino_ser.readline().decode().strip()
                    if line:
                        parts = line.split(",")
                        if len(parts) == 3:
                            x, y, z = map(float, parts)
                            callback(x, y, z)
                except:
                    pass
            time.sleep(0.1)
    threading.Thread(target=loop, daemon=True).start()
