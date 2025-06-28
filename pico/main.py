from machine import Pin, I2C
import sys
import time
from MPU6050 import MPU6050

# --- LED Setup ---
led = Pin("LED", Pin.OUT)

# --- MPU6050 Setup ---
i2c = I2C(1, scl=Pin(15), sda=Pin(14))
mpu = MPU6050(i2c)
mpu.wake()

while True:
    command = sys.stdin.readline().strip()

    if command == "ON":
        led.on()

    elif command == "OFF":
        led.off()

    elif command == "READ":
        accel = mpu.read_accel_data()
        gyro = mpu.read_gyro_data()
        print("{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f}".format(
            accel[0], accel[1], accel[2], gyro[0], gyro[1], gyro[2]
        ))
