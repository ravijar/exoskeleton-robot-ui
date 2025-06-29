from machine import I2C, Pin
import time
import math
from MPU6050 import MPU6050

# --- I2C setup for both sensors ---
i2c0 = I2C(0, scl=Pin(1), sda=Pin(0))      # Sensor 1 (AD0 = GND → address 0x68)
i2c1 = I2C(1, scl=Pin(15), sda=Pin(14))    # Sensor 2 (AD0 = 3.3V → address 0x69)

# --- Initialize MPU6050 sensors ---
mpu1 = MPU6050(i2c0, address=0x68)
mpu2 = MPU6050(i2c1, address=0x69)

mpu1.wake()
mpu2.wake()

# --- Complementary filter parameters ---
pitch1 = 0.0
pitch2 = 0.0
alpha = 0.90
dt = 0.05

# --- Compute pitch and roll from accelerometer ---
def compute_pitch_roll(ax, ay, az):
    pitch = math.degrees(math.atan2(ax, math.sqrt(ay**2 + az**2)))
    roll = math.degrees(math.atan2(ay, math.sqrt(ax**2 + az**2)))
    return pitch, roll

# --- Convert pitch and roll to unit orientation vector ---
def get_vector(pitch, roll):
    pitch_rad = math.radians(pitch)
    roll_rad = math.radians(roll)
    vx = math.sin(roll_rad)
    vy = -math.sin(pitch_rad)
    vz = math.cos(roll_rad) * math.cos(pitch_rad)
    return (vx, vy, vz)

# --- Compute angle between two vectors ---
def vector_angle(v1, v2):
    dot = sum(a * b for a, b in zip(v1, v2))
    dot = max(min(dot, 1.0), -1.0)  # Clamp to avoid math domain errors
    return math.degrees(math.acos(dot))

# --- Main loop ---
while True:
    # Sensor 1
    ax1, ay1, az1 = mpu1.read_accel_data()
    gx1, _, _ = mpu1.read_gyro_data()
    accel_pitch1, accel_roll1 = compute_pitch_roll(ax1, ay1, az1)
    pitch1 += gx1 * dt
    pitch1 = alpha * pitch1 + (1 - alpha) * accel_pitch1
    roll1 = accel_roll1  # using accel-only for roll

    # Sensor 2
    ax2, ay2, az2 = mpu2.read_accel_data()
    gx2, _, _ = mpu2.read_gyro_data()
    accel_pitch2, accel_roll2 = compute_pitch_roll(ax2, ay2, az2)
    pitch2 += gx2 * dt
    pitch2 = alpha * pitch2 + (1 - alpha) * accel_pitch2
    roll2 = accel_roll2  # using accel-only for roll

    # Orientation vectors
    vec1 = get_vector(pitch1, roll1)
    vec2 = get_vector(pitch2, roll2)

    # 3D angle between rods
    bend_angle = vector_angle(vec1, vec2)

    # Display output
    print("3D Bending Angle: {:.2f}°"
          .format(pitch1, roll1, pitch2, roll2, bend_angle))

    time.sleep(dt)

