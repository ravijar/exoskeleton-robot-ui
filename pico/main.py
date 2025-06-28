from machine import Pin
import sys

led = Pin("LED", Pin.OUT)

while True:
    command = sys.stdin.readline().strip()
    if command == "ON":
        led.on()
    elif command == "OFF":
        led.off()
