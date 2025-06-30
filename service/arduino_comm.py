import serial
import serial.tools.list_ports
import threading
import time

arduino_ser = None  # Global serial object

def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def connect_to_arduino(port, baud=9600):
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

def read_response_async(callback, expected_prefix):
    """Reads the next matching message that starts with the expected prefix."""
    def loop():
        start_time = time.time()
        timeout = 3  # seconds
        while time.time() - start_time < timeout:
            if arduino_ser and arduino_ser.in_waiting:
                try:
                    line = arduino_ser.readline().decode().strip()
                    if line.startswith(expected_prefix + ":"):
                        payload = line.split(":", 1)[1]
                        callback(payload)
                        return
                except:
                    pass
            time.sleep(0.1)
        callback("❌ Timeout")

    threading.Thread(target=loop, daemon=True).start()
