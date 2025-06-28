import serial
import time

PICO_PORT = "COM14"
BAUD_RATE = 115200

try:
    ser = serial.Serial(PICO_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
except Exception as e:
    ser = None
    print("Serial connection failed:", e)

def send_to_pico(command):
    if ser and ser.is_open:
        try:
            ser.write((command + "\n").encode())
        except Exception as e:
            print("Failed to send command:", e)
            
def read_response():
    if ser and ser.is_open:
        try:
            return ser.readline().decode().strip()
        except Exception as e:
            print("Failed to read:", e)
    return None
