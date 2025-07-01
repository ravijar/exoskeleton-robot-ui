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
        print(f"Connected to Arduino on {port}")
        return True
    except Exception as e:
        print("Failed to connect to Arduino:", e)
        arduino_ser = None
        return False

def send_to_arduino(command):
    if arduino_ser and arduino_ser.is_open:
        try:
            arduino_ser.write((command.strip() + "\n").encode())
            print(f"Sent to Arduino: {command}")
        except Exception as e:
            print("Failed to send to Arduino:", e)

def read_response_async(callback, expected_prefix):
    def loop():
        start_time = time.time()
        timeout = 3  # seconds

        while time.time() - start_time < timeout:
            try:
                if arduino_ser and arduino_ser.in_waiting:
                    line = arduino_ser.readline().decode(errors='ignore').strip()
                    print(f"[Serial Received] {line}")
                    if line.startswith(expected_prefix + ":"):
                        payload = line.split(":", 1)[1].strip()
                        callback(payload)
                        return
            except Exception as e:
                print("Error while reading from Arduino:", e)

            time.sleep(0.1)

        callback(None)

    threading.Thread(target=loop, daemon=True).start()

def get_encoder_value(callback):
        send_to_arduino("GET_ENCODER_VALUE")

        def handle_response(value_str):
            try:
                value = int(value_str)
                callback(value)
            except (ValueError, TypeError):
                print("Invalid encoder value:", value_str)
                callback(None)

        read_response_async(handle_response, expected_prefix="ENCODER_VALUE")