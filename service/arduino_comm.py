import serial
import threading
import time

ARDUINO_PORT = "COM9"   # Update with actual COM port
BAUD_RATE = 9600

try:
    arduino_ser = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
except Exception as e:
    arduino_ser = None
    print("Arduino connection failed:", e)

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
